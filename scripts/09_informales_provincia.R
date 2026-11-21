# ============================================================
# 09_informales_provincia.R
# ¿Dónde se concentra la masa de trabajadores informales?
# La tasa dice qué tan informal es una provincia; el conteo dice
# cuánta gente es. Sin las dos, el mapa engaña.
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

ruta_sav <- file.path(ruta_inec, "1_BDD_ENEMDU_2025_SPSS",
                      "BDDenemdu_personas_2025_anual.sav")

d <- haven::read_sav(ruta_sav, col_select = c(empleo, secemp, fexp, prov, p03))
d <- haven::zap_labels(d)

oc <- d |>
  filter(p03 >= 15, !is.na(empleo), empleo == 1, !is.na(secemp)) |>
  mutate(informal = as.integer(secemp == 2))

prov <- oc |>
  group_by(prov) |>
  summarise(ocupados  = sum(fexp),
            informales = sum(fexp * informal),
            tasa      = weighted.mean(informal, fexp),
            .groups = "drop") |>
  left_join(prov_regiones, by = "prov") |>
  filter(!is.na(provincia)) |>
  mutate(provincia = factor(provincia))

nacional <- sum(prov$informales)
prov <- prov |>
  arrange(desc(informales)) |>
  mutate(acumulado = cumsum(informales) / nacional,
         orden = row_number())

exportar_tabla(prov |> select(provincia, ocupados, informales, tasa, acumulado),
               "09_informales_provincia")

cat("Informales en el pais:", fmt_num(nacional / 1e6, 2), "millones\n")
cat("Guayas + Pichincha concentran:",
    fmt_pct(sum(prov$informales[prov$orden <= 2]) / nacional), "\n")
cat("Cinco primeras concentran:",
    fmt_pct(sum(prov$informales[prov$orden <= 5]) / nacional), "\n")

# ------------------------------------------------------------
# La figura: barras por volumen, color por tasa
# ------------------------------------------------------------
# Dos lecturas en una sola imagen: el largo de la barra es la
# gente, el color es la proporcion. Asi se ve de un golpe que la
# tasa alta esta en la Amazonia y la masa esta en Guayas.
p <- ggplot(prov, aes(informales / 1e3, fct_reorder(provincia, informales))) +
  geom_col(aes(fill = tasa), width = 0.72) +
  geom_text(aes(label = paste0(fmt_num(informales / 1e3), "  ·  ", fmt_pct(tasa))),
            hjust = -0.14, size = 2.8, colour = "grey25") +
  scale_fill_gradient2(low = "#9DC3E6", mid = "#E8C07D", high = col_acento,
                       midpoint = 0.58, labels = percent_format(accuracy = 1),
                       name = "Tasa de informalidad") +
  scale_x_continuous(labels = comma_format(big.mark = ".", decimal.mark = ","),
                     expand = expansion(mult = c(0, 0.26))) +
  labs(title = "El volumen no está donde está la tasa",
       subtitle = paste0("Trabajadores informales por provincia, en miles, y tasa de informalidad. ",
                         "La barra es la gente; el color, la proporción"),
       x = "Miles de trabajadores informales", y = NULL,
       caption = paste0(fuente_enemdu,
                        "\nGuayas y Pichincha reúnen el ",
                        fmt_pct(sum(prov$informales[prov$orden <= 2]) / nacional),
                        " de los informales del país; las cinco primeras, el ",
                        fmt_pct(sum(prov$informales[prov$orden <= 5]) / nacional), ".")) +
  theme(legend.position = "bottom",
        legend.key.width = unit(2.4, "lines"),
        panel.grid.major.y = element_blank())
guardar_fig(p, "09_informales_concentracion", ancho = 8.4, alto = 7)

# ------------------------------------------------------------
# Contraste explicito: tasa y volumen no coinciden
# ------------------------------------------------------------
cat("\nLas cinco con tasa mas alta:\n")
print(prov |> arrange(desc(tasa)) |> select(provincia, tasa, informales) |>
        head(5) |> mutate(tasa = round(100 * tasa, 1),
                          informales = round(informales / 1e3)) |> as.data.frame(),
      row.names = FALSE)

cat("\nLas cinco con mas informales en volumen:\n")
print(prov |> arrange(desc(informales)) |> select(provincia, tasa, informales) |>
        head(5) |> mutate(tasa = round(100 * tasa, 1),
                          informales = round(informales / 1e3)) |> as.data.frame(),
      row.names = FALSE)
