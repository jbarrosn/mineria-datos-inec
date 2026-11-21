"""Contenido de los siete juegos de diapositivas.

Cada bloque sigue el mismo recorrido: qué es la técnica, qué exige antes
de aplicarla, cómo se hace en R y cómo se ve aplicada a la ENEMDU.
"""
import os

from diapositivas import Deck, SALIDA

BLOCKS = [
    dict(
        archivo="01_crisp_dm", numero="01",
        portada=("El dato antes del modelo",
                 "3.1.1 · Metodología CRISP-DM y preprocesamiento",
                 "ENEMDU anual 2025 · 334.786 registros · 139 variables"),
        bloques=[
            dict(tipo="definicion",
                 kicker="3.1.1 · QUÉ ES",
                 titular="CRISP-DM no es un modelo: es el proceso",
                 definicion="Cross Industry Standard Process for Data Mining. Seis fases "
                            "publicadas en 1999 para llevar un proyecto de datos desde la "
                            "pregunta hasta el uso del resultado. Se recorre en ciclo: si la "
                            "evaluación falla, se vuelve a preparar el dato.",
                 claves=["Nació en la industria —SPSS, NCR, Daimler— y hoy es el estándar "
                         "de facto de la analítica.",
                         "Cada fase deja un producto que la siguiente necesita: no se "
                         "avanza con supuestos.",
                         "El preprocesamiento es la fase 3 y ahí se decide buena parte del "
                         "resultado."],
                 para_que=["La pregunta del proyecto —dónde y en quién se concentra la "
                           "vulnerabilidad laboral— no se responde con la encuesta tal como "
                           "viene.",
                           "Hay que convertir 139 columnas en una base con unidad de "
                           "análisis, denominadores y definiciones declaradas.",
                           "Ese trabajo es el 70% del proyecto."],
                 pie="Fuente: CRISP-DM 1.0 (2000)."),
            dict(tipo="criterios",
                 kicker="3.1.1 · ANTES DE APLICARLO",
                 titular="Qué exige y dónde se rompe",
                 exige=["Una unidad de análisis declarada: persona, hogar o provincia.",
                        "Un denominador coherente con la pregunta: ocupados, PEA o 15+.",
                        "Los pesos de expansión: sin fexp se describe la muestra.",
                        "Un criterio escrito para cada exclusión."],
                 cuidado=["Centinelas: el -1 y el 999999 del ingreso no son datos.",
                          "NA estructural: los menores de 15 no tienen condición de actividad.",
                          "Definiciones que hay que construir: la informalidad no viene hecha.",
                          "Borrar atípicos sin criterio previo y no reportarlo."],
                 nota="En este curso cada transformación lleva un control que falla si algo se rompe.",
                 pie="La encuesta documenta sus códigos: leerlos es parte de la fase 2."),
            dict(tipo="pasos",
                 kicker="3.1.1 · CÓMO SE HACE",
                 titular="De 139 columnas a una base analítica",
                 secuencia=[
                     ("Leer solo lo necesario, no las 139 columnas",
                      "read_sav(col_select = vars)"),
                     ("Verificar la estructura antes de tocar nada",
                      "stopifnot(nrow(d) == 334786)"),
                     ("Tratar centinelas y perdidos con criterio",
                      "case_when(ingrl < 0 ~ NA)"),
                     ("Recodificar con etiquetas, no con códigos",
                      "factor(levels = , labels = )"),
                     ("Ponderar y comprobar el indicador",
                      "weighted.mean(x, fexp)")],
                 nota_codigo="Script 01_crisp_dm.R · quedan 161.906 ocupados de 15 años y más.",
                 pie=""),
            dict(tipo="aplicacion",
                 kicker="3.1.1 · APLICADO A LA ENEMDU",
                 titular="La tasa no es la carga",
                 imagen_nombre="09_informales_concentracion.png",
                 ideas=["Guayas 947 mil · Pichincha 436 mil",
                        "Juntas, 32,4% de los informales del país",
                        "Morona 87,4%, pero solo 77 mil personas"],
                 pie="Fuente: INEC, ENEMDU 2025. Conteo expandido por fexp.")],
        cierre=("¿Preguntas?", "Siguiente: 02 · Análisis de componentes principales"),
    ),
    dict(
        archivo="02_pca", numero="02",
        portada=("Nueve indicadores, un eje",
                 "3.2.1 · Análisis de componentes principales",
                 "24 provincias · 9 indicadores · ENEMDU 2025"),
        bloques=[
            dict(tipo="definicion",
                 kicker="3.2 · QUÉ SON",
                 titular="Analizar varias variables a la vez",
                 definicion="El análisis multivariante estudia varias variables en conjunto. "
                            "Tres familias: reducir dimensiones (PCA, factorial), agrupar "
                            "casos (jerárquico, k-medias) y modelar dependencia (regresión "
                            "múltiple, discriminante, MANOVA).",
                 claves=["PCA reduce: ¿cuántas dimensiones hay detrás de nueve indicadores?",
                         "Cada componente es una combinación lineal de las variables "
                         "originales, no una de ellas.",
                         "Es exploratorio: describe estructura, no prueba causalidad."],
                 para_que=["Nueve indicadores provinciales están correlacionados entre sí: "
                           "informalidad y empleo adecuado llegan a r = -0,95.",
                           "No hacen falta nueve ejes. Con uno se ordena el país de lo "
                           "formal a lo informal.",
                           "Ese eje es el que después sirve para agrupar provincias."],
                 pie="Fuente: Hair et al., Análisis multivariante."),
            dict(tipo="criterios",
                 kicker="3.2.1 · ANTES DE APLICARLO",
                 titular="Qué exigir y qué vigilar",
                 exige=["Variables comparables: estandarizar si cambian de escala.",
                        "Muestra suficiente: entre 5 y 10 casos por variable.",
                        "Redundancia real: sin correlación no hay nada que reducir.",
                        "Criterio de retención fijado antes: Kaiser, codo o varianza."],
                 cuidado=["Sin estandarizar, la variable con más unidades manda.",
                          "Interpretar componentes sin leer las cargas.",
                          "Retener componentes porque «queda bonito el gráfico».",
                          "Leer la CP2 antes de saber qué variables la cargan."],
                 nota="Con 24 casos ningún PCA es estable: se lee como exploración, no como prueba.",
                 pie=""),
            dict(tipo="pasos",
                 kicker="3.2.1 · CÓMO SE HACE",
                 titular="De la matriz provincial a un índice",
                 secuencia=[
                     ("Construir la matriz 24 × 9 y estandarizar",
                      "scale(X)"),
                     ("Ajustar el PCA sobre la matriz Z",
                      "prcomp(scale. = TRUE)"),
                     ("Leer cargas y varianza explicada",
                      "pca$rotation · summary(pca)"),
                     ("Verificar la CP1 contra cada indicador",
                      "cor(scores$CP1, X[[v]])"),
                     ("Usar los puntajes como índice",
                      "pca$x[, 1]")],
                 nota_codigo="Script 02_pca.R · CP1 explica 62,6%; con la CP2, 79,6%.",
                 pie=""),
            dict(tipo="aplicacion",
                 kicker="3.2.1 · APLICADO A LA ENEMDU",
                 titular="El país en dos ejes",
                 imagen_nombre="02_biplot.png",
                 ideas=["Derecha: Pichincha y Galápagos",
                        "Izquierda: la Amazonía",
                        "El eje vertical separa Costa y Sierra"],
                 pie="Puntajes de las dos primeras componentes sobre 24 provincias.")],
        cierre=("¿Preguntas?", "Siguiente: 03 · Conglomerados"),
    ),
    dict(
        archivo="03_cluster", numero="03",
        portada=("Tres regímenes",
                 "3.2.2 · Análisis de conglomerados: k-medias y jerárquico",
                 "24 provincias · matriz estandarizada"),
        bloques=[
            dict(tipo="definicion",
                 kicker="3.2.2 · QUÉ ES",
                 titular="Agrupar casos que se parecen",
                 definicion="El agrupamiento busca grupos homogéneos dentro de los datos, sin "
                            "etiqueta previa. Dos familias: jerárquico, que construye un "
                            "dendrograma de abajo hacia arriba, y de partición, que reparte "
                            "los casos en k grupos.",
                 claves=["La distancia se elige antes: euclidiana es lo habitual con variables "
                         "estandarizadas.",
                         "k-medias pide el número de grupos; el jerárquico no.",
                         "La silueta mide qué tan bien asignado está cada caso."],
                 para_que=["Si el PCA mostró un eje de formalidad, la pregunta siguiente es "
                           "cuántos tipos de mercado laboral hay.",
                           "Aquí los casos son provincias: 24 observaciones, nueve "
                           "indicadores.",
                           "El resultado no son 24 provincias: son dos o tres regímenes."],
                 pie="Fuente: Everitt et al., Cluster Analysis."),
            dict(tipo="criterios",
                 kicker="3.2.2 · ANTES DE APLICARLO",
                 titular="Qué exigir y qué vigilar",
                 exige=["Distancia y método declarados antes de mirar el resultado.",
                        "Variables estandarizadas, o la escala decide los grupos.",
                        "Un criterio para el número de grupos.",
                        "Revisar que cada grupo tenga más de dos casos."],
                 cuidado=["Elegir k por gusto y llamarlo «criterio del codo».",
                          "Nombrar un grupo mirando una sola variable.",
                          "Comparar métodos y quedarse con el que confirma la hipótesis.",
                          "Con 24 casos, un grupo de dos provincias puede ser un artefacto."],
                 nota="Regla del curso: se toma el k más pequeño con silueta a menos del 10% del máximo.",
                 pie=""),
            dict(tipo="pasos",
                 kicker="3.2.2 · CÓMO SE HACE",
                 titular="Del dendrograma a tres grupos",
                 secuencia=[
                     ("Estandarizar y calcular la distancia",
                      "dist(Z, method = 'euclidean')"),
                     ("Construir el árbol con Ward",
                      "hclust(method = 'ward.D2')"),
                     ("Probar k y medir la silueta",
                      "kmeans(nstart = 50) · silhouette()"),
                     ("Comparar k-medias con el corte del árbol",
                      "mclust::adjustedRandIndex()"),
                     ("Perfilar cada grupo en unidades originales",
                      "group_by(grupo) · summarise()")],
                 nota_codigo="Script 03_cluster.R · k = 3; silueta 0,357; k-medias y Ward coinciden.",
                 pie=""),
            dict(tipo="aplicacion",
                 kicker="3.2.2 · APLICADO A LA ENEMDU",
                 titular="Tres Ecuador, no veinticuatro provincias",
                 imagen_nombre="03_grupos_provincia.png",
                 ideas=["19 intermedias",
                        "3 informal-rurales",
                        "2 de enclave formal"],
                 pie="Provincias ordenadas por informalidad y coloreadas por conglomerado.")],
        cierre=("¿Preguntas?", "Siguiente: 04 · Árboles y k-vecinos"),
    ),
    dict(
        archivo="04_arboles_knn", numero="04",
        portada=("Predecir sin preguntar de más",
                 "3.3.1 · Árboles de decisión y k-vecinos más cercanos",
                 "30.000 personas ocupadas · 9 predictores"),
        bloques=[
            dict(tipo="definicion",
                 kicker="3.3 · QUÉ ES",
                 titular="Aprender de los ejemplos",
                 definicion="El aprendizaje supervisado ajusta un modelo con ejemplos que ya "
                            "tienen respuesta, para predecir casos nuevos. Familias: árboles, "
                            "vecinos, modelos lineales y ensambles. No busca explicar el "
                            "mundo: busca acertar fuera de la muestra.",
                 claves=["El árbol parte el problema en preguntas y deja reglas legibles.",
                         "kNN no aprende: mide distancias y vota entre los vecinos.",
                         "La prueba de fuego es generalizar, no memorizar."],
                 para_que=["La pregunta: ¿se puede anticipar si alguien es informal sin "
                           "preguntarle por su establecimiento?",
                           "Se usan solo características conocidas antes del desenlace: edad, "
                           "sexo, educación, rama, horas.",
                           "El tamaño del establecimiento queda fuera: es la definición "
                           "disfrazada de variable."],
                 pie="Fuente: Hastie et al., The Elements of Statistical Learning."),
            dict(tipo="criterios",
                 kicker="3.3.1 · ANTES DE APLICARLO",
                 titular="Qué exigir y dónde se rompe",
                 exige=["Una variable objetivo con definición única.",
                        "Partición de entrenamiento y prueba antes de mirar métricas.",
                        "Predictores disponibles antes del desenlace.",
                        "Una métrica acorde al desbalance de clases."],
                 cuidado=["Fuga de información: el predictor define lo que se predice.",
                          "kNN sin escalar: las horas aplastan a la edad.",
                          "Clases desbalanceadas: la exactitud engaña.",
                          "Un árbol sin poda: decenas de hojas ilegibles."],
                 nota="Fuga de información: el modelo aprende la respuesta que ya estaba en otra columna.",
                 pie=""),
            dict(tipo="pasos",
                 kicker="3.3.1 · CÓMO SE HACE",
                 titular="Del dato a la regla de decisión",
                 secuencia=[
                     ("Descartar predictores que definen el desenlace",
                      "select(-p47a, -p49, -p48)"),
                     ("Partir la base antes de modelar",
                      "createDataPartition(p = 0.7)"),
                     ("Ajustar el árbol y elegir la poda",
                      "rpart(control = rpart.control(cp))"),
                     ("Ajustar kNN con variables escaladas",
                      "caret(method = 'knn', preProcess = c('center','scale'))"),
                     ("Comparar con la línea base aburrida",
                      "glm(informal ~ ., family = binomial)")],
                 nota_codigo="Script 04_arboles_knn.R · árbol de 5 hojas; k = 27 en kNN.",
                 pie=""),
            dict(tipo="aplicacion",
                 kicker="3.3.1 · APLICADO A LA ENEMDU",
                 titular="Cinco hojas que se explican solas",
                 imagen_nombre="04_arbol.png",
                 ideas=["Primera pregunta: categoría ocupacional",
                        "Segunda: rama de actividad",
                        "Ni la edad ni el sexo aparecen"],
                 pie="Árbol podado a cp = 0,01 sobre 21.001 casos de entrenamiento.")],
        cierre=("¿Preguntas?", "Siguiente: 05 · Validación y métricas"),
    ),
    dict(
        archivo="05_validacion", numero="05",
        portada=("Medir sin engañarse",
                 "3.3.2 · Validación cruzada y métricas de desempeño",
                 "21.001 de entrenamiento · 8.999 de prueba"),
        bloques=[
            dict(tipo="definicion",
                 kicker="3.3.2 · QUÉ ES",
                 titular="Estimar el desempeño en lo que no se vio",
                 definicion="Validar es medir el modelo con datos que no participaron en el "
                            "ajuste. Familias: partición simple, validación cruzada de k "
                            "pliegues y validación temporal para series. Cada una responde a "
                            "una estructura de datos distinta.",
                 claves=["La exactitud sola no sirve cuando una clase es mayoritaria.",
                         "El umbral de decisión es una elección, no un 0,5 natural.",
                         "El AUC mide ordenamiento; el F1, acierto con un umbral dado."],
                 para_que=["Tres modelos compiten: árbol, kNN y regresión logística.",
                           "Hay que decidir cuál va al informe y con qué costo.",
                           "La matriz de confusión dice a quién se equivoca, no solo cuánto."],
                 pie="Fuente: Kuhn & Johnson, Applied Predictive Modeling."),
            dict(tipo="criterios",
                 kicker="3.3.2 · ANTES DE VALIDAR",
                 titular="Qué exigir y dónde se rompe",
                 exige=["Separar prueba antes de tocar el modelo.",
                        "Elegir el umbral en entrenamiento, nunca en prueba.",
                        "Reportar sensibilidad y especificidad, no solo exactitud.",
                        "Repetir la validación para conocer la variación."],
                 cuidado=["Elegir el umbral mirando el test: es una forma de hacer trampa.",
                          "Una sola partición como si fuera el resultado.",
                          "Comparar modelos con métricas distintas.",
                          "Ocultar el diagnóstico cuando el modelo falla."],
                 nota="La línea base es obligatoria: un modelo que no le gana al azar no aporta.",
                 pie=""),
            dict(tipo="pasos",
                 kicker="3.3.2 · CÓMO SE MIDE",
                 titular="Del modelo a la decisión",
                 secuencia=[
                     ("Elegir el umbral con Youden en entrenamiento",
                      "pROC::coords(..., 'best', 'youden')"),
                     ("Construir la matriz de confusión",
                      "caret::confusionMatrix()"),
                     ("Calcular AUC y comparar curvas",
                      "pROC::roc() · auc()"),
                     ("Repetir con 5 pliegues y 3 repeticiones",
                      "trainControl(method = 'repeatedcv')"),
                     ("Reportar el error del modelo más simple",
                      "snaive() · meanf()")],
                 nota_codigo="Script 05_validacion.R · AUC: 0,933 · 0,931 · 0,884.",
                 pie=""),
            dict(tipo="aplicacion",
                 kicker="3.3.2 · APLICADO A LA ENEMDU",
                 titular="El modelo más simple gana",
                 imagen_nombre="05_roc.png",
                 ideas=["Logística 0,933", "kNN 0,931", "Árbol 0,884"],
                 pie="Curvas ROC sobre el 30% de prueba.")],
        cierre=("¿Preguntas?", "Siguiente: 06 · Descomposición de series"),
    ),
    dict(
        archivo="06_series", numero="06",
        portada=("Calendario e historia",
                 "3.4.1 · Descomposición y suavizado de series",
                 "60 meses de siniestros de tránsito · 2018-2022"),
        bloques=[
            dict(tipo="definicion",
                 kicker="3.4 · QUÉ ES",
                 titular="Datos ordenados en el tiempo",
                 definicion="Una serie temporal es una sucesión de observaciones que no son "
                            "independientes: lo de hoy depende de lo de ayer. Se descompone "
                            "en tendencia, estacionalidad, ciclo e irregular.",
                 claves=["La tendencia cuenta la historia larga; la estacionalidad, el "
                         "calendario.",
                         "Suavizar es elegir qué se quiere ver: ventana corta o larga.",
                         "Estacionaria: no cambia de nivel ni de varianza con el tiempo."],
                 para_que=["La ENEMDU 2025 trae 12 meses: alcanza para leer una serie, no para "
                           "modelarla.",
                           "Se cambia de tabla y se mantiene el país: siniestros de tránsito, "
                           "60 meses.",
                           "Elegir la fuente también es parte del trabajo."],
                 pie="Fuente: Hyndman & Athanasopoulos, Forecasting: Principles and Practice."),
            dict(tipo="criterios",
                 kicker="3.4.1 · ANTES DE APLICARLA",
                 titular="Qué exigir y dónde se rompe",
                 exige=["Frecuencia declarada: mensual, trimestral, anual.",
                        "Al menos dos ciclos completos para hablar de estacionalidad.",
                        "Revisar quiebres: una pandemia no es un patrón.",
                        "Separar tendencia de estacionalidad antes de interpretar."],
                 cuidado=["Confundir tendencia con estacionalidad.",
                          "Suavizar y creer que el dato cambió.",
                          "Modelar con 12 puntos como si fueran 60.",
                          "Ignorar un quiebre y leerlo como residuo."],
                 nota="Un mes de 2020 no es un diciembre: los choques se tratan aparte.",
                 pie=""),
            dict(tipo="pasos",
                 kicker="3.4.1 · CÓMO SE HACE",
                 titular="De la serie cruda a sus componentes",
                 secuencia=[
                     ("Construir el objeto de serie con su frecuencia",
                      "ts(x, start = c(2018, 1), frequency = 12)"),
                     ("Mirar la serie antes de cualquier modelo",
                      "autoplot() · ggseasonplot()"),
                     ("Descomponer con loess robusto",
                      "stl(s.window = 'periodic', robust = TRUE)"),
                     ("Suavizar con medias móviles",
                      "zoo::rollmean(x, k = 12, fill = NA)"),
                     ("Medir la fuerza de cada componente",
                      "1 - var(R) / var(S + R)")],
                 nota_codigo="Script 06_series.R · fuerza estacional 0,24; tendencia 0,53.",
                 pie=""),
            dict(tipo="aplicacion",
                 kicker="3.4.1 · APLICADO A LOS SINIESTROS",
                 titular="Tres cosas a la vez",
                 imagen_nombre="06_stl.png",
                 ideas=["Tendencia: la historia larga",
                        "Estacionalidad: diciembre y febrero",
                        "Residuo: el choque de 2020"],
                 pie="Serie mensual de víctimas, 2018-2022.")],
        cierre=("¿Preguntas?", "Siguiente: 07 · ARIMA y pronóstico"),
    ),
    dict(
        archivo="07_arima", numero="07",
        portada=("El pronóstico que pierde",
                 "3.4.2 · Modelos ARIMA y pronóstico",
                 "48 meses de entrenamiento · 12 de prueba"),
        bloques=[
            dict(tipo="definicion",
                 kicker="3.4.2 · QUÉ ES",
                 titular="Un modelo con memoria",
                 definicion="ARIMA describe una serie a partir de sus propios rezagos. AR: el "
                            "valor depende de los anteriores. I: se diferencia hasta "
                            "estabilizar. MA: el error también tiene memoria. SARIMA añade el "
                            "ciclo estacional.",
                 claves=["p, d, q son los órdenes de la parte regular; P, D, Q los de la "
                         "estacional.",
                         "Un ARIMA no conoce el futuro: extrapola el patrón que encontró.",
                         "El pronóstico se juzga contra el ingenuo, no contra cero."],
                 para_que=["Se entrena con 2018-2021 y se pronostica 2022, que el modelo nunca vio.",
                           "La comparación honesta es contra el ingenuo estacional y el "
                           "promedio.",
                           "El resultado incómodo es la lección: el ARIMA pierde."],
                 pie="Fuente: Hyndman & Athanasopoulos (2021)."),
            dict(tipo="criterios",
                 kicker="3.4.2 · ANTES DE AJUSTARLO",
                 titular="Qué exigir y dónde se rompe",
                 exige=["Estacionariedad comprobada, no supuesta: ADF y KPSS.",
                        "Un quiebre modelado como intervención, no como residuo.",
                        "Diagnóstico del residuo antes de usar el pronóstico.",
                        "Comparación contra una línea base.",
                        "Longitud suficiente: dos ciclos como mínimo."],
                 cuidado=["Pronosticar sin banda de confianza.",
                          "Elegir el modelo por el test.",
                          "Ignorar la autocorrelación que queda en el residuo.",
                          "Presentar un pronóstico como certeza."],
                 nota="Un pronóstico sin banda no es un pronóstico: es una opinión con decimales.",
                 pie=""),
            dict(tipo="pasos",
                 kicker="3.4.2 · CÓMO SE HACE",
                 titular="Del ACF al intervalo de pronóstico",
                 secuencia=[
                     ("Comprobar estacionariedad y leer el ACF",
                      "tseries::adf.test() · kpss.test()"),
                     ("Ajustar el modelo automático y uno manual",
                      "auto.arima() · Arima(order, seasonal)"),
                     ("Modelar el quiebre como variable externa",
                      "xreg = covid"),
                     ("Diagnosticar el residuo",
                      "checkresiduals() · Box.test()"),
                     ("Pronosticar y comparar con el ingenuo",
                      "forecast(h = 12) · accuracy()")],
                 nota_codigo="Script 07_arima.R · RMSE 287 del ARIMA frente a 219 del ingenuo.",
                 pie=""),
            dict(tipo="aplicacion",
                 kicker="3.4.2 · APLICADO A LOS SINIESTROS",
                 titular="El modelo pierde y hay que decirlo",
                 imagen_nombre="07_pronostico.png",
                 ideas=["El ARIMA pronostica por debajo",
                        "El ingenuo sigue mejor el nivel",
                        "La banda no cubre 2022"],
                 pie="Pronóstico a 12 meses para 2022, banda al 80%.")],
        cierre=("¿Preguntas?", "Fin del bloque: repositorio e informe"),
    ),
]


def construir(cfg):
    d = Deck()
    d.portada(cfg["numero"], *cfg["portada"])
    for bloque in cfg["bloques"]:
        b = dict(bloque)
        tipo = b.pop("tipo")
        getattr(d, tipo)(**b)
    d.cierre(*cfg["cierre"])
    ruta = os.path.join(SALIDA, cfg["archivo"] + ".pptx")
    d.guardar(ruta)
    return ruta


def main():
    os.makedirs(SALIDA, exist_ok=True)
    for cfg in BLOCKS:
        print("OK", construir(cfg))


if __name__ == "__main__":
    main()
