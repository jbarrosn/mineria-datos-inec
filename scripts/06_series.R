# ============================================================
# 06_series.R — Bloque 3.4.1
# Descomposición y suavizado de series
# Segunda ventana de datos del proyecto: la misma institución,
# otra tabla. La ENEMDU 2025 tiene 12 puntos mensuales: alcanza
# para leer una serie, no para modelarla. Cuando el método exige
# historia, se cambia de tabla, no de país.
# ============================================================

source("scripts/00_setup.R")

# ------------------------------------------------------------
# 1. Construcción de la serie mensual 2018-2022 (+ 2025-I)
# ------------------------------------------------------------
leer_siniestros <- function(anio) {
  f <- list.files(file.path(ruta_inec, "Transporte", paste0("ESTRA_", anio)),
                  recursive = TRUE, pattern = "SINIESTROS.*[.]sav$",
                  full.names = TRUE, ignore.case = TRUE)
  f <- f[!grepl("diccionario", f, ignore.case = TRUE)]
  d <- haven::read_sav(f[1]) |> haven::zap_labels()
  names(d) <- toupper(iconv(names(d), to = "ASCII//TRANSLIT"))
  d |>
    transmute(anio = anio,
              mes  = as.integer(MES),
              victimas   = as.numeric(TOTAL_VICTIMAS),
              fallecidos = as.numeric(NUM_FALLECIDO))
}

mensual <- map_dfr(c(2018, 2019, 2020, 2021, 2022), leer_siniestros) |>
  group_by(anio, mes) |>
  summarise(victimas = sum(victimas, na.rm = TRUE),
            fallecidos = sum(fallecidos, na.rm = TRUE),
            .groups = "drop") |>
  arrange(anio, mes) |>
  mutate(fecha = as.Date(sprintf("%d-%02d-01", anio, mes)))

# 2025 (primer trimestre), desde el zip
dir_tmp <- file.path(dir_datos, "_extraido")
dir.create(dir_tmp, showWarnings = FALSE)
zip25 <- file.path(ruta_inec, "Siniestros_de_Transito",
                   "2025_SINIESTROS_BDD_ITRIMESTRE_SPSS.zip")
# El zip trae un nombre de archivo en codificación CP850 ("TRµNSITO").
# R no puede decodificarlo y unzip() falla; se extrae con .NET en
# CP850 desde PowerShell (ver 00_leeme.md). Si ya está extraído, se usa.
f25 <- list.files(dir_tmp, pattern = "[.]sav$", recursive = TRUE, full.names = TRUE)
if (!length(f25)) {
  ok <- tryCatch({ utils::unzip(zip25, exdir = dir_tmp, junkpaths = TRUE); TRUE },
                 error = function(e) FALSE, warning = function(w) FALSE)
  if (!ok) stop("Extraiga el zip 2025 a mano: el nombre interno está en CP850.")
  f25 <- list.files(dir_tmp, pattern = "[.]sav$", recursive = TRUE, full.names = TRUE)
}
d25 <- haven::read_sav(f25[1]) |> haven::zap_labels()
names(d25) <- toupper(iconv(names(d25), to = "ASCII//TRANSLIT"))
s25 <- d25 |>
  transmute(anio = 2025L, mes = as.integer(MES),
            victimas = as.numeric(TOTAL_VICTIMAS),
            fallecidos = as.numeric(NUM_FALLECIDO)) |>
  group_by(anio, mes) |>
  summarise(victimas = sum(victimas, na.rm = TRUE),
            fallecidos = sum(fallecidos, na.rm = TRUE),
            .groups = "drop") |>
  mutate(fecha = as.Date(sprintf("%d-%02d-01", anio, mes)))

exportar_tabla(mensual, "06_serie_mensual")
exportar_tabla(s25, "06_serie_2025")
cat("Meses 2018-2022:", nrow(mensual), "| meses 2025:", nrow(s25), "\n")
cat("Rango:", format(min(mensual$fecha)), "a", format(max(mensual$fecha)), "\n")

# La serie de trabajo: 60 meses. La de 2025 queda como control
# externo y se usa en el bloque 3.4.2.
victimas_ts <- ts(mensual$victimas, start = c(2018, 1), frequency = 12)

# ------------------------------------------------------------
# 2. La serie cruda: qué se ve antes de cualquier modelo
# ------------------------------------------------------------
p_serie <- mensual |>
  ggplot(aes(fecha, victimas)) +
  geom_line(colour = col_principal, linewidth = 0.8) +
  geom_point(size = 1.1, colour = col_principal, alpha = 0.6) +
  annotate("rect", xmin = as.Date("2020-03-01"), xmax = as.Date("2020-06-01"),
           ymin = -Inf, ymax = Inf, alpha = 0.12, fill = col_acento) +
  annotate("text", x = as.Date("2020-04-15"), y = max(mensual$victimas),
           label = "confinamiento", vjust = 1, size = 3, colour = col_acento) +
  scale_x_date(date_labels = "%Y", date_breaks = "1 year") +
  scale_y_continuous(labels = comma_format(big.mark = ".", decimal.mark = ",")) +
  labs(title = "Una serie no es una tendencia: son cuatro cosas a la vez",
       subtitle = "Víctimas mensuales de siniestros de tránsito en Ecuador",
       x = NULL, y = "Víctimas por mes", caption = fuente_siniestros)
guardar_fig(p_serie, "06_serie_cruda", ancho = 8.5, alto = 4.2)

