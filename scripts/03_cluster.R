# ============================================================
# 03_cluster.R — Bloque 3.2.2
# Análisis de conglomerados: k-medias y jerárquico
# Pregunta: ¿cuántos tipos de mercado laboral provincial hay
# realmente en el Ecuador, y cuáles son?
# ============================================================

source("scripts/00_setup.R")

ind <- readRDS(file.path(dir_datos, "indicadores_provincia.rds"))

X <- ind |>
  transmute(
    provincia,
    region,
    informalidad       = tasa_informal,
    desempleo          = tasa_desempleo,
    empleo_adecuado    = tasa_adecuado,
    log_ingreso        = log10(ingreso_medio),
    horas              = horas_promedio,
    mujeres_ocupadas   = pct_mujeres,
    ruralidad          = pct_rural,
    educacion_superior = pct_superior,
    pobreza            = pct_pobreza
  )

vars_cl <- setdiff(names(X), c("provincia", "region"))

# Estandarizar es obligatorio: sin esto, log_ingreso domina la
# distancia euclidiana y los conglomerados son solo "provincias
# ricas vs. pobres".
Z <- scale(X[vars_cl])
rownames(Z) <- X$provincia

# ------------------------------------------------------------
# 1. ¿Cuántos grupos? Dos criterios que deben coincidir
# ------------------------------------------------------------
set.seed(SEMILLA)   # k-medias arranca en puntos aleatorios

ks <- 2:6
res_k <- map_dfr(ks, function(k) {
  km <- kmeans(Z, centers = k, nstart = 50, iter.max = 100)
  sil <- cluster::silhouette(km$cluster, dist(Z))
  tibble(k = k,
         withinss = km$tot.withinss,
         between_pct = km$betweenss / km$totss,
         silueta = mean(sil[, "sil_width"]),
         min_grupo = min(table(km$cluster)))
})

# La silueta no es un oráculo. Con 24 provincias, k = 5 gana por
# 0,006 puntos pero añade dos grupos que no aportan un tipo nuevo.
# Regla declarada ANTES de mirar el resultado: se toma el k más
# pequeño cuya silueta esté a menos del 10% del máximo. Parsimonia
# con evidencia, no con gusto.
sil_max <- max(res_k$silueta)
k_opt   <- min(res_k$k[res_k$silueta >= 0.90 * sil_max])
res_k   <- res_k |> mutate(elegido = k == k_opt)
exportar_tabla(res_k, "03_seleccion_k")
print(res_k)

cat("\nk elegido:", k_opt, "| silueta:", round(res_k$silueta[res_k$elegido], 3),
    "| máximo:", round(sil_max, 3), "\n")

p_k <- res_k |>
  pivot_longer(c(withinss, silueta), names_to = "criterio", values_to = "valor") |>
  mutate(criterio = factor(criterio, levels = c("withinss", "silueta"),
                           labels = c("Codo: inercia intra-grupo",
                                      "Silueta media"))) |>
  ggplot(aes(k, valor)) +
  geom_line(colour = col_principal, linewidth = 1) +
  geom_point(colour = col_principal, size = 2.8) +
  geom_vline(xintercept = k_opt, linetype = "dashed", colour = col_acento) +
  facet_wrap(~criterio, scales = "free_y") +
  scale_x_continuous(breaks = ks) +
  labs(title = "El codo sugiere un número; la silueta lo confirma",
       subtitle = "Dos criterios de selección sobre la misma matriz estandarizada",
       x = "Número de conglomerados (k)", y = NULL, caption = fuente_enemdu) +
  theme(strip.text = element_text(face = "bold"))
guardar_fig(p_k, "03_seleccion_k", ancho = 9, alto = 4)

# ------------------------------------------------------------
# 2. k-medias con el k elegido
# ------------------------------------------------------------
set.seed(SEMILLA)
km <- kmeans(Z, centers = k_opt, nstart = 50, iter.max = 100)

asignacion <- tibble(provincia = X$provincia,
                     region = X$region,
                     grupo_km = factor(km$cluster))

# ------------------------------------------------------------
# 3. Jerárquico: Ward sobre la misma distancia
# ------------------------------------------------------------
# Ward minimiza el incremento de inercia; con variables
# estandarizadas y 24 casos es el método más estable.
d <- dist(Z, method = "euclidean")
hc <- hclust(d, method = "ward.D2")
grupo_hc <- cutree(hc, k = k_opt)

asignacion <- asignacion |> mutate(grupo_hc = factor(grupo_hc))

cat("\nConcordancia entre métodos (índice de Rand ajustado):",
    round(mclust::adjustedRandIndex(km$cluster, grupo_hc), 3), "\n")

