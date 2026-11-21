"""Criterios de aceptación por lámina.

Cada entrada responde a una pregunta: ¿qué tiene que cumplirse para
dar esta lámina por buena? Son tres comprobaciones cortas, verificables
sobre el entregable, no sobre la intención.
"""

ACEPTA = {
    # ---------------- bloque 3.1 ----------------
    "3.1 · EL BLOQUE": [
        "Al cerrar el bloque existe una base analítica guardada",
        "Cada decisión sobre el dato tiene su fila en la bitácora",
        "Sabes qué registro entra al análisis y cuál no",
    ],
    "3.1.1 · QUÉ ES": [
        "Nombra las seis fases sin leer la lámina",
        "Dice el producto que deja cada fase",
        "Ubica el preprocesamiento en la fase 3",
    ],
    "3.1.1 · LAS SEIS FASES": [
        "El proyecto declara en qué fase está hoy",
        "Cada fase tiene su producto escrito",
        "Ninguna fase se salta por prisa",
    ],
    "3.1.1 · PREPROCESAR": [
        "Las cuatro operaciones están en el script",
        "Cada una deja un stopifnot que la verifica",
        "Ninguna transformación ocurre en silencio",
    ],
    "3.1.1 · CALIDAD": [
        "Las cinco dimensiones se reportan con cifras",
        "Sabes cuántos casos se pierden y por qué",
        "El conteo se mide, no se supone",
    ],
    "3.1.1 · TRANSFORMAR": [
        "La asimetría se corrige o se justifica",
        "Ninguna categórica entra como número",
        "Los atípicos tienen una regla escrita antes",
    ],
    "3.1.1 · EL DATO": [
        "Unidad de análisis y denominador escritos",
        "fexp aplicado en todo indicador",
        "Cada exclusión tiene criterio y conteo",
    ],
    "3.1.1 · LOS CÓDIGOS": [
        "Ningún centinela sobrevive a la limpieza",
        "Cada NA se explica: estructural o no respuesta",
        "El conteo por código está en la tabla",
    ],
    "3.1.1 · EXPLORAR": [
        "La bitácora registra cada hallazgo",
        "Sabes cuántos casos quedan y por qué",
        "El exploratorio cambió al menos una decisión",
    ],
    "3.1.1 · AUDITORÍA": [
        "Cada filtro tiene su conteo y su motivo escrito",
        "El embudo nunca crece al filtrar",
        "El informe dice sobre cuántos casos habla",
    ],
    "3.1.1 · CÓMO SE HACE": [
        "El script corre de cero sin editar nada",
        "Cierra con la semilla y sessionInfo()",
        "Cada paso deja un archivo verificable",
    ],
    "3.1.1 · APLICADO A LA ENEMDU": [
        "Cada cifra de la lámina sale del script",
        "La tasa y el volumen no se confunden",
        "La figura declara fuente y n",
    ],

    # ---------------- bloque 3.2 ----------------
    "3.2 · EL BLOQUE": [
        "El bloque deja un índice y tres grupos",
        "Ambos se recalculan desde el bloque 3.1",
        "Sabes qué familia resuelve qué pregunta",
    ],
    "3.2 · QUÉ ES": [
        "Ubica PCA y clustering en su familia",
        "Dice qué pregunta responde cada una",
        "No las usa para afirmar causalidad",
    ],
    "3.2 · LAS FAMILIAS": [
        "Elige la familia por la pregunta, no al revés",
        "Declara el supuesto de la familia elegida",
        "Sabe qué técnica no aplica a este caso",
    ],
    "3.2.1 · ESCALAS": [
        "Sabes qué variable dominaría sin estandarizar",
        "El escalado se aplica antes de medir distancias",
        "La tabla muestra el rango antes y después",
    ],
    "3.2.1 · PCA": [
        "Estandariza antes de ajustar",
        "Reporta la varianza explicada por componente",
        "Lee las cargas antes de nombrar el eje",
    ],
    "3.2.1 · ANTES DE APLICARLO": [
        "Kaiser, codo y varianza coinciden",
        "Ninguna variable domina por su escala",
        "Con 24 casos se reporta como exploración",
    ],
    "3.2.1 · CÍRCULO DE CORRELACIONES": [
        "Cada flecha es una correlación, no una carga",
        "Lo que queda fuera del círculo no está representado",
        "El cuadrante se lee antes de nombrar el eje",
    ],
    "3.2.1 · APLICADO A LA ENEMDU": [
        "El eje va de formal a informal sin ambigüedad",
        "El signo de CP1 está impuesto, no supuesto",
        "Cada punto se rastrea a una provincia",
    ],
    "3.2.2 · CONGLOMERADOS": [
        "Distancia y método declarados antes de mirar",
        "El corte del dendrograma está marcado",
        "La silueta sostiene el número de grupos",
    ],
    "3.2.2 · APLICADO A LA ENEMDU": [
        "Cada grupo tiene nombre y perfil propio",
        "Ningún grupo es un artefacto de dos casos",
        "La tabla y el mapa dicen lo mismo",
    ],
    "3.2 · CÓMO SE HACE": [
        "k-medias y Ward coinciden en la asignación",
        "Cada grupo supera los dos casos",
        "El perfil se lee en unidades originales",
    ],

    # ---------------- bloque 3.3 ----------------
    "3.3 · EL BLOQUE": [
        "El bloque deja tres modelos comparables",
        "La comparación usa el mismo conjunto de prueba",
        "Sabes cuál modelo va al informe y por qué",
    ],
    "3.3 · QUÉ ES": [
        "Distingue estimar de generalizar",
        "Toda métrica que reporta es fuera de muestra",
        "Declara la incertidumbre del resultado",
    ],
    "3.3 · EL MAPA DE TÉCNICAS": [
        "Elige la familia por el tipo de respuesta",
        "Nombra una técnica que no aplicaría aquí",
        "Sabe qué exige la familia que eligió",
    ],
    "3.3 · TEORÍA": [
        "Explica sesgo y varianza con este modelo",
        "Relaciona la poda con el error esperado",
        "No usa el error de entrenamiento para decidir",
    ],
    "3.3.1 · ÁRBOLES": [
        "El árbol cabe en una lámina y se explica",
        "La poda se eligió por validación, no a ojo",
        "Se reporta lo que cuesta la explicabilidad",
    ],
    "3.3.1 · K-VECINOS": [
        "Las variables están escaladas",
        "La k se eligió por validación",
        "Se reporta la maldición de la dimensionalidad",
    ],
    "3.3 · ANTES DE APLICARLO": [
        "Ningún predictor define el desenlace",
        "La clase está balanceada o se reporta",
        "La métrica responde al costo del error",
    ],
    "3.3 · CÓMO SE HACE": [
        "La partición ocurre antes de mirar métricas",
        "La semilla se fija antes de partir",
        "El flujo corre de cero con un comando",
    ],
    "3.3.2 · VALIDACIÓN": [
        "El test se toca una sola vez",
        "El umbral se elige fuera de muestra",
        "Se reporta la variación entre pliegues",
    ],
    "3.3.2 · MÉTRICAS": [
        "La métrica elegida responde al costo",
        "Se reportan sensibilidad y especificidad",
        "No se usa la exactitud con clases desbalanceadas",
    ],
    "3.3.1 · APLICADO A LA ENEMDU": [
        "Las reglas del árbol se leen en voz alta",
        "Se declara qué variable no se usó y por qué",
        "La tasa del árbol se compara con la ponderada",
    ],
    "3.3.2 · APLICADO A LA ENEMDU": [
        "El ganador se eligió por validación cruzada",
        "El test se usó una vez, al final",
        "Se reporta el que pierde y por qué pierde",
    ],

    # ---------------- bloque 3.4 ----------------
    "3.4 · EL BLOQUE": [
        "El bloque deja una serie y un pronóstico",
        "La serie declara su frecuencia y su rango",
        "El pronóstico se compara con una línea base",
    ],
    "3.4 · QUÉ ES": [
        "Distingue tendencia, estacionalidad y ruido",
        "Sabe por qué la serie no admite partición aleatoria",
        "Declara la frecuencia antes de graficar",
    ],
    "3.4.1 · COMPONENTES": [
        "Cada componente se identifica con un método",
        "Se dice si la descomposición es aditiva o multiplicativa",
        "El residuo no se confunde con estacionalidad",
    ],
    "3.4.1 · ESTACIONARIEDAD": [
        "ADF y KPSS se leen juntos, no por separado",
        "La diferenciación aplicada está justificada",
        "La ACF se interpreta con el ciclo declarado",
    ],
    "3.4 · ANTES DE MODELAR": [
        "Hay al menos dos ciclos completos",
        "El quiebre se modela como intervención",
        "La validación es temporal, no aleatoria",
    ],
    "3.4.2 · ARIMA": [
        "Los órdenes se justifican por AIC y diagnóstico",
        "El residuo pasa el diagnóstico, o se reporta",
        "El pronóstico lleva banda de confianza",
    ],
    "3.4 · CÓMO SE HACE": [
        "El script corre de cero con un comando",
        "La serie se construye con su frecuencia",
        "El pronóstico se compara contra el ingenuo",
    ],
    "3.4.1 · APLICADO A LOS SINIESTROS": [
        "La estacionalidad se ve en el gráfico estacional",
        "El quiebre de 2020 se explica aparte",
        "La fuerza de cada componente está reportada",
    ],
    "3.4.2 · APLICADO A LOS SINIESTROS": [
        "El pronóstico se mide contra el ingenuo",
        "Se reporta qué modelo gana en cada métrica",
        "La banda y el dato observado se comparan",
    ],

    # ---------------- índice ----------------
    "EL CURSO": [
        "Sabes en qué orden se dictan los cuatro bloques",
        "Cada bloque tiene su archivo y su producto",
        "Ningún bloque se explica sin el anterior",
    ],
}
