import pandas as pd
import matplotlib.pyplot as plt
import os
import json
import folium
import requests
import numpy as np
from sklearn.model_selection import train_test_split
import tensorflow as tf
import requests
from requests.exceptions import ConnectTimeout

# Coordenadas de las estaciones dentro del estado de Durango
coordinates = {
    "Las_vegas": {
        "Latitud": 24.1851,
        "Longitud": -105.4652,
        "Altitud": 1526,
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

# Límites geográficos del estado de Durango (aproximados)
durango_boundaries = {
    "north": 26.1,
    "south": 22.5,
    "west": -107.0,
    "east": -102.0
}

def get_elevation(lat, lon):
    url = f"https://api.open-elevation.com/api/v1/lookup?locations={lat},{lon}"
    
    try:
        response = requests.get(url, timeout=10)  # Ajustar el tiempo de espera según sea necesario
        data = response.json()
        elevation = data['results'][0]['elevation']
        return elevation
    except ConnectTimeout:
        print("Error: Tiempo de espera agotado al intentar conectarse al servicio de elevación API.")
        return None
    except Exception as e:
        print(f"Error al obtener la elevación: {e}")
        return None

def exploratory_analysis(dataframes, file_list):
    for i, df in enumerate(dataframes):
        station_name = file_list[i].split("/")[-1].split(".")[0]
        print(f"\n■ ■ ■ Análisis exploratorio de datos para la estación '{station_name}':")
        print(df.describe())

        # Gráficos para visualizar algunas variables
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

        # Guardar solo algunas estadísticas clave como datos JSON
        json_data = {
            "station_name": station_name,
            "statistics": {
                "min_temperature": df["T2M_RANGE"].min(),
                "max_temperature": df["T2M_RANGE"].max(),
                "mean_humidity": df["RH2M"].mean(),
                "total_precipitation": df["PRECTOTCORR"].sum(),
                "max_wind_speed": df["WS10M_MAX"].max()
            }
        }
        json_path = os.path.join(station_folder, f"{station_name}_statistics.json")
        with open(json_path, "w") as file:
            json.dump(json_data, file)

        print(f"Estadísticas guardadas para la estación '{station_name}'.")

def read_json_files(folder_path):
    json_data = []
    for file_name in os.listdir(folder_path):
        if file_name.endswith(".json"):
            file_path = os.path.join(folder_path, file_name)
            with open(file_path, "r") as file:
                data = json.load(file)
                json_data.append(data)
    return json_data

def filter_potential_locations(data, elevation_threshold=500):
    potential_locations = []
    for station_data in data:
        station_name = station_data["station_name"]
        lat = coordinates[station_name]["Latitud"]
        lon = coordinates[station_name]["Longitud"]
        elevation = coordinates[station_name].get("Altitud", 0)  # Utilizar altitud 0 si no está presente

        # Obtener la elevación en tiempo real si es 0
        if elevation == 0:
            elevation = get_elevation(lat, lon)
            coordinates[station_name]["Altitud"] = elevation

        # Verificar si la elevación cumple con el umbral y está dentro del estado de Durango
        if elevation > elevation_threshold and durango_boundaries["south"] <= lat <= durango_boundaries["north"] \
                and durango_boundaries["west"] <= lon <= durango_boundaries["east"]:
            potential_locations.append((lat, lon))

    return potential_locations

def create_interactive_map(potential_locations):
    map_center = [24.6, -103.6]  # Centro del mapa en las coordenadas de Durango (latitud, longitud)
    my_map = folium.Map(location=map_center, zoom_start=7)

    # Agregar diferentes vistas al mapa (vista satelital, vista de relieve, etc.)
    folium.TileLayer('openstreetmap').add_to(my_map)
    folium.TileLayer('Stamen Terrain').add_to(my_map)
    folium.TileLayer('Stamen Toner').add_to(my_map)
    folium.TileLayer('stamentonerlabels').add_to(my_map)

    # Crear un grupo de marcadores para las ubicaciones potenciales
    potential_group = folium.FeatureGroup(name='Ubicaciones Potenciales')
    my_map.add_child(potential_group)

    # Marcar las ubicaciones potenciales en el mapa con diferentes estilos
    for lat, lon in potential_locations:
        elevation = get_elevation(lat, lon)
        popup_content = f"Latitud: {lat}<br>Longitud: {lon}<br>Altitud: {elevation}"
        
        folium.Marker(
            location=[lat, lon],
            popup=folium.Popup(popup_content, parse_html=True),
            icon=folium.Icon(color='green', icon='info-sign')
        ).add_to(potential_group)
    
    # Agregar control de capas al mapa
    folium.LayerControl().add_to(my_map)

    # Guardar el mapa como archivo HTML
    map_file_path = os.path.join("Update", "potential_presa_locations_map.html")
    my_map.save(map_file_path)

    print("Mapa interactivo con las ubicaciones potenciales para la construcción de una presa generado.")

def prepare_data():
    # Leer los datos de las estadísticas desde los archivos .json y etiquetar las ubicaciones
    data = []
    labels = []
    for station_name in coordinates.keys():
        station_folder = os.path.join("Estaciones", station_name)
        station_data = read_json_files(station_folder)
        for data_point in station_data:
            elevation = coordinates[station_name]["Altitud"]
            label = 1 if elevation > 500 else 0  # 1 si es potencial, 0 si no lo es
            if "statistics" in data_point:
                data.append(list(data_point["statistics"].values()))
                labels.append(label)

    # Convertir los datos y etiquetas a arrays numpy
    data = np.array(data)
    labels = np.array(labels)

    # Dividir los datos en conjuntos de entrenamiento y prueba
    X_train, X_test, y_train, y_test = train_test_split(data, labels, test_size=0.2, random_state=42)

    return X_train, X_test, y_train, y_test

def create_and_train_model(X_train, y_train):
    # Crear el modelo de RNA
    model = tf.keras.Sequential([
        tf.keras.layers.Input(shape=(5,)),
        tf.keras.layers.Dense(64, activation='relu'),
        tf.keras.layers.Dense(1, activation='sigmoid')
    ])

    # Compilar el modelo
    model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])

    # Entrenar el modelo
    model.fit(X_train, y_train, epochs=50, batch_size=32)

    return model

