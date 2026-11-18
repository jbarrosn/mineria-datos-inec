# ============================================================
# 00_setup.R — configuración común del proyecto
# Curso: Minería de datos con R e información del INEC
# ============================================================

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

faltan <- paquetes[!paquetes %in% rownames(installed.packages())]
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
guardar_fig <- function(plot, nombre, ancho = 7, alto = 5) {
  ruta <- file.path(dir_fig, paste0(nombre, ".png"))
  ggsave(ruta, plot, width = ancho, height = alto, dpi = 150, bg = "white")
  invisible(ruta)
}

exportar_tabla <- function(x, nombre) {
  readr::write_excel_csv(x, file.path(dir_tab, paste0(nombre, ".csv")))
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
