# ============================================================
# 00_setup.R — configuración común del proyecto
# Curso: Minería de datos con R e información del INEC
# ============================================================

# --- Raíz del proyecto ---------------------------------------
# Este archivo se puede ejecutar desde la raíz, desde scripts/ o
# con Rscript. Se ubica solo: su propia ruta dice dónde está la
# raíz, y el resto del proyecto se resuelve desde ahí.
.este_archivo <- tryCatch(normalizePath(sys.frame(1)$ofile), error = function(e) NA_character_)

raiz <- if (!is.na(.este_archivo) && file.exists(.este_archivo)) {
  dirname(dirname(.este_archivo))
} else if (file.exists("scripts/00_setup.R")) {
  normalizePath(".")
} else if (file.exists("../scripts/00_setup.R")) {
  normalizePath("..")
} else {
  NA_character_
}

if (is.na(raiz)) {
  stop("No se encontró la raíz del proyecto.\n",
       "  Abre mineria-inec.Rproj o ejecuta el script desde la carpeta que ",
       "contiene a scripts/.\n  Directorio actual: ", getwd())
}

setwd(raiz)

# --- Rutas ---------------------------------------------------
# Los microdatos del INEC no se distribuyen con el repositorio:
# son 170 MB de archivos SPSS. Se descargan aparte y se apunta la
# variable de entorno INEC_DIR a la carpeta que los contiene.
#   Windows (PowerShell):  $env:INEC_DIR = "D:/DatosINEC"
#   Linux / macOS:         export INEC_DIR="$HOME/DatosINEC"
ruta_inec  <- Sys.getenv("INEC_DIR", unset = "D:/DatosINEC")
dir_datos  <- "datos"                          # datos procesados
dir_sal    <- "salidas"
dir_fig    <- file.path(dir_sal, "figuras")
dir_tab    <- file.path(dir_sal, "tablas")
dir_mod    <- file.path(dir_sal, "modelos")

for (d in c(dir_datos, dir_sal, dir_fig, dir_tab, dir_mod)) {
  if (!dir.exists(d)) dir.create(d, recursive = TRUE)
}

if (!dir.exists(ruta_inec)) {
  warning("No existe la carpeta de microdatos: ", ruta_inec,
          "\n  Los scripts que leen el INEC van a fallar. Define INEC_DIR.",
          call. = FALSE)
}

# --- Semilla única y documentada ------------------------------
# Todos los resultados aleatorios del curso dependen de esta semilla.
SEMILLA <- 20261112
set.seed(SEMILLA)

# --- Paquetes ------------------------------------------------
paquetes <- c("haven", "dplyr", "tidyr", "purrr", "stringr", "forcats",
              "ggplot2", "scales", "readr", "tibble",
              "FactoMineR", "factoextra", "cluster", "NbClust",
              "rpart", "class", "caret", "pROC",
              "forecast", "tseries", "urca", "zoo",
              "knitr", "gt", "broom")

# Estos se usan siempre con :: y NO se cargan: mclust define su propio
# map() y taparía el de purrr, que es el que usan los scripts.
paquetes_extra <- c("ggrepel", "mclust")

faltan <- setdiff(c(paquetes, paquetes_extra), rownames(installed.packages()))
if (length(faltan)) {
  stop("Faltan paquetes: ", paste(faltan, collapse = ", "))
}

invisible(lapply(paquetes, function(p) suppressPackageStartupMessages(
  library(p, character.only = TRUE))))

# --- Tema gráfico del curso ----------------------------------
tema_curso <- function(base = 12) {
  theme_minimal(base_size = base) +
    theme(
      plot.title    = element_text(face = "bold", size = base + 2),
      plot.subtitle = element_text(colour = "grey35", size = base - 1),
      plot.caption  = element_text(colour = "grey45", size = base - 3, hjust = 0),
      panel.grid.minor = element_blank(),
      panel.grid.major.x = element_blank(),
      legend.position = "bottom",
      plot.title.position = "plot"
    )
}
theme_set(tema_curso())

# --- Paleta --------------------------------------------------
col_principal <- "#1F4E79"   # azul institucional
col_acento    <- "#C0504D"   # rojo terracota
col_apoyo     <- "#7F9DB9"
col_verde     <- "#4F7D5A"
pal_curso     <- c(col_principal, col_acento, col_verde, "#E3A857", "#6C5B7B")

# --- Etiquetas de figuras ------------------------------------
fuente_enemdu  <- "Fuente: INEC, ENEMDU anual 2025. Elaboración propia."
fuente_siniestros <- "Fuente: INEC, Estadísticas de Transporte (siniestros de tránsito). Elaboración propia."

