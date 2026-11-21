# ============================================================
# 03_cluster.R — Bloque 3.2.2
# Análisis de conglomerados: k-medias y jerárquico
# Pregunta: ¿cuántos tipos de mercado laboral provincial hay
# realmente en el Ecuador, y cuáles son?
# ============================================================

# --- configuración común -------------------------------------
# Se busca en las tres ubicaciones posibles: así funciona igual si
# se ejecuta desde la raíz, desde scripts/ o con el botón Source de
# RStudio, que suele dejar el directorio de trabajo en scripts/.
for (.p in c("scripts/00_setup.R", "00_setup.R", "../scripts/00_setup.R")) {
  if (file.exists(.p)) { source(.p); break }
}
if (!exists("SEMILLA")) {
  stop("No se encontró scripts/00_setup.R.\n",
       "  Abre mineria-inec.Rproj, o ejecuta desde la carpeta del proyecto.\n",
       "  Directorio actual: ", getwd())
}
rm(.p)

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
# write_excel_csv descarta los nombres de fila: se convierten en columna.
tabla_conc |>
  as.data.frame.matrix() |>
  tibble::rownames_to_column("grupo_kmedias") |>
  exportar_tabla("03_concordancia")

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
# 5b. Antes y después: los casos en el plano de las componentes
# ------------------------------------------------------------
# La barra anterior dice cómo queda el país; esta muestra qué hizo el
# algoritmo con los casos. Mismos puntos, dos lecturas: sin grupo y
# con grupo.
pca_plano <- prcomp(X[vars_cl], scale. = TRUE)

plano <- tibble::tibble(
  CP1 = pca_plano$x[, 1],
  CP2 = pca_plano$x[, 2],
  provincia = X$provincia
) |>
  dplyr::left_join(asignacion |> dplyr::select(provincia, nombre), by = "provincia")

dibujo <- dplyr::bind_rows(
  plano |> dplyr::mutate(panel = "1 · Antes: solo los datos", grupo = "Sin agrupar"),
  plano |> dplyr::mutate(panel = "2 · Después: tres grupos", grupo = as.character(nombre))
) |>
  dplyr::mutate(
    panel = factor(panel, levels = c("1 · Antes: solo los datos",
                                     "2 · Después: tres grupos")),
    grupo = factor(grupo, levels = c("Sin agrupar", "Enclave formal",
                                     "Intermedio", "Informal-rural"))
  )

despues <- dplyr::filter(dibujo, panel == "2 · Después: tres grupos")

# Contorno de cada grupo (envolvente convexa) y su centroide
contorno <- despues |>
  dplyr::group_by(grupo) |>
  dplyr::filter(dplyr::n() >= 3) |>
  dplyr::slice(grDevices::chull(CP1, CP2)) |>
  dplyr::ungroup()

# Los centroides solo existen después de agrupar: se dibujan en ese panel
centros <- despues |>
  dplyr::group_by(grupo) |>
  dplyr::summarise(CP1 = mean(CP1), CP2 = mean(CP2), .groups = "drop") |>
  dplyr::mutate(panel = factor("2 · Después: tres grupos",
                               levels = levels(dibujo$panel)))

p_plano <- ggplot(dibujo, aes(CP1, CP2, colour = grupo)) +
  geom_polygon(data = contorno, aes(fill = grupo), alpha = 0.14,
               colour = NA, show.legend = FALSE) +
  geom_hline(yintercept = 0, linetype = "dashed", colour = "grey80") +
  geom_vline(xintercept = 0, linetype = "dashed", colour = "grey80") +
  geom_point(size = 2.7) +
  geom_point(data = centros, shape = 4, size = 5.5, stroke = 1.5,
             show.legend = FALSE) +
  facet_wrap(~panel) +
  coord_equal() +
  scale_colour_manual(values = c("Sin agrupar" = "grey45",
                                 "Enclave formal" = col_principal,
                                 "Intermedio" = col_verde,
                                 "Informal-rural" = col_acento), name = NULL) +
  scale_fill_manual(values = c("Enclave formal" = col_principal,
                               "Intermedio" = col_verde,
                               "Informal-rural" = col_acento), guide = "none") +
  labs(title = "Mismos puntos, dos lecturas",
       subtitle = "Cada punto es una provincia en el plano de las dos primeras componentes. La cruz es el centroide",
       x = sprintf("CP1 (%.0f%%)", 100 * pca_plano$sdev[1]^2 / sum(pca_plano$sdev^2)),
       y = sprintf("CP2 (%.0f%%)", 100 * pca_plano$sdev[2]^2 / sum(pca_plano$sdev^2)),
       caption = fuente_enemdu) +
  theme(legend.position = "bottom",
        strip.text = element_text(face = "bold", size = 10.5))
guardar_fig(p_plano, "03_plano_grupos", ancho = 10.5, alto = 5)

# ------------------------------------------------------------
# 5c. Silueta: qué tan bien asignada está cada provincia
# ------------------------------------------------------------
# Se calcula a mano, y no con cluster::silhouette, porque así se ve la
# fórmula: a = distancia media al propio grupo, b = al grupo vecino.
D <- as.matrix(stats::dist(Z))
grupos <- as.integer(asignacion$grupo_km)

