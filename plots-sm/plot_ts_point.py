import netCDF4 as nc
import numpy as np
import matplotlib.pyplot as plt
import os
plt.style.use('seaborn-v0_8-dark')
import datetime


def get_datadir():
    return '/mnt/ypy3_5/land/gldas/data/2015/'


def get_fn():
    start_date = '20150201' 
    num_days = 28

    file_names = []

    for i in range(num_days):
        date_str = (datetime.datetime.strptime(start_date, '%Y%m%d') + datetime.timedelta(days=i)).strftime('%Y%m%d')
        
        for hour in range(0, 24, 3):
            file_name = f'GLDAS_NOAH025_3H.A{date_str}.{hour:02d}00.021.nc4'
            file_names.append(file_name) # file_names tiene los nombres de archivo para los N días
    return file_names


def read_ncfile(file_path):
    ds = nc.Dataset(file_path)
    return ds


def get_latlon():
    '''
    Manfredi: Lat -31.86,Lon -63.75
    Sombrerito - EEA Corrientes: Lat -27.65, Lon -58.77
    Colonia Popular - EEA Col Benitez: Lat -27.27,Lon -59.14
    '''
    point_lat = -27.27
    point_lon = -59.14
    return point_lat, point_lon


def filter_data_point(file_path, point_lat, point_lon):
    ds = read_ncfile(file_path)
    lon = ds.variables['lon'][:]
    lat = ds.variables['lat'][:]
    time_var = ds.variables['time']

    # Encontrar el índice más cercano a las coordenadas del punto de interés
    lat_index = np.abs(lat - point_lat).argmin()
    lon_index = np.abs(lon - point_lon).argmin()

    
    soil_data = ds.variables['SoilMoi0_10cm_inst'][:, lat_index, lon_index]
    rain_data = ds.variables['Rainf_f_tavg'][:, lat_index, lon_index]

    time_units = time_var.units
    time_values = nc.num2date(time_var[:], time_units)
     
    return soil_data, rain_data, lon[lon_index], lat[lat_index], time_values


def acum_data():
    file_names = get_fn()
    data_dir = get_datadir()

    soil_data_combined = []
    rain_data_combined = []
    time_values_combined = []


    for file_name in file_names:
        file_path = os.path.join(data_dir, file_name)
        point_lat, point_lon = get_latlon()
        soil_data, rain_data, _, _, time_values = filter_data_point(file_path, point_lat, point_lon)

        soil_data_combined.extend(soil_data)
        rain_data_combined.extend(rain_data)
        time_values_combined.extend(time_values)


    soil_data_combined = np.array(soil_data_combined)
    rain_data_combined = np.array(rain_data_combined)
    time_values_combined = np.array(time_values_combined)

    time_numeric = np.arange(len(time_values_combined))
    return time_numeric, soil_data_combined, rain_data_combined, time_values_combined


def plot_vble_point():
    '''
    Grafico de lineas para una variable en puntos de tiempo
    '''
    time_numeric, soil_data_combined, time_values_combined = acum_data()

    plt.figure(figsize=(10, 6))
    plt.plot(time_numeric, soil_data_combined, linestyle='-')
    #t = plt.title('GLDAS NOAH-Total precipitation rate\n\n15 days Mar 2015 - Sáenz Peña,Chaco\n')
    #t = plt.title('GLDAS NOAH-Soil Moisture (0_10cm)\n\n15 days Mar 2015 - Manfredi,Córdoba\n')
    t = plt.title('GLDAS NOAH-Soil Moisture (0_10cm underground)\n\n15 days Mar 2015 - Sáenz Peña,Chaco\n')
    t.set_fontsize(12)
    t.set_fontname('monospace')
    t.set_fontweight('semibold')
    plt.xlabel('Time', fontsize=10)
    # 0,01 m3/m3
    plt.ylabel('Total precipitation rate (kg m-2 s1) = (mm seg)', fontsize=10)
    #plt.ylabel('Soil Moisture (0_10cm) = (0,01 m3/m3)', fontsize=10)
    #plt.grid(True)
    #plt.xticks(time_numeric, time_values_combined, rotation=90, fontsize=6)
    plt.savefig('soil_region_sp.png', dpi=300, bbox_inches='tight')
    

def plot_vbles_point():
    '''
    Gráfico de líneas para dos variables en puntos de tiempo
    '''
    time_numeric, soil_data_combined, rain_data_combined, time_values_combined = acum_data()
    
    fig, ax1 = plt.subplots()

    #fig = fig.suptitle('GLDAS NOAH\nNovember 2022 - Manfredi,Córdoba', fontsize=9.5)
    fig = fig.suptitle('GLDAS NOAH\n February 2015 - Colonia Popular,Chaco', fontsize=9.5)
    #fig = fig.suptitle('GLDAS NOAH\nApril 2016 - El Sombrerito,Corrientes', fontsize=9.5)
    fig.set_fontweight('semibold')
    fig.set_fontname('monospace')
    #plotvlbe1
    color_one = 'tomato'
    ax1.plot(time_numeric, soil_data_combined, color='tomato', label='Soil moisture (0-10cm)') # alpha=0.5 
    ax1.set_ylabel('Soil moisture (kg m2) = (0,01 m3/m3)', fontsize=6)
    ax1.legend()
    ax1.tick_params(axis='y', labelcolor=color_one)
    #plotvble2
    ax2 = ax1.twinx()  # instantiate a second axes that shares the same x-axis
    color = 'royalblue'
    ax2.plot(time_numeric, rain_data_combined, color='royalblue', label='Total precipitation rate') 
    ax2.set_ylabel('Total precipitation rate (kg m-2 s1) = (mm seg)', fontsize=6)
    ax2.tick_params(axis='y', labelcolor=color)
    ax1.set_xlabel('Time', fontsize=8)

    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    lines = lines1 + lines2
    labels = labels1 + labels2
    ax1.legend(lines, labels, loc='upper right', fontsize=8)

    plt.tight_layout()
    plt.savefig('sm_tpr_point_cp.png', dpi=300, bbox_inches='tight')
    plt.show()

plot_vbles_point()