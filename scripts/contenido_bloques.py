"""Bloques 3.1, 3.2 y 3.4 con la estructura de lección."""
import os

from diapositivas import Deck, SALIDA
from criterios_aceptacion import ACEPTA


def bloque_31():
    d = Deck(ACEPTA)
    d.portada("3.1", "Procedimientos de minería de datos",
              "3.1 · 3.1.1 Metodología CRISP-DM y preprocesamiento",
              "ENEMDU 2025 · 334.786 registros · 139 variables")
    d.mapa("3.1 · EL BLOQUE", "Lo que se ve en esta sesión", [
        ("3.1", "Procedimientos básicos de minería de datos",
         "Qué distingue un proyecto de datos de un ejercicio de software."),
        ("3.1.1", "Metodología CRISP-DM y preprocesamiento",
         "El proceso completo y la fase donde se decide el resultado."),
    ], pie="Bloque 1 de 4 · 100 minutos · la práctica se hace sobre la ENEMDU 2025")

    d.definicion("3.1.1 · QUÉ ES", "Un proceso, no un algoritmo",
                 "CRISP-DM (Cross Industry Standard Process for Data Mining) es un modelo "
                 "de proceso publicado en 1999 por SPSS, NCR y Daimler. Ordena un proyecto "
                 "de datos en seis fases y se recorre en ciclo: el resultado de la "
                 "evaluación puede devolver el trabajo a la preparación.",
                 ["Viene de la industria, no de la academia, y por eso habla de negocio y "
                  "de despliegue.",
                  "Cada fase tiene un producto verificable; sin él no se avanza.",
                  "El preprocesamiento es la fase 3 y concentra la mayor parte del esfuerzo."],
                 ["La pregunta del proyecto —dónde se concentra la vulnerabilidad laboral— "
                  "no se responde con la encuesta tal como llega.",
                  "139 columnas deben convertirse en una base con unidad de análisis, "
                  "denominadores y definiciones escritas.",
                  "Todo lo que se decida aquí condiciona el modelo de la sesión 3."],
                 pie="Fuente: CRISP-DM 1.0 (2000); Shearer (2000).")

    d.tabla("3.1.1 · LAS SEIS FASES", "Cada fase responde una pregunta",
            ["Fase", "Pregunta", "Producto"],
            [["1 · Comprensión del negocio", "¿Qué decisión se quiere apoyar?",
              "Objetivos y criterio de éxito"],
             ["2 · Comprensión de los datos", "¿Qué hay y qué calidad tiene?",
              "Diccionario, cobertura, inventario"],
             ["3 · Preparación", "¿Cómo se deja el dato listo para modelar?",
              "Base analítica y bitácora"],
             ["4 · Modelado", "¿Qué técnica responde la pregunta?",
              "Modelo ajustado y validado"],
             ["5 · Evaluación", "¿Sirve para la decisión, o solo para la métrica?",
              "Informe de resultados y límites"],
             ["6 · Despliegue", "¿Cómo se usa y se mantiene?",
              "Repositorio, guion, monitoreo"]],
            [3.2, 4.6, 4.2],
            pie="Las fases 1 a 3 ocupan cerca del 70% del tiempo en un proyecto real.")

    d.teoria("3.1.1 · PREPROCESAR", "Cuatro operaciones, en orden",
             ["Seleccionar: quedarse con las variables que responden la pregunta.",
              "Limpiar: tratar centinelas, perdidos y duplicados con criterio escrito.",
              "Transformar: recodificar, cambiar escala, construir derivadas.",
              "Verificar: cada paso deja un control que falla si algo se rompió."],
             ["dimensión:  139 → 29 columnas",
              "",
              "clases:     nominal / ordinal",
              "            intervalo / razón"],
             nota="La escala manda: un código nominal no se promedia, aunque venga como número.",
             pie="Fuente: Stevens (1946), sobre escalas de medida.")

    d.tabla("3.1.1 · CALIDAD", "Cinco preguntas antes de confiar en la base",
            ["Dimensión", "Pregunta", "En la ENEMDU 2025"],
            [["Completitud", "¿Cuántos faltan y por qué?",
              "188.650 sin ingreso: menores, inactivos y no respuesta"],
             ["Consistencia", "¿Los totales cuadran?",
              "Horas sobre 168 o ingreso negativo"],
             ["Unicidad", "¿Hay duplicados?", "id_persona debe ser único"],
             ["Validez", "¿El rango es posible?",
              "Máximo de ingreso tras quitar el 999999"],
             ["Oportunidad", "¿La fecha sirve?",
              "Doce meses de levantamiento en 2025"]],
            [2.5, 4.2, 5.3],
            pie="Tabla 01_centinelas.csv · el conteo se reporta, no se supone.")

    d.teoria("3.1.1 · TRANSFORMAR", "Tres arreglos que cambian el modelo",
             ["La asimetría se corrige con logaritmo; la escala, estandarizando.",
              "Las categóricas se vuelven indicadores, nunca números sueltos.",
              "Los atípicos se detectan con una regla previa y se reportan."],
             ["log1p(x)   ·   (x − μ) / σ",
              "",
              "IQR = q75 − q25",
              "atípico:  x < q25 − 1,5·IQR"],
             nota="El ingreso laboral tiene asimetría 9,2; en logaritmo baja a −0,9.",
             pie="Fuente: Tukey (1977), sobre la regla del rango intercuartílico.")
    d.criterios("3.1.1 · EL DATO", "Qué exige la ENEMDU y dónde se rompe",
               ["Unidad de análisis declarada: persona, hogar o provincia.",
                "Denominador coherente: ocupados, PEA o población de 15 y más.",
                "Factor de expansión aplicado en todo indicador.",
                "Criterio escrito para cada exclusión."],
               ["Centinelas: -1 y 999999 en ingreso no son datos.",
                "NA estructural: los menores de 15 no tienen condición de actividad.",
                "Definiciones que hay que construir: la informalidad no viene hecha.",
                "Borrar atípicos sin criterio previo y no reportarlo."],
               nota="En este curso cada transformación lleva un stopifnot que la verifica.",
               pie="")

    d.tabla("3.1.1 · LOS CÓDIGOS", "Qué hacer con cada valor raro",
            ["Código", "Qué significa", "Qué se hace"],
            [["-1 en ingreso", "No percibió ingreso o no respondió", "Pasar a NA y reportar cuántos"],
             ["999999 en ingreso", "Tope de no respuesta", "Pasar a NA, nunca dejarlo"],
             ["0 en ingreso", "Ocupado sin ingreso declarado", "Decidir y documentar"],
             ["NA en sector", "Menor de 15 o inactivo", "No imputar: excluir del denominador"],
             ["Blanco en horas", "No aplica a quien no trabaja", "No es cero: es no aplica"]],
            [2.9, 4.6, 4.5],
            pie="Script 01_crisp_dm.R · la tabla 01_centinelas.csv documenta el conteo.")

    d.definicion("3.1.1 · EXPLORAR", "Antes de modelar, mirar",
                 "El análisis exploratorio no es decorativo: decide. Cada gráfico de este "
                 "bloque responde una pregunta que cambia la base o el modelo, y todo lo que "
                 "se decide queda escrito en la bitácora.",
                 ["Distribución y atípicos: ¿conviene la media o la mediana?",
                  "Perdidos: distinguir el estructural del de no respuesta.",
                  "Cada hallazgo entra a la bitácora con fecha y criterio."],
                 ["La bitácora es el producto de la fase 3: qué se excluyó, con qué criterio "
                  "y qué efecto tuvo.",
                  "Sin ella el informe no se defiende cuando preguntan por qué quedan 144.103 "
                  "casos y no 161.906.",
                  "Es también lo que permite que otra persona repita el trabajo."],
                 pie="")
    d.pasos("3.1.1 · CÓMO SE HACE", "De la encuesta a la base analítica",
            [("Leer solo las columnas necesarias", "read_sav(col_select = vars)"),
             ("Verificar la integridad del archivo", "stopifnot(nrow(d) == 334786)"),
             ("Tratar centinelas y perdidos", "case_when(ingrl < 0 ~ NA)"),
             ("Recodificar con etiquetas", "factor(levels = , labels = )"),
             ("Ponderar y comprobar el indicador", "weighted.mean(x, fexp)")],
            pie="Script 01_crisp_dm.R · quedan 161.906 ocupados de 15 años y más")

    d.aplicacion("3.1.1 · APLICADO A LA ENEMDU", "La tasa no es la carga",
                 "09_informales_concentracion.png",
                 ["Guayas 947 mil · Pichincha 436 mil",
                  "Juntas, 32,4% de los informales",
                  "Morona 87,4%, pero solo 77 mil"],
                 pie="Fuente: INEC, ENEMDU 2025. Conteo expandido por fexp.")

    d.cierre("¿Preguntas?", "Siguiente: 3.2 · Análisis multivariante")
    return d