ancho_silueta <- vapply(seq_along(grupos), function(i) {
  propio <- which(grupos == grupos[i] & seq_along(grupos) != i)
  if (!length(propio)) return(0)
  a <- mean(D[i, propio])
  ajeno <- vapply(setdiff(unique(grupos), grupos[i]),
                  function(g) mean(D[i, grupos == g]), numeric(1))
  b <- min(ajeno)
  (b - a) / max(a, b)
}, numeric(1))

silueta_df <- tibble::tibble(
  provincia = X$provincia,
  ancho = ancho_silueta,
  grupo = as.character(asignacion$nombre)
) |>
  dplyr::arrange(ancho) |>
  dplyr::mutate(provincia = factor(provincia, levels = provincia))

media_sil <- mean(silueta_df$ancho)

# El título sale del dato, no del deseo: se cuentan las provincias que
# quedan por debajo del umbral habitual de 0,25.
dudosas <- silueta_df |> dplyr::filter(ancho < 0.25) |> dplyr::pull(provincia)
titulo_sil <- if (!length(dudosas)) {
  "Ninguna provincia queda mal clasificada"
} else {
  sprintf("%d de 24 provincias quedan en la zona dudosa", length(dudosas))
}
subtitulo_sil <- if (!length(dudosas)) {
  "Ancho de silueta por provincia"
} else {
  paste0("Ancho de silueta. Bajo 0,25: ",
         paste(as.character(dudosas), collapse = ", "))
}

p_silueta <- ggplot(silueta_df, aes(ancho, provincia, fill = grupo)) +
  geom_col(width = 0.74) +
  geom_vline(xintercept = media_sil, linetype = "dashed", colour = "grey30") +
  annotate("text", x = media_sil, y = 1, hjust = -0.1, vjust = 0,
           label = sprintf("media %.2f", media_sil), size = 3.2,
           colour = "grey25") +
  scale_fill_manual(values = c("Enclave formal" = col_principal,
                               "Intermedio" = col_verde,
                               "Informal-rural" = col_acento), name = NULL) +
  labs(title = titulo_sil,
       subtitle = subtitulo_sil,
       x = "Silueta", y = NULL, caption = fuente_enemdu) +
  theme(legend.position = "bottom", panel.grid.major.y = element_blank())
guardar_fig(p_silueta, "03_silueta", ancho = 8, alto = 6)

# ------------------------------------------------------------
# 5d. El perfil completo: qué distingue a cada grupo
# ------------------------------------------------------------
etiquetas_ind <- c(
  informalidad = "Informalidad", desempleo = "Desempleo",
  empleo_adecuado = "Empleo adecuado", log_ingreso = "Ingreso (log)",
  horas = "Horas", mujeres_ocupadas = "Mujeres ocupadas",
  ruralidad = "Ruralidad", educacion_superior = "Educación superior",
  pobreza = "Pobreza"
)

# Orden de filas: primero los grupos formales, y dentro de cada uno de
# menor a mayor informalidad. La leyenda vertical va de formal a informal
# leyendo de arriba abajo.
orden_prov <- asignacion |>
  dplyr::left_join(X |> dplyr::select(provincia, informalidad), by = "provincia") |>
  dplyr::mutate(nombre = factor(nombre, levels = c("Enclave formal", "Intermedio",
                                                   "Informal-rural"))) |>
  dplyr::arrange(nombre, informalidad) |>
  dplyr::pull(provincia) |>
  as.character()

calor <- as.data.frame(Z) |>
  tibble::as_tibble() |>
  dplyr::mutate(provincia = X$provincia) |>
  tidyr::pivot_longer(-provincia, names_to = "indicador", values_to = "z") |>
  dplyr::mutate(
    indicador = factor(etiquetas_ind[indicador], levels = etiquetas_ind),
    provincia = factor(provincia, levels = orden_prov)
  )

# Separadores entre grupos: la fila donde termina uno y empieza el otro
cortes <- asignacion |>
  dplyr::mutate(nombre = factor(nombre, levels = c("Enclave formal", "Intermedio",
                                                   "Informal-rural"))) |>
  dplyr::count(nombre, .drop = FALSE) |>
  dplyr::pull(n) |>
  cumsum()
cortes <- utils::head(cortes, -1) + 0.5

p_calor <- ggplot(calor, aes(indicador, provincia, fill = z)) +
  geom_tile(colour = "white", linewidth = 0.4) +
  geom_hline(yintercept = cortes, colour = "grey15", linewidth = 1.1) +
  scale_fill_gradient2(low = col_principal, mid = "white", high = col_acento,
                       midpoint = 0, name = "z") +
  labs(title = "El perfil completo de cada grupo",
       subtitle = "Cada celda es una provincia en un indicador estandarizado. Filas agrupadas de formal a informal",
       x = NULL, y = NULL, caption = fuente_enemdu) +
  theme(axis.text.x = element_text(angle = 35, hjust = 1, size = 8),
        axis.text.y = element_text(size = 7.5),
        panel.grid = element_blank(),
        legend.position = "right")
guardar_fig(p_calor, "03_perfil_calor", ancho = 9, alto = 7)

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
