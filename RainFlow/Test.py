# La primera version del proyecto "Maquetado" (Not working now)

import pandas as pd
import matplotlib.pyplot as plt
import os
import json
import folium

# Coordenadas de las estaciones
coordinates = {
    "Las_vegas": {
        "Latitud": 24.1851,
        "Longitud": -105.4652,
        #"Altitud": xxxxxx,
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

def exploratory_analysis(dataframes):
    for i, df in enumerate(dataframes):
        station_name = file_list[i].split("/")[-1].split(".")[0]
        print(f"\n■ ■ ■ Análisis exploratorio de datos para la estación '{station_name}':")
        print(df.describe())

        # Gráficos para visualizar las variables
        plt.figure(figsize=(12, 6))
        plt.subplot(2, 2, 1)
        plt.plot(df["Year"], df["T2M_RANGE"])
        plt.xlabel("Año")
        plt.ylabel("Rango de Temperatura (T2M_RANGE)")
        plt.title(f"Rango de Temperatura en la estación '{station_name}'")

        plt.subplot(2, 2, 2)
        plt.plot(df["Year"], df["RH2M"])
        plt.xlabel("Año")
        plt.ylabel("Humedad Relativa (RH2M)")
        plt.title(f"Humedad Relativa en la estación '{station_name}'")

        plt.subplot(2, 2, 3)
        plt.plot(df["Year"], df["PRECTOTCORR"])
        plt.xlabel("Año")
        plt.ylabel("Precipitación (PRECTOTCORR)")
        plt.title(f"Precipitación en la estación '{station_name}'")

        plt.subplot(2, 2, 4)
        plt.plot(df["Year"], df["WS10M_MAX"], label="WS10M_MAX")
        plt.plot(df["Year"], df["WS10M_MIN"], label="WS10M_MIN")
        plt.xlabel("Año")
        plt.ylabel("Velocidad del Viento (WS10M)")
        plt.title(f"Velocidad del Viento en la estación '{station_name}'")
        plt.legend()

        plt.tight_layout()

        # Crear carpeta para cada estación si no existe
        station_folder = os.path.join("Estaciones", station_name)
        if not os.path.exists(station_folder):
            os.makedirs(station_folder)

        # Guardar el gráfico como imagen
        image_path = os.path.join(station_folder, f"{station_name}_grafica.png")
        plt.savefig(image_path)
        plt.close()

        # Guardar los datos de la gráfica en un archivo .json
        json_data = {
            "station_name": station_name,
            "x_data": df["Year"].tolist(),
            "y_data": {
                "T2M_RANGE": df["T2M_RANGE"].tolist(),
                "RH2M": df["RH2M"].tolist(),
                "PRECTOTCORR": df["PRECTOTCORR"].tolist(),
                "WS10M_MAX": df["WS10M_MAX"].tolist(),
                "WS10M_MIN": df["WS10M_MIN"].tolist()
            }
        }
        json_path = os.path.join(station_folder, f"{station_name}_grafica_data.json")
        with open(json_path, "w") as file:
            json.dump(json_data, file)

        print(f"Gráfica y datos guardados para la estación '{station_name}'.")

def read_json_files(folder_path):
    json_data = []
    for file_name in os.listdir(folder_path):
        if file_name.endswith(".json"):
            file_path = os.path.join(folder_path, file_name)
            with open(file_path, "r") as file:
                data = json.load(file)
                json_data.append(data)
    return json_data

def filter_potential_locations(data, elevation_threshold=1000):
    potential_locations = []
    for station_data in data:
        station_name = station_data["station_name"]
        lat = coordinates[station_name]["Latitud"]
        lon = coordinates[station_name]["Longitud"]
        elevation = coordinates[station_name].get("Altitud", 0)
        
        # Verificar si la elevación cumple con el umbral y agregar a las ubicaciones potenciales
        if elevation > elevation_threshold:
            potential_locations.append((lat, lon))

    return potential_locations

def create_interactive_map(potential_locations):
    map_center = [24.6, -103.6]  # Centro del mapa en las coordenadas de Durango (latitud, longitud)
    my_map = folium.Map(location=map_center, zoom_start=7)

    # Marcar las ubicaciones potenciales en el mapa
    for lat, lon in potential_locations:
        folium.Marker(location=[lat, lon], popup="Ubicación Potencial").add_to(my_map)

    # Guardar el mapa como archivo HTML
    map_file_path = os.path.join("Update", "potential_presa_locations_map.html")
    my_map.save(map_file_path)

    print("Mapa interactivo con las ubicaciones potenciales para la construcción de una presa generado.")

# Lista de nombres de archivos CSV que deseas leer
file_list = ["csv/Las_vegas.csv", "csv/San_Juan_de_Guadalupe.csv", "csv/AgustinMelgar.csv", "csv/LAMICHILIADGO.csv"]

# Cargar los dataframes desde los archivos CSV
dataframes = [pd.read_csv(file) for file in file_list]

# Realizar el análisis exploratorio de datos y guardar gráficas en imágenes y archivos .json
exploratory_analysis(dataframes)

# Leer los datos de los archivos .json y filtrar las ubicaciones potenciales para la construcción de una presa
potential_data = []
for station_name in coordinates.keys():
    station_folder = os.path.join("Estaciones", station_name)
    station_data = read_json_files(station_folder)
    potential_data.extend(station_data)

potential_locations = filter_potential_locations(potential_data)

# Crear un mapa interactivo con las ubicaciones potenciales para la construcción de una presa
create_interactive_map(potential_locations)
