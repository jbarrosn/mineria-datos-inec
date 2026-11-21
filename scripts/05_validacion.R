# ============================================================
# 05_validacion.R — Bloque 3.3.2
# Validación cruzada y métricas de desempeño
# Pregunta: ¿cuál de los tres modelos sirve para decidir, y con
# qué umbral? Porque la exactitud sola engaña.
# ============================================================

source("scripts/00_setup.R")

m     <- readRDS(file.path(dir_datos, "modelos_331.rds"))
train <- m$train
test  <- m$test

# ------------------------------------------------------------
# 1. Un tercer modelo: la línea base aburrida
# ------------------------------------------------------------
# Regresión logística. Si un modelo complicado no le gana a esto,
# el modelo complicado no se justifica.
logit <- glm(informal ~ ., data = train, family = binomial)

modelos <- list(
  "Árbol (5 hojas)" = m$arbol,
  "kNN (k = 27)"    = m$knn,
  "Logística"       = logit
)

probs <- map(modelos, function(mod) {
  if (inherits(mod, "glm")) {
    predict(mod, newdata = test, type = "response")
  } else {
    predict(mod, newdata = test, type = "prob")[, "Informal"]
  }
})

# ------------------------------------------------------------
# 2. El umbral no es 0,5 por naturaleza
# ------------------------------------------------------------
# Se elige el umbral en ENTRENAMIENTO (índice de Youden), no en
# prueba: elegirlo mirando el test es una forma elegante de hacer
# trampa y de inflar el resultado que se reporta.
probs_train <- map(modelos, function(mod) {
  if (inherits(mod, "glm")) predict(mod, newdata = train, type = "response")
  else predict(mod, newdata = train, type = "prob")[, "Informal"]
})

umbral_youden <- function(p, y) {
  r <- pROC::roc(y, p, quiet = TRUE, levels = c("Formal", "Informal"))
  as.numeric(pROC::coords(r, "best", ret = "threshold",
                          best.method = "youden")[1])
}

umbrales <- map2_dbl(probs_train, list(train$informal), umbral_youden)
print(round(umbrales, 3))

# ------------------------------------------------------------
# 3. Métricas: exactitud, sensibilidad, especificidad, F1, AUC
# ------------------------------------------------------------
metricas <- function(p, y, umbral) {
  pred <- factor(ifelse(p >= umbral, "Informal", "Formal"),
                 levels = c("Formal", "Informal"))
  cm <- table(real = y, predicho = pred)
  vp <- cm["Informal", "Informal"]; fp <- cm["Formal", "Informal"]
  vn <- cm["Formal", "Formal"];     fn <- cm["Informal", "Formal"]
  precision <- vp / (vp + fp)
  recall    <- vp / (vp + fn)
  tibble(
    exactitud     = (vp + vn) / sum(cm),
    sensibilidad  = recall,
    especificidad = vn / (vn + fp),
    precision     = precision,
    f1            = 2 * precision * recall / (precision + recall),
    auc           = as.numeric(pROC::auc(pROC::roc(
      y, p, quiet = TRUE, levels = c("Formal", "Informal"))))
  )
}

tabla_metricas <- map2_dfr(probs, umbrales, ~ metricas(.x, test$informal, .y),
                           .id = "modelo") |>
  mutate(across(where(is.numeric), ~ round(.x, 3)),
         umbral = round(umbrales, 3), .after = modelo) |>
  arrange(desc(f1)) |>
  select(modelo, umbral, exactitud, sensibilidad, especificidad,
         precision, f1, auc)

exportar_tabla(tabla_metricas, "05_metricas")
print(tabla_metricas)

# ------------------------------------------------------------
# 4. La matriz de confusión del modelo elegido
# ------------------------------------------------------------
# Exactitud alta con sensibilidad baja es el patrón típico de un
# modelo que "acierta" porque la clase mayoritaria es la formal.
elegido <- tabla_metricas$modelo[1]
p_eleg  <- probs[[elegido]]
pred    <- factor(ifelse(p_eleg >= umbrales[[elegido]], "Informal", "Formal"),
                  levels = c("Formal", "Informal"))
cm <- table(real = test$informal, predicho = pred)
print(cm)

cm_df <- as.data.frame(cm) |>
  mutate(etiqueta = paste0(fmt_num(Freq), "\n(", fmt_pct(Freq / sum(Freq)), ")"))

