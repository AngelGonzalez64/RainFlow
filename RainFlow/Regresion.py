import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from sklearn.neural_network import MLPRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error

# Lee el archivo CSV
df = pd.read_csv('csv/San_guadalupe.csv')

# Selecciona las columnas relevantes para la predicción
columns = ['T2M_MAX', 'T2M_RANGE', 'T2M_MIN', 'RH2M', 'PRECTOTCORR', 'WS10M_MAX', 'WS10M_MIN']
data = df[columns]

# Divide los datos en características (X) y etiquetas (y)
X = data.iloc[:, 1:]  # Todas las columnas excepto la primera (fecha)
y = data.iloc[:, 0]   # Primera columna (T2M_MAX) 

# Divide los datos en conjuntos de entrenamiento y prueba
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Regresión lineal
linear_model = LinearRegression()
linear_model.fit(X_train, y_train)

# Predicción con regresión lineal
linear_predictions = linear_model.predict(X_test)
linear_mse = mean_squared_error(y_test, linear_predictions)

# Red Neuronal Artificial (RNA)
mlp_model = MLPRegressor(hidden_layer_sizes=(100,), activation='relu', random_state=42)
mlp_model.fit(X_train, y_train)

# Predicción con RNA
mlp_predictions = mlp_model.predict(X_test)
mlp_mse = mean_squared_error(y_test, mlp_predictions)

# Gráfica de regresión lineal
plt.scatter(y_test, linear_predictions)
plt.plot([min(y_test), max(y_test)], [min(y_test), max(y_test)], '--', color='red')
plt.xlabel('Valores reales')
plt.ylabel('Predicciones (Regresión Lineal)')
plt.title('Regresión Lineal - Predicciones vs. Valores reales')
plt.show()

# Gráfica de RNA
plt.scatter(y_test, mlp_predictions)
plt.plot([min(y_test), max(y_test)], [min(y_test), max(y_test)], '--', color='red')
plt.xlabel('Valores reales')
plt.ylabel('Predicciones (RNA)')
plt.title('RNA - Predicciones vs. Valores reales')
plt.show()

print("MSE (Regresión Lineal):", linear_mse)
print("MSE (RNA):", mlp_mse)
