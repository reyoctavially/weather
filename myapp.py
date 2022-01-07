# import library yang dibutuhkan
import datetime
from os.path import dirname, join
import numpy as np
import pandas as pd
from scipy.signal import savgol_filter

# Import modul bokeh
from bokeh.io import curdoc
from bokeh.layouts import column, row
from bokeh.models import ColumnDataSource, DataRange1d, Select, Slider, Range1d
from bokeh.plotting import figure

# Memilih kolom yang digunakan yaitu temp, min, dan max
STATISTICS = ['temp', 'min', 'max']

def get_dataset(src, name, distribution):  # Membaca data dari dataset
    dataset = src[src.country == name].copy()
    del dataset['country']
    dataset['date'] = pd.to_datetime(dataset.date)
    dataset['left'] = dataset.date - datetime.timedelta(days=0.5)
    dataset['right'] = dataset.date + datetime.timedelta(days=0.5)
    dataset = dataset.set_index(['date'])
    dataset.sort_index(inplace=True)
    if distribution == 'Halus':  # Membuat distribusi halus agar data terlihat lebih halus
        window, order = 51, 3
        for key in STATISTICS:
            dataset[key] = savgol_filter(dataset[key], window, order)

    return ColumnDataSource(data=dataset)


def make_plot(source, title):  # Membuat plot
    plot = figure(x_axis_type="datetime", width=700,
                  tools="pan, wheel_zoom, box_zoom, reset", toolbar_location="below", y_range=Range1d(start=0, end=100))
    plot.title.text = title

    # Membuat plot untuk kolom maksimum
    plot.quad(top='max', bottom=0, left='left', right='right',
              color="#FFB061", source=source, legend_label="Maksimum")
    # Membuat plot untuk kolom rata-rata
    plot.quad(top='temp', bottom=0, left='left', right='right',
              color="#FDE5A9", source=source, legend_label="Rata-rata")
    # Membuat plot untuk kolom minimum
    plot.quad(top='min', bottom=0, left='left', right='right',
              color="#C6946F", source=source, legend_label="Minimum")

    # Menambahkan atribut yang akan ditampilkan
    plot.xaxis.axis_label = "Tanggal"
    plot.yaxis.axis_label = "Temperatur (F)"
    plot.axis.axis_label_text_font_style = "bold"
    plot.x_range = DataRange1d(range_padding=0.0)
    plot.grid.grid_line_alpha = 0.5

    return plot


def update_plot(attrname, old, new):  # Memperbarui plot sesuai negara yang dipilih
    country = country_select.value
    plot.title.text = "Data cuaca untuk " + countries[country]['title']

    src = get_dataset(dataset, countries[country]['country'],
                      distribution_select.value)
    source.data.update(src.data)


def update_zoom(attrname, old, new):  # Memperbarui plot sesuai negara yang dipilih
    global last_value
    if last_value is not None:
        if new > 0:
            if new > last_value:
                plot.y_range.start = plot.y_range.start + new
                plot.y_range.end = plot.y_range.end - new

                plot.x_range.start = plot.x_range.start + new
                plot.x_range.end = plot.x_range.end - new
            else:
                plot.y_range.start = plot.y_range.start - new
                plot.y_range.end = plot.y_range.end + new

                plot.x_range.start = plot.x_range.start - new
                plot.x_range.end = plot.x_range.end + new
        elif new < 0:
            if new < last_value:
                plot.y_range.start = plot.y_range.start + new
                plot.y_range.end = plot.y_range.end - new

                plot.x_range.start = plot.x_range.start + new
                plot.x_range.end = plot.x_range.end - new
            else:
                plot.y_range.start = plot.y_range.start - new
                plot.y_range.end = plot.y_range.end + new

                plot.x_range.start = plot.x_range.start - new
                plot.x_range.end = plot.x_range.end + new

    last_value = new


# Default negara dan distribusi yang akan ditampilkan
country = 'Indonesia'
distribution = 'Diskrit'

# Memilih negara apa saja yang akan ditampilkan
countries = {
    'Afrika Tengah': {
        'country': 'Central African Republic',
        'title': 'Afrika Tengah, Benua Arfika',
    },
    'Amerika Serikat': {
        'country': 'US',
        'title': 'Amerika Serikat, Benua Amerika',
    },
    'China': {
        'country': 'China',
        'title': 'China, Benua Asia',
    },
    'Indonesia': {
        'country': 'Indonesia',
        'title': 'Indonesia, Benua Asia',
    },
    'Inggris': {
        'country': 'United Kingdom',
        'title': 'Inggris, Benua Eropa',
    }
}

# Membuat dropdown
country_select = Select(value=country, title='Negara',
                        options=sorted(countries.keys()))
distribution_select = Select(
    value=distribution, title='Distribusi', options=['Diskrit', 'Halus'])

# Membaca dataset dalam format csv
dataset = pd.read_csv(join(dirname(__file__), 'data/weather.csv'))
# Menggunakan kolom country
source = get_dataset(dataset, countries[country]['country'], distribution)
# Menyesuakan judul berdasarkan isi dari kolom country
plot = make_plot(source, "Data cuaca untuk " + countries[country]['title'])

x = np.linspace(-40, 40, 200)
y = x

slider_zoom = Slider(title='Zoom', start=-12, end=8, value=0, step=1)
zoom_value = slider_zoom.value
last_value = None

# Update data dengan menggunakan fitur select
slider_zoom.on_change('value', update_zoom)
country_select.on_change('value', update_plot)
distribution_select.on_change('value', update_plot)

controls = column(country_select, distribution_select, slider_zoom)

curdoc().add_root(row(plot, controls))
curdoc().title = "Data Cuaca Tahun 2020"
