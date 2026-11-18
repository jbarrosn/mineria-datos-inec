# ============================================================
# 01_crisp_dm.R — Bloque 3.1
# Metodología CRISP-DM y preprocesamiento
# Proyecto: "Observatorio de vulnerabilidad laboral del Ecuador"
# ============================================================
# Este script es el módulo 1 del curso. Hace, en orden, las tres
# primeras fases de CRISP-DM sobre la ENEMDU anual 2025:
#   (1) comprensión del negocio  -> pregunta y unidad de análisis
#   (2) comprensión de los datos -> diccionario, cobertura, centinelas
#   (3) preparación de los datos -> base analítica y indicadores
# Todo lo que se afirma en clase sale de aquí.
# ============================================================

source("scripts/00_setup.R")
dir.create("datos", showWarnings = FALSE)

ruta_sav <- file.path(ruta_inec, "1_BDD_ENEMDU_2025_SPSS",
                      "BDDenemdu_personas_2025_anual.sav")

# ------------------------------------------------------------
# 1. Comprensión de los datos: lectura y contrato de calidad
# ------------------------------------------------------------
# Solo se leen las columnas que el proyecto va a usar. Leer 139
# columnas "por si acaso" es el primer error de un proyecto real.
vars <- c("id_persona", "id_hogar", "upm", "estrato", "fexp",
          "prov", "area", "dominio", "mes",
          "p02", "p03", "p04", "p06", "p10a", "p15",
          "condact", "empleo", "desempleo", "secemp",
          "p42", "rama1", "grupo1", "p47a", "p51a",
          "ingrl", "ingpc", "pobreza", "epobreza", "nnivins")

enemdu <- haven::read_sav(ruta_sav, col_select = all_of(vars))
enemdu <- haven::zap_labels(enemdu)

n_original <- nrow(enemdu)
stopifnot(n_original == 334786)   # control de integridad de la fuente

cat("Registros leídos:", fmt_num(n_original), "\n")
cat("Columnas:", ncol(enemdu), "| Meses:", length(unique(enemdu$mes)), "\n")

# ------------------------------------------------------------
# 2. Comprensión de los datos: centinelas y valores perdidos
# ------------------------------------------------------------
# La ENEMDU usa códigos centinela que NO son datos: -1 y 999999
# en ingreso, 999 en horas. Si no se tratan, la media de ingreso
# se dispara y cualquier modelo aprende ruido.
centinelas <- enemdu |>
  summarise(
    ingrl_menos1   = sum(ingrl == -1, na.rm = TRUE),
    ingrl_999999   = sum(ingrl == 999999, na.rm = TRUE),
    ingrl_cero     = sum(ingrl == 0, na.rm = TRUE),
    ingrl_na       = sum(is.na(ingrl)),
    horas_999      = sum(p51a == 999, na.rm = TRUE),
    horas_na       = sum(is.na(p51a))
  )
print(centinelas)
exportar_tabla(centinelas, "01_centinelas")

# Mapa de perdidos por variable (figura del bloque 3.1)
perdidos <- enemdu |>
  summarise(across(everything(), ~ mean(is.na(.x)))) |>
  pivot_longer(everything(), names_to = "variable", values_to = "pct_na") |>
  filter(pct_na > 0) |>
  arrange(desc(pct_na))

p_perdidos <- perdidos |>
  mutate(variable = fct_reorder(variable, pct_na)) |>
  ggplot(aes(pct_na, variable)) +
  geom_col(fill = col_principal, width = 0.7) +
  geom_text(aes(label = fmt_pct(pct_na)), hjust = -0.15, size = 3) +
  scale_x_continuous(labels = percent_format(accuracy = 1),
                     limits = c(0, 1.05), expand = c(0, 0)) +
  labs(title = "Los perdidos no son un accidente: son el diseño de la encuesta",
       subtitle = "Porcentaje de valores perdidos por variable, ENEMDU 2025",
       x = "Valores perdidos", y = NULL, caption = fuente_enemdu) +
  theme(panel.grid.major.y = element_blank())
guardar_fig(p_perdidos, "01_mapa_perdidos", ancho = 7, alto = 4.5)

# ------------------------------------------------------------
# 3. Preparación: recodificación con etiquetas legibles
# ------------------------------------------------------------
# Regla del curso: ningún modelo se ajusta sobre códigos 1, 2, 3.
# Los códigos se convierten en factores con nombre antes de modelar.

etiquetas_nnivins <- c("1" = "Ninguno", "2" = "Alfabetización",
                       "3" = "Básica", "4" = "Bachillerato", "5" = "Superior")

etiquetas_categoria <- c(
  "1"  = "Empleado público",
  "2"  = "Empleado privado",
  "3"  = "Empleado tercerizado",
  "4"  = "Jornalero",
  "5"  = "Patrono",
  "6"  = "Cuenta propia",
  "7"  = "Trabajador del hogar no remunerado",
  "8"  = "Trabajador no del hogar no remunerado",
  "9"  = "Ayudante no remunerado",
  "10" = "Empleado doméstico")

