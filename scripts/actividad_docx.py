"""Genera el enunciado de la actividad final en Word (editable)."""
import os

from docx import Document
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls
from docx.shared import Cm, Pt, RGBColor

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SALIDA = os.path.join(RAIZ, "actividad", "Actividad_final_ENEMDU_2025.docx")

VERDE = RGBColor(0x0E, 0x5E, 0x5A)
TINTA = RGBColor(0x1A, 0x1A, 0x1A)
GRIS = RGBColor(0x5A, 0x5A, 0x5A)
ROJO = RGBColor(0xC0, 0x39, 0x2B)
REPO = "github.com/jbarrosn/mineria-datos-inec"


def doc_base():
    d = Document()
    sec = d.sections[0]
    sec.page_width, sec.page_height = Cm(21), Cm(29.7)
    sec.left_margin = sec.right_margin = Cm(2.2)
    sec.top_margin = Cm(2.0)
    sec.bottom_margin = Cm(1.8)
    estilo = d.styles["Normal"]
    estilo.font.name = "Calibri"
    estilo.font.size = Pt(10.5)
    estilo.font.color.rgb = TINTA
    estilo.paragraph_format.space_after = Pt(6)
    estilo.paragraph_format.line_spacing = 1.12
    return d


def h1(d, texto):
    p = d.add_paragraph()
    p.paragraph_format.space_before = Pt(16)
    p.paragraph_format.space_after = Pt(5)
    r = p.add_run(texto)
    r.font.name = "Georgia"
    r.font.size = Pt(14)
    r.font.bold = True
    r.font.color.rgb = VERDE
    borde = parse_xml(
        r'<w:pBdr %s><w:bottom w:val="single" w:sz="6" w:space="3" '
        r'w:color="0E5E5A"/></w:pBdr>' % nsdecls("w"))
    p._p.get_or_add_pPr().append(borde)
    return p


def body(d, texto, **kw):
    p = d.add_paragraph()
    r = p.add_run(texto)
    r.font.size = Pt(kw.get("tam", 10.5))
    if kw.get("italic"):
        r.font.italic = True
    if kw.get("color"):
        r.font.color.rgb = kw["color"]
    if kw.get("bold"):
        r.font.bold = True
    return p


def code(d, lineas):
    p = d.add_paragraph()
    p.paragraph_format.left_indent = Cm(0.4)
    p.paragraph_format.space_before = Pt(4)
    p.paragraph_format.space_after = Pt(8)
    sombra = parse_xml(
        r'<w:shd %s w:val="clear" w:fill="F1EFE8"/>' % nsdecls("w"))
    p._p.get_or_add_pPr().append(sombra)
    for i, ln in enumerate(lineas):
        r = p.add_run(ln + ("\n" if i < len(lineas) - 1 else ""))
        r.font.name = "Consolas"
        r.font.size = Pt(9)
        r.font.color.rgb = TINTA
    return p


def numerada(d, n, texto):
    p = d.add_paragraph()
    p.paragraph_format.left_indent = Cm(0.7)
    p.paragraph_format.first_line_indent = Cm(-0.7)
    p.paragraph_format.space_after = Pt(4)
    r = p.add_run(f"{n}.  ")
    r.font.size = Pt(10.5)
    r.font.bold = True
    r.font.color.rgb = VERDE
    r2 = p.add_run(texto)
    r2.font.size = Pt(10.5)


def vineta(d, texto):
    p = d.add_paragraph()
    p.paragraph_format.left_indent = Cm(0.7)
    p.paragraph_format.first_line_indent = Cm(-0.7)
    p.paragraph_format.space_after = Pt(3)
    r = p.add_run("\u2022  ")
    r.font.size = Pt(10.5)
    r.font.color.rgb = ROJO
    r2 = p.add_run(texto)
    r2.font.size = Pt(10.5)


def celda(cell, texto, bold=False, blanco=False, tam=9.5, centro=False):
    cell.text = ""
    p = cell.paragraphs[0]
    p.paragraph_format.space_after = Pt(2)
    p.paragraph_format.space_before = Pt(2)
    if centro:
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run(texto)
    r.font.size = Pt(tam)
    r.font.bold = bold
    r.font.name = "Calibri"
    if blanco:
        r.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)


def tabla(d, encabezados, filas, anchos):
    t = d.add_table(rows=1, cols=len(encabezados))
    t.style = "Table Grid"
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    t.autofit = False
    for i, h in enumerate(encabezados):
        c = t.rows[0].cells[i]
        c.width = Cm(anchos[i])
        celda(c, h, bold=True, blanco=True, tam=9.5)
        c._tc.get_or_add_tcPr().append(
            parse_xml(r'<w:shd %s w:val="clear" w:fill="0E5E5A"/>' % nsdecls("w")))
    for fila in filas:
        cells = t.add_row().cells
        for i, v in enumerate(fila):
            cells[i].width = Cm(anchos[i])
            celda(cells[i], v, tam=9.5)
    d.add_paragraph().paragraph_format.space_after = Pt(2)
    return t


