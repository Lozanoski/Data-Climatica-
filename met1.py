from tkinter.tix import Tree

Tree
try:
    import ee
    ee.Initialize()
except Exception:
    ee = None
    # Informative fallback: Google Earth Engine API not available.
    # To install: pip install earthengine-api and run `earthengine authenticate`.
    print("Warning: Google Earth Engine 'ee' not found. Install 'earthengine-api' and authenticate to use this script.")
import pandas as pd
try:
    import matplotlib.pyplot as plt
except Exception:
    plt = None
    print("Warning: matplotlib.pyplot not found. Install matplotlib to use plotting features.")
try:
    import seaborn as sns
except Exception:
    sns = None
    print("Warning: seaborn not found. Install seaborn to use plotting features.")

# Inicio desde la API De Google Earth Engine
import ee

# Trigger the authentication flow
ee.Authenticate()


# Initialize the library with your Google Cloud Project ID
ee.Initialize(project='YOUR_PROJECT_ID')
if ee is not None:
    ee.Initialize()
    
# Estilo de graficos

if sns is not None:
    sns.set(style="whitegrid")

# Coordenadas de area de analisis y periodo de analisis

point = ee.Geometry.Point([-10.347059, -64.340663]) 
start_date = '2013-01-01' 
end_date   = '2023-12-31'

# Analisis de coleccion de datos ERAS de Temperaturas minimas
# Extraccion de temperaturas maximas
temp_min = (
    ee.ImageCollection("ECMWF/ERA5/DAILY")
    .filterDate(start_date, end_date)
    .select("minimum_2m_air_temperature")
)
# Analisis de coleccion de datos ERAS de Precipitaciones 
precipitation = (
    ee.ImageCollection("ECMWF/ERA5/DAILY")
    .filterDate(start_date, end_date)
    .select("total_precipitation")
)

# Extraccion de temperaturas maximas
temp_max = (
    ee.ImageCollection("ECMWF/ERA5/DAILY")
    .filterDate(start_date, end_date)
    .select("maximum_2m_air_temperature")
)


# Extraccion y procesamiento de temperaturas minimas
temp_min_data = temp_min.getRegion(point, scale=1000).getInfo()
temp_min_df = pd.DataFrame(temp_min_data[1:], columns=temp_min_data[0])
temp_min_df['date'] = pd.to_datetime(temp_min_df['time'], unit='ms')
temp_min_df = temp_min_df[['date', 'minimum_2m_air_temperature']].dropna()
temp_min_df['minimum_2m_air_temperature'] = temp_min_df['minimum_2m_air_temperature'].astype(float)

# Función para procesar y graficar otras variables
def extract_and_process(image_collection, point, var_name):
    data = image_collection.getRegion(point, scale=1000).getInfo()
    df = pd.DataFrame(data[1:], columns=data[0])
    df['date'] = pd.to_datetime(df['time'], unit='ms')
    df = df[['date', var_name]].dropna()
    df[var_name] = df[var_name].astype(float)
    return df


# Extracción y procesamiento de precipitaciones y temperaturas

# Extraccion de precipitaciones

precip_df = extract_and_process(precipitation, point, 'total_precipitation')

precip_df['total_precipitation'] *= 1000
precip_df['year'] = precip_df['date'].dt.year
precip_yearly = precip_df.groupby('year')['total_precipitation'].sum()

# Temperaturas maximas
temp_max_df = extract_and_process(temp_max, point, 'maximum_2m_air_temperature')
temp_max_df['year'] = temp_max_df['date'].dt.year
temp_max_yearly = temp_max_df.groupby('year')['maximum_2m_air_temperature'].max()


# Temperaturas minimas

temp_min_df['year'] = temp_min_df['date'].dt.year
temp_min_yearly = temp_min_df.groupby('year')['minimum_2m_air_temperature'].min()


# Creacion de los graficos


# Creacion de graficos de precipitaciones acumuladas por año

plt.figure(figsize=(10, 6))
sns.barplot(x=temp_max_yearly.index, y=temp_max_yearly.values - 273.15, color='red')
plt.title('Temperaturas Máximas Anuales')
plt.xlabel('Año')
plt.ylabel('Temperatura Máxima (°C)')
plt.grid(True)
plt.show()

# Creacion de graficos de temperaturas maximas por año


plt.figure(figsize=(10, 6))
sns.barplot(x=temp_max_yearly.index, y=temp_max_yearly.values - 273.15, color='red')
plt.title('Temperaturas Máximas Anuales')
plt.xlabel('Año')
plt.ylabel('Temperatura Máxima (°C)')
plt.grid(True)
plt.show()

# Creacion de graficos de temperaturas minimas  por año 
plt.figure(figsize=(10, 6)) 
sns.barplot(x=temp_min_yearly.index, y=temp_min_yearly.values - 273.15, color='blue') 
plt.title('Temperaturas Mínimas Anuales') 
plt.xlabel('Año') 
plt.ylabel('Temperatura Mínima (°C)') 
plt.grid(True)
plt.show()


# Temperaturas minimas anuales absolutas

min_temp_value = temp_min_df['minimum_2m_air_temperature'].min()
print("Temperatura mínima más baja registrada:", min_temp_value - 273.15, "°C")


# Verificación de la fecha más reciente en la colección de datos
latest_date = temp_min.sort('system:time_start', False).first().date().format('YYYY-MM-dd').getInfo() 
print("La fecha más reciente disponible en la colección es:", latest_date)