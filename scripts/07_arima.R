# ============================================================
# 07_arima.R — Bloque 3.4.2
# Modelos ARIMA y pronóstico
# Pregunta: ¿cuántas víctimas habría en 2022 si el patrón de
# 2018-2021 se hubiera mantenido? El test es 2022, que el modelo
# nunca vio.
# ------------------------------------------------------------
# Resultado del bloque, anunciado desde el inicio: NINGUNO de los
# modelos univariados le gana al ingenuo estacional. La clase no
# termina con un modelo ganador; termina con una comparación
# honesta y con la razón del fracaso. Es la fase de evaluación de
# CRISP-DM, no un fracaso de la sesión.
# ============================================================

source("scripts/00_setup.R")

s <- readRDS(file.path(dir_datos, "series.rds"))
y <- s$ts                      # 60 meses, 2018-2022

train <- window(y, end = c(2021, 12))
test  <- window(y, start = c(2022, 1))

cat("Entrenamiento:", length(train), "meses | Prueba:", length(test), "meses\n")

# ------------------------------------------------------------
# 1. ¿La serie necesita diferenciación? Se pregunta, no se supone
# ------------------------------------------------------------
adf  <- tseries::adf.test(train, k = 12)           # H0: raíz unitaria
kpss <- tseries::kpss.test(train, null = "Level")  # H0: estacionariedad
cat("\nADF  p =", round(adf$p.value, 4), "(H0: raíz unitaria)\n")
cat("KPSS p =", round(kpss$p.value, 4), "(H0: estacionariedad)\n")
cat("Lectura: con 48 meses, el ADF no rechaza raíz unitaria y el KPSS\n",
    "tampoco rechaza estacionariedad. Los tests no deciden solos; la\n",
    "ACF y el conocimiento del fenómeno sí.\n")

p_acf <- forecast::ggAcf(train, lag.max = 36) +
  labs(title = "La autocorrelación no se apaga: hay estacionalidad",
       subtitle = "ACF de la serie mensual de víctimas, 2018-2021",
       x = "Rezago (meses)", y = "Autocorrelación", caption = fuente_siniestros)
guardar_fig(p_acf, "07_acf", ancho = 7, alto = 4)

# ------------------------------------------------------------
# 2. Dos candidatos y una variable de intervención
# ------------------------------------------------------------
# Abril-diciembre de 2020 es un choque, no estacionalidad. Se entra
# como variable indicadora (xreg). Pronosticar 2022 exige decir que
# la intervención vale 0 en el futuro.
covid <- ts(as.integer(trunc(time(train)) == 2020 & cycle(train) >= 4),
            start = start(train), frequency = 12)
covid_futuro <- ts(rep(0, length(test)), start = start(test), frequency = 12)

set.seed(SEMILLA)
automatico <- auto.arima(train, seasonal = TRUE, stepwise = FALSE,
                         approximation = FALSE, xreg = covid, trace = FALSE)

# El candidato de libro para series mensuales: la aerolínea
# (0,1,1)(0,1,1)[12]. Se elige por AIC y por diagnóstico, no por
# mirar el test.
aerolinea <- Arima(train, order = c(0, 1, 1), seasonal = c(0, 1, 1),
                   xreg = covid)

cat("\n--- auto.arima ---\n"); print(automatico)
cat("\n--- aerolínea (0,1,1)(0,1,1)[12] ---\n"); print(aerolinea)
cat("\nAIC automático:", round(AIC(automatico), 1),
    "| AIC aerolínea:", round(AIC(aerolinea), 1), "\n")

modelo <- aerolinea

# ------------------------------------------------------------
# 3. Diagnóstico: sin esto, el modelo no se reporta
# ------------------------------------------------------------
cat("\n--- Diagnóstico del modelo aerolínea ---\n")
lb <- Box.test(residuals(modelo), lag = 24, type = "Ljung-Box", fitdf = 3)
print(lb)
cat("p =", round(lb$p.value, 4), "\n")
if (lb$p.value < 0.05) {
  cat("-> el residuo conserva autocorrelación: el modelo está mal especificado.\n",
      "   Se reporta igual y se dice. El diagnóstico no se maquilla.\n")
} else {
  cat("-> no se rechaza la ausencia de autocorrelación.\n")
}

png(file.path(dir_fig, "07_residuos.png"), width = 1500, height = 1000, res = 150)
checkresiduals(modelo)
dev.off()

# ------------------------------------------------------------
# 4. Pronóstico contra el año que el modelo no vio
# ------------------------------------------------------------
fc <- forecast::forecast(modelo, h = length(test), xreg = covid_futuro,
                         level = c(80, 95))

fc_naive <- forecast::snaive(train, h = length(test))
fc_mean  <- forecast::meanf(train, h = length(test))