# ============================================================
d = doc_base()

# --- cabecera -------------------------------------------------
p = d.add_paragraph()
p.paragraph_format.space_after = Pt(0)
r = p.add_run("MINERÍA DE DATOS CON R · UNIDAD 3")
r.font.name = "Segoe UI"
r.font.size = Pt(9)
r.font.bold = True
r.font.color.rgb = ROJO

p = d.add_paragraph()
p.paragraph_format.space_after = Pt(0)
r = p.add_run("Actividad final")
r.font.name = "Georgia"
r.font.size = Pt(26)
r.font.bold = True
r.font.color.rgb = VERDE

p = d.add_paragraph()
p.paragraph_format.space_after = Pt(10)
r = p.add_run("Un hallazgo propio con la ENEMDU 2025")
r.font.name = "Georgia"
r.font.size = Pt(14)
r.font.italic = True
r.font.color.rgb = TINTA

tabla(d, ["Entrega", "Presentación", "Peso", "Equipos"], [[
    "Domingo 29 de noviembre, 23h59",
    "Miércoles 3 de diciembre, 5 minutos por equipo",
    "30% de la unidad",
    "De 2 a 3 personas"]],
    [5.2, 5.6, 2.6, 3.2])

body(d, "Durante la clase vimos cómo se trabaja un proyecto completo, de los datos crudos "
        "al informe. Ahora les toca a ustedes hacer uno más pequeño: elegir una pregunta, "
        "responderla con los mismos datos y mostrar el resultado. La pregunta y las "
        "variables son distintas de las que trabajamos, así que no sirve copiar el script "
        "de la sesión.")

# --- 1. repositorio ------------------------------------------
h1(d, "1. Empiecen por el repositorio")

body(d, "Todo el material está en GitHub: los datos, los diccionarios, la plantilla del "
        "script y la rúbrica. Es la misma versión que voy a revisar cuando califique, así "
        "que conviene trabajar sobre esa copia. Si los datos cambian, sus cifras dejan de "
        "coincidir con las mías y no hay manera de verificarlas.")

p = d.add_paragraph()
p.paragraph_format.space_before = Pt(4)
p.paragraph_format.space_after = Pt(10)
p.paragraph_format.left_indent = Cm(0.4)
sombra = parse_xml(r'<w:shd %s w:val="clear" w:fill="E8F1EF"/>' % nsdecls("w"))
p._p.get_or_add_pPr().append(sombra)
r = p.add_run("  " + REPO + "  ")
r.font.name = "Consolas"
r.font.size = Pt(12)
r.font.bold = True
r.font.color.rgb = VERDE

body(d, "Para empezar:")
for i, texto in enumerate([
    "Entren al repositorio y abran la carpeta actividad/.",
    "Descarguen el proyecto con Code → Download ZIP, o clónenlo si ya usan Git: "
    "git clone https://github.com/jbarrosn/mineria-datos-inec",
    "Trabajen sobre esa copia. Solo necesitan R y RStudio.",
], 1):
    numerada(d, i, texto)

body(d, "Al final van a entregar el script que produce sus cifras. Si ese script corre "
        "sobre los datos del repositorio, cualquiera puede obtener el mismo resultado, y eso "
        "es lo que se evalúa.", italic=True, color=GRIS)

# --- 2. datos ------------------------------------------------
h1(d, "2. Los datos")

body(d, "Van a trabajar con un extracto de la ENEMDU anual 2025: 161.906 personas ocupadas "
        "de 15 años y más, y 72 variables. Incluye cosas que no vimos en clase, como "
        "seguridad social, prestaciones, tipo de contrato, pluriempleo, RUC y contabilidad "
        "del negocio.")

tabla(d, ["Archivo", "Qué contiene"], [
    ["datos/enemdu_actividad.csv.gz", "161.906 ocupados y 72 variables. Se lee directo con read_csv()."],
    ["datos/diccionario.csv", "Nombre y descripción de cada variable."],
    ["datos/diccionario_valores.csv", "230 códigos con su etiqueta. Sin esto no se puede recodificar."],
    ["plantilla_analisis.R", "El esqueleto del script, con los controles ya escritos."],
    ["rubrica.md", "Cómo se evalúa, con pesos y penalizaciones."],
], [6.0, 10.6])

body(d, "Los códigos vienen sin etiquetas. Es a propósito: antes de usar una variable tienen "
        "que revisar qué significa cada valor en el diccionario.")
code(d, [
    'library(readr); library(dplyr)',
    'act <- read_csv("actividad/datos/enemdu_actividad.csv.gz", show_col_types = FALSE)',
    'val <- read_csv("actividad/datos/diccionario_valores.csv", show_col_types = FALSE)',
    '',
    'val |> filter(variable == "p05a")   # ¿qué significa cada código?',
])

