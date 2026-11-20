# Actividad final — Un hallazgo propio con la ENEMDU 2025

Después de la sesión, cada equipo entrega **un hallazgo**, no un resumen de la clase.
Elige una de las cuatro preguntas de abajo y la responde con el mismo flujo que
trabajamos: preprocesar, describir, modelar y verificar.

## Punto de partida: el repositorio

La actividad vive en **github.com/jbarrosn/mineria-datos-inec**. Ahí están los datos, los
diccionarios, la plantilla y la rúbrica, en la misma versión que se evalúa.

1. Abre el repositorio y entra a la carpeta `actividad/`.
2. Descárgalo con **Code → Download ZIP**, o clónalo:
   `git clone https://github.com/jbarrosn/mineria-datos-inec`
3. Trabaja sobre esa copia. Solo necesitas R y RStudio.

El repositorio no es solo el depósito de archivos: es la prueba de que tu trabajo se puede
repetir. Si tu script corre sobre estos datos, cualquiera obtiene tu cifra.

## Los datos

`actividad/datos/enemdu_actividad.csv.gz` — **161.906 personas ocupadas** de 15 años y
más, con **72 variables** de la ENEMDU anual 2025.

Trae variables que **no se usaron en clase**: seguridad social, prestaciones, contrato,
pluriempleo, tenencia de RUC y contabilidad del negocio.

Los códigos vienen **sin etiquetas a propósito**. Para recodificar hay que leer:

| Archivo | Qué contiene |
|---|---|
| `datos/diccionario.csv` | nombre y descripción de cada variable |
| `datos/diccionario_valores.csv` | 230 códigos con su etiqueta |

```r
library(readr); library(dplyr)

act <- read_csv("actividad/datos/enemdu_actividad.csv.gz", show_col_types = FALSE)
val <- read_csv("actividad/datos/diccionario_valores.csv", show_col_types = FALSE)

# ¿qué significa el código 2 en p05a?
val |> filter(variable == "p05a")
```

## Las cuatro preguntas

Elige **una**. Todas se responden con las variables entregadas.

### P1. ¿Quién aporta a la seguridad social y quién no?

Solo el **24,8%** de los ocupados aporta. La pregunta es quiénes son el otro 75%.

- Desenlace: `p05a` (aporta) y `p61b1` (a qué régimen).
- Técnica: clasificación con árbol y regresión logística; métricas y umbral.
- Trampa: usar `p44f` (recibe seguro social) como predictor. Es la misma cosa medida
  dos veces.

### P2. ¿Qué es un empleo protegido?

Once prestaciones en la encuesta: alimentación, vivienda, transporte, vacaciones, ropa,
seguro social, seguro médico, guardería, capacitación, décimo tercero y décimo cuarto.

- Insumo: `p44a` a `p44k`, cada una como indicador 0/1.
- Técnica: componentes principales sobre las once, y un índice 0-11.
- Trampa: sumar los códigos sin revisar cuántos son «no aplica» antes de sumar.

### P3. ¿Quiénes tienen más de un trabajo?

El **6,9%** de los ocupados tiene pluriempleo: `p50` mayor que 1, y horas repartidas
entre `p51a`, `p51b` y `p51c`.

- Desenlace: `p50 > 1`.
- Técnica: clasificación con clases desbalanceadas. **La exactitud engaña**: con 93%
  de no pluriactivos, un modelo que diga «nadie tiene dos trabajos» acierta el 93%.
- Trampa: reportar exactitud sin sensibilidad ni AUC.

### P4. ¿Cuánto se brecha el ingreso por hora entre hombres y mujeres?

Ingreso por hora = `ingrl` entre horas totales. Comparar controlando educación, rama y
jornada.

- Insumo: `ingrl`, `p51a`, `p02`, `p10a`, `rama1`.
- Técnica: descriptivo ponderado y una regresión simple con los controles disponibles.
- Trampa: comparar medianas sin controlar la jornada. Quien trabaja 20 horas gana
  menos por mes y no por eso está peor pagado.

## Qué se entrega

Una carpeta con el apellido del equipo y cuatro archivos:

| Archivo | Contenido |
|---|---|
| `apellido_analisis.R` | Corre de cero, sin objetos de la consola |
| `apellido_resultados.csv` | La tabla que sostiene el hallazgo |
| `apellido_laminas.pptx` | Seis láminas: pregunta, datos, método, resultado, límite, cierre |
| `apellido_resumen.md` | 250 palabras: qué encontró, con qué cifra y qué no puede afirmar |

## Reglas

1. **Si no está en el script, no ocurrió.** Ningún número del resumen puede venir de
   la consola.
2. **Semilla fijada** al inicio y `sessionInfo()` al final.
3. **Ponderar con `fexp`.** Sin pesos se describe la muestra, no el país.
4. **Declarar las definiciones** que se elijan, y sostenerlas en todo el trabajo.
5. **Sin fuga de información.** Ningún predictor puede ser parte de la definición del
   desenlace.
6. **Citar la fuente**: INEC, ENEMDU anual 2025.

## Fechas

- **Entrega:** domingo 29 de noviembre, 23h59, por el aula virtual.
- **Presentación:** cinco minutos por equipo en la sesión del 3 de diciembre.

## Evaluación

Cinco criterios, detallados en [`rubrica.md`](rubrica.md): reproducibilidad,
decisiones de datos, análisis, interpretación y comunicación.

## Errores que restan puntos

- Dejar `NA` avanzar hasta el modelo sin decir cuántos casos se perdieron.
- Reportar exactitud sin sensibilidad ni AUC.
- Elegir el umbral mirando el conjunto de prueba.
- Presentar una tabla sin unidades ni fuente.
- Un resumen que describe el método y no dice qué se encontró.
