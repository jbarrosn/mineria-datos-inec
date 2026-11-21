"""Índice del curso: los cuatro bloques y su orden de exposición."""
import os

from diapositivas import Deck, SALIDA
from criterios_aceptacion import ACEPTA

d = Deck(ACEPTA)

d.portada("4", "Minería de datos con R e INEC",
          "Cuatro bloques · cuatro sesiones de 100 minutos",
          "ENEMDU 2025 y Estadísticas de Transporte · R 4.6")

d.mapa("EL CURSO", "El recorrido completo", [
    ("3.1", "Procedimientos básicos de minería de datos",
     "CRISP-DM y preprocesamiento. La base analítica y la bitácora de decisiones."),
    ("3.2", "Técnicas básicas de análisis multivariante",
     "Componentes principales y conglomerados. El índice de formalidad y los tres regímenes."),
    ("3.3", "Técnicas básicas de aprendizaje automático",
     "Árboles, k-vecinos, validación y métricas. La comparación de modelos."),
    ("3.4", "Técnicas básicas de análisis temporal",
     "Descomposición, suavizado, ARIMA y pronóstico. La serie de siniestros."),
], pie="Cada bloque tiene su archivo: 31, 32, 33 y 34")

d.mapa("EL CURSO", "Cómo se encadenan los productos", [
    ("3.1", "Deja la base analítica",
     "161.906 ocupados con definiciones declaradas y controles de calidad."),
    ("3.2", "Deja un eje y tres grupos",
     "Índice de formalidad provincial y tipología de mercados laborales."),
    ("3.3", "Deja la comparación de modelos",
     "Árbol, kNN y logística con AUC, F1 y matriz de confusión."),
    ("3.4", "Deja el pronóstico y su error",
     "Descomposición, ARIMA y comparación contra el ingenuo estacional."),
], pie="Ningún bloque se explica solo: cada uno consume el producto del anterior")

d.cierre("¿Empezamos?", "Bloque 1 · 3.1 Procedimientos de minería de datos")

os.makedirs(SALIDA, exist_ok=True)
ruta = os.path.join(SALIDA, "00_indice.pptx")
d.guardar(ruta)
print(ruta)
