# ============================================================
# 02_pca.R — Bloque 3.2.1
# Análisis de componentes principales
# Pregunta: ¿en cuántas dimensiones se organiza la estructura
# laboral de las provincias ecuatorianas?
# ============================================================

source("scripts/00_setup.R")

ind <- readRDS(file.path(dir_datos, "indicadores_provincia.rds"))

# ------------------------------------------------------------
# 1. La matriz de entrada: 24 provincias × 9 indicadores
# ------------------------------------------------------------
# El ingreso entra en logaritmo: sin eso, Pichincha y Guayas
# dominan la primera componente por magnitud y no por estructura.
X <- ind |>
  transmute(
    provincia,
    region,
    informalidad      = tasa_informal,
    desempleo         = tasa_desempleo,
    empleo_adecuado   = tasa_adecuado,
    log_ingreso       = log10(ingreso_medio),
    horas             = horas_promedio,
    mujeres_ocupadas  = pct_mujeres,
    ruralidad         = pct_rural,
    educacion_superior = pct_superior,
    pobreza           = pct_pobreza
  )

vars_pca <- setdiff(names(X), c("provincia", "region"))

stopifnot(nrow(X) == 24, !anyNA(X[vars_pca]))
cat("Matriz:", nrow(X), "provincias ×", length(vars_pca), "indicadores\n")
cat("Correlaciones altas (|r| > 0,7):\n")
M <- cor(X[vars_pca], use = "complete.obs")
altas <- which(abs(M) > 0.7 & upper.tri(M), arr.ind = TRUE)
if (nrow(altas)) {
  for (i in seq_len(nrow(altas))) {
    cat("  ", rownames(M)[altas[i, 1]], "~", colnames(M)[altas[i, 2]],
        "=", round(M[altas[i, 1], altas[i, 2]], 2), "\n")
  }
}

# ------------------------------------------------------------
# 2. Ajuste: PCA sobre variables estandarizadas
# ------------------------------------------------------------
# scale. = TRUE es obligatorio aquí: las tasas van de 0 a 1 y el
# ingreso en dólares. Sin estandarizar, la componente 1 sería
# "ingreso" y nada más.
pca <- prcomp(X[vars_pca], scale. = TRUE, center = TRUE)
print(summary(pca))

var_expl <- (pca$sdev^2) / sum(pca$sdev^2)
tabla_var <- tibble(
  componente  = paste0("CP", seq_along(var_expl)),
  autovalor   = pca$sdev^2,
  var_exp     = var_expl,
  var_acum    = cumsum(var_expl)
)
exportar_tabla(tabla_var, "02_varianza_explicada")
print(tabla_var)

# Criterio de Kaiser: retener autovalores > 1
k_kaiser <- sum(pca$sdev^2 > 1)
cat("\nComponentes con autovalor > 1 (Kaiser):", k_kaiser, "\n")

# Se interpretan las dos primeras aunque Kaiser retenga k_kaiser:
# CP1 y CP2 acumulan 79,6% y sostienen el índice. CP3 no se usa en
# el relato porque su autovalor (0,93) no supera el criterio.
n_comp <- max(k_kaiser, 2L)

# Orientación de CP1: el signo de un vector propio es arbitrario.
# Se fija para que "más grande = más formal" y no dependa de la corrida.
if (cor(pca$x[, 1], X$informalidad) > 0) {
  pca$x[, 1]      <- -pca$x[, 1]
  pca$rotation[, 1] <- -pca$rotation[, 1]
}

# ------------------------------------------------------------
# 3. Cargas: qué significa cada componente
# ------------------------------------------------------------
cargas <- as.data.frame(pca$rotation[, seq_len(n_comp)]) |>
  tibble::rownames_to_column("indicador") |>
  mutate(across(starts_with("PC"), ~ round(.x, 2)))
exportar_tabla(cargas, "02_cargas")
print(cargas)

p_cargas <- cargas |>
  pivot_longer(starts_with("PC"), names_to = "componente", values_to = "carga") |>
  mutate(componente = factor(componente,
                             levels = c("PC1", "PC2", "PC3"),
                             labels = sprintf("CP%d (%.0f%%)", 1:3,
                                              100 * var_expl[1:3])),
         indicador = fct_reorder(indicador, carga)) |>
  ggplot(aes(carga, indicador, fill = carga > 0)) +
  geom_col(width = 0.68) +
  geom_vline(xintercept = 0, colour = "grey30") +
  facet_wrap(~componente, ncol = 3, scales = "free_x") +
  scale_fill_manual(values = c(`TRUE` = col_principal, `FALSE` = col_acento),
                    guide = "none") +
  labs(title = "Cada componente es una mezcla de indicadores, no un indicador",
       subtitle = "Cargas factoriales de las tres primeras componentes",
       x = "Carga", y = NULL, caption = fuente_enemdu) +
  theme(strip.text = element_text(face = "bold"),
        panel.grid.major.y = element_blank())
guardar_fig(p_cargas, "02_cargas", ancho = 11, alto = 4.2)

# ------------------------------------------------------------
# 4. Varianza explicada (scree) y criterios de retención
# ------------------------------------------------------------
p_scree <- tabla_var |>
  ggplot(aes(componente, var_exp)) +
  geom_col(fill = col_apoyo, width = 0.65) +
  geom_line(aes(group = 1), colour = col_principal, linewidth = 1) +
  geom_point(colour = col_principal, size = 2.5) +
  geom_hline(yintercept = 1 / length(vars_pca), linetype = "dashed",
             colour = col_acento) +
  annotate("text", x = 1, y = 1 / length(vars_pca) + 0.02,
           label = "criterio de Kaiser (1/9)", hjust = 0, size = 3,
           colour = col_acento) +
  scale_y_continuous(labels = percent_format(accuracy = 1)) +
  labs(title = sprintf("Una sola componente ya explica %.0f%% de la estructura provincial",
                       100 * var_expl[1]),
       subtitle = sprintf("Varianza explicada por componente. Las dos primeras acumulan %.1f%%",
                          100 * sum(var_expl[1:2])),
       x = NULL, y = "Varianza explicada", caption = fuente_enemdu) +
  theme(panel.grid.major.x = element_blank())
guardar_fig(p_scree, "02_scree", ancho = 7, alto = 4.5)

# ------------------------------------------------------------
# 5. Puntajes: el mapa de las provincias en dos ejes
# ------------------------------------------------------------
# En este ajuste CP1 ya viene orientada "más grande = más formal"
# (carga +0,41 en empleo adecuado y -0,41 en informalidad). Se deja
# tal cual y se escribe la convención: no se invierte un eje sin
# decir por qué.
scores <- as.data.frame(pca$x[, seq_len(n_comp)]) |>
  bind_cols(provincia = X$provincia, region = X$region) |>
  mutate(CP1_formalidad = PC1,
         indice_0_100 = 100 * (CP1_formalidad - min(CP1_formalidad)) /
           diff(range(CP1_formalidad))) |>
  as_tibble() |>
  arrange(desc(indice_0_100))

exportar_tabla(scores, "02_puntajes")
print(scores |> select(provincia, region, CP1_formalidad, indice_0_100), n = 24)

p_biplot <- ggplot(scores, aes(CP1_formalidad, PC2)) +
  geom_hline(yintercept = 0, colour = "grey85") +
  geom_vline(xintercept = 0, colour = "grey85") +
  geom_point(aes(colour = region), size = 3.2) +
  ggrepel::geom_text_repel(aes(label = provincia, colour = region),
                           size = 3, max.overlaps = 30, seed = SEMILLA,
                           show.legend = FALSE) +
  scale_colour_manual(values = c(Sierra = col_principal, Costa = col_acento,
                                 Amazonía = col_verde, Galápagos = "#E3A857")) +
  labs(title = "El Ecuador laboral se ordena en un eje formal-informal",
       subtitle = "Puntajes de las dos primeras componentes (CP1: derecha = más formal)",
       x = "CP1 · formalidad del empleo provincial",
       y = "CP2 · contraste rural-femenino / urbano-masculino",
       colour = NULL, caption = fuente_enemdu)
guardar_fig(p_biplot, "02_biplot", ancho = 8.5, alto = 6)

# Contribución de cada provincia a CP1 (quién mueve el eje)
contrib <- factoextra::get_pca_ind(pca)$contrib[, 1:2] |>
  as.data.frame() |>
  bind_cols(provincia = X$provincia) |>
  arrange(desc(Dim.1))
exportar_tabla(contrib, "02_contribucion_provincias")

# ------------------------------------------------------------
# 6. Contraste con los indicadores originales
# ------------------------------------------------------------
# Un PCA que no se puede explicar con las variables de origen no
# sirve para decidir nada. Se verifica la correlación CP1 vs. cada
# indicador por separado.
# OJO: 'scores' está ordenado por el índice; los puntajes que se
# alinean fila a fila con la matriz X son los crudos, sin ordenar.
cp_crudos <- tibble(CP1 = pca$x[, 1], CP2 = pca$x[, 2], provincia = X$provincia)

verif <- map_dfr(vars_pca, function(v) {
  tibble(indicador = v,
         r_CP1 = cor(cp_crudos$CP1, X[[v]], use = "complete.obs"),
         r_CP2 = cor(cp_crudos$CP2, X[[v]], use = "complete.obs"))
}) |>
  arrange(desc(abs(r_CP1)))
exportar_tabla(verif, "02_verificacion_cp1")
print(verif)

saveRDS(list(pca = pca, scores = scores, X = X), file.path(dir_datos, "pca.rds"))
cat("\nBloque 3.2.1 completado.\n")
