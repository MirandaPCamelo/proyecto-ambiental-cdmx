from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st
ICONO = Path(__file__).parent / "iconoCDMX.png"
st.set_page_config(
    page_title="Análisis espacio-temporal y modelado de PM2.5",
    page_icon=str(ICONO),
    layout="wide",
    initial_sidebar_state="expanded"
)

# app.py se encuentra dentro de la carpeta app.
# parent.parent permite llegar a la carpeta principal ProyAmbiental.
CARPETA_PROYECTO = Path(__file__).resolve().parent.parent
CARPETA_RESULTADOS = CARPETA_PROYECTO / "resultados"

RUTA_DATASET = (
    CARPETA_RESULTADOS
    / "dataset_analisis_pm25_2024_2025.csv"
)

RUTA_METRICAS_REGRESION = (
    CARPETA_RESULTADOS
    / "tablas"
    / "metricas_modelos_regresion.csv"
)

RUTA_METRICAS_CLASIFICACION = (
    CARPETA_RESULTADOS
    / "tablas"
    / "metricas_clasificacion_episodios.csv"
)

@st.cache_data
def cargar_datos(ruta: Path) -> pd.DataFrame:
    """
    Carga el dataset principal y prepara las columnas necesarias
    para el dashboard.
    """

    if not ruta.exists():
        raise FileNotFoundError(
            f"No se encontró el archivo: {ruta}"
        )

    df = pd.read_csv(
        ruta,
        parse_dates=["DATETIME", "FECHA"],
        low_memory=False
    )

    columnas_obligatorias = {
        "DATETIME",
        "ANIO",
        "MES",
        "HORA_DIA",
        "ESTACION",
        "nom_estac",
        "PM25",
        "longitud",
        "latitud"
    }

    faltantes = columnas_obligatorias - set(df.columns)

    if faltantes:
        raise ValueError(
            "Faltan columnas obligatorias: "
            + ", ".join(sorted(faltantes))
        )
    return df

@st.cache_data
def cargar_csv_opcional(
    ruta: Path
) -> pd.DataFrame | None:
    """
    Carga un archivo CSV si existe.
    Si no existe, devuelve None.
    """

    if not ruta.exists():
        return None

    return pd.read_csv(ruta)

@st.cache_data
def convertir_csv(
    dataframe: pd.DataFrame
) -> bytes:
    """
    Convierte un DataFrame a CSV para permitir su descarga.
    """

    return dataframe.to_csv(
        index=False
    ).encode("utf-8-sig")

try:
    datos = cargar_datos(RUTA_DATASET)

except (FileNotFoundError, ValueError) as error:
    st.error(str(error))
    st.stop()

except Exception as error:
    st.error(
        "Ocurrió un error inesperado al cargar los datos."
    )
    st.exception(error)
    st.stop()
    
metricas_regresion = cargar_csv_opcional(
    RUTA_METRICAS_REGRESION
    )

metricas_clasificacion = cargar_csv_opcional(
    RUTA_METRICAS_CLASIFICACION
    )

st.title(
    "Análisis espacio-temporal y modelado de PM2.5"
)

st.markdown(
    """
    **Caso de estudio:** concentraciones de PM2.5 registradas en el
    Valle de México durante 2024–2025.

    El dashboard permite explorar patrones temporales y espaciales,
    comparar estaciones de monitoreo y consultar los resultados
    experimentales de modelos de aprendizaje automático.
    """
)

st.caption(
    "Laboratorio de Inteligencia Geo-Espacial y Cómputo Móvil, "
    "UPIITA–IPN"
)

st.divider()

st.sidebar.header("Filtros de consulta")

anios_disponibles = sorted(
    datos["ANIO"]
    .dropna()
    .astype(int)
    .unique()
    .tolist()
)

anios_seleccionados = st.sidebar.multiselect(
    "Año",
    options=anios_disponibles,
    default=anios_disponibles
)

