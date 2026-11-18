"""Contenido y armado de los siete juegos de diapositivas.

Cuatro láminas por script: portada, figura con lectura, segunda
figura o código, y cierre. El enlace al repositorio va en todas.
"""
import os

from diapositivas import Deck, SALIDA

DECK = [
    dict(
        archivo="01_crisp_dm", numero="01",
        titulo="El dato antes del modelo",
        subtema="3.1.1 · CRISP-DM y preprocesamiento",
        datos="ENEMDU anual 2025 · 334.786 registros",
        fig1=("EL PROBLEMA", "La tasa no es la carga",
              "09_informales_concentracion.png",
              ["Guayas 947 mil · Pichincha 436 mil",
               "Juntas, 32,4% de los informales del país",
               "Morona 87,4%, pero solo 77 mil personas"],
              "Fuente: INEC, ENEMDU 2025. Conteo expandido por factor de expansión."),
        codigo=("EL CÓDIGO", "Limpiar es decidir, y hay que dejarlo escrito",
                ["ingreso <- case_when(",
                 "  ingrl < 0       ~ NA_real_,",
                 "  ingrl == 999999 ~ NA_real_,",
                 "  TRUE            ~ as.numeric(ingrl))",
                 "",
                 "stopifnot(all(ingreso >= 0 | is.na(ingreso)))"],
                "Un perdido no es un cero. Un centinela no es un dato."),
        siguiente="Siguiente: 02 · Componentes principales"),
    dict(
        archivo="02_pca", numero="02",
        titulo="Nueve cosas son una",
        subtema="3.2.1 · Análisis de componentes principales",
        datos="24 provincias · 9 indicadores · 12 meses",
        fig1=("LA REDUNDANCIA", "Nueve indicadores, una historia",
              "02_cargas.png",
              ["Informalidad y empleo adecuado: r = -0,95",
               "CP1 explica 62,6% de la varianza",
               "Con la CP2, el acumulado llega a 79,6%"],
              "Cargas factoriales sobre indicadores provinciales estandarizados."),
        fig2=("EL MAPA", "El país en un eje formal-informal",
              "02_biplot.png",
              ["Derecha: Pichincha y Galápagos",
               "Izquierda: la Amazonía",
               "El eje vertical separa Costa y Sierra"],
              "Puntajes de las dos primeras componentes."),
        siguiente="Siguiente: 03 · Conglomerados"),
    dict(
        archivo="03_cluster", numero="03",
        titulo="Tres regímenes",
        subtema="3.2.2 · Conglomerados: k-medias y jerárquico",
        datos="24 provincias estandarizadas",
        fig1=("LA DECISIÓN", "El k no se elige por gusto",
              "03_seleccion_k.png",
              ["La silueta máxima aparece en k = 5",
               "Regla previa: silueta a menos del 10% del máximo",
               "Con esa regla, k = 3"],
              "Codo y silueta sobre la misma matriz estandarizada."),
        fig2=("EL RESULTADO", "Tres Ecuador, no 24 provincias",
              "03_grupos_provincia.png",
              ["19 intermedias", "3 informal-rurales", "2 de enclave formal"],
              "k-medias y Ward coinciden en el 100% de las asignaciones."),
        siguiente="Siguiente: 04 · Árboles y k-vecinos"),
    dict(
        archivo="04_arboles_knn", numero="04",
        titulo="La trampa de la fuga",
        subtema="3.3.1 · Árboles de decisión y k-vecinos",
        datos="30.000 personas ocupadas",
        fig1=("LA TRAMPA", "Repetir la definición no es predecir",
              "04_arbol.png",
              ["El tamaño del establecimiento define la informalidad",
               "Incluirlo da 95% de exactitud y cero anticipación",
               "Tampoco entra el ingreso: es consecuencia"],
              "Árbol podado a cp = 0,01 sobre 21.001 casos de entrenamiento."),
        fig2=("K-VECINOS", "Elegir k es elegir el sesgo",
              "04_knn_k.png",
              ["k = 27 maximiza el AUC",
               "Con k pequeño la frontera se vuelve nerviosa",
               "kNN no explica el porqué de cada caso"],
              "Validación cruzada de 10 pliegues."),
        siguiente="Siguiente: 05 · Validación"),
    dict(
        archivo="05_validacion", numero="05",
        titulo="¿Con qué métrica se decide?",
        subtema="3.3.2 · Validación cruzada y métricas",
        datos="21.001 de entrenamiento · 8.999 de prueba",
        fig1=("LA COMPARACIÓN", "El modelo más simple gana",
              "05_roc.png",
              ["Logística: AUC 0,933",
               "kNN: 0,931",
               "Árbol de cinco hojas: 0,884"],
              "Curvas ROC sobre el 30% de prueba."),
        fig2=("EL COSTO", "Cada celda de la matriz es una decisión",
              "05_matriz_confusion.png",
              ["4.273 formales acertados",
               "547 informales perdidos",
               "680 falsos informales"],
              "Umbral elegido con Youden en entrenamiento, nunca en prueba."),
        siguiente="Siguiente: 06 · Series de tiempo"),
    dict(
        archivo="06_series", numero="06",
        titulo="Calendario e historia",
        subtema="3.4.1 · Descomposición y suavizado",
        datos="60 meses de siniestros de tránsito",
        fig1=("LA DESCOMPOSICIÓN", "Una serie son tres cosas a la vez",
              "06_stl.png",
              ["Fuerza estacional 0,24",
               "Fuerza de tendencia 0,53",
               "El residuo guarda el choque de 2020"],
              "Serie mensual de víctimas, 2018-2022."),
        fig2=("EL CALENDARIO", "Diciembre es el pico; febrero, el valle",
              "06_estacional.png",
              ["El patrón se repite cada año",
               "El nivel no",
               "Por eso hay que separarlos"],
              "Víctimas por mes, un año por línea."),
        siguiente="Siguiente: 07 · ARIMA"),
    dict(
        archivo="07_arima", numero="07",
        titulo="El pronóstico que pierde",
        subtema="3.4.2 · Modelos ARIMA y pronóstico",
        datos="48 meses de entrenamiento · 12 de prueba",
        fig1=("EL RESULTADO", "El modelo sofisticado no es el que acierta",
              "07_pronostico.png",
              ["ARIMA: RMSE 287",
               "Ingenuo estacional: 219",
               "Promedio histórico: 203"],
              "Pronóstico a 12 meses para 2022, banda al 80%."),
        fig2=("LA CONFIANZA", "A tres años, la banda es la noticia",
              "07_pronostico_largo.png",
              ["36 meses de proyección",
               "La banda se abre con el horizonte",
               "2025 quedó fuera del intervalo"],
              "Proyección desde 2022 y los tres meses observados de 2025."),
        siguiente="Fin del bloque: repositorio e informe"),
]


def construir(cfg):
    d = Deck()
    d.portada(cfg["numero"], cfg["titulo"], cfg["subtema"], cfg["datos"])
    d.figura(*cfg["fig1"])
    if "codigo" in cfg:
        d.codigo(*cfg["codigo"])
    else:
        d.figura(*cfg["fig2"])
    d.cierre("¿Preguntas?", cfg["siguiente"])
    ruta = os.path.join(SALIDA, cfg["archivo"] + ".pptx")
    d.guardar(ruta)
    return ruta


def main():
    os.makedirs(SALIDA, exist_ok=True)
    for cfg in DECK:
        print("OK", construir(cfg))


if __name__ == "__main__":
    main()