# ------------------------------------------------------------
# 3. Descomposición STL
# ------------------------------------------------------------
# STL = Seasonal-Trend decomposition using Loess. Separa tendencia,
# estacionalidad y resto sin imponer una forma funcional.
stl_fit <- stl(victimas_ts, s.window = "periodic", robust = TRUE)
print(summary(stl_fit))

componentes <- as.data.frame(stl_fit$time.series) |>
  mutate(fecha = seq(min(mensual$fecha), by = "month", length.out = n())) |>
  pivot_longer(c(seasonal, trend, remainder), names_to = "componente",
               values_to = "valor") |>
  mutate(componente = factor(componente,
                             levels = c("trend", "seasonal", "remainder"),
                             labels = c("Tendencia", "Estacionalidad", "Residuo")))

p_stl <- ggplot(componentes, aes(fecha, valor)) +
  geom_line(colour = col_principal, linewidth = 0.7) +
  geom_hline(yintercept = 0, colour = "grey80", linewidth = 0.3) +
  facet_wrap(~componente, ncol = 1, scales = "free_y") +
  scale_x_date(date_labels = "%Y", date_breaks = "1 year") +
  labs(title = "La tendencia cuenta la historia; la estacionalidad, el calendario",
       subtitle = "Descomposición STL de la serie mensual, 2018-2022",
       x = NULL, y = NULL, caption = fuente_siniestros) +
  theme(strip.text = element_text(face = "bold", hjust = 0))
guardar_fig(p_stl, "06_stl", ancho = 8.5, alto = 6)

# Fuerza de la estacionalidad y de la tendencia (Wang, Smith & Hyndman):
# qué proporción de la varianza explica cada componente frente al residuo.
comp <- stl_fit$time.series
var_res <- var(comp[, "remainder"])
fuerza <- function(x) max(0, 1 - var_res / var(x + comp[, "remainder"]))
cat("Fuerza de la estacionalidad:", round(fuerza(comp[, "seasonal"]), 3), "\n")
cat("Fuerza de la tendencia:      ", round(fuerza(comp[, "trend"]), 3), "\n")

# ------------------------------------------------------------
# 4. Suavizado: media móvil de 3 y de 12 meses
# ------------------------------------------------------------
mensual <- mensual |>
  mutate(mm3  = zoo::rollmean(victimas, 3,  fill = NA, align = "center"),
         mm12 = zoo::rollmean(victimas, 12, fill = NA, align = "center"))

p_suave <- mensual |>
  ggplot(aes(fecha)) +
  geom_line(aes(y = victimas), colour = "grey70", linewidth = 0.6) +
  geom_line(aes(y = mm3, colour = "Media móvil 3 meses"), linewidth = 0.9) +
  geom_line(aes(y = mm12, colour = "Media móvil 12 meses"), linewidth = 1.1) +
  scale_colour_manual(values = c("Media móvil 3 meses" = col_principal,
                                 "Media móvil 12 meses" = col_acento)) +
  scale_x_date(date_labels = "%Y", date_breaks = "1 year") +
  scale_y_continuous(labels = comma_format(big.mark = ".", decimal.mark = ",")) +
  labs(title = "Suavizar es elegir qué se quiere ver",
       subtitle = "La ventana corta deja ver el calendario; la larga, la tendencia",
       x = NULL, y = "Víctimas por mes", colour = NULL,
       caption = fuente_siniestros)
guardar_fig(p_suave, "06_suavizado", ancho = 8.5, alto = 4.4)

# ------------------------------------------------------------
# 5. El calendario: qué meses pesan
# ------------------------------------------------------------
meses_es <- c("ene", "feb", "mar", "abr", "may", "jun",
              "jul", "ago", "sep", "oct", "nov", "dic")
# El promedio bruto por mes mezcla el calendario con el nivel del
# año: abril de 2020 (confinamiento) hunde el promedio de abril y no
# por razones estacionales. Por eso el ranking se toma de la
# componente estacional de STL, que ya viene libre de tendencia.
efecto_mes <- tibble(mes = 1:12,
                     efecto = as.numeric(stl_fit$time.series[1:12, "seasonal"]))
orden_mes <- efecto_mes |> arrange(desc(efecto))
mes_alto  <- meses_es[orden_mes$mes[1]]
mes_bajo  <- meses_es[orden_mes$mes[nrow(orden_mes)]]
print(orden_mes)

p_estacional <- mensual |>
  mutate(mes_nom = factor(meses_es[mes], levels = meses_es),
         anio = factor(anio)) |>
  ggplot(aes(mes_nom, victimas, group = anio, colour = anio)) +
  geom_line(linewidth = 0.8, alpha = 0.85) +
  scale_colour_manual(values = c("#9DC3E6", "#2E75B6", col_acento,
                                 col_verde, "#E3A857")) +
  scale_y_continuous(labels = comma_format(big.mark = ".", decimal.mark = ",")) +
  labs(title = sprintf("%s es el mes más cargado; %s, el más liviano",
                       tools::toTitleCase(mes_alto), mes_bajo),
       subtitle = "Víctimas por mes, un año por línea",
       x = NULL, y = "Víctimas", colour = NULL, caption = fuente_siniestros)
guardar_fig(p_estacional, "06_estacional", ancho = 8, alto = 4.4)

saveRDS(list(mensual = mensual, s25 = s25, ts = victimas_ts, stl = stl_fit),
        file.path(dir_datos, "series.rds"))
cat("\nBloque 3.4.1 completado.\n")
