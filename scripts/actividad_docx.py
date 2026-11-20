"""Genera el enunciado de la actividad final en Word (editable)."""
import os

from docx import Document
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls, qn
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
    p.paragraph_format.space_after = Pt(4)
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


def numerada(d, n, texto):
    p = d.add_paragraph()
    p.paragraph_format.left_indent = Cm(0.7)
    p.paragraph_format.first_line_indent = Cm(-0.7)
    p.paragraph_format.space_after = Pt(3)
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
    p.paragraph_format.space_after = Pt(2)
    r = p.add_run("\u2022  ")
    r.font.size = Pt(10.5)
    r.font.color.rgb = ROJO
    r2 = p.add_run(texto)
    r2.font.size = Pt(10.5)


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

tabla(d, ["Entrega", "Presentación", "Peso", "Modalidad"], [[
    "Domingo 29 de noviembre, 23h59",
    "Miércoles 3 de diciembre, 5 min por equipo",
    "30% de la unidad",
    "Equipos de 2 a 3 personas"]],
    [5.2, 5.6, 2.6, 3.2])

body(d, "El objetivo no es repetir la clase. Es responder una pregunta propia con el mismo "
        "método que trabajamos, y poder demostrar que el resultado se repite.")

# --- 1. repositorio ------------------------------------------
h1(d, "1. El punto de partida es el repositorio")

body(d, "La actividad vive en GitHub. Ahí están los datos, los diccionarios, la plantilla y "
        "la rúbrica, en la misma versión que se va a evaluar. Si trabajas sobre otra copia, "
        "los números pueden no coincidir y no hay forma de verificarlo.")

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

body(d, "Cómo llegar, en tres pasos:")
for i, texto in enumerate([
    "Abre el repositorio en el navegador y entra a la carpeta actividad/.",
    "Descarga el proyecto con Code → Download ZIP, o clónalo si ya usas Git: "
    "git clone https://github.com/jbarrosn/mineria-datos-inec",
    "Trabaja sobre esa copia. No necesitas instalar nada más que R y RStudio.",
], 1):
    numerada(d, i, texto)

body(d, "El repositorio no es solo el lugar donde están los archivos: es la prueba de que tu "
        "trabajo se puede repetir. Si tu script corre sobre estos datos, cualquier persona "
        "puede obtener tu cifra.", italic=True, color=GRIS)

# --- 2. datos ------------------------------------------------
h1(d, "2. Los datos")

body(d, "Un extracto de la ENEMDU anual 2025 del INEC: 161.906 personas ocupadas de 15 años "
        "y más, con 72 variables. Trae variables que no se usaron en clase —seguridad social, "
        "prestaciones, contrato, pluriempleo, RUC y contabilidad— para que el ejercicio no se "
        "resuelva copiando el script de la sesión.")

tabla(d, ["Archivo", "Qué contiene"], [
    ["datos/enemdu_actividad.csv.gz", "161.906 ocupados y 72 variables. Se lee directo con read_csv()."],
    ["datos/diccionario.csv", "Nombre y descripción de cada variable."],
    ["datos/diccionario_valores.csv", "230 códigos con su etiqueta. Sin esto no se puede recodificar."],
    ["plantilla_analisis.R", "Esqueleto del script, con los controles ya escritos."],
    ["rubrica.md", "Cómo se evalúa, con pesos y penalizaciones."],
], [6.0, 10.6])

body(d, "Los códigos vienen sin etiquetas a propósito. Recodificar es parte del ejercicio: "
        "antes de decidir qué significa un 2, hay que leerlo.")
code(d, [
    'library(readr); library(dplyr)',
    'act <- read_csv("actividad/datos/enemdu_actividad.csv.gz", show_col_types = FALSE)',
    'val <- read_csv("actividad/datos/diccionario_valores.csv", show_col_types = FALSE)',
    '',
    'val |> filter(variable == "p05a")   # ¿qué significa cada código?',
])

# --- 3. preguntas --------------------------------------------
h1(d, "3. Elige una pregunta")

body(d, "Las cuatro se responden con las variables entregadas. El equipo escoge una y la "
        "sostiene hasta el final.")