def evaluate_model(model, X_test, y_test):
    # Evaluar el modelo en el conjunto de prueba
    loss, accuracy = model.evaluate(X_test, y_test)
    print(f"Pérdida en el conjunto de prueba: {loss}")
    print(f"Exactitud en el conjunto de prueba: {accuracy}")

def calculate_error_rate(y_true, y_pred):
    # Calcular el grado de error en porcentaje
    error_rate = np.mean(np.abs(y_true - y_pred)) * 100
    return error_rate

def main():
    # Lista de nombres de archivos CSV que deseas leer
    file_list = ["csv/Las_vegas.csv", "csv/San_Juan_de_Guadalupe.csv", "csv/AgustinMelgar.csv", "csv/LAMICHILIADGO.csv"]

    # Cargar los dataframes desde los archivos CSV
    dataframes = [pd.read_csv(file) for file in file_list]

    # Realizar el análisis exploratorio de datos y guardar estadísticas clave en archivos .json
    exploratory_analysis(dataframes, file_list)

    # Leer los datos de las estadísticas desde los archivos .json y etiquetar las ubicaciones
    X_train, X_test, y_train, y_test = prepare_data()

    # Crear y entrenar el modelo de RNA
    model = create_and_train_model(X_train, y_train)

    # Evaluar el modelo en el conjunto de prueba
    evaluate_model(model, X_test, y_test)

    # Evaluar el modelo en el conjunto de prueba
    loss, accuracy = model.evaluate(X_test, y_test)
    print(f"Pérdida en el conjunto de prueba: {loss}")
    print(f"Exactitud en el conjunto de prueba: {accuracy}")

    # Predecir las etiquetas en el conjunto de prueba
    y_pred = model.predict(X_test)
    y_pred_binary = np.round(y_pred)

    # Calcular el grado de error en porcentaje
    error_rate = calculate_error_rate(y_test, y_pred_binary)
    print(f"Grado de error en porcentaje: {error_rate:.2f}%")

    # Filtrar las ubicaciones potenciales basadas en las predicciones de la RNA
    potential_locations = []
    for i, station_data in enumerate(X_test):
        if y_pred_binary[i] == 1:  # Si la ubicación es predicha como potencial
            lat = station_data[0]
            lon = station_data[1]
            potential_locations.append((lat, lon))

    # Filtrar las ubicaciones potenciales dentro del estado de Durango
    filtered_potential_locations = [loc for loc in potential_locations if
                                    durango_boundaries["south"] <= loc[0] <= durango_boundaries["north"] and
                                    durango_boundaries["west"] <= loc[1] <= durango_boundaries["east"]]

    # List of potential locations' coordinates (lat, lon)
    potential_locations = [
        (24.6375, -102.7827778),
        (25.26333333, -104.0661111),
        (23.38775, -104.247)
    ]

    # Create an interactive map with potential locations
    create_interactive_map(potential_locations)

if __name__ == "__main__":
    main()
