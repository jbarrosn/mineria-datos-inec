"""Bloque 3.3 completo: técnicas básicas de aprendizaje automático."""
import os

from diapositivas import Deck, SALIDA
from criterios_aceptacion import ACEPTA

d = Deck(ACEPTA)

d.portada("3.3", "Aprendizaje automático",
          "3.3 · 3.3.1 Árboles y k-vecinos · 3.3.2 Validación y métricas",
          "ENEMDU 2025 · 30.000 ocupados · 9 predictores")

d.mapa("3.3 · EL BLOQUE", "Lo que se ve en esta sesión", [
    ("3.3", "Técnicas básicas de aprendizaje automático",
     "Qué familias existen y cuál se usa para qué problema."),
    ("3.3.1", "Árboles de decisión y k-vecinos más cercanos",
     "Dos formas opuestas de aprender: partir el espacio o medir distancias."),
    ("3.3.2", "Validación cruzada y métricas de desempeño",
     "Cómo se estima el error fuera de muestra y qué métrica responde a cada costo."),
], pie="Bloque 3 de 4 · 100 minutos · la práctica se hace sobre la ENEMDU 2025")

d.definicion("3.3 · QUÉ ES", "Un modelo es una función estimada",
             "El aprendizaje supervisado busca una función f: X → Y a partir de n pares "
             "(xi, yi). No se busca la f verdadera, que no se conoce, sino una f̂ que "
             "minimice el error sobre casos nuevos. El error en la muestra es solo su "
             "estimación.",
             ["Aprender es estimar; el objetivo es generalizar, no memorizar.",
              "La muestra de entrenamiento es una realización: otra muestra daría otro f̂.",
              "Todo lo que se afirma del desempeño es una estimación con incertidumbre."],
             ["Aquí f̂ predice si una persona ocupada es informal, usando solo "
              "características observables antes del desenlace.",
              "El interés no está en acertar sobre las 21.001 personas de entrenamiento, "
              "sino sobre quienes no están en la base.",
              "Por eso se separa una prueba que el modelo nunca ve."],
             pie="Fuente: Vapnik (1998); Hastie, Tibshirani & Friedman (2009).")

d.tabla("3.3 · EL MAPA DE TÉCNICAS", "Cinco familias, cinco problemas distintos",
        ["Familia", "Ejemplos", "Cuándo se usa", "Lo que exige"],
        [["Supervisado · clasificación", "Árbol, kNN, logística, SVM",
          "Hay etiqueta y es categórica", "Clase definida y etiqueta confiable"],
         ["Supervisado · regresión", "Lineal, regularizada, árbol de regresión",
          "La respuesta es numérica", "Supuestos sobre el error"],
         ["No supervisado · agrupamiento", "k-medias, jerárquico, DBSCAN",
          "No hay etiqueta; se buscan grupos", "Distancia y escala definidas"],
         ["No supervisado · reducción", "PCA, factorial, t-SNE",
          "Muchas variables correlacionadas", "Estandarización previa"],
         ["Ensamble", "Random forest, boosting",
          "Se prioriza precisión sobre interpretabilidad", "Más datos y cómputo"]],
        [2.9, 3.3, 3.3, 2.5],
        pie="Esta sesión se queda en la primera fila: árbol y kNN como casos base.")

d.teoria("3.3 · TEORÍA", "El error tiene tres partes",
         ["El error de un modelo se descompone en sesgo, varianza y ruido irreducible.",
          "Un árbol profundo tiene poco sesgo y mucha varianza: cambia con cada muestra.",
          "Podar sube el sesgo y baja la varianza; el óptimo está en el punto medio."],
         ["E[(y − f̂)²] = Sesgo² + Var + σ²",
          "",
          "Sesgo = E[f̂] − f",
          "Var   = E[(f̂ − E[f̂])²]"],
         nota="La validación cruzada estima ese error fuera de muestra; el error de "
              "entrenamiento no sirve para decidirlo.",
         pie="Fuente: Geman, Bienenstock & Doursat (1992).")

d.teoria("3.3.1 · ÁRBOLES", "Partir el espacio en regiones",
         ["Un árbol divide el espacio de predictores en rectángulos y predice la clase "
          "mayoritaria de cada uno.",
          "Cada corte se elige para maximizar la reducción de impureza, no para acertar "
          "el caso siguiente.",
          "El tamaño se controla con el criterio de parada y con la poda por cp."],
         ["Gini(t) = 1 − Σk p(k|t)²",
          "",
          "H(t) = − Σk p(k|t) log2 p(k|t)",
          "",
          "Δi = i(t) − (ni/n) i(ti) − (nd/n) i(td)"],
         nota="CART es voraz: elige el mejor corte ahora, no la mejor combinación de cortes.",
         pie="Fuente: Breiman, Friedman, Olshen & Stone (1984).")