tabla(d, ["", "Pregunta", "El dato que la hace interesante", "La trampa"], [
    ["P1", "¿Quién aporta a la seguridad social y quién no?",
     "Solo el 24,8% de los ocupados aporta",
     "Usar «recibe seguro social» como predictor: es lo mismo medido dos veces"],
    ["P2", "¿Qué es un empleo protegido?",
     "Once prestaciones entre alimentación, vacaciones y décimos",
     "Sumar códigos sin separar los «no aplica»"],
    ["P3", "¿Quiénes tienen más de un trabajo?",
     "El 6,9% tiene pluriempleo",
     "Reportar exactitud: decir «nadie tiene dos trabajos» acierta el 93%"],
    ["P4", "¿Cuánto se brecha el ingreso por hora entre hombres y mujeres?",
     "El ingreso mensual mezcla sueldo y jornada",
     "Comparar sueldos sin controlar las horas trabajadas"],
], [1.0, 5.0, 5.3, 5.3])

# --- 4. entregables ------------------------------------------
h1(d, "4. Qué se entrega")

body(d, "Una carpeta con tu apellido y cuatro archivos. Comprímela en ZIP y súbela al aula "
        "virtual antes de la fecha.")
code(d, [
    "entregas/apellido/",
    "├── apellido_analisis.R      corre de cero, con semilla y sessionInfo()",
    "├── apellido_resultados.csv  la tabla que sostiene el hallazgo",
    "├── apellido_laminas.pptx    seis láminas: pregunta, datos, método,",
    "│                             resultado, límite, cierre",
    "└── apellido_resumen.md      250 palabras con una cifra propia y un límite",
])

# --- 5. reglas -----------------------------------------------
h1(d, "5. Reglas")

for i, texto in enumerate([
    "Si no está en el script, no ocurrió. Ningún número del resumen puede venir de la consola.",
    "Semilla fijada al inicio y sessionInfo() al final.",
    "Ponderar con fexp. Sin pesos se describe la muestra, no el país.",
    "Declarar las definiciones que se elijan y sostenerlas en todo el trabajo.",
    "Sin fuga de información: ningún predictor puede ser parte de la definición del desenlace.",
    "Citar la fuente: INEC, ENEMDU anual 2025.",
], 1):
    numerada(d, i, texto)

# --- 6. evaluación -------------------------------------------
h1(d, "6. Cómo se evalúa")

tabla(d, ["Criterio", "Peso", "Qué se mira"], [
    ["Reproducibilidad", "25%", "El script corre de cero y otra persona obtiene las mismas cifras"],
    ["Decisiones de datos", "20%", "Cada recodificación y cada exclusión tiene criterio y control"],
    ["Análisis", "25%", "La técnica corresponde a la pregunta, con partición honesta y métricas adecuadas"],
    ["Interpretación", "20%", "Cada cifra se traduce en una frase y en su límite"],
    ["Comunicación", "10%", "Tablas con unidades, fuente y n; una idea por lámina"],
], [4.2, 1.8, 10.6])

body(d, "La rúbrica completa, con los cuatro niveles y las penalizaciones, está en "
        "actividad/rubrica.md del repositorio.", italic=True, color=GRIS)

# --- 7. errores ----------------------------------------------
h1(d, "7. Errores que restan puntos")

for texto in [
    "Dejar que los NA avancen hasta el modelo sin decir cuántos casos se perdieron.",
    "Reportar exactitud sin sensibilidad ni AUC cuando las clases están desbalanceadas.",
    "Elegir el umbral mirando el conjunto de prueba.",
    "Presentar una tabla sin unidades ni fuente.",
    "Un resumen que describe el método y no dice qué se encontró.",
    "Fuga de información: baja el criterio de análisis aunque las métricas sean perfectas.",
]:
    vineta(d, texto)

# --- pie ------------------------------------------------------
d.add_paragraph()
p = d.add_paragraph()
p.paragraph_format.space_before = Pt(10)
r = p.add_run("Cualquier duda sobre el enunciado se resuelve antes de la entrega, no después. "
              "Si un paso no está claro, pregúntalo en clase o por el foro del aula virtual.")
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