# --- 3. preguntas --------------------------------------------
h1(d, "3. Elijan una pregunta")

body(d, "Cada equipo escoge una de estas cuatro. Todas se responden con las variables que "
        "están en la carpeta, sin buscar datos por fuera.")

tabla(d, ["", "Pregunta", "Por qué vale la pena", "Dónde se suele fallar"], [
    ["P1", "¿Quién aporta a la seguridad social y quién no?",
     "Solo el 24,8% de los ocupados aporta",
     "Usar «recibe seguro social» como predictor: es la misma cosa medida dos veces"],
    ["P2", "¿Qué es un empleo protegido?",
     "Hay once prestaciones en la encuesta: alimentación, vacaciones, décimos…",
     "Sumar los códigos sin separar antes los «no aplica»"],
    ["P3", "¿Quiénes tienen más de un trabajo?",
     "El 6,9% tiene pluriempleo",
     "Reportar exactitud: un modelo que diga «nadie tiene dos trabajos» acierta el 93%"],
    ["P4", "¿Cuánto se brecha el ingreso por hora entre hombres y mujeres?",
     "El ingreso mensual mezcla sueldo y jornada",
     "Comparar sueldos sin controlar las horas trabajadas"],
], [1.0, 5.0, 5.3, 5.3])

# --- 4. entregables ------------------------------------------
h1(d, "4. Qué tienen que entregar")

body(d, "Armen una carpeta con el apellido del equipo y guarden estos cuatro archivos. Al "
        "final la comprimen en ZIP y la suben al aula virtual.")
code(d, [
    "entregas/apellido/",
    "├── apellido_analisis.R      corre de cero, con semilla y sessionInfo()",
    "├── apellido_resultados.csv  la tabla que sostiene el hallazgo",
    "├── apellido_laminas.pptx    seis láminas: pregunta, datos, método,",
    "│                             resultado, límite, cierre",
    "└── apellido_resumen.md      250 palabras con una cifra propia y un límite",
])

# --- 5. reglas -----------------------------------------------
h1(d, "5. Reglas del trabajo")

for i, texto in enumerate([
    "Todo número que aparezca en el resumen tiene que salir del script. Si lo calcularon "
    "en la consola y no quedó escrito, no cuenta.",
    "Fijen la semilla al inicio del script y dejen sessionInfo() al final.",
    "Ponderen con fexp. Si no lo hacen, están describiendo a las personas encuestadas y "
    "no al país.",
    "Escriban qué definición usaron y manténganla en todo el trabajo.",
    "Revisen que ninguna variable predictora forme parte de la definición de lo que quieren "
    "predecir.",
    "Citen la fuente de los datos: INEC, ENEMDU anual 2025.",
], 1):
    numerada(d, i, texto)

# --- 6. evaluación -------------------------------------------
h1(d, "6. Cómo se evalúa")

tabla(d, ["Criterio", "Peso", "Qué se mira"], [
    ["Reproducibilidad", "25%", "Que el script corra de cero y otra persona obtenga las mismas cifras"],
    ["Decisiones de datos", "20%", "Que cada recodificación y cada exclusión tengan criterio y control"],
    ["Análisis", "25%", "Que la técnica corresponda a la pregunta, con partición honesta y métricas adecuadas"],
    ["Interpretación", "20%", "Que cada cifra venga acompañada de una frase y de su límite"],
    ["Comunicación", "10%", "Tablas con unidades, fuente y n; una idea por lámina"],
], [4.2, 1.8, 10.6])

body(d, "En actividad/rubrica.md están los cuatro niveles de cada criterio y las "
        "penalizaciones.", italic=True, color=GRIS)

# --- 7. errores ----------------------------------------------
h1(d, "7. Dónde se pierden puntos")

for texto in [
    "Dejar que los NA lleguen al modelo sin decir cuántos casos se perdieron.",
    "Reportar solo la exactitud cuando las clases están desbalanceadas.",
    "Elegir el umbral mirando el conjunto de prueba.",
    "Presentar una tabla sin unidades ni fuente.",
    "Escribir un resumen que explica el método pero no dice qué encontraron.",
    "Incluir en el modelo una variable que forma parte de la definición del desenlace.",
]:
    vineta(d, texto)

# --- pie ------------------------------------------------------
d.add_paragraph()
p = d.add_paragraph()
p.paragraph_format.space_before = Pt(10)
r = p.add_run("Si algo de esto no queda claro, pregunten antes de la entrega. Es más fácil "
              "aclararlo ahora que corregirlo después, y para eso están las clases.")
r.font.size = Pt(9.5)
r.font.italic = True
r.font.color.rgb = GRIS

pie = d.sections[0].footer.paragraphs[0]
pie.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = pie.add_run("Minería de datos con R · INEC 2025 · " + REPO)
r.font.size = Pt(8)
r.font.color.rgb = GRIS

os.makedirs(os.path.dirname(SALIDA), exist_ok=True)
d.save(SALIDA)
print(SALIDA)