nombres_meses = {
    1: "Enero",
    2: "Febrero",
    3: "Marzo",
    4: "Abril",
    5: "Mayo",
    6: "Junio",
    7: "Julio",
    8: "Agosto",
    9: "Septiembre",
    10: "Octubre",
    11: "Noviembre",
    12: "Diciembre"
}

meses_disponibles = sorted(
    datos["MES"]
    .dropna()
    .astype(int)
    .unique()
    .tolist()
)

meses_seleccionados = st.sidebar.multiselect(
    "Mes",
    options=meses_disponibles,
    default=meses_disponibles,
    format_func=lambda mes: nombres_meses.get(
        mes,
        str(mes)
    )
)

estaciones_disponibles = sorted(
    datos["ESTACION"]
    .dropna()
    .astype(str)
    .unique()
    .tolist()
)

estaciones_seleccionadas = st.sidebar.multiselect(
    "Estación",
    options=estaciones_disponibles,
    default=estaciones_disponibles
)

datos_filtrados = datos[
    datos["ANIO"].isin(anios_seleccionados)
    & datos["MES"].isin(meses_seleccionados)
    & datos["ESTACION"].isin(
        estaciones_seleccionadas
    )
].copy()

if datos_filtrados.empty:
    st.warning(
        "No existen registros para la combinación de filtros seleccionada."
    )
    st.stop()

    st.sidebar.markdown("---")

st.sidebar.write(
    f"**Registros mostrados:** "
    f"{len(datos_filtrados):,}"
)

csv_filtrado = convertir_csv(
    datos_filtrados
)

st.sidebar.download_button(
    label="Descargar datos filtrados",
    data=csv_filtrado,
    file_name="datos_pm25_filtrados.csv",
    mime="text/csv",
    use_container_width=True
)

total_registros = len(datos_filtrados)

total_estaciones = (
    datos_filtrados["ESTACION"]
    .nunique()
)

promedio_pm25 = (
    datos_filtrados["PM25"]
    .mean()
)

maximo_pm25 = (
    datos_filtrados["PM25"]
    .max()
)

percentil_90 = (
    datos_filtrados["PM25"]
    .quantile(0.90)
)

resumen_kpi_estaciones = (
    datos_filtrados
    .groupby(
        ["ESTACION", "nom_estac"],
        as_index=False
    )
    .agg(
        promedio_pm25=("PM25", "mean"),
        registros=("PM25", "count")
    )
)

estacion_mayor = (
    resumen_kpi_estaciones
    .sort_values(
        by="promedio_pm25",
        ascending=False
    )
    .iloc[0]
)

estacion_menor = (
    resumen_kpi_estaciones
    .sort_values(
        by="promedio_pm25",
        ascending=True
    )
    .iloc[0]
)

col1, col2, col3, col4, col5, col6 = st.columns(6)

col1.metric(
    "Registros",
    f"{total_registros:,}"
)

col2.metric(
    "Estaciones",
    f"{total_estaciones}"
)

col3.metric(
    "PM2.5 promedio",
    f"{promedio_pm25:.2f} µg/m³"
)

col4.metric(
    "PM2.5 máximo",
    f"{maximo_pm25:.2f} µg/m³"
)

col5.metric(
    "Mayor promedio",
    estacion_mayor["ESTACION"],
    f"{estacion_mayor['promedio_pm25']:.2f} µg/m³",
    delta_color="off"
)

col6.metric(
    "Menor promedio",
    estacion_menor["ESTACION"],
    f"{estacion_menor['promedio_pm25']:.2f} µg/m³",
    delta_color="off"
)

st.divider()

tab_resumen, tab_temporal, tab_espacial, tab_modelos = st.tabs(
    [
        "Resumen",
        "Análisis temporal",
        "Análisis espacial",
        "Modelos"
    ]
)

