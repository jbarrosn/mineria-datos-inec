# Rúbrica de la actividad final

Cinco criterios, cuatro niveles. Se entrega el primer día, no el último.

| Criterio | Peso | 4 · Logrado | 3 · En proceso | 2 · Inicial |
|---|---|---|---|---|
| **Reproducibilidad** | 25% | El script corre de cero, con semilla y `sessionInfo()`. Otra persona obtiene las mismas cifras. | Corre con un ajuste manual menor, declarado en el propio script. | Depende de objetos que quedaron en la sesión o de rutas absolutas. |
| **Decisiones de datos** | 20% | Cada recodificación y cada exclusión tiene criterio escrito y un control que la verifica. | Documenta lo principal; omite decisiones menores. | Recodifica sin justificar y sin verificar. |
| **Análisis** | 25% | La técnica corresponde a la pregunta y está bien aplicada: partición honesta, umbral en entrenamiento, métricas adecuadas al desbalance, y la variación al cambiar la semilla reportada. | Aplica bien la técnica pero con algún atajo (solo una partición, una sola métrica). | Aplica la técnica sin relación clara con la pregunta, o sin validación. |
| **Interpretación** | 20% | Cada cifra se traduce en una frase que la explica y en su límite explícito. | Interpreta bien, pero generaliza de más. | Describe la salida del software sin traducirla. |
| **Comunicación** | 10% | Tablas con unidades, fuente y n. Láminas de una idea cada una. | Correcto, con algún descuido de unidades o fuente. | Figuras sin ejes rotulados ni fuente. |

## Condiciones de aprobación

- El script **debe correr** en una máquina limpia con los paquetes declarados.
- La tabla de resultados debe traer **unidades y fuente**.
- El resumen de 250 palabras debe contener **al menos una cifra propia** y **un límite**.

## Penalizaciones

| Situación | Efecto |
|---|---|
| Fuga de información en el modelo | El criterio de análisis baja a 2, aunque las métricas sean perfectas. |
| Exactitud como única métrica en un desbalance | Análisis baja a 3. |
| Umbral elegido mirando el conjunto de prueba | Análisis baja a 2. |
| Cifras que no se pueden reproducir con el script | Reproducibilidad baja a 2. |
| Entrega tardía | −10% por día, hasta 48 horas. |

## Comentario sobre el 2

Un trabajo en nivel 2 no reprueba automáticamente. Reprueba cuando el promedio
ponderado queda por debajo de 2,5 **o** cuando hay fuga de información sin advertirla:
un modelo que aprende la respuesta no es un resultado, es un error de método.