etiquetas_etnia <- c("1" = "Indígena", "2" = "Afroecuatoriano", "3" = "Negro",
                     "4" = "Mulato", "5" = "Montuvio", "6" = "Mestizo",
                     "7" = "Blanco", "8" = "Otra")

etiquetas_rama <- c(
  "1" = "Agricultura", "2" = "Minas", "3" = "Manufactura",
  "4" = "Electricidad", "5" = "Construcción", "6" = "Comercio",
  "7" = "Transporte", "8" = "Alojamiento y comida", "9" = "Información",
  "10" = "Finanzas", "11" = "Inmobiliario", "12" = "Profesional",
  "13" = "Administración pública", "14" = "Enseñanza", "15" = "Salud",
  "16" = "Arte y recreación", "17" = "Otros servicios",
  "18" = "Hogares", "19" = "Organizaciones")

base <- enemdu |>
  left_join(prov_regiones, by = "prov") |>
  mutate(
    # --- limpieza de centinelas -------------------------------------
    ingreso = case_when(
      ingrl < 0            ~ NA_real_,   # -1 y otros negativos
      ingrl == 999999      ~ NA_real_,   # tope de no respuesta
      is.na(ingrl)         ~ NA_real_,
      TRUE                 ~ ingrl
    ),
    horas = case_when(p51a >= 999 ~ NA_real_, TRUE ~ as.numeric(p51a)),
    # --- recodificación con etiquetas ------------------------------
    sexo    = factor(p02, levels = c(1, 2), labels = c("Hombre", "Mujer")),
    area    = factor(area, levels = c(1, 2), labels = c("Urbana", "Rural")),
    educ    = factor(etiquetas_nnivins[as.character(nnivins)],
                     levels = etiquetas_nnivins),
    etnia   = factor(etiquetas_etnia[as.character(p15)]),
    etnia_g = fct_collapse(etnia, "Indígena" = "Indígena",
                           "Afroecuatoriano" = c("Afroecuatoriano", "Negro", "Mulato"),
                           "Mestizo" = "Mestizo",
                           "Otro" = c("Montuvio", "Blanco", "Otra")),
    categoria = factor(etiquetas_categoria[as.character(p42)]),
    rama      = factor(etiquetas_rama[as.character(rama1)]),
    region    = factor(region, levels = c("Sierra", "Costa", "Amazonía", "Galápagos")),
    provincia = factor(provincia),
    # --- variable objetivo binaria ---------------------------------
    # Informales = sector informal según la clasificación del INEC.
    informal = case_when(is.na(secemp) ~ NA,
                         secemp == 2    ~ 1L,
                         TRUE           ~ 0L),
    pobre = as.integer(pobreza == 1),
    # Indicadores de condición de actividad SIN NA contagioso:
    # en R, NA == 1 devuelve NA, y sum() de un NA devuelve NA. Es la
    # causa más común de que un indicador "desaparezca" en un tablero.
    ocupado = as.integer(!is.na(empleo)   & empleo   == 1),
    desoc   = as.integer(!is.na(desempleo) & desempleo == 1),
    # --- grupos de edad (para tablas y gráficos) -------------------
    grupo_edad = cut(p03, breaks = c(14, 24, 34, 44, 54, 64, Inf),
                     labels = c("15-24", "25-34", "35-44", "45-54",
                                "55-64", "65 y más"),
                     right = FALSE)
  )

# ------------------------------------------------------------
# 4. Controles de calidad (cada transformación se verifica)
# ------------------------------------------------------------
cat("\n--- Controles de preprocesamiento ---\n")
cat("Personas 15+ años:            ", fmt_num(sum(base$p03 >= 15)), "\n")
cat("Ocupados:                     ", fmt_num(sum(base$ocupado)), "\n")
cat("Ocupados con ingreso válido:  ", fmt_num(sum(base$ocupado == 1 & !is.na(base$ingreso))), "\n")
cat("Ingreso mediano (ocupados):   ", fmt_num(median(base$ingreso[base$ocupado == 1], na.rm = TRUE), 2), "USD\n")
cat("Horas medias (ocupados):      ", fmt_num(mean(base$horas[base$ocupado == 1], na.rm = TRUE), 1), "\n")
cat("Rango de ingreso:             ", fmt_num(range(base$ingreso, na.rm = TRUE), 0), "\n")

stopifnot(
  all(base$ingreso >= 0 | is.na(base$ingreso)),
  all(base$horas > 0 | is.na(base$horas)),
  all(base$horas <= 168 | is.na(base$horas)),
  nrow(base) == n_original
)

# La asimetría del ingreso justifica la escala logarítmica: es una
# decisión de preprocesamiento que se documenta, no un adorno.
asimetria <- function(x) {
  x <- x[!is.na(x)]
  mean((x - mean(x))^3) / mean((x - mean(x))^2)^(3/2)
}
cat("Asimetría del ingreso (nivel):", round(asimetria(base$ingreso), 2), "\n")
cat("Asimetría del ingreso (log):  ", round(asimetria(log(base$ingreso[base$ingreso > 0])), 2), "\n")

