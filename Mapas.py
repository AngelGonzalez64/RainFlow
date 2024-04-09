#Archivo para la creacion de mapas de las ubicaciones de las estaciones y generar reporte del estado del los CSV (Finished)

import pandas as pd
import folium
import os

EXPECTED_COLUMNS = ["Year", "T2M_RANGE", "T2M_MAX", "T2M_MIN", "RH2M", "PRECTOTCORR", "WS10M_MAX", "WS10M_MIN"]

# Coordenadas de las estaciones
coordinates = {
    "Las_vegas": {
        "Latitud": 24.1851,
        "Longitud": -105.4652,
        "Altitud": 1700,
        "Tipo Horario": "UTC"
    },
    "San_Juan_de_Guadalupe": {
        "Latitud": 24.6375,
        "Longitud": -102.7827778,
        "Altitud": 1526,
        "Tipo Horario": "UTC"
    },
    "AgustinMelgar": {
        "Latitud": 25.26333333,
        "Longitud": -104.0661111,
        "Altitud": 1226,
        "Tipo Horario": "UTC"
    },
    "LAMICHILIADGO": {
        "Latitud": 23.38775,
        "Longitud": -104.247,
        "Altitud": 2464.492,
        "Tipo Horario": "UTC"
    }
}

def read_csv_files(file_list):
    property_file = None

    for file in file_list:
        if file.endswith('San_Juan_de_Guadalupe.csv'):
            property_file = file
            file_list.remove(file)

    if property_file:
        file_list = [property_file] + file_list

    dataframes = []
    status_messages = []  # Lista para almacenar los mensajes de estado
    for file in file_list:
        try:
            df = pd.read_csv(file)
            if all(col in df.columns for col in EXPECTED_COLUMNS):
                dataframes.append(df)
                station_name = file.split("/")[-1].split(".")[0]
                status_messages.append(f"✔ Archivo '{file}' leído correctamente con el orden de columnas esperado.")
                status_messages.append(f"■ ■ ■ Coordenadas de la estación '{station_name}':")
                status_messages.append(str(coordinates.get(station_name, "✘ Información de coordenadas no disponible.")))
                create_map(coordinates[station_name]["Latitud"], coordinates[station_name]["Longitud"], station_name)
            else:
                status_messages.append(f">>> El archivo '{file}' no tiene el orden de columnas esperado.")
        except FileNotFoundError:
            status_messages.append(f">>> El archivo '{file}' no fue encontrado.")
        except pd.errors.EmptyDataError:
            status_messages.append(f">>> El archivo '{file}' está vacío.")
        except pd.errors.ParserError:
            status_messages.append(f">>> Error al procesar el archivo '{file}'. Asegúrate de que sea un archivo CSV válido.")
        except Exception as e:
            status_messages.append(f">>> Ocurrió un error inesperado al leer el archivo '{file}': {e}")
    
    # Guardar los mensajes de estado en un archivo
    save_status_messages(status_messages)

    return dataframes

def create_map(lat, lon, station_name):
    map_center = [lat, lon]
    my_map = folium.Map(location=map_center, zoom_start=10)
    folium.Marker(location=map_center, popup=station_name).add_to(my_map)
    
    # Crear la carpeta "Mapas" si no existe
    if not os.path.exists("Mapas"):
        os.makedirs("Mapas")
    
    file_path = os.path.join("Mapas", f"{station_name}_map.html")
    my_map.save(file_path)

def save_status_messages(messages):
    # Crear la carpeta "Reports" si no existe
    if not os.path.exists("Reports"):
        os.makedirs("Reports")
    
    file_path = os.path.join("Reports", "status_csv.txt")
    with open(file_path, "w", encoding="utf-8") as file:  # Especificamos 'utf-8' para la codificación
        file.write("\n".join(messages))

# Lista de nombres de archivos CSV que deseas leer
file_list = ["csv/Las_vegas.csv", "csv/San_Juan_de_Guadalupe.csv", "csv/AgustinMelgar.csv", "csv/LAMICHILIADGO.csv"]

# Llama a la función para leer los archivos CSV
dataframes = read_csv_files(file_list)

# Ahora puedes usar los dataframes para realizar operaciones y análisis de datos.
