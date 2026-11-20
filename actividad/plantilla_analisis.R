# ============================================================
# plantilla_analisis.R
# Actividad final — Minería de datos con R e información del INEC
#
# Copia este archivo, renómbralo con tu apellido y complétalo.
# La regla del curso: si no está acá, no ocurrió.
# ============================================================

# --- 0. Pregunta elegida -------------------------------------
# Escribe cuál de las cuatro y por qué en dos líneas (P1, P2, P3 o P4).
# PREGUNTA:

# --- 1. Entorno ----------------------------------------------
library(readr)
library(dplyr)
library(ggplot2)

# Tu semilla es personal: se calcula de tu correo institucional.
# No la escribas a mano, deja que la calcule la función. Así queda
# atada a ti y sigue siendo reproducible: quien conozca tu correo
# obtiene el mismo número.
semilla_personal <- function(cadena, base = 131, modulo = 1000000) {
  codigos <- utf8ToInt(tolower(trimws(cadena)))
  h <- 0
  for (cod in codigos) h <- (h * base + cod) %% modulo
  floor(h)
}

SEMILLA <- semilla_personal("nombre.apellido@utm.edu.ec")  # <-- tu correo
set.seed(SEMILLA)
cat("Semilla personal:", SEMILLA, "\n")

act <- read_csv("actividad/datos/enemdu_actividad.csv.gz", show_col_types = FALSE)
val <- read_csv("actividad/datos/diccionario_valores.csv", show_col_types = FALSE)
dic <- read_csv("actividad/datos/diccionario.csv", show_col_types = FALSE)

# --- 2. Controles de la base ---------------------------------
# Si estas comprobaciones fallan, no sigas: algo se descargó mal.
stopifnot(nrow(act) == 161906, all(act$fexp > 0))

cat("Ocupados:", nrow(act), "\n")
cat("Sin factor de expansión:", sum(is.na(act$fexp)), "\n")

# --- 3. Recodificación ---------------------------------------
# Mira los códigos antes de decidir. Ejemplo:
# val |> filter(variable == "p05a")
#
# TODO: construir tu variable de desenlace y las de control.
# Regla: un factor con etiquetas, nunca un código 1/2/3.

# --- 4. Describir (ponderado) --------------------------------
# TODO: media o proporción con weighted.mean(x, fexp), y el n de cada grupo.
# Ojo: un grupo con 40 casos no sostiene una conclusión.

# --- 5. Modelar ----------------------------------------------
# TODO: la técnica que corresponda a tu pregunta.
#   P1 y P3: clasificación (árbol, kNN o logística) con partición 70/30.
#   P2: componentes principales sobre las once prestaciones.
#   P4: descriptivo ponderado y regresión con controles.
#
# Si haces clasificación, no olvides:
#   - partición con set.seed()
#   - umbral elegido en entrenamiento
#   - matriz de confusión y AUC

# --- 6. Verificar --------------------------------------------
# TODO: ¿el resultado aguanta un cambio razonable?
#   - Repite la partición con otra semilla (por ejemplo SEMILLA + 1)
#     y reporta cuánto cambia la métrica. Un solo corte es una muestra.
#   - ¿cambia si excluyes un grupo pequeño?
#   - ¿qué porcentaje de casos perdiste por NA?

# --- 7. Exportar ---------------------------------------------
# TODO: la tabla que sostiene tu hallazgo, con unidades y fuente.
# readr::write_csv(tabla, "apellido_resultados.csv")

# --- 8. Cierre -----------------------------------------------
# Deja esta línea: sin ella el trabajo no es reproducible.
sessionInfo()