p_ingreso <- base |>
  filter(ocupado == 1, !is.na(ingreso)) |>
  ggplot(aes(ingreso)) +
  geom_histogram(bins = 60, fill = col_principal, colour = "white", linewidth = 0.2) +
  geom_vline(xintercept = median(base$ingreso[base$ocupado == 1], na.rm = TRUE),
             colour = col_acento, linewidth = 1, linetype = "dashed") +
  scale_x_continuous(labels = dollar_format(prefix = "$", big.mark = ".",
                                            decimal.mark = ",")) +
  labs(title = "El ingreso laboral no es una normal: es una cola",
       subtitle = "Personas ocupadas de 15 años y más. La línea marca la mediana",
       x = "Ingreso laboral mensual (USD)", y = "Personas",
       caption = fuente_enemdu) +
  annotate("text", x = median(base$ingreso[base$ocupado == 1], na.rm = TRUE),
           y = Inf, label = " mediana", vjust = 1.5, hjust = 0,
           colour = col_acento, size = 3.2)
guardar_fig(p_ingreso, "01_ingreso_hist", ancho = 7.5, alto = 4.5)

# ------------------------------------------------------------
# 5. Base analítica: dos unidades de análisis distintas
# ------------------------------------------------------------
# La misma encuesta sirve para dos preguntas y dos unidades:
#   (a) personas  -> clasificación (módulo 3.3)
#   (b) provincias -> análisis multivariante (módulo 3.2)

personas <- base |>
  filter(p03 >= 15) |>
  transmute(
    id_persona, provincia, region, area, sexo, edad = p03,
    grupo_edad, educ, etnia_g, categoria, rama,
    horas, ingreso, informal, pobre, fexp, dominio, mes,
    ocupado
  )

ocupados <- personas |> filter(ocupado == 1)

# --- (b) Indicadores provinciales ponderados por el factor de expansión
# Sin fexp, el indicador describe la muestra y no la provincia.
# Regla de cálculo: proporción = suma ponderada del numerador /
# suma ponderada del denominador. Se escribe así, y no con
# weighted.mean(), porque el denominador cambia según el indicador.
wshare <- function(cond, w) sum(cond * w, na.rm = TRUE) / sum(w, na.rm = TRUE)

ind_prov <- base |>
  filter(p03 >= 15, !is.na(region)) |>
  group_by(provincia, region) |>
  summarise(
    n_muestra      = n(),
    pob_15         = sum(fexp, na.rm = TRUE),
    # mercado laboral (denominador: ocupados o PEA)
    tasa_informal  = wshare(informal == 1, fexp * ocupado),
    tasa_desempleo = wshare(desoc == 1, fexp * (ocupado == 1 | desoc == 1)),
    tasa_adecuado  = wshare(condact == 1, fexp * ocupado),
    # ingresos y horas (solo ocupados con dato válido)
    ingreso_medio  = weighted.mean(if_else(ocupado == 1, ingreso, NA_real_),
                                   fexp, na.rm = TRUE),
    horas_promedio = weighted.mean(if_else(ocupado == 1, horas, NA_real_),
                                   fexp, na.rm = TRUE),
    # composición de la ocupación
    pct_mujeres    = wshare(sexo == "Mujer", fexp * ocupado),
    pct_rural      = wshare(area == "Rural", fexp * ocupado),
    pct_superior   = wshare(educ == "Superior", fexp * ocupado),
    # pobreza por ingresos: se mide sobre la población de 15 y más
    pct_pobreza    = wshare(pobre == 1, fexp),
    .groups = "drop"
  ) |>
  arrange(desc(tasa_informal))

print(ind_prov, n = 24)

exportar_tabla(personas, "01_personas")
exportar_tabla(ind_prov, "01_indicadores_provincia")
saveRDS(ocupados, file.path(dir_datos, "ocupados.rds"))
saveRDS(ind_prov,  file.path(dir_datos, "indicadores_provincia.rds"))

# ------------------------------------------------------------
# 6. La figura que abre el proyecto
# ------------------------------------------------------------
p_informal <- ind_prov |>
  mutate(provincia = fct_reorder(provincia, tasa_informal)) |>
  ggplot(aes(tasa_informal, provincia, fill = region)) +
  geom_col(width = 0.72) +
  geom_text(aes(label = fmt_pct(tasa_informal)), hjust = -0.12, size = 3) +
  scale_x_continuous(labels = percent_format(accuracy = 1),
                     expand = expansion(mult = c(0, 0.12))) +
  scale_fill_manual(values = c(Sierra = col_principal, Costa = col_acento,
                               Amazonía = col_verde, Galápagos = "#E3A857")) +
  labs(title = "La informalidad no se reparte igual en el mapa",
       subtitle = "Proporción de personas ocupadas en el sector informal, por provincia",
       x = "Tasa de informalidad", y = NULL, fill = NULL,
       caption = fuente_enemdu) +
  theme(panel.grid.major.y = element_blank())
guardar_fig(p_informal, "01_informalidad_provincia", ancho = 8, alto = 7)

cat("\nBloque 3.1 completado. Archivos en datos/ y salidas/.\n")