with tab_resumen:

    st.subheader(
        "Distribución de las concentraciones de PM2.5"
    )

    figura_distribucion = px.histogram(
        datos_filtrados,
        x="PM25",
        nbins=50,
        labels={
            "PM25": "Concentración de PM2.5"
        },
        title=(
            "Distribución de concentraciones "
            "para la selección actual"
        )
    )

    figura_distribucion.update_layout(
        yaxis_title="Frecuencia",
        showlegend=False
    )

    st.plotly_chart(
        figura_distribucion,
        width="stretch"
    )

    st.subheader("Estadística descriptiva")

    variables_resumen = [
        "PM25",
        "TMP",
        "RH",
        "WSP",
        "WDR"
    ]

    estadisticas = (
        datos_filtrados[variables_resumen]
        .describe()
        .T
        .round(2)
    )

    st.dataframe(
        estadisticas,
        width="stretch"
    )

with tab_temporal:

    st.subheader("Evolución temporal de PM2.5")

    # Promedio diario
    promedio_diario = (
        datos_filtrados
        .set_index("DATETIME")
        .resample("D")["PM25"]
        .mean()
        .reset_index()
    )

    figura_diaria = px.line(
        promedio_diario,
        x="DATETIME",
        y="PM25",
        labels={
            "DATETIME": "Fecha",
            "PM25": "PM2.5 promedio"
        },
        title="Concentración diaria promedio"
    )

    st.plotly_chart(
        figura_diaria,
        use_container_width=True
    )

    # Crear dos columnas
    columna_mensual, columna_horaria = st.columns(2)

    # Promedio mensual
    promedio_mensual = (
        datos_filtrados
        .groupby(
            ["ANIO", "MES"],
            as_index=False
        )["PM25"]
        .mean()
    )

    figura_mensual = px.line(
        promedio_mensual,
        x="MES",
        y="PM25",
        color="ANIO",
        markers=True,
        labels={
            "MES": "Mes",
            "PM25": "PM2.5 promedio",
            "ANIO": "Año"
        },
        title="Promedio mensual"
    )

    figura_mensual.update_xaxes(
        tickmode="array",
        tickvals=list(nombres_meses.keys()),
        ticktext=list(nombres_meses.values())
    )

    columna_mensual.plotly_chart(
        figura_mensual,
        use_container_width=True
    )

    # Promedio horario
    promedio_horario = (
        datos_filtrados
        .groupby(
            "HORA_DIA",
            as_index=False
        )["PM25"]
        .mean()
    )

    figura_horaria = px.line(
        promedio_horario,
        x="HORA_DIA",
        y="PM25",
        markers=True,
        labels={
            "HORA_DIA": "Hora del día",
            "PM25": "PM2.5 promedio"
        },
        title="Promedio por hora del día"
    )

    figura_horaria.update_xaxes(
        dtick=1
    )

    columna_horaria.plotly_chart(
        figura_horaria,
        use_container_width=True
    )



    mes_mayor = promedio_mensual.loc[
        promedio_mensual["PM25"].idxmax()
    ]

    hora_mayor = promedio_horario.loc[
        promedio_horario["PM25"].idxmax()
    ]

    nombre_mes_mayor = nombres_meses.get(
        int(mes_mayor["MES"]),
        str(int(mes_mayor["MES"]))
    )

    st.markdown("### Interpretación de la selección")

    if not promedio_mensual.empty and not promedio_horario.empty:
        fila_mes_mayor = promedio_mensual.loc[
            promedio_mensual["PM25"].idxmax()
        ]

        fila_hora_mayor = promedio_horario.loc[
            promedio_horario["PM25"].idxmax()
        ]

        numero_mes_mayor = int(fila_mes_mayor["MES"])

        nombre_mes_mayor = nombres_meses.get(
            numero_mes_mayor,
            str(numero_mes_mayor)
        )

        st.info(
            f"""
            Para la selección actual, el mayor promedio mensual se
            registró en **{nombre_mes_mayor} de
            {int(fila_mes_mayor['ANIO'])}**, con una concentración
            promedio de **{fila_mes_mayor['PM25']:.2f}**.

            El mayor promedio horario se presentó aproximadamente a las
            **{int(fila_hora_mayor['HORA_DIA']):02d}:00 horas**,
            con un valor de **{fila_hora_mayor['PM25']:.2f}**.
            """
        )