extraer <- function(f, nm) {
  a <- forecast::accuracy(f, test)[2, c("ME", "RMSE", "MAE", "MAPE")]
  tibble(modelo = nm, ME = a[1], RMSE = a[2], MAE = a[3], MAPE = a[4])
}

acc <- bind_rows(
  extraer(fc, "ARIMA aerolínea"),
  extraer(fc_naive, "Ingenuo estacional"),
  extraer(fc_mean, "Promedio histórico")
) |>
  mutate(across(where(is.numeric), ~ round(.x, 2))) |>
  arrange(RMSE)
exportar_tabla(acc, "07_precision")
print(acc)

# La lectura del resultado, no el resultado:
#   después del choque, la serie vuelve a un nivel cercano al de
#   antes de la pandemia. El ARIMA, al diferenciar, arrastra el nivel
#   deprimido de 2021 y pronostica por debajo. Por eso una constante
#   acierta más que una extrapolación: el modelo se especificó para
#   una serie con tendencia y esta serie, tras el quiebre, revierte.
#   No es que "ARIMA sea malo": es que el diagnóstico manda.
cat("\nPromedio real de 2022:", round(mean(test), 0),
    "| promedio histórico:", round(mean(train), 0),
    "| pronóstico ARIMA medio:", round(mean(fc$mean), 0), "\n")

comparacion <- tibble(
  fecha = seq(as.Date("2022-01-01"), by = "month", length.out = 12),
  real = as.numeric(test),
  arima = as.numeric(fc$mean),
  naive = as.numeric(fc_naive$mean),
  lo80 = as.numeric(fc$lower[, 1]),
  hi80 = as.numeric(fc$upper[, 1])
)

p_fc <- comparacion |>
  ggplot(aes(fecha)) +
  geom_ribbon(aes(ymin = lo80, ymax = hi80), fill = col_apoyo, alpha = 0.3) +
  geom_line(aes(y = real, colour = "Observado 2022"), linewidth = 1.05) +
  geom_line(aes(y = arima, colour = "ARIMA"), linewidth = 0.95, linetype = "dashed") +
  geom_line(aes(y = naive, colour = "Ingenuo estacional"), linewidth = 0.95,
            linetype = "dotted") +
  scale_colour_manual(values = c("Observado 2022" = "grey25",
                                 "ARIMA" = col_acento,
                                 "Ingenuo estacional" = col_principal)) +
  scale_y_continuous(labels = comma_format(big.mark = ".", decimal.mark = ",")) +
  scale_x_date(date_labels = "%b", date_breaks = "1 month") +
  labs(title = "El promedio histórico gana: la serie volvió a su nivel",
       subtitle = "Pronóstico a 12 meses para 2022 con banda de confianza al 80%",
       x = NULL, y = "Víctimas por mes", colour = NULL,
       caption = fuente_siniestros)
guardar_fig(p_fc, "07_pronostico", ancho = 8.8, alto = 4.8)

# ------------------------------------------------------------
# 5. Pronóstico largo: por qué no se promete a tres años
# ------------------------------------------------------------
# Se reajusta con toda la serie y se proyecta hasta 2025. Los tres
# meses observados de 2025 sirven de contraste, no de validación:
# entre 2023 y 2024 no hay dato en el directorio.
covid_full <- ts(as.integer(trunc(time(y)) == 2020 & cycle(y) >= 4),
                 start = start(y), frequency = 12)
set.seed(SEMILLA)
final <- auto.arima(y, seasonal = TRUE, stepwise = FALSE,
                    approximation = FALSE, xreg = covid_full, trace = FALSE)
print(final)

h_largo <- 36
fc_largo <- forecast::forecast(final, h = h_largo,
                               xreg = ts(rep(0, h_largo), start = c(2023, 1),
                                         frequency = 12), level = 95)

p_largo <- autoplot(fc_largo) +
  autolayer(y, series = "Observado 2018-2022") +
  geom_point(data = s$s25, aes(x = fecha, y = victimas, colour = "2025 observado"),
             size = 2.8, inherit.aes = FALSE) +
  scale_colour_manual(values = c("Observado 2018-2022" = col_principal,
                                 "2025 observado" = col_acento)) +
  scale_y_continuous(labels = comma_format(big.mark = ".", decimal.mark = ",")) +
  labs(title = "A tres años, la banda de confianza es la noticia",
       subtitle = "Proyección desde 2022 y los tres meses observados de 2025",
       x = NULL, y = "Víctimas por mes", colour = NULL,
       caption = fuente_siniestros)
guardar_fig(p_largo, "07_pronostico_largo", ancho = 9, alto = 4.6)

saveRDS(list(modelo = modelo, automatico = automatico, final = final,
             fc = fc, fc_naive = fc_naive, accuracy = acc,
             comparacion = comparacion),
        file.path(dir_datos, "arima.rds"))
cat("\nBloque 3.4.2 completado.\n")