# --- Utilidades ----------------------------------------------
# Regla del curso: lo que el script produce se ve en pantalla. Guardar
# sin mostrar obliga al estudiante a saltar de una ventana a otra y a
# creerle al archivo en vez de leer el resultado.
mostrar <- function(x, n = 12, titulo = NULL) {
  if (!is.null(titulo)) cat("\n== ", titulo, " ==\n", sep = "")
  filas <- if (is.data.frame(x)) nrow(x) else length(x)
  print(utils::head(x, n), width = 220)
  if (filas > n) {
    cat("(", filas - n, " filas más · archivo completo en salidas/ )\n", sep = "")
  }
  invisible(x)
}

guardar_fig <- function(plot, nombre, ancho = 7, alto = 5, pantalla = TRUE) {
  ruta <- file.path(dir_fig, paste0(nombre, ".png"))
  ggsave(ruta, plot, width = ancho, height = alto, dpi = 150, bg = "white")

  # Copia sin título ni subtítulo para las diapositivas: la lámina ya
  # trae su encabezado y repetirlo se ve como un error.
  dir_slide <- file.path(dir_fig, "_slide")
  if (!dir.exists(dir_slide)) dir.create(dir_slide, recursive = TRUE)
  ggsave(file.path(dir_slide, paste0(nombre, ".png")),
         plot + labs(title = NULL, subtitle = NULL),
         width = ancho, height = alto, dpi = 150, bg = "white")

  # La figura se dibuja en el panel de Plots mientras se corre el
  # script. Con Rscript no hay panel: se guarda y se sigue.
  if (pantalla && interactive()) print(plot)

  cat("[figura] ", nombre, "  ->  ", ruta, "\n", sep = "")
  invisible(ruta)
}

# Para los gráficos de base R (checkresiduals, plot, ...) que no son
# ggplot: se guardan igual y se vuelven a dibujar en pantalla.
guardar_grafico_base <- function(nombre, expr, ancho = 1500, alto = 1000, res = 150) {
  e <- substitute(expr)
  ruta <- file.path(dir_fig, paste0(nombre, ".png"))
  png(ruta, width = ancho, height = alto, res = res)
  eval(e, parent.frame())
  dev.off()
  if (interactive()) eval(e, parent.frame())
  cat("[figura] ", nombre, "  ->  ", ruta, "\n", sep = "")
  invisible(ruta)
}

exportar_tabla <- function(x, nombre, pantalla = interactive(), n = 12) {
  readr::write_excel_csv(x, file.path(dir_tab, paste0(nombre, ".csv")))
  if (pantalla) mostrar(x, n = n, titulo = nombre)
  cat("[tabla]  ", nombre, "  ->  ", file.path(dir_tab, paste0(nombre, ".csv")),
      "\n", sep = "")
  invisible(x)
}

# Separador de miles en formato ecuatoriano (1.234,56)
fmt_num <- function(x, dec = 0) {
  formatC(x, format = "f", digits = dec, big.mark = ".", decimal.mark = ",")
}
fmt_pct <- function(x, dec = 1) paste0(fmt_num(100 * x, dec), "%")

# --- Región natural a partir de la provincia -----------------
prov_regiones <- tribble(
  ~prov, ~provincia,              ~region,
   1, "Azuay",                    "Sierra",
   2, "Bolívar",                  "Sierra",
   3, "Cañar",                    "Sierra",
   4, "Carchi",                   "Sierra",
   5, "Cotopaxi",                 "Sierra",
   6, "Chimborazo",               "Sierra",
   7, "El Oro",                   "Costa",
   8, "Esmeraldas",               "Costa",
   9, "Guayas",                   "Costa",
  10, "Imbabura",                 "Sierra",
  11, "Loja",                     "Sierra",
  12, "Los Ríos",                 "Costa",
  13, "Manabí",                   "Costa",
  14, "Morona Santiago",          "Amazonía",
  15, "Napo",                     "Amazonía",
  16, "Pastaza",                  "Amazonía",
  17, "Pichincha",                "Sierra",
  18, "Tungurahua",               "Sierra",
  19, "Zamora Chinchipe",         "Amazonía",
  20, "Galápagos",                "Galápagos",
  21, "Sucumbíos",                "Amazonía",
  22, "Orellana",                 "Amazonía",
  23, "Santo Domingo de los Tsáchilas", "Costa",
  24, "Santa Elena",              "Costa"
)

cat("Setup listo | semilla =", SEMILLA, "| R =", R.version.string, "\n")
