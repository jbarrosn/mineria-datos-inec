# ============================================================
# 04_arboles_knn.R — Bloque 3.3.1
# Árboles de decisión y k-vecinos más cercanos
# Pregunta: ¿se puede anticipar si un trabajador es informal
# a partir de sus características, sin preguntarle dónde trabaja?
# ============================================================

source("scripts/00_setup.R")

ocupados <- readRDS(file.path(dir_datos, "ocupados.rds"))

# ------------------------------------------------------------
# 1. La decisión que define el ejercicio: qué NO entra al modelo
# ------------------------------------------------------------
# 'informal' se construye con el tamaño del establecimiento, el
# RUC y la contabilidad del negocio. Si esas variables entran como
# predictoras, el modelo "aprende" la definición y la exactitud
# se vuelve una ilusión (fuga de información, leakage).
# Tampoco entra el ingreso: es consecuencia, no causa, y su
# inclusión convierte el problema en una tautología.
predictoras <- c("edad", "sexo", "area", "region", "educ",
                 "etnia_g", "categoria", "rama", "horas")

datos <- ocupados |>
  filter(!is.na(informal)) |>
  select(all_of(predictoras), informal) |>
  # Categorías con poquísimos casos: se agrupan para que el árbol no
  # invente ramas con 4 personas. Se declara y se documenta.
  mutate(categoria = fct_collapse(categoria,
           "Asalariado privado" = c("Empleado privado", "Empleado tercerizado",
                                    "Empleado doméstico"),
           "Asalariado público" = "Empleado público",
           "Cuenta propia"      = "Cuenta propia",
           "Patrono"            = "Patrono",
           "Jornalero"          = "Jornalero",
           "No remunerado"      = c("Trabajador del hogar no remunerado",
                                    "Trabajador no del hogar no remunerado",
                                    "Ayudante no remunerado")),
         informal = factor(informal, levels = c(0, 1),
                           labels = c("Formal", "Informal")))

cat("Casos con variable objetivo:", fmt_num(nrow(datos)), "\n")
print(colSums(is.na(datos[, predictoras])))

datos <- datos |> drop_na()

cat("Casos completos para modelar:", fmt_num(nrow(datos)), "\n")
cat("Balance de clases:\n"); print(round(prop.table(table(datos$informal)), 3))

# Muestra: 30.000 casos. No es una limitación del método, es una
# decisión de costo computacional para una clase de 90 minutos.
set.seed(SEMILLA)
datos <- datos |> slice_sample(n = 30000)

particion <- createDataPartition(datos$informal, p = 0.7, list = FALSE)
train <- datos[particion, ]
test  <- datos[-particion, ]

cat("Entrenamiento:", fmt_num(nrow(train)), "| Prueba:", fmt_num(nrow(test)), "\n")

ctrl <- trainControl(method = "cv", number = 10,
                     classProbs = TRUE, summaryFunction = twoClassSummary,
                     savePredictions = "final")

# ------------------------------------------------------------
# 2. Árbol: el que gana en validación y el que cabe en el tablero
# ------------------------------------------------------------
# cp = parámetro de complejidad: cuánto tiene que mejorar un corte
# para justificar una rama nueva. Se busca por validación cruzada.
set.seed(SEMILLA)
arbol_cv <- train(informal ~ ., data = train, method = "rpart",
                  trControl = ctrl, metric = "ROC",
                  tuneGrid = expand.grid(cp = c(0.001, 0.005, 0.01, 0.02, 0.05)))
print(arbol_cv$results[, c("cp", "ROC", "Spec", "Sens")])

# Gana cp = 0,001. Ese árbol tiene 24 hojas: predice mejor y no se
# puede explicar. Para la clase se ajusta el mismo modelo con
# cp = 0,01 y se mide exactamente lo que cuesta esa decisión.
# OJO: en rpart, cp no es un argumento suelto sino un parámetro de
# rpart.control. Si se pasa como cp = ..., se ignora en silencio.
arbol_opt <- rpart(informal ~ ., data = train, method = "class",
                   control = rpart.control(cp = arbol_cv$bestTune$cp),
                   parms = list(split = "gini"))

arbol <- rpart(informal ~ ., data = train, method = "class",
               control = rpart.control(cp = 0.01, minsplit = 200,
                                       minbucket = 100),
               parms = list(split = "gini"))
print(arbol)

cat("\nHojas — árbol óptimo:", sum(arbol_opt$frame$var == "<leaf>"),
    "| árbol de clase:", sum(arbol$frame$var == "<leaf>"), "\n")

auc_test <- function(modelo) {
  p <- predict(modelo, test, type = "prob")[, "Informal"]
  as.numeric(pROC::auc(pROC::roc(test$informal, p, quiet = TRUE,
                                 levels = c("Formal", "Informal"))))
}
cat("ROC en prueba — óptimo:", round(auc_test(arbol_opt), 3),
    "| de clase:", round(auc_test(arbol), 3), "\n")