d.criterios("3.3.1 · ÁRBOLES", "Qué gana y qué pierde un árbol",
           ["Reglas legibles: cada rama se puede explicar en voz alta.",
            "No exige escala ni transformación de las variables.",
            "Captura interacciones sin declararlas.",
            "Sirve de base para ensambles."],
           ["Inestable: cambia la muestra y cambia el árbol.",
            "Sesgado hacia variables con muchos niveles.",
            "Sin poda, memoriza el ruido.",
            "No extrapola fuera del rango observado."],
           nota="Un árbol de cinco hojas se explica en una diapositiva; uno de cincuenta, no.",
           pie="")

d.teoria("3.3.1 · K-VECINOS", "Decidir mirando al vecino",
         ["kNN no estima parámetros: guarda los datos y decide en el momento de consultar.",
          "Con k pequeño la frontera es nerviosa; con k grande se suaviza y sesga.",
          "En dimensión alta las distancias se igualan: la maldición de la dimensionalidad."],
         ["ŷ(x) = moda{ yi : i ∈ Nk(x) }",
          "",
          "d(x, x') = sqrt(Σj (xj − x'j)²)",
          "",
          "|Nk(x)| = k, impar si hay dos clases"],
         nota="Sin estandarizar, la variable con mayor rango domina la distancia.",
         pie="Fuente: Cover & Hart (1967).")

d.criterios("3.3 · ANTES DE APLICARLO", "Qué exige y dónde se rompe",
           ["Una etiqueta definida con un protocolo único y documentado.",
            "La prueba separada antes de tocar el modelo.",
            "Predictores conocidos antes del desenlace.",
            "La métrica elegida según el costo del error."],
           ["Fuga de información: el predictor define lo que se predice.",
            "Desbalance: exactitud alta con sensibilidad nula.",
            "kNN sin escalar: las horas aplastan a la edad.",
            "Un solo corte presentado como resultado."],
           nota="La prueba de fuego de un modelo es un caso que no estaba en la base.",
           pie="")

d.pasos("3.3 · CÓMO SE HACE", "El flujo completo en R",
        [("Descartar predictores que definen el desenlace",
          "select(-p47a, -p49, -p48)"),
         ("Partir antes de modelar, estratificando",
          "createDataPartition(p = 0.7)"),
         ("Ajustar el árbol y elegir la poda",
          "rpart(control = rpart.control(cp))"),
         ("Ajustar kNN con variables escaladas",
          "caret(method = 'knn', preProcess = ...)"),
         ("Comparar con la línea base y medir",
          "glm(family = binomial) · roc()")],
        pie="Scripts 04_arboles_knn.R y 05_validacion.R")

d.teoria("3.3.2 · VALIDACIÓN", "Estimar el error fuera de muestra",
         ["Validar es medir con datos que no participaron del ajuste.",
          "k-fold usa cada caso como prueba una vez; repetir mide la variabilidad.",
          "En series, la validación no es aleatoria: el futuro se predice con el pasado."],
         ["CV = (1/K) Σk error(f̂(−k), Dk)",
          "",
          "Var(CV) ≈ desviación entre pliegues",
          "",
          "K = 5 o 10 · repetir 3 veces"],
         nota="Elegir el umbral o el modelo mirando el test convierte la estimación en una "
              "ilusión.",
         pie="Fuente: Kohavi (1995).")

d.tabla("3.3.2 · MÉTRICAS", "Cada métrica responde a un costo distinto",
        ["Métrica", "Fórmula", "Cuándo usarla"],
        [["Exactitud", "(VP + VN) / N", "Clases balanceadas y errores simétricos"],
         ["Sensibilidad", "VP / (VP + FN)", "Perder un positivo es caro"],
         ["Especificidad", "VN / (VN + FP)", "Un falso positivo es caro"],
         ["Precisión", "VP / (VP + FP)", "Se necesita confiar en la alerta"],
         ["F1", "2PR / (P + R)", "Compromiso entre precisión y sensibilidad"],
         ["AUC-ROC", "P(s⁺ > s⁻)", "Comparar modelos sin fijar umbral"]],
        [2.3, 3.5, 6.2],
        pie="Con 45% de informales la exactitud funciona; con 7% sería una trampa.")

d.aplicacion("3.3.1 · APLICADO A LA ENEMDU", "Cinco hojas que se explican solas",
             "04_arbol.png",
             ["Primera pregunta: categoría ocupacional",
              "Segunda: rama de actividad",
              "Ni la edad ni el sexo aparecen"],
             pie="Árbol podado a cp = 0,01 sobre 21.001 casos de entrenamiento.")

d.aplicacion("3.3.2 · APLICADO A LA ENEMDU", "El modelo más simple gana",
             "05_roc.png",
             ["Logística 0,933", "kNN 0,931", "Árbol 0,884"],
             pie="Curvas ROC sobre el 30% de prueba, 8.999 casos.")

d.cierre("¿Preguntas?", "Siguiente: 3.4 · Análisis temporal")

ruta = os.path.join(SALIDA, "03_aprendizaje_automatico.pptx")
os.makedirs(SALIDA, exist_ok=True)
d.guardar(ruta)
print(ruta)