with tab_espacial:

    st.subheader("Concentración promedio por estación")

    resumen_estaciones = (
        datos_filtrados
        .groupby(
            [
                "ESTACION",
                "nom_estac",
                "longitud",
                "latitud"
            ],
            as_index=False
        )
        .agg(
            registros=("PM25", "count"),
            promedio_pm25=("PM25", "mean"),
            maximo_pm25=("PM25", "max")
        )
    )

    resumen_estaciones["promedio_pm25"] = (
        resumen_estaciones["promedio_pm25"]
        .round(2)
    )

    resumen_estaciones["maximo_pm25"] = (
        resumen_estaciones["maximo_pm25"]
        .round(2)
    )

    # Eliminar registros que no tengan coordenadas
    resumen_mapa = resumen_estaciones.dropna(
        subset=["latitud", "longitud"]
    ).copy()

    st.markdown("### Mapa interactivo de estaciones")

    centro_mapa = {
    "lat": resumen_mapa["latitud"].mean(),
    "lon": resumen_mapa["longitud"].mean()
}
    
    centro_mapa = {
        "lat": resumen_mapa["latitud"].mean(),
        "lon": resumen_mapa["longitud"].mean()
    }

    figura_mapa = px.scatter_map(
        resumen_mapa,
        lat="latitud",
        lon="longitud",
        color="promedio_pm25",
        size="registros",
        center=centro_mapa,
        zoom=9.5,
        hover_name="nom_estac",
        hover_data={
            "ESTACION": True,
            "promedio_pm25": ":.2f",
            "maximo_pm25": ":.2f",
            "registros": ":,",
            "latitud": False,
            "longitud": False
        },
        color_continuous_scale=[
            [0.00, "#2E7D32"],
            [0.35, "#F9A825"],
            [0.65, "#EF6C00"],
            [1.00, "#C62828"]
        ],
        height=650,
        labels={
            "ESTACION": "Clave",
            "promedio_pm25": "PM2.5 promedio",
            "maximo_pm25": "PM2.5 máximo",
            "registros": "Registros"
        },
        title="Distribución espacial del promedio de PM2.5"
    )

    figura_mapa.update_layout(
        map_style="open-street-map",
        margin={
            "r": 0,
            "t": 50,
            "l": 0,
            "b": 0
        }
    )

    st.plotly_chart(
        figura_mapa,
        use_container_width=True
    )

    st.markdown(
        "### Estaciones con mayor concentración promedio"
    )

    top_estaciones = (
        resumen_estaciones
        .sort_values(
            by="promedio_pm25",
            ascending=False
        )
        .head(10)
    )

    figura_top = px.bar(
        top_estaciones.sort_values(
            by="promedio_pm25",
            ascending=True
        ),
        x="promedio_pm25",
        y="ESTACION",
        orientation="h",
        hover_name="nom_estac",
        labels={
            "promedio_pm25": "PM2.5 promedio",
            "ESTACION": "Estación"
        },
        title="Diez estaciones con mayor promedio"
    )

    st.plotly_chart(
        figura_top,
        use_container_width=True
    )

    st.dataframe(
        top_estaciones,
        use_container_width=True,
        hide_index=True
    )



    st.markdown("### Interpretación de la selección")

    nombre_mayor = estacion_mayor["nom_estac"]
    clave_mayor = estacion_mayor["ESTACION"]
    valor_mayor = estacion_mayor["promedio_pm25"]

    nombre_menor = estacion_menor["nom_estac"]
    clave_menor = estacion_menor["ESTACION"]
    valor_menor = estacion_menor["promedio_pm25"]

    diferencia_estaciones = valor_mayor - valor_menor

    if total_estaciones == 1:
        st.info(
            f"""
            La selección actual contiene únicamente la estación
            **{nombre_mayor} ({clave_mayor})**, con una concentración
            promedio de PM2.5 de **{valor_mayor:.2f}**.
            """
        )
    else:
        st.info(
            f"""
            Para la selección actual, **{nombre_mayor} ({clave_mayor})**
            presenta la mayor concentración promedio de PM2.5,
            con **{valor_mayor:.2f}**.

            La concentración promedio más baja corresponde a
            **{nombre_menor} ({clave_menor})**, con
            **{valor_menor:.2f}**.

            La diferencia entre ambas estaciones es de
            **{diferencia_estaciones:.2f}**.
            """
        )