def bloque_32():
    d = Deck(ACEPTA)
    d.portada("3.2", "Análisis multivariante",
              "3.2 · 3.2.1 Componentes principales · 3.2.2 Conglomerados",
              "24 provincias · 9 indicadores · ENEMDU 2025")
    d.mapa("3.2 · EL BLOQUE", "Lo que se ve en esta sesión", [
        ("3.2", "Técnicas básicas de análisis multivariante",
         "Qué familias existen: reducir, agrupar y modelar dependencia."),
        ("3.2.1", "Análisis de componentes principales",
         "Nueve indicadores correlacionados se resumen en un eje."),
        ("3.2.2", "Análisis de conglomerados: k-medias y jerárquico",
         "Las 24 provincias se agrupan en dos o tres regímenes."),
    ], pie="Bloque 2 de 4 · 100 minutos · 24 casos, nueve variables")

    d.definicion("3.2 · QUÉ ES", "Estudiar varias variables a la vez",
                 "El análisis multivariante agrupa los métodos que estudian varias variables "
                 "en conjunto, considerando su correlación. Se ordenan en tres familias: "
                 "reducción de dimensión, agrupamiento de casos y modelos de dependencia.",
                 ["Reducir: PCA y análisis factorial buscan ejes que resuman la variabilidad.",
                  "Agrupar: jerárquico y k-medias buscan tipos de casos, sin etiqueta.",
                  "Depender: regresión múltiple, discriminante y MANOVA explican una variable "
                  "con las demás."],
                 ["Nueve indicadores provinciales son redundantes: informalidad y empleo "
                  "adecuado correlacionan a -0,95.",
                  "Primero se reduce a un eje de formalidad; después se agrupan las provincias.",
                  "Es exploratorio: describe estructura, no prueba causalidad."],
                 pie="Fuente: Hair, Black, Babin & Anderson (2019).")

    d.tabla("3.2 · LAS FAMILIAS", "Tres preguntas, tres métodos",
            ["Familia", "Métodos", "Pregunta que responde", "Supuesto clave"],
            [["Reducción", "PCA, factorial, correspondencias",
              "¿Cuántas dimensiones hay detrás?", "Variables correlacionadas y estandarizadas"],
             ["Agrupamiento", "Jerárquico, k-medias, DBSCAN",
              "¿Cuántos tipos de casos hay?", "Distancia definida y grupos compactos"],
             ["Dependencia", "Regresión múltiple, discriminante, MANOVA",
              "¿Qué explica a qué?", "Forma funcional y errores bien comportados"]],
            [2.2, 3.4, 3.4, 3.0],
            pie="Esta sesión cubre las dos primeras; la tercera se ve en estadística aplicada.")

    d.teoria("3.2.1 · PCA", "Cambiar de ejes, no de datos",
             ["Se estandariza para que ninguna variable pese por su escala.",
              "Cada componente es una combinación lineal de las originales y es ortogonal "
              "a las demás.",
              "El autovalor mide la varianza que recoge; su cociente, la proporción explicada."],
             ["Z   = (X − μ) / σ",
              "",
              "CPk = wk' Z,   Var(CPk) = λk",
              "",
              "λ1/Σλ = 0,626"],
             nota="Las cargas dicen qué variables forman el eje; los puntajes, dónde cae cada caso.",
             pie="Fuente: Jolliffe (2002).")

    d.criterios("3.2.1 · PCA", "Qué exige y dónde se rompe",
               ["Variables continuas o indicadores comparables entre sí.",
                "Correlación real: sin redundancia no hay nada que reducir.",
                "Entre 5 y 10 casos por variable.",
                "Criterio de retención fijado antes: Kaiser, codo o varianza acumulada."],
               ["Sin estandarizar, la variable con más unidades manda.",
                "Interpretar el eje sin leer las cargas.",
                "Retener componentes porque el gráfico queda bonito.",
                "Con 24 casos, tomar el resultado como prueba."],
               nota="En este curso: Kaiser si el autovalor supera 1; se reportan los tres criterios.",
               pie="")

    d.aplicacion("3.2.1 · CÍRCULO DE CORRELACIONES",
                 "Los cuadrantes dicen qué se opone a qué",
                 "02_circulo_correlaciones.png",
                 ["Derecha: empleo formal, horas, educación",
                  "Izquierda: informalidad y pobreza",
                  "Arriba el desempleo; abajo, ruralidad y mujeres"],
                 pie="Correlación de cada indicador con CP1 y CP2. Comunalidad = largo².")
    d.aplicacion("3.2.1 · APLICADO A LA ENEMDU", "El país en dos ejes",
                 "02_biplot.png",
                 ["Derecha: Pichincha y Galápagos",
                  "Izquierda: la Amazonía",
                  "El eje vertical separa Costa y Sierra"],
                 pie="Puntajes de las dos primeras componentes sobre 24 provincias.")

    d.teoria("3.2.2 · CONGLOMERADOS", "Agrupar es elegir una distancia",
             ["k-medias minimiza la suma de cuadrados dentro de cada grupo.",
              "Ward une de abajo hacia arriba minimizando el incremento de inercia.",
              "La silueta mide qué tan bien asignado está cada caso."],
             ["min Σk Σi∈Ck ||xi − μk||²",
              "",
              "s(i) = (b − a) / max(a, b)",
              "",
              "a = media al propio grupo"],
             nota="Con 24 casos, un grupo de dos provincias puede ser un artefacto estadístico.",
             pie="Fuente: Everitt, Landau, Leese & Stahl (2011).")

    d.criterios("3.2.2 · CONGLOMERADOS", "Qué exige y dónde se rompe",
               ["Distancia y método declarados antes de ver el resultado.",
                "Variables estandarizadas.",
                "Un criterio para el número de grupos.",
                "Cada grupo con más de dos casos y un perfil interpretable."],
               ["Elegir k por gusto y llamarlo codo.",
                "Nombrar un grupo mirando una sola variable.",
                "Probar métodos hasta que confirme la hipótesis.",
                "Presentar el dendrograma sin decir dónde se corta."],
               nota="Regla del curso: el k más pequeño con silueta a menos del 10% del máximo.",
               pie="")

    d.aplicacion("3.2.2 · APLICADO A LA ENEMDU", "Tres Ecuador, no veinticuatro provincias",
                 "03_grupos_provincia.png",
                 ["19 intermedias", "3 informal-rurales", "2 de enclave formal"],
                 pie="k-medias y Ward coinciden en el 100% de las asignaciones.")

    d.pasos("3.2 · CÓMO SE HACE", "De la matriz provincial a los grupos",
            [("Construir la matriz y estandarizar", "scale(X)"),
             ("Ajustar componentes y leer cargas", "prcomp(scale. = TRUE)"),
             ("Retener según varianza acumulada", "summary(pca)$importance"),
             ("Agrupar con k-medias y con Ward", "kmeans(nstart = 50) · hclust()"),
             ("Evaluar el corte con silueta", "cluster::silhouette()")],
            pie="Scripts 02_pca.R y 03_cluster.R")

    d.cierre("¿Preguntas?", "Siguiente: 3.3 · Aprendizaje automático")
    return d


def bloque_34():
    d = Deck(ACEPTA)
    d.portada("3.4", "Análisis temporal",
              "3.4 · 3.4.1 Descomposición y suavizado · 3.4.2 ARIMA",
              "60 meses de siniestros de tránsito · 2018-2022")
    d.mapa("3.4 · EL BLOQUE", "Lo que se ve en esta sesión", [
        ("3.4", "Técnicas básicas de análisis temporal",
         "Por qué una serie no se analiza como una tabla cualquiera."),
        ("3.4.1", "Descomposición y suavizado de series",
         "Separar tendencia, estacionalidad y residuo."),
        ("3.4.2", "Modelos ARIMA y pronóstico",
         "Modelar la dependencia y medir la incertidumbre del pronóstico."),
    ], pie="Bloque 4 de 4 · 100 minutos · la serie sale de siniestros, no de la ENEMDU")

    d.definicion("3.4 · QUÉ ES", "Observaciones que no son independientes",
                 "Una serie temporal es una sucesión de observaciones ordenadas en el tiempo, "
                 "donde el valor de hoy depende del de ayer. Esa dependencia rompe el supuesto "
                 "de independencia en que se apoyan las técnicas de las sesiones anteriores.",
                 ["Cuatro componentes: tendencia, estacionalidad, ciclo e irregular.",
                  "La frecuencia —mensual, trimestral— define qué es un ciclo.",
                  "Sin al menos dos ciclos completos no se puede hablar de estacionalidad."],
                 ["La ENEMDU 2025 trae 12 meses: alcanza para leer, no para modelar.",
                  "Se cambia de tabla y se mantiene el país: 60 meses de siniestros.",
                  "Elegir la fuente según el método es parte del trabajo."],
                 pie="Fuente: Hyndman & Athanasopoulos (2021).")

    d.tabla("3.4.1 · COMPONENTES", "Qué se separa y con qué",
            ["Componente", "Qué representa", "Cómo se identifica"],
            [["Tendencia", "Dirección de largo plazo", "Media móvil de 12 meses"],
             ["Estacionalidad", "Patrón que se repite cada año", "Gráfico estacional, STL"],
             ["Ciclo", "Oscilación de varios años", "No separable con 60 puntos"],
             ["Irregular", "Choque o ruido", "Residuo del modelo"]],
            [2.8, 4.4, 4.8],
            pie="Descomposición aditiva si la amplitud estacional es estable; multiplicativa si crece.")

    d.teoria("3.4.1 · ESTACIONARIEDAD", "La condición que casi nadie verifica",
             ["Estacionaria: media y varianza constantes, autocorrelación que depende solo "
              "del rezago.",
              "Diferenciar quita tendencia; diferenciar 12 meses quita estacionalidad.",
              "La ACF y el PACF dicen qué órdenes probar."],
             ["Yt = Tt + St + Rt",
              "",
              "ACF(k) = Cor(Yt, Yt−k)",
              "ΔYt = Yt − Yt−1"],
             nota="ADF y KPSS se contradicen a menudo: con 48 meses, ninguno decide solo.",
             pie="Fuente: Dickey & Fuller (1979); Kwiatkowski et al. (1992).")

    d.criterios("3.4 · ANTES DE MODELAR", "Qué exige y dónde se rompe",
               ["Frecuencia declarada y serie regular, sin huecos.",
                "Dos ciclos completos como mínimo.",
                "Quiebres identificados y modelados aparte.",
                "Validación temporal: el futuro se predice con el pasado."],
               ["Confundir tendencia con estacionalidad.",
                "Modelar 12 puntos como si fueran 60.",
                "Ignorar el quiebre y leerlo como residuo.",
                "Pronosticar sin banda de confianza."],
               nota="Un mes de 2020 no es un diciembre: los choques se tratan aparte.",
               pie="")

    d.teoria("3.4.2 · ARIMA", "Un modelo con memoria",
             ["AR: el valor depende de los rezagos anteriores de la serie.",
              "I: se diferencia hasta estabilizar el nivel.",
              "MA: el error también tiene memoria; SARIMA añade el ciclo estacional."],
             ["φ(B)(1−B)d yt = θ(B) εt",
              "",
              "(1−B)12 yt  quita la estacionalidad",
              "",
              "ARIMA(p,d,q)(P,D,Q)12"],
             nota="p y q se eligen por AIC y por diagnóstico del residuo, no por el test.",
             pie="Fuente: Box, Jenkins, Reinsel & Ljung (2015).")

    d.criterios("3.4.2 · ARIMA", "Qué exige y dónde se rompe",
               ["Estacionariedad comprobada, no supuesta.",
                "El quiebre modelado como intervención.",
                "Diagnóstico del residuo antes de usar el pronóstico.",
                "Comparación con el ingenuo estacional."],
               ["Elegir el modelo mirando el test.",
                "Interpretar un Ljung-Box que falla como si nada.",
                "Presentar el pronóstico como certeza.",
                "Ocultar que el ingenuo gana."],
               nota="Un pronóstico sin banda no es un pronóstico: es una opinión con decimales.",
               pie="")

    d.pasos("3.4 · CÓMO SE HACE", "De la serie cruda al intervalo",
            [("Construir la serie con su frecuencia", "ts(x, start = c(2018,1), frequency = 12)"),
             ("Descomponer y suavizar", "stl(s.window = 'periodic') · rollmean()"),
             ("Comprobar estacionariedad y leer el ACF", "adf.test() · kpss.test() · ggAcf()"),
             ("Ajustar y diagnosticar", "auto.arima() · checkresiduals()"),
             ("Pronosticar y comparar", "forecast(h = 12) · accuracy()")],
            pie="Scripts 06_series.R y 07_arima.R")

    d.aplicacion("3.4.1 · APLICADO A LOS SINIESTROS", "Tres cosas a la vez",
                 "06_stl.png",
                 ["Tendencia: la historia larga",
                  "Estacionalidad: diciembre y febrero",
                  "Residuo: el choque de 2020"],
                 pie="Serie mensual de víctimas, 2018-2022.")

    d.aplicacion("3.4.2 · APLICADO A LOS SINIESTROS", "El modelo pierde y hay que decirlo",
                 "07_pronostico.png",
                 ["ARIMA: RMSE 287",
                  "Ingenuo: 219",
                  "La banda no cubre 2022"],
                 pie="Pronóstico a 12 meses para 2022, banda al 80%.")

    d.cierre("¿Preguntas?", "Fin del bloque: repositorio e informe")
    return d


if __name__ == "__main__":
    os.makedirs(SALIDA, exist_ok=True)
    for nombre, constructor in [("01_procedimientos.pptx", bloque_31),
                                ("02_multivariante.pptx", bloque_32),
                                ("04_analisis_temporal.pptx", bloque_34)]:
        constructor().guardar(os.path.join(SALIDA, nombre))
        print("OK", nombre)
