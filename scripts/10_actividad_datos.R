# ============================================================
# 10_actividad_datos.R
# Prepara el extracto de la ENEMDU 2025 para la actividad final.
# Trae variables que NO se usaron en clase: seguridad social,
# beneficios, contrato, pluriempleo, tenencia de RUC y contabilidad.
# ============================================================

source("scripts/00_setup.R")

ruta_sav <- file.path(ruta_inec, "1_BDD_ENEMDU_2025_SPSS",
                      "BDDenemdu_personas_2025_anual.sav")

vars <- c(
  # identificacion y diseno muestral
  "id_persona", "prov", "area", "dominio", "estrato", "upm", "fexp", "mes",
  # caracteristicas de la persona
  "p02", "p03", "p06", "p07", "p10a", "p10b", "p12a", "p12b", "p15",
  # seguridad social
  "p05a", "p05b", "p61b1",
  # trabajo principal
  "p42", "rama1", "grupo1", "p43", "p44a", "p44b", "p44c", "p44d", "p44e",
  "p44f", "p44g", "p44h", "p44i", "p44j", "p44k",
  "p45", "p46", "p47b", "p48", "p49", "p50", "p51a", "p51b", "p51c",
  # ingresos
  "p63", "p64a", "p64b", "p65", "p66", "p67", "p68a", "p68b", "p69",
  "p71a", "p71b", "p72a", "p72b", "p73a", "p73b", "p74a", "p74b",
  "p75", "p76", "p77", "p78",
  # variables derivadas del INEC
  "empleo", "secemp", "condact", "ingrl", "ingpc", "pobreza", "nnivins"
)

d <- haven::read_sav(ruta_sav, col_select = all_of(vars))

cat("Registros leidos:", nrow(d), "| variables:", ncol(d), "\n")

# Unidad de analisis: personas ocupadas de 15 anos y mas.
# Se entrega sin recodificar a proposito: recodificar es parte del
# ejercicio.
act <- d |>
  haven::zap_labels() |>
  filter(p03 >= 15, !is.na(empleo), empleo == 1)

cat("Ocupados de 15+:", nrow(act), "\n")

dir.create("actividad/datos", recursive = TRUE, showWarnings = FALSE)
readr::write_csv(act, "actividad/datos/enemdu_actividad.csv.gz", na = "")

# Diccionarios: nombre de cada variable y, sobre todo, el
# significado de cada codigo. Sin esto no se puede recodificar.
etiquetas <- sapply(d[vars], function(x) attr(x, "label"))
dic <- tibble::tibble(variable = names(etiquetas),
                      etiqueta = as.character(etiquetas))
readr::write_csv(dic, "actividad/datos/diccionario.csv")

valores <- purrr::map_dfr(vars, function(v) {
  lb <- attr(d[[v]], "labels")
  if (is.null(lb)) return(tibble::tibble())
  tibble::tibble(variable = v, codigo = as.numeric(lb),
                 etiqueta = names(lb))
})
readr::write_csv(valores, "actividad/datos/diccionario_valores.csv")
cat("Codigos documentados:", nrow(valores), "\n")

tam <- file.size("actividad/datos/enemdu_actividad.csv.gz") / 1e6
cat("Archivo:", fmt_num(tam, 1), "MB comprimido\n")
cat("Filas:", fmt_num(nrow(act)), "| columnas:", ncol(act), "\n")

# Chequeo rapido de las variables que sostienen las cuatro preguntas
cat("\nCobertura de las variables nuevas (ocupados):\n")
cat("  aporta a seguridad social (p05a):",
    fmt_pct(weighted.mean(act$p05a == 1, act$fexp, na.rm = TRUE)), "\n")
cat("  contrato permanente o temporal (p43):",
    fmt_pct(weighted.mean(!is.na(act$p43) & act$p43 > 0, act$fexp, na.rm = TRUE)), "\n")
cat("  mas de un trabajo (p50 > 1):",
    fmt_pct(weighted.mean(act$p50 > 1, act$fexp, na.rm = TRUE)), "\n")
cat("  establecimiento con RUC (p49):",
    fmt_pct(weighted.mean(act$p49 == 1, act$fexp, na.rm = TRUE)), "\n")
cat("  lleva contabilidad (p48):",
    fmt_pct(weighted.mean(act$p48 == 1, act$fexp, na.rm = TRUE)), "\n")
cat("  recibe decimo tercero (p44j):",
    fmt_pct(weighted.mean(act$p44j == 1, act$fexp, na.rm = TRUE)), "\n")