with tab_modelos:
    st.subheader(
        "Resultados experimentales de aprendizaje automático"
    )

    st.info(
        """
        Los modelos fueron entrenados con datos de 2024
        y evaluados con registros de 2025.
        """
    )
    
    st.markdown("### Modelos de regresión") 
    with st.expander(
        "¿Cómo se interpretan las métricas de regresión?"
    ):
        st.markdown(
            """
            - **MAE:** error promedio de las predicciones. Un valor menor
            representa un mejor desempeño.
            - **RMSE:** penaliza con mayor intensidad los errores grandes.
            También se busca un valor menor.
            - **R²:** proporción de la variabilidad explicada por el modelo.
            Un valor mayor representa una mayor capacidad explicativa.
            """
        )
    if metricas_regresion is None:

        st.warning(
            "No se encontró el archivo de métricas de regresión."
        )

    else:

        st.dataframe(
            metricas_regresion,
            width="stretch",
            hide_index=True
        )

        figura_regresion = px.bar(
            metricas_regresion,
            x="modelo",
            y="R2",
            labels={
                "modelo": "Modelo",
                "R2": "R²"
            },
            title="Comparación del R²"
        )

        st.plotly_chart(
            figura_regresion,
            width="stretch"
        )

    st.markdown("### Clasificación de episodios elevados")

    with st.expander(
        "¿Cómo se interpretan las métricas de clasificación?"
    ):
        st.markdown(
            """
            - **Precision:** de los episodios clasificados como elevados,
            indica cuántos realmente lo eran.
            - **Recall:** de todos los episodios elevados reales,
            indica cuántos logró detectar el modelo.
            - **F1:** representa el equilibrio entre precision y recall.
            - **ROC-AUC:** mide la capacidad general del modelo para
            diferenciar ambas clases.
            - **PR-AUC:** evalúa especialmente el desempeño sobre los
            episodios elevados, que son menos frecuentes.
            """
        )

    if metricas_clasificacion is None:

        st.warning(
            "No se encontró el archivo "
            "de métricas de clasificación."
        )

    else:

        st.dataframe(
            metricas_clasificacion,
            width="stretch",
            hide_index=True
        )

        metricas_largas = (
            metricas_clasificacion
            .melt(
                id_vars="modelo",
                value_vars=[
                    "precision",
                    "recall",
                    "f1"
                ],
                var_name="Métrica",
                value_name="Valor"
            )
        )

        figura_clasificacion = px.bar(
            metricas_largas,
            x="modelo",
            y="Valor",
            color="Métrica",
            barmode="group",
            range_y=[0, 1],
            labels={
                "modelo": "Modelo"
            },
            title=(
                "Precision, recall y F1 "
                "de los clasificadores"
            )
        )

        st.plotly_chart(
            figura_clasificacion,
            width="stretch"
        )
        st.warning(
            """
            **Nota metodológica:** los modelos y el umbral basado en el
            percentil 90 tienen un propósito exploratorio y académico.

            No representan un sistema oficial de pronóstico ni un criterio
            normativo de calidad del aire.
            """
)
        st.divider()
        st.caption(
            """
            Prototipo experimental desarrollado durante el Verano DELFÍN 2026.
            Los resultados no sustituyen criterios regulatorios ni evaluaciones oficiales de calidad del aire.
            """
    )