tabla_conc <- table(kmedias = asignacion$grupo_km, jerarquico = asignacion$grupo_hc)
print(tabla_conc)
exportar_tabla(as.data.frame.matrix(tabla_conc), "03_concordancia")

p_dend <- factoextra::fviz_dend(
  hc, k = k_opt, cex = 0.65, main = NULL,
  palette = pal_curso[seq_len(k_opt)],
  rect = TRUE, rect_border = pal_curso[seq_len(k_opt)],
  rect_fill = TRUE, rect_alpha = 0.12,
  ggtheme = tema_curso(11)
) +
  labs(title = "El dendrograma confirma tres regímenes, no un continuo",
       subtitle = "Conglomerado jerárquico, método de Ward, distancia euclidiana estandarizada",
       x = NULL, y = "Distancia", caption = fuente_enemdu) +
  theme(plot.margin = margin(8, 14, 28, 8),
        axis.text.x = element_text(size = 8))
guardar_fig(p_dend, "03_dendrograma", ancho = 9.5, alto = 6.4)

# ------------------------------------------------------------
# 4. Perfil de cada grupo (en unidades originales)
# ------------------------------------------------------------
# El promedio de la variable estandarizada no se le enseña a nadie:
# se reporta en la unidad en que se mide (porcentaje, dólares).
perfil <- X |>
  left_join(asignacion, by = c("provincia", "region")) |>
  group_by(grupo_km) |>
  summarise(n_provincias = n(),
            informalidad = mean(informalidad),
            desempleo = mean(desempleo),
            empleo_adecuado = mean(empleo_adecuado),
            ingreso_medio = mean(10^log_ingreso),
            horas = mean(horas),
            mujeres_ocupadas = mean(mujeres_ocupadas),
            ruralidad = mean(ruralidad),
            educacion_superior = mean(educacion_superior),
            pobreza = mean(pobreza),
            .groups = "drop") |>
  arrange(desc(informalidad))
exportar_tabla(perfil, "03_perfil_grupos")
print(perfil, width = Inf)

# Nombre substantivo de cada grupo, a partir de su perfil
nombres_grupo <- perfil |>
  mutate(nombre = case_when(
    informalidad > 0.65 ~ "Informal-rural",
    informalidad > 0.45 ~ "Intermedio",
    TRUE                ~ "Enclave formal")) |>
  select(grupo_km, nombre)

asignacion <- asignacion |>
  left_join(nombres_grupo, by = "grupo_km")

exportar_tabla(asignacion, "03_asignacion_grupos")

# ------------------------------------------------------------
# 5. La figura que cierra el bloque: el mapa en una barra
# ------------------------------------------------------------
p_grupos <- asignacion |>
  left_join(X, by = c("provincia", "region")) |>
  mutate(provincia = fct_reorder(provincia, informalidad)) |>
  ggplot(aes(informalidad, provincia, fill = nombre)) +
  geom_col(width = 0.72) +
  scale_x_continuous(labels = percent_format(accuracy = 1),
                     expand = expansion(mult = c(0, 0.08))) +
  scale_fill_manual(values = c("Enclave formal" = col_principal,
                               "Intermedio" = col_verde,
                               "Informal-rural" = col_acento)) +
  labs(title = "Tres Ecuador laborales, no 24 provincias sueltas",
       subtitle = "Provincias ordenadas por informalidad. El color resume nueve indicadores, no solo este",
       x = "Tasa de informalidad", y = NULL, fill = NULL,
       caption = fuente_enemdu) +
  theme(panel.grid.major.y = element_blank())
guardar_fig(p_grupos, "03_grupos_provincia", ancho = 8, alto = 6.5)

# ------------------------------------------------------------
# 6. Verificación: ¿los grupos se separan en las variables?
# ------------------------------------------------------------
# Un conglomerado que no se distingue en ninguna variable es un
# artefacto del algoritmo. Se contrasta con un ANOVA por variable.
separacion <- map_dfr(vars_cl, function(v) {
  m <- aov(Z[, v] ~ asignacion$grupo_km)
  tibble(variable = v,
         F = summary(m)[[1]][["F value"]][1],
         p = summary(m)[[1]][["Pr(>F)"]][1],
         eta2 = summary(m)[[1]][["Sum Sq"]][1] / sum(summary(m)[[1]][["Sum Sq"]]))
}) |>
  arrange(desc(eta2))
exportar_tabla(separacion, "03_separacion_variables")
print(separacion)

saveRDS(list(km = km, hc = hc, Z = Z, asignacion = asignacion, k = k_opt),
        file.path(dir_datos, "clusters.rds"))
cat("\nBloque 3.2.2 completado.\n")