p_cm <- ggplot(cm_df, aes(predicho, real, fill = Freq)) +
  geom_tile(colour = "white", linewidth = 1.5) +
  geom_text(aes(label = etiqueta), colour = "white", size = 4.2,
            fontface = "bold", lineheight = 0.9) +
  scale_fill_gradient(low = col_apoyo, high = col_principal, guide = "none") +
  labs(title = sprintf("Matriz de confusión: %s, umbral %.2f", elegido,
                       umbrales[[elegido]]),
       subtitle = "Cada celda es un error que alguien va a pagar en la política pública",
       x = "Lo que el modelo dice", y = "Lo que la encuesta dice",
       caption = fuente_enemdu) +
  coord_equal()
guardar_fig(p_cm, "05_matriz_confusion", ancho = 5.5, alto = 4.8)

# ------------------------------------------------------------
# 5. Curvas ROC: la comparación honesta
# ------------------------------------------------------------
curvas <- map_dfr(names(probs), function(nm) {
  r <- pROC::roc(test$informal, probs[[nm]], quiet = TRUE,
                 levels = c("Formal", "Informal"))
  tibble(modelo = nm,
         especificidad = rev(r$specificities),
         sensibilidad  = rev(r$sensitivities),
         auc = as.numeric(pROC::auc(r)))
}) |>
  mutate(modelo = fct_reorder(modelo, auc, .desc = TRUE))

etiquetas_auc <- curvas |> distinct(modelo, auc) |>
  mutate(etiqueta = sprintf("%s (AUC = %.3f)", modelo, auc))

p_roc <- ggplot(curvas, aes(1 - especificidad, sensibilidad, colour = modelo)) +
  geom_abline(linetype = "dashed", colour = "grey65") +
  geom_line(linewidth = 1.1) +
  scale_colour_manual(values = setNames(c(col_principal, col_acento, col_verde),
                                        levels(curvas$modelo)),
                      labels = setNames(etiquetas_auc$etiqueta, etiquetas_auc$modelo)) +
  scale_x_continuous(labels = percent_format(accuracy = 1)) +
  scale_y_continuous(labels = percent_format(accuracy = 1)) +
  coord_equal() +
  labs(title = "Tres modelos, un mismo test: las curvas se pegan",
       subtitle = "Cuanto más cerca del vértice superior izquierdo, mejor",
       x = "1 − especificidad (falsos positivos)",
       y = "Sensibilidad (verdaderos positivos)",
       colour = NULL, caption = fuente_enemdu)
guardar_fig(p_roc, "05_roc", ancho = 6.6, alto = 5.4)

# ------------------------------------------------------------
# 6. Validación cruzada repetida: ¿el orden es estable?
# ------------------------------------------------------------
# Una sola partición puede ordenar los modelos por azar. Se repite
# la validación 3 veces con 5 pliegues y se reporta la dispersión.
set.seed(SEMILLA)
ctrl_rep <- trainControl(method = "repeatedcv", number = 5, repeats = 3,
                         classProbs = TRUE, summaryFunction = twoClassSummary,
                         savePredictions = "final")

set.seed(SEMILLA)
cv_arbol <- train(informal ~ ., data = train, method = "rpart",
                  trControl = ctrl_rep, metric = "ROC",
                  tuneGrid = data.frame(cp = 0.01))
set.seed(SEMILLA)
cv_knn <- train(informal ~ ., data = train, method = "knn",
                trControl = ctrl_rep, metric = "ROC",
                preProcess = c("center", "scale"),
                tuneGrid = data.frame(k = 27))

cv_resumen <- bind_rows(
  cv_arbol$results |> transmute(modelo = "Árbol (cp = 0,01)", ROC, ROCSD),
  cv_knn$results   |> transmute(modelo = "kNN (k = 27)",       ROC, ROCSD)
) |>
  mutate(ROC = round(ROC, 3), ROCSD = round(ROCSD, 3))
exportar_tabla(cv_resumen, "05_cv_repetida")
print(cv_resumen)

# El modelo de clase se guarda para el informe final
saveRDS(list(tabla = tabla_metricas, cm = cm, logit = logit,
             umbrales = umbrales, cv = cv_resumen),
        file.path(dir_datos, "validacion.rds"))
cat("\nBloque 3.3.2 completado.\n")