# El árbol de clase, dibujado con ggplot.
# plot.rpart desborda cuando una rama lista trece niveles de 'rama';
# se dibuja a mano, leyendo las condiciones con path.rpart().
dibujar_arbol <- function(fit, etiquetas_clase = c("Formal", "Informal")) {
  fr <- fit$frame
  fr$id <- as.integer(rownames(fr))
  fr$depth <- floor(log2(fr$id))
  fr$padre <- fr$id %/% 2L
  fr$var <- as.character(fr$var)

  # posición horizontal: hojas en recorrido in-orden (izquierda a
  # derecha tal como se lee el árbol), nodos internos al centro
  hojas <- integer(0)
  recorrer <- function(id) {
    if (fr$var[fr$id == id] == "<leaf>") hojas <<- c(hojas, id)
    else { recorrer(2 * id); recorrer(2 * id + 1) }
  }
  recorrer(1L)

  fr$x <- NA_real_
  fr$x[match(hojas, fr$id)] <- seq_along(hojas)
  for (i in order(-fr$depth)) {
    if (fr$var[i] != "<leaf>") fr$x[i] <- mean(fr$x[fr$padre == fr$id[i]])
  }

  abreviar <- c("Administración pública" = "Adm. pública",
                "Alojamiento y comida"   = "Alojamiento",
                "Arte y recreación"      = "Arte",
                "Asalariado privado"     = "Asal. privado",
                "Asalariado público"     = "Asal. público",
                "No remunerado"          = "No remun.",
                "Otros servicios"        = "Otros serv.")

  fr$texto <- NA_character_
  for (i in seq_len(nrow(fr))) {
    cond <- rpart::path.rpart(fit, fr$id[i], print.it = FALSE)[[1]]
    cond <- cond[length(cond)]
    if (fr$var[i] == "<leaf>") {
      fr$texto[i] <- sprintf("%s\nn = %s\n%.0f%% informal",
                             etiquetas_clase[fr$yval[i]],
                             fmt_num(fr$n[i]),
                             100 * fr$yval2[i, 5])
    } else if (fr$id[i] == 1) {
      fr$texto[i] <- sprintf("Todos\nn = %s\n%.0f%% informal",
                             fmt_num(fr$n[i]), 100 * fr$yval2[i, 5])
    } else {
      et <- cond
      for (k in names(abreviar)) et <- gsub(k, abreviar[[k]], et, fixed = TRUE)
      et <- sub("^categoria=", "Categoría: ", et)
      et <- sub("^rama=", "Rama: ", et)
      et <- sub("^region=", "Región: ", et)
      et <- sub("^educ=", "Educación: ", et)
      et <- gsub(",", ", ", et, fixed = TRUE)
      fr$texto[i] <- stringr::str_wrap(et, width = 26)
    }
  }

  aristas <- fr |>
    filter(padre > 0) |>
    transmute(x = x, y = -depth,
              xend = fr$x[match(padre, fr$id)],
              yend = -fr$depth[match(padre, fr$id)])

  ggplot(fr, aes(x, -depth)) +
    geom_segment(data = aristas, aes(x = xend, y = yend, xend = x, yend = y),
                 colour = "grey55", linewidth = 0.5) +
    geom_label(aes(label = texto), size = 2.8, lineheight = 0.95,
               label.size = 0.18, label.padding = unit(0.2, "lines"),
               fill = ifelse(fr$var == "<leaf>",
                             ifelse(fr$yval == 2, "#F8E5E4", "#E6EEF6"), "white"),
               colour = "grey15") +
    scale_x_continuous(expand = expansion(add = 0.7)) +
    scale_y_continuous(expand = expansion(add = 0.5)) +
    labs(title = "El árbol separa por categoría ocupacional, no por edad ni por sexo",
         subtitle = "Cinco hojas, cuatro preguntas: la versión del modelo que cabe en una diapositiva",
         x = NULL, y = NULL, caption = fuente_enemdu) +
    theme(axis.text = element_blank(), panel.grid = element_blank(),
          plot.margin = margin(12, 12, 10, 12))
}

p_arbol <- dibujar_arbol(arbol)
guardar_fig(p_arbol, "04_arbol", ancho = 12, alto = 7)

# ------------------------------------------------------------
# 3. k-vecinos más cercanos
# ------------------------------------------------------------
# kNN depende de la escala: sin estandarizar, 'horas' (0-100) pesa
# mucho más que 'edad' en la distancia. caret lo hace aquí, y se
# dice explícitamente.
set.seed(SEMILLA)
knn <- train(informal ~ ., data = train, method = "knn",
             trControl = ctrl, metric = "ROC",
             preProcess = c("center", "scale"),
             tuneLength = 12)
print(knn)

p_knn <- ggplot(knn$results, aes(k, ROC)) +
  geom_line(colour = col_principal, linewidth = 1) +
  geom_point(colour = col_principal, size = 2.5) +
  geom_point(data = knn$results[knn$results$k == knn$bestTune$k, ],
             colour = col_acento, size = 4, shape = 1, stroke = 1.4) +
  scale_x_continuous(breaks = knn$results$k) +
  labs(title = "Elegir k es elegir el sesgo: pocos vecinos, frontera nerviosa",
       subtitle = sprintf("Curva de validación cruzada. k óptimo = %d", knn$bestTune$k),
       x = "Número de vecinos (k)", y = "Área bajo la curva ROC (validación cruzada)",
       caption = fuente_enemdu)
guardar_fig(p_knn, "04_knn_k", ancho = 7, alto = 4.2)

# ------------------------------------------------------------
# 4. Importancia de variables del árbol
# ------------------------------------------------------------
imp <- tibble(variable = names(arbol$variable.importance),
              Overall  = as.numeric(arbol$variable.importance))

p_imp <- ggplot(imp, aes(Overall, fct_reorder(variable, Overall))) +
  geom_col(fill = col_principal, width = 0.7) +
  labs(title = "Qué pesa de verdad para predecir informalidad",
       subtitle = "Importancia de cada variable en el árbol (escala 0-100)",
       x = "Importancia", y = NULL, caption = fuente_enemdu) +
  theme(panel.grid.major.y = element_blank())
guardar_fig(p_imp, "04_importancia", ancho = 7, alto = 4.5)

saveRDS(list(arbol = arbol, arbol_opt = arbol_opt, arbol_cv = arbol_cv,
             knn = knn, train = train, test = test, predictoras = predictoras),
        file.path(dir_datos, "modelos_313.R"))
cat("\nBloque 3.3.1 completado.\n")
