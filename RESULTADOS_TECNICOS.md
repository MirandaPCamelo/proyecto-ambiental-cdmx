# Resultados técnicos

## Desarrollo del dashboard

Se desarrolló un dashboard interactivo en Streamlit para analizar las
concentraciones de PM2.5 registradas en el Valle de México durante
2024 y 2025.

La aplicación permite filtrar los registros por año, mes y estación de
monitoreo. También presenta indicadores generales, análisis
descriptivo, patrones temporales, comparación espacial entre estaciones
y resultados experimentales de modelos de aprendizaje automático.

## Resultados de regresión

El modelo Random Forest obtuvo el mejor desempeño entre los modelos
evaluados, con valores aproximados de:

- MAE: 7.31
- RMSE: 9.86
- R²: 0.283

La regresión lineal obtuvo un R² aproximado de 0.152, mientras que el
modelo Dummy presentó un R² cercano a -0.011.

Aunque Random Forest superó a las líneas base, su capacidad explicativa
fue moderada. Por ello, los resultados deben interpretarse como
experimentales.

## Resultados de clasificación

El modelo Random Forest Classifier obtuvo aproximadamente:

- Accuracy: 0.9045
- Precision: 0.331
- Recall: 0.332
- F1: 0.332
- ROC-AUC: 0.796
- PR-AUC: 0.277

La regresión logística obtuvo un recall aproximado de 0.747, lo que
indica una mayor capacidad para detectar episodios elevados. Sin
embargo, su precision fue menor, cercana a 0.146, lo que implica una
mayor cantidad de falsas alarmas.

## Consideraciones metodológicas

Los modelos fueron entrenados con datos de 2024 y evaluados con
registros de 2025.

El umbral utilizado para identificar episodios elevados se calculó a
partir del percentil 90 de los datos de entrenamiento. Este umbral tiene
un propósito exploratorio y académico, por lo que no representa un
criterio normativo oficial de calidad del aire.

## Limitaciones

- La disponibilidad de datos no fue uniforme entre todas las estaciones.
- Los registros faltantes pueden influir en los promedios temporales y
  espaciales.
- El mapa representa estaciones de monitoreo y no una superficie
  continua de contaminación.
- El modelo de regresión presentó una capacidad explicativa moderada.
- Los episodios elevados constituyen una clase minoritaria.
- El percentil 90 es un umbral exploratorio y no normativo.
- Los resultados no sustituyen sistemas oficiales de monitoreo,
  pronóstico o evaluación de calidad del aire.