# ============================================================
# 08_documento.R — Documento maestro de la clase (DOCX)
# Se genera desde los resultados guardados por los scripts 01-07.
# Si cambia un número en el análisis, cambia en el documento.
# ============================================================

# --- configuración común -------------------------------------
# Se busca en las tres ubicaciones posibles: así funciona igual si
# se ejecuta desde la raíz, desde scripts/ o con el botón Source de
# RStudio, que suele dejar el directorio de trabajo en scripts/.
for (.p in c("scripts/00_setup.R", "00_setup.R", "../scripts/00_setup.R")) {
  if (file.exists(.p)) { source(.p); break }
}
if (!exists("SEMILLA")) {
  stop("No se encontró scripts/00_setup.R.\n",
       "  Abre mineria-inec.Rproj, o ejecuta desde la carpeta del proyecto.\n",
       "  Directorio actual: ", getwd())
}
rm(.p)
library(officer)
library(flextable)

set_flextable_defaults(font.family = "Calibri", font.size = 9,
                       theme_fun = function(x) theme_booktabs(x), padding = 3)

# --- cifras que se citan en el texto -------------------------
oc   <- readRDS(file.path(dir_datos, "ocupados.rds"))
ind  <- readRDS(file.path(dir_datos, "indicadores_provincia.rds"))
cl   <- readRDS(file.path(dir_datos, "clusters.rds"))
pca  <- readRDS(file.path(dir_datos, "pca.rds"))
val  <- readRDS(file.path(dir_datos, "validacion.rds"))
ar   <- readRDS(file.path(dir_datos, "arima.rds"))
ser  <- readRDS(file.path(dir_datos, "series.rds"))

inf_nac <- weighted.mean(oc$informal == 1, oc$fexp, na.rm = TRUE)
var_exp <- pca$pca$sdev^2 / sum(pca$pca$sdev^2)
tab_met <- val$tabla
rmse    <- ar$accuracy

# --- utilidades de escritura ---------------------------------
# Los textos van escritos en varias líneas por legibilidad del
# script; Word no interpreta esos saltos como espacios. Se normaliza.
limpia <- function(x) trimws(gsub("[[:space:]]+", " ", x))
H1 <- function(d, x) body_add_par(d, limpia(x), style = "heading 1")
H2 <- function(d, x) body_add_par(d, limpia(x), style = "heading 2")
P  <- function(d, x) body_add_par(d, limpia(x), style = "Normal")
Q  <- function(d, x) body_add_fpar(d, fpar(ftext(limpia(x), prop = fp_text(italic = TRUE, color = "#1F4E79", font.size = 10.5)),
                                        fp_p = fp_par(padding.left = 140, line_spacing = 1.15)))
B  <- function(d, x) body_add_fpar(d, fpar(
  ftext("\u2022  ", prop = fp_text(color = "#1F4E79", bold = TRUE)),
  ftext(limpia(x), prop = fp_text(font.size = 10.5)),
  fp_p = fp_par(padding.left = 240, line_spacing = 1.12)))
contador <- new.env(parent = emptyenv()); contador$n <- 0
N  <- function(d, x) {
  contador$n <- contador$n + 1
  body_add_fpar(d, fpar(
    ftext(paste0(contador$n, ".  "), prop = fp_text(bold = TRUE, color = "#1F4E79")),
    ftext(limpia(x), prop = fp_text(font.size = 10.5)),
    fp_p = fp_par(padding.left = 240, line_spacing = 1.12)))
}

foto <- function(d, archivo, ancho = 6.3, ratio = 0.7, pie = NULL) {
  ruta <- file.path(dir_fig, paste0(archivo, ".png"))
  d <- body_add_img(d, ruta, width = ancho, height = ancho * ratio)
  if (!is.null(pie)) d <- body_add_par(d, pie, style = "Normal")
  d
}

tabla <- function(d, x, pie = NULL, size = 9) {
  ft <- flextable(x) |>
    fontsize(size = size, part = "all") |>
    autofit()
  if (!is.null(pie)) ft <- set_caption(ft, pie)
  body_add_flextable(d, ft)
}

dir.create("docs", showWarnings = FALSE)
doc <- read_docx()
doc <- body_set_default_section(doc, prop_section(
  page_size = page_size(orient = "portrait", width = 8.27, height = 11.69),
  page_margins = page_mar(top = 2.1, bottom = 2.1, left = 2.3,
                          right = 2.3, header = 1, footer = 1)))

# ============================================================
# PORTADA
# ============================================================
doc <- body_add_fpar(doc, fpar(ftext("Minería de datos con R e información del INEC",
                                    prop = fp_text(font.size = 26, font.family = "Calibri",
                                                   bold = TRUE, color = "#1F4E79")),
                               fp_p = fp_par(padding.top = 60, padding.bottom = 6)))
doc <- body_add_fpar(doc, fpar(ftext(
  "Diseño de una clase en co-docencia (team teaching) para los temas 3.1 a 3.4",
  prop = fp_text(font.size = 14, font.family = "Calibri", color = "#404040")),
  fp_p = fp_par(padding.bottom = 18)))
doc <- P(doc, "")
doc <- P(doc, "Cuatro sesiones de 100 minutos. Un solo proyecto. Ocho scripts que corren de punta a punta.")
doc <- P(doc, "")
doc <- tabla(doc, tibble::tibble(
  Elemento = c("Asignatura", "Unidad", "Contenido", "Duración",
               "Modalidad", "Software", "Datos", "Requisito técnico"),
  Detalle = c("Minería de datos / Analítica de datos",
              "Unidad 3. Técnicas básicas",
              "3.1 a 3.4 del temario (CRISP-DM, multivariante, aprendizaje automático, series)",
              "4 sesiones de 100 minutos",
              "Co-docencia con dos profesores en el mismo espacio",
              "R 4.6 con tidyverse, caret, forecast, factoextra",
              "ENEMDU anual 2025 y siniestros de tránsito 2018-2025 (INEC)",
              "R y RStudio instalados; los datos ya están en el equipo")),
  size = 9)
doc <- body_add_par(doc, paste("Documento generado el", format(Sys.Date(), "%d/%m/%Y"),
                               "por scripts/08_documento.R"), style = "Normal")
doc <- body_add_break(doc)

# ============================================================
# 1. LA APUESTA
# ============================================================
doc <- H1(doc, "1. La apuesta: un proyecto con técnicas adentro")
doc <- P(doc,
 "La unidad 3 del temario lista seis técnicas. Enseñadas una detrás de otra producen
 lo de siempre: estudiantes que saben escribir prcomp() y no saben qué hacer cuando la
 matriz tiene un perdido, un centinela de 999999 y una provincia con 2.400 casos.
 La clase se organiza al revés: se elige un proyecto que obliga a usar las seis técnicas,
 y cada técnica entra cuando el proyecto la necesita.")
doc <- P(doc,
 "El proyecto es un observatorio de vulnerabilidad laboral con datos abiertos del INEC.
 La pregunta que lo sostiene todo el semestre: ¿dónde y en quién se concentra la
 vulnerabilidad laboral del Ecuador, y qué parte de ella se puede anticipar?")
doc <- Q(doc, "Regla de la clase: si no está en el script, no ocurrió. Ningún número del informe puede venir de la consola.")
doc <- P(doc, "Tres consecuencias prácticas de esa regla:")
doc <- B(doc, "Cada afirmación del estudiante tiene una línea de código que la produce.")
doc <- B(doc, "La semilla se fija una vez, al inicio, y se documenta.")
doc <- B(doc, "El script se ejecuta de cero, sin objetos que sobrevivan de la sesión anterior.")

# ============================================================
# 2. EL PROYECTO
# ============================================================
doc <- H1(doc, "2. El hilo conductor y sus cuatro productos")
doc <- P(doc,
 "Cada bloque del temario responde una pregunta del proyecto y deja un producto que
 el siguiente bloque vuelve a usar. Nada se hace dos veces y nada se hace para la basura.")
doc <- tabla(doc, tibble::tibble(
  Bloque = c("3.1", "3.2", "3.3", "3.4"),
  Pregunta = c("¿Qué datos sirven y en qué estado están?",
               "¿Cuántas dimensiones tiene la estructura laboral del país?",
               "¿Se puede anticipar la informalidad sin preguntar por el negocio?",
               "¿Qué se puede pronosticar y con qué confianza?"),
  Producto = c("Base analítica y bitácora de decisiones",
               "Índice de formalidad y tipología de provincias",
               "Comparación de tres clasificadores con métricas",
               "Descomposición, pronóstico y comparación con el ingenuo"),
  Script = c("01_crisp_dm.R", "02_pca.R y 03_cluster.R",
             "04_arboles_knn.R y 05_validacion.R",
             "06_series.R y 07_arima.R")),
  pie = "Tabla 1. El proyecto como hilo: cada bloque deja un insumo del siguiente.")
doc <- P(doc, "")
doc <- P(doc,
 "La elección del proyecto no es neutral. La ENEMDU tiene tres virtudes didácticas que
 un dataset de juguete no tiene: pesa (334.786 registros), trae valores perdidos que
 significan cosas distintas y tiene un factor de expansión que obliga a decidir entre
 describir la muestra o describir el país.")

# ============================================================
# 3. LOS DATOS
# ============================================================
doc <- H1(doc, "3. Los datos: qué se usa, por qué, y qué se paga por usarlo")
doc <- tabla(doc, tibble::tibble(
  Fuente = c("ENEMDU anual 2025, personas",
             "ENEMDU anual 2025, vivienda",
             "Diccionario y sintaxis 2025",
             "Siniestros de tránsito 2018-2022",
             "Siniestros de tránsito 2025 (I trimestre)"),
  Archivo = c("BDDenemdu_personas_2025_anual.sav (109 MB)",
              "BDDenemdu_vivienda_2025_anual.sav (62 MB)",
              "Diccionario_de_variables y Sintaxis_anual_2025",
              "ESTRA_2018 a ESTRA_2022 (SPSS)",
              "2025_SINIESTROS_BDD_ITRIMESTRE_SPSS.zip"),
  Uso = c("Unidad de análisis personas y provincias",
          "No se usa en esta versión: queda para el módulo de hogar",
          "Lectura del diccionario antes de tocar el modelo",
          "Serie mensual de víctimas: 60 puntos",
          "Control externo del pronóstico")),
  pie = "Tabla 2. Fuentes utilizadas. Todo el material es público y está en el directorio local.")
doc <- P(doc, "")
doc <- H2(doc, "3.1 Una decisión que hay que declarar: qué es un informal")
doc <- P(doc, sprintf(
 "La variable secemp del INEC clasifica a los ocupados en sector formal, sector informal,
 empleo doméstico y no clasificados. Si se toma solo el sector informal, la tasa nacional
 ponderada es %.1f%% (%s personas ocupadas). La definición amplia de empleo informal suma
 el servicio doméstico y los no clasificados, y sube varios puntos. La clase usa la
 definición estrecha y lo dice en voz alta, porque el informe tiene que poder defenderse.",
 100 * inf_nac, fmt_num(round(sum(oc$fexp[oc$informal == 1])))))
doc <- Q(doc, "Una definición no se elige por comodidad: se elige, se declara y se sostiene en todo el trabajo.")
doc <- H2(doc, "3.2 Por qué el bloque de series usa otra tabla")
doc <- P(doc,
 "La ENEMDU 2025 trae 12 meses. Con 12 puntos se puede leer una serie; no se puede
 descomponer ni ajustar un ARIMA estacional, que necesita al menos dos ciclos completos.
 En vez de forzar la tabla, se cambia de tabla y se mantiene el país: los siniestros de
 tránsito dan 60 meses continuos. El episodio se usa en clase para enseñar que el método
 impone requisitos sobre el dato, y que elegir la fuente es parte del trabajo.")
doc <- tabla(doc, tibble::tibble(
  Decisión = c("Usar ENEMDU y no el censo",
               "Ponderar con fexp",
               "Tratar -1 y 999999 como perdidos",
               "Excluir tamaño de establecimiento y RUC del modelo",
               "Excluir el ingreso del modelo de informalidad",
               "Agrupar categorías ocupacionales con menos de 1% de casos"),
  `Costo o justificación` = c("El censo no mide ingresos ni condición de actividad con el detalle que el proyecto necesita",
                            "Sin pesos el indicador describe la muestra, no el país",
                            "Son códigos de no respuesta, no ingresos de un dólar ni de un millón",
                            "Son parte de la definición de informalidad: incluirlos es fuga de información",
                            "Es consecuencia de la informalidad, no causa: incluirlo vuelve el problema tautológico",
                            "Evita ramas del árbol construidas con cuatro personas")),
  pie = "Tabla 3. Bitácora de decisiones de datos. Se entrega junto con el script.")

# ============================================================
# 4. CO-DOCENCIA
# ============================================================
doc <- H1(doc, "4. Cómo se reparte la clase entre dos profesores")
doc <- P(doc,
 "La co-docencia fracasa de una sola manera: dos monólogos alternados. Para evitarlo,
 cada sesión usa una de tres modalidades y cada profesor tiene una función distinta,
 no un turno distinto.")
doc <- tabla(doc, tibble::tibble(
  Modalidad = c("Dueto", "Estación rotativa", "Uno enseña, otro observa"),
  `Quién hace qué` = c("D1 conduce el teclado y narra; D2 interrumpe con la pregunta que el estudiante no hará",
                     "D1 sostiene la estación de código; D2 la de interpretación; los grupos rotan a mitad de sesión",
                     "D1 dicta; D2 registra errores y tiempos en una hoja y los devuelve al cierre"),
  Cuándo = c("Apertura de cada bloque y momentos de síntesis",
             "Práctica guiada del bloque 3.2",
             "Sesiones 1 y 3, mientras se corre el modelo")),
  pie = "Tabla 4. Tres modalidades de co-docencia y su uso en esta unidad.")
doc <- P(doc, "")
doc <- P(doc, "Cuatro acuerdos que se fijan antes de la primera sesión:")
doc <- N(doc, "D1 es el dueño del reloj. Solo D1 corta un bloque cuando se pasa de tiempo.")
doc <- N(doc, "D2 tiene derecho a interrumpir dos veces por bloque, y solo dos: la interrupción se prepara.")
doc <- N(doc, "Nadie corrige al otro frente al curso. La corrección se hace como pregunta: «¿y el factor de expansión?».")
doc <- N(doc, "El cierre lo hace siempre el profesor que no condujo el bloque: resumir es más difícil que ejecutar.")
doc <- P(doc, "")
doc <- tabla(doc, tibble::tibble(
  Sesión = c("1", "2", "3", "4"),
  "D1 · perfil de datos" = c("Conduce CRISP-DM y preprocesamiento",
                             "Estación de código (PCA y k-medias)",
                             "Observa y registra errores",
                             "Conduce descomposición"),
  "D2 · perfil metodológico" = c("Interrumpe con supuestos y validez",
                                 "Estación de interpretación",
                                 "Conduce árboles y validación",
                                 "Conduce ARIMA y diagnóstico")),
  pie = "Tabla 5. Reparto por sesión. Los perfiles se intercambian a mitad de la unidad a propósito.")

# ============================================================
# SESIÓN 1
# ============================================================
doc <- body_add_break(doc)
doc <- H1(doc, "5. Sesión 1 — Bloque 3.1: procedimientos básicos de minería de datos")
doc <- H2(doc, "Subtemas: 3.1.1 Metodología CRISP-DM y preprocesamiento")
doc <- P(doc, "Objetivo observable: al terminar, el estudiante construye una base analítica
 a partir de la ENEMDU, documenta cada transformación con su control y justifica por
 escrito tres decisiones de limpieza.")
doc <- P(doc, "Prerrequisito: saber leer una tabla y distinguir una fila de una columna.
 Diagnóstico de 5 minutos, dos preguntas:")
doc <- B(doc, "¿Qué significa que una persona tenga ingreso = -1 en la base?")
doc <- B(doc, "Si la muestra tiene 334.786 personas y el país 18 millones, ¿la media de la muestra es la media del país?")
doc <- P(doc,
 "Si la mayoría contesta «es un error» y «sí», la sesión arranca por el centinela y por
 el factor de expansión. Si contestan bien, se salta directo al modelo de datos.")
doc <- tabla(doc, tibble::tibble(
  Min = c("0-10", "10-25", "25-50", "50-60", "60-85", "85-100"),
  Momento = c("Activación", "Lectura del diccionario", "Del dato crudo a la base",
              "Corte", "Práctica guiada", "Cierre y bitácora"),
  "D1 conduce" = c("Muestra la cifra de informalidad y pregunta de dónde sale",
                   "Abre el diccionario y busca los centinelas en vivo",
                   "Escribe el script de limpieza, con stopifnot en cada paso",
                   "—",
                   "Acompaña la construcción de la base por parejas",
                   "Pide tres decisiones y su justificación"),
  "D2 interrumpe" = c("Pregunta qué unidad de análisis es cada fila",
                      "Pregunta qué significa cada perdido",
                      "Pregunta qué se pierde al borrar filas",
                      "Recoge las dudas del curso en el tablero",
                      "Revisa interpretación, no sintaxis",
                      "Cierra con la regla de la bitácora")),
  pie = "Tabla 6. Secuencia de la sesión 1.")
doc <- H2(doc, "Lo que queda en el tablero")
doc <- B(doc, "Un perdido no es un cero. Un centinela no es un dato.")
doc <- B(doc, "La unidad de análisis se declara antes de la primera línea de código.")
doc <- B(doc, "Cada transformación se verifica con un control que falla si algo se rompe.")
doc <- H2(doc, "Errores frecuentes y su corrección")
doc <- tabla(doc, tibble::tibble(
  Error = c("sum(x) devuelve NA y el indicador desaparece",
            "Calcular la tasa sin fexp",
            "Borrar los ingresos altos «porque son atípicos»",
            "Confundir «no aplica» con «no responde»"),
  Corrección = c("Escribir la condición sin NA contagioso: !is.na(x) & x == 1",
                 "Comparar la tasa ponderada y la simple en la misma tabla, y ver cuánto cambia",
                 "Excluir solo con criterio previo, documentado, y reportar el efecto sobre el resultado",
                 "Leer el diccionario: son dos códigos distintos y dos decisiones distintas")),
  pie = "Tabla 7. Errores de la sesión 1.")
doc <- P(doc, "Evidencia de aprendizaje (ticket de salida, 3 minutos): la base corre, el
 stopifnot pasa y el estudiante entrega tres líneas de bitácora con la decisión, el
 criterio y el efecto esperado.")

# ============================================================
# SESIÓN 2
# ============================================================
doc <- H1(doc, "6. Sesión 2 — Bloque 3.2: técnicas básicas de análisis multivariante")
doc <- H2(doc, "Subtemas: 3.2.1 Análisis de componentes principales · 3.2.2 Análisis de conglomerados: k-medias y jerárquico")
doc <- P(doc, "Objetivo observable: al terminar, el estudiante interpreta la primera
 componente de un PCA sobre provincias y asigna cada provincia a uno de tres regímenes
 laborales, justificando el número de grupos con dos criterios.")
doc <- P(doc, sprintf(
 "Punto de partida: 24 provincias y 9 indicadores. Las correlaciones son altas
 (informalidad y empleo adecuado, r = -0,95), y eso es exactamente lo que justifica
 reducir dimensiones. La primera componente explica %.1f%% de la varianza y la segunda
 %.1f%%; juntas, %.1f%%.",
 100 * var_exp[1], 100 * var_exp[2], 100 * sum(var_exp[1:2])))
doc <- tabla(doc, tibble::tibble(
  Min = c("0-10", "10-30", "30-45", "45-50", "50-80", "80-100"),
  Momento = c("Activación", "PCA: cargas y biplot", "Rotación de estaciones",
              "Corte", "Conglomerados", "Cierre"),
  "D1 · estación de código" = c("Pregunta cuántas variables hacen falta para describir una provincia",
                                "Estandariza, ajusta prcomp y lee las cargas",
                                "Recibe el grupo A: repite el PCA con ellos",
                                "—",
                                "Recibe el grupo B: codo, silueta, dendrograma",
                                "Verifica que el código corra"),
  "D2 · estación de interpretación" = c("Pregunta qué significa «provincia formal»",
                                        "Interroga el signo de cada carga y el nombre que se le pone",
                                        "Recibe el grupo B: interpreta el biplot",
                                        "—",
                                        "Recibe el grupo A: nombra los grupos con su perfil",
                                        "Cierra con la regla del nombre")),
  pie = "Tabla 8. Secuencia de la sesión 2, con estación rotativa.")
doc <- H2(doc, "Lo que queda en el tablero")
doc <- B(doc, "Sin estandarizar, la componente uno es «ingreso» y nada más.")
doc <- B(doc, "Una componente se puede leer en los dos sentidos; la convención se escribe.")
doc <- B(doc, "El número de grupos se decide con un criterio declarado antes de mirar el resultado.")
doc <- H2(doc, "Errores frecuentes y su corrección")
doc <- tabla(doc, tibble::tibble(
  Error = c("Ajustar el PCA sin estandarizar",
            "Interpretar la CP2 sin mirar las cargas",
            "Elegir k por gusto y llamarlo «criterio del codo»",
            "Nombrar un grupo mirando una sola variable"),
  Corrección = c("Comparar las cargas con y sin scale = TRUE y mostrar cómo cambia la historia",
                 "Leer la tabla de cargas antes del biplot y escribir una frase por componente",
                 "Declarar la regla antes (aquí: silueta a menos del 10% del máximo) y aplicarla",
                 "Nombrar con el perfil completo: el grupo de 3 provincias tiene 82% de informalidad y 89% de ruralidad")),
  pie = "Tabla 9. Errores de la sesión 2.")
doc <- P(doc, sprintf(
 "Resultado de referencia de esta corrida: tres grupos (%s provincias el informal-rural,
 %s el intermedio, %s el enclave formal), silueta media de 0,357 y concordancia perfecta
 entre k-medias y Ward (índice de Rand ajustado = 1,000).",
 sum(cl$asignacion$nombre == "Informal-rural", na.rm = TRUE),
 sum(cl$asignacion$nombre == "Intermedio", na.rm = TRUE),
 sum(cl$asignacion$nombre == "Enclave formal", na.rm = TRUE)))

# ============================================================
# SESIÓN 3
# ============================================================
doc <- body_add_break(doc)
doc <- H1(doc, "7. Sesión 3 — Bloque 3.3: técnicas básicas de aprendizaje automático")
doc <- H2(doc, "Subtemas: 3.3.1 Árboles de decisión y k-vecinos más cercanos · 3.3.2 Validación cruzada y métricas de desempeño")
doc <- P(doc, "Objetivo observable: al terminar, el estudiante entrena un árbol y un kNN
 para clasificar informalidad, los compara con una regresión logística usando AUC y F1,
 y elige uno justificando el costo de la decisión.")
doc <- P(doc,
 "La sesión tiene una trampa deliberada. Antes de mostrar cualquier modelo, se pregunta
 qué variables entrarían. Si alguien propone el tamaño del establecimiento o el RUC,
 la clase se detiene: esas variables construyen la definición de informalidad. Incluirlas
 produce un modelo con 95% de exactitud que no sirve para nada, porque no anticipa:
 repite.")
doc <- Q(doc, "Fuga de información: el modelo aprende la respuesta que ya estaba escrita en otra columna.")
doc <- tabla(doc, tibble::tibble(
  Min = c("0-10", "10-25", "25-55", "55-60", "60-85", "85-100"),
  Momento = c("Trampa de la fuga", "Árbol", "kNN y partición", "Corte",
              "Métricas y umbral", "Cierre"),
  "D1 conduce" = c("Pregunta qué variables entran y por qué",
                   "Observa y registra dónde se traba el curso",
                   "—",
                   "—",
                   "Explica matriz de confusión, sensibilidad y umbral",
                   "Pide la decisión y su costo"),
  "D2 conduce" = c("Cierra la trampa con la definición de secemp",
                   "Conduce rpart: cp, poda y lectura del árbol",
                   "Conduce caret: partición, CV y kNN estandarizado",
                   "Ordena los errores registrados",
                   "Conduce ROC y comparación con la logística",
                   "Cierra con la regla del reporte")),
  pie = "Tabla 10. Secuencia de la sesión 3.")
doc <- H2(doc, "Resultados de referencia")
doc <- tabla(doc, tab_met |>
  rename(Modelo = modelo, Umbral = umbral, Exactitud = exactitud,
         Sensibilidad = sensibilidad, Especificidad = especificidad,
         Precisión = precision, F1 = f1, AUC = auc),
  pie = "Tabla 11. Comparación sobre el 30% de prueba. La logística gana, y eso es parte de la lección.")
doc <- P(doc, sprintf(
 "La lectura que se lleva el curso: el árbol de cinco hojas acierta %.1f%% y tiene un AUC
 de %.3f; el kNN con k = 27 llega a %.3f; la regresión logística, a %.3f. El modelo más
 interpretable no es el más preciso, y el más preciso no es el más nuevo. Elegir es
 decidir qué se gana y qué se pierde, y escribirlo.",
 100 * tab_met$exactitud[tab_met$modelo == "Árbol (5 hojas)"],
 tab_met$auc[tab_met$modelo == "Árbol (5 hojas)"],
 tab_met$auc[tab_met$modelo == "kNN (k = 27)"],
 tab_met$auc[tab_met$modelo == "Logística"]))
doc <- H2(doc, "Errores frecuentes y su corrección")
doc <- tabla(doc, tibble::tibble(
  Error = c("Incluir variables de la definición del target",
            "Elegir el umbral mirando el test",
            "Reportar exactitud sin sensibilidad",
            "Usar kNN sin estandarizar",
            "Comparar modelos con una sola partición"),
  Corrección = c("Listar los predictores y preguntar, uno por uno, si se conocen antes del desenlace",
                 "Elegir el umbral en entrenamiento (Youden) y reportarlo como decisión",
                 "Mostrar la matriz completa: 4.273 aciertos formales, 680 falsos informales, 547 informales perdidos",
                 "Mostrar la distancia con y sin escala: las horas aplastan a la edad",
                 "Repetir la validación 3 veces con 5 pliegues y reportar la desviación")),
  pie = "Tabla 12. Errores de la sesión 3.")
doc <- P(doc, sprintf(
 "Evidencia de aprendizaje: una tabla de tres modelos con AUC y F1, y una frase que
 empiece con «elijo este modelo porque…» y termine con el costo aceptado. En esta
 corrida, el árbol pierde %.3f puntos de AUC frente a la logística y gana la posibilidad
 de explicarse en una diapositiva.",
 tab_met$auc[tab_met$modelo == "Logística"] -
   tab_met$auc[tab_met$modelo == "Árbol (5 hojas)"]))

# ============================================================
# SESIÓN 4
# ============================================================
doc <- H1(doc, "8. Sesión 4 — Bloque 3.4: técnicas básicas de análisis temporal")
doc <- H2(doc, "Subtemas: 3.4.1 Descomposición y suavizado de series · 3.4.2 Modelos ARIMA y pronóstico")
doc <- P(doc, "Objetivo observable: al terminar, el estudiante descompone una serie
 mensual, pronostica doce meses con un ARIMA y decide si el pronóstico sirve, comparándolo
 con el ingenuo estacional y leyendo el diagnóstico del residuo.")
doc <- P(doc,
 "La sesión empieza con la serie cruda y una pregunta: ¿qué se ve? Casi todos dicen
 «una caída en 2020». Esa respuesta es correcta y es insuficiente: la serie tiene
 tendencia, estacionalidad y un choque. STL separa las tres cosas y deja ver que la
 estacionalidad explica poco (fuerza 0,24) y la tendencia bastante (0,53).")
doc <- tabla(doc, tibble::tibble(
  Min = c("0-10", "10-30", "30-45", "45-50", "50-80", "80-100"),
  Momento = c("Activación", "Descomposición y suavizado", "Corte",
              "Estacionariedad y ACF", "ARIMA e intervención", "Cierre"),
  "D1 conduce" = c("Pregunta qué se ve antes de cualquier modelo",
                   "STL, medias móviles de 3 y 12, gráfico estacional",
                   "—",
                   "—",
                   "auto.arima, aerolínea, intervención COVID",
                   "Pide el pronóstico con su error"),
  "D2 conduce" = c("Pregunta qué parte es calendario y qué parte es historia",
                   "Interpreta los componentes y su fuerza",
                   "Recoge las lecturas del curso",
                   "ADF, KPSS y la lectura honesta de tests que no coinciden",
                   "Diagnóstico del residuo y comparación con el ingenuo",
                   "Cierra con la regla de la banda")),
  pie = "Tabla 13. Secuencia de la sesión 4.")
doc <- H2(doc, "El resultado incómodo, que es el corazón de la sesión")
doc <- P(doc, sprintf(
 "Al pronosticar 2022 con datos hasta 2021, el ARIMA aerolínea obtiene un RMSE de %.0f;
 el promedio histórico, %.0f; el ingenuo estacional, %.0f. Gana el más simple. Y el
 diagnóstico del residuo falla: Ljung-Box da p = 0,033, es decir, queda autocorrelación
 sin explicar.",
 rmse$RMSE[rmse$modelo == "ARIMA aerolínea"],
 rmse$RMSE[rmse$modelo == "Promedio histórico"],
 rmse$RMSE[rmse$modelo == "Ingenuo estacional"]))
doc <- P(doc,
 "La clase no esconde ese resultado: lo interpreta. La serie se comporta distinto después
 del choque de 2020; el ARIMA, al diferenciar, arrastra el nivel deprimido de 2021 y
 pronostica por debajo. Ningún modelo univariado reconstruye un cambio de régimen. La
 lección no es «ARIMA no sirve»: es que el diagnóstico manda y que el ingenuo es el
 estándar que hay que vencer antes de presumir.")
doc <- Q(doc, "Un pronóstico sin banda de confianza no es un pronóstico: es una opinión con decimales.")
doc <- H2(doc, "Errores frecuentes y su corrección")
doc <- tabla(doc, tibble::tibble(
  Error = c("Confundir tendencia con estacionalidad",
            "Pronosticar sin comparar con el ingenuo",
            "Ignorar el quiebre de 2020",
            "Ocultar un diagnóstico que falla"),
  Corrección = c("Mirar el panel estacional de STL: el patrón se repite cada 12 meses, el nivel no",
                 "Reportar siempre RMSE del ingenuo estacional en la misma tabla",
                 "Modelar la intervención con xreg y decir qué vale en el futuro",
                 "Reportar el p-valor de Ljung-Box y explicar qué implica para el uso del pronóstico")),
  pie = "Tabla 14. Errores de la sesión 4.")
doc <- P(doc, "Evidencia de aprendizaje: una frase de pronóstico con su intervalo y su
 error, más una línea que diga para qué sirve y para qué no.")

# ============================================================
# 9. EVALUACIÓN
# ============================================================
doc <- body_add_break(doc)
doc <- H1(doc, "9. Evaluación")
doc <- P(doc, "El entregable es un repositorio que corre y un informe de cuatro páginas.
 La rúbrica tiene cinco criterios y cuatro niveles; se entrega al inicio, no al final.")
doc <- tabla(doc, tibble::tibble(
  `Criterio` = c("Reproducibilidad", "Decisiones de datos", "Interpretación",
               "Validación", "Comunicación"),
  "4 · Logrado" = c("Corre de cero, semilla fijada, sessionInfo incluido",
                    "Cada decisión tiene criterio y control",
                    "Cada resultado tiene una frase que lo traduce",
                    "Compara contra una línea base y reporta umbral",
                    "Figuras rotuladas y tabla de resultados"),
  "3 · En proceso" = c("Corre con un ajuste manual menor",
                       "Documenta lo principal, omite lo menor",
                       "Interpreta bien, generaliza de más",
                       "Compara, pero no reporta el costo",
                       "Correcto pero sin unidades"),
  "2 · Inicial" = c("Depende de objetos de la sesión",
                    "Decisiones sin criterio explícito",
                    "Describe la salida del software",
                    "Solo exactitud",
                    "Figuras sin fuente")),
  pie = "Tabla 15. Rúbrica del proyecto.")
doc <- P(doc, "Pesos: reproducibilidad 25%, decisiones de datos 20%, interpretación 25%,
 validación 20%, comunicación 10%.")

# ============================================================
# ANEXO A — FIGURAS
# ============================================================
doc <- H1(doc, "Anexo A. Resultados de referencia")
doc <- P(doc, "Las figuras que siguen salen de los scripts 01 a 07 y son las que se
 proyectan en clase. Están en salidas/figuras/ a 150 ppp.")
doc <- foto(doc, "01_informalidad_provincia", 5.4, 0.875,
            "Figura 1. La informalidad provincial, que abre el proyecto en la sesión 1.")
doc <- foto(doc, "02_biplot", 5.9, 0.706,
            "Figura 2. Biplot de las dos primeras componentes, sesión 2.")
doc <- foto(doc, "03_grupos_provincia", 5.2, 0.812,
            "Figura 3. Los tres regímenes laborales, sesión 2.")
doc <- foto(doc, "04_arbol", 6.6, 0.583,
            "Figura 4. El árbol de cinco hojas, sesión 3.")
doc <- foto(doc, "05_roc", 5.0, 0.818,
            "Figura 5. Curvas ROC de los tres modelos, sesión 3.")
doc <- foto(doc, "06_stl", 5.6, 0.706,
            "Figura 6. Descomposición STL, sesión 4.")
doc <- foto(doc, "07_pronostico", 5.9, 0.545,
            "Figura 7. El pronóstico que pierde contra el ingenuo, sesión 4.")

# ============================================================
# ANEXO B — EJECUCIÓN
# ============================================================
doc <- H1(doc, "Anexo B. Cómo se ejecuta")
doc <- P(doc, "Todo el material vive en la carpeta clase_mineria_inec. El orden de
 ejecución es el de la numeración; cada script lee lo que dejó el anterior.")
doc <- tabla(doc, tibble::tibble(
  Script = c("00_setup.R", "01_crisp_dm.R", "02_pca.R", "03_cluster.R",
             "04_arboles_knn.R", "05_validacion.R", "06_series.R",
             "07_arima.R", "08_documento.R"),
  `Qué produce` = c("Rutas, paquetes, semilla y tema gráfico",
                  "Base analítica, indicadores provinciales, dos figuras",
                  "Componentes, cargas, biplot, índice provincial",
                  "Conglomerados, dendrograma, perfiles",
                  "Árbol, kNN, importancia de variables",
                  "Métricas, matriz de confusión, curvas ROC, CV repetida",
                  "Serie mensual, STL, suavizado, gráfico estacional",
                  "ARIMA, diagnóstico, pronóstico y comparación",
                  "Este documento")),
  pie = "Tabla 16. Orden de ejecución.")
doc <- P(doc, "En PowerShell, desde la carpeta del proyecto:")
doc <- body_add_fpar(doc, fpar(ftext(
  "1..8 | ForEach-Object { $f = (Get-ChildItem scripts -Filter (\"0\" + $_ + \"_*.R\")).FullName;",
  prop = fp_text(font.family = "Consolas", font.size = 8)),
  fp_p = fp_par(padding.left = 140)))
doc <- body_add_fpar(doc, fpar(ftext(
  "  & \"C:/Program Files/R/R-4.6.1/bin/x64/Rscript.exe\" $f }",
  prop = fp_text(font.family = "Consolas", font.size = 8)),
  fp_p = fp_par(padding.left = 140)))
doc <- P(doc, "La semilla 20261112 está fijada en 00_setup.R. Sin ella, la partición de
 entrenamiento y prueba cambia y las métricas de la sesión 3 no se repiten.")

# ============================================================
# ANEXO C — PRÁCTICA
# ============================================================
doc <- H1(doc, "Anexo C. Práctica autónoma por bloque")
doc <- tabla(doc, tibble::tibble(
  Bloque = c("3.1", "3.1", "3.2", "3.3", "3.4"),
  Ejercicio = c("Reconstruir la tasa de informalidad sin el factor de expansión y comparar",
                "Añadir la dimensión de vivienda al proyecto y documentar qué cambia",
                "Repetir el PCA con los 24 cantones de mayor población y comparar la CP1",
                "Probar un árbol con profundidad máxima 2 y medir cuánto se pierde",
                "Pronosticar solo los meses de diciembre y evaluar el error del pico"),
  `Criterio de logro` = c("La diferencia se explica por escrito en dos líneas",
                        "El diccionario se cita y la decisión se justifica",
                        "La CP1 conserva el signo y la interpretación",
                        "La tabla de métricas se actualiza y la conclusión se mantiene o cambia",
                        "El error del pico se compara con el error medio")),
  pie = "Tabla 17. Práctica autónoma.")

doc <- P(doc, "")
doc <- P(doc, paste("Documento generado por scripts/08_documento.R con",
                    R.version.string, "| semilla", SEMILLA,
                    "|", format(Sys.time(), "%Y-%m-%d %H:%M")))

salida_docx <- file.path("docs", "Plan_team_teaching_mineria_datos.docx")
tmp_docx <- file.path("docs", "_tmp.docx")
print(doc, target = tmp_docx)
ok <- file.rename(tmp_docx, salida_docx)
cat(if (isTRUE(ok)) paste("Documento generado en", salida_docx)
    else paste("No se pudo reemplazar el documento (está abierto en Word).",
               "La versión nueva quedó en", tmp_docx), "\n")
