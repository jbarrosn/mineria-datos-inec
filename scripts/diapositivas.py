"""Motor de las diapositivas del curso (16:9, sin plantilla).

Reglas:
  · contenido a 16 puntos o más; pies a 12 en negrita
  · toda lámina de contenido cierra con una banda de criterios de
    aceptación: qué tiene que cumplirse para darla por buena
"""
import os

from PIL import Image
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.util import Inches, Pt

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIG = os.path.join(RAIZ, "salidas", "figuras")
SALIDA = os.path.join(RAIZ, "docs", "diapositivas")

W, H = 13.333, 7.5
TINTA = RGBColor(0x12, 0x20, 0x1E)
VERDE = RGBColor(0x0E, 0x5E, 0x5A)
VERDE_CLARO = RGBColor(0x1B, 0x7A, 0x73)
CREMA = RGBColor(0xF4, 0xF1, 0xEA)
ROJO = RGBColor(0xC0, 0x39, 0x2B)
GRIS = RGBColor(0x6E, 0x6A, 0x63)
BLANCO = RGBColor(0xFF, 0xFF, 0xFF)
HUESO = RGBColor(0xE7, 0xE2, 0xD8)
PANEL = RGBColor(0xEA, 0xE4, 0xD8)
BANDA = RGBColor(0xE2, 0xEC, 0xE9)
GREY_HUESO = RGBColor(0x9A, 0xA8, 0xA4)

FUENTE = "Georgia"
SANS = "Segoe UI"
MONO = "Consolas"
REPO = "github.com/jbarrosn/mineria-datos-inec"

CUERPO = 16
PIE = 12
Y_BANDA = 5.36          # inicio de la banda de criterios
Y_FIN = 5.42            # fin del área de contenido


def caja(slide, x, y, ancho, alto, relleno=None, linea=None, radio=0):
    forma = slide.shapes.add_shape(
        MSO_SHAPE.ROUNDED_RECTANGLE if radio else MSO_SHAPE.RECTANGLE,
        Inches(x), Inches(y), Inches(ancho), Inches(alto))
    forma.shadow.inherit = False
    if relleno is None:
        forma.fill.background()
    else:
        forma.fill.solid()
        forma.fill.fore_color.rgb = relleno
    if linea is None:
        forma.line.fill.background()
    else:
        forma.line.color.rgb = linea
        forma.line.width = Pt(0.75)
    if radio:
        forma.adjustments[0] = radio
    return forma


def texto(slide, x, y, ancho, alto, lineas, fuente=FUENTE, tam=CUERPO,
          color=TINTA, bold=False, italic=False, alineacion=PP_ALIGN.LEFT,
          espaciado=6, interlineado=1.0, ancla=MSO_ANCHOR.TOP, mayus=False,
          tracking=0):
    tb = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(ancho), Inches(alto))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = ancla
    tf.margin_left = tf.margin_right = 0
    tf.margin_top = tf.margin_bottom = 0
    if isinstance(lineas, str):
        lineas = [lineas]
    for i, item in enumerate(lineas):
        if isinstance(item, dict) and "runs" in item:
            p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
            p.alignment = item.get("alineacion", alineacion)
            p.line_spacing = item.get("interlineado", interlineado)
            p.space_after = Pt(item.get("espaciado", espaciado))
            for trozo, o in item["runs"]:
                r = p.add_run()
                r.text = trozo
                f = r.font
                f.name = o.get("fuente", fuente)
                f.size = Pt(o.get("tam", tam))
                f.bold = o.get("bold", bold)
                f.italic = o.get("italic", italic)
                f.color.rgb = o.get("color", color)
            continue
        txt, opts = (item, {}) if isinstance(item, str) else item
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = opts.get("alineacion", alineacion)
        p.line_spacing = opts.get("interlineado", interlineado)
        p.space_after = Pt(opts.get("espaciado", espaciado))
        r = p.add_run()
        r.text = txt.upper() if opts.get("mayus", mayus) else txt
        f = r.font
        f.name = opts.get("fuente", fuente)
        f.size = Pt(opts.get("tam", tam))
        f.bold = opts.get("bold", bold)
        f.italic = opts.get("italic", italic)
        f.color.rgb = opts.get("color", color)
        if tracking:
            r._r.get_or_add_rPr().set("spc", str(int(tracking * 100)))
    return tb


def imagen(slide, ruta, x, y, ancho, alto):
    with Image.open(ruta) as im:
        ar = im.width / im.height
    if ancho / alto > ar:
        h, w = alto, alto * ar
    else:
        w, h = ancho, ancho / ar
    slide.shapes.add_picture(ruta, Inches(x + (ancho - w) / 2),
                             Inches(y + (alto - h) / 2), Inches(w), Inches(h))


class Deck:
    # Criterios por lámina: {kicker: [c1, c2, c3]}
    acepta = {}

    def __init__(self, acepta=None):
        self.prs = Presentation()
        self.prs.slide_width = Inches(W)
        self.prs.slide_height = Inches(H)
        self.blanco = self.prs.slide_layouts[6]
        self.acepta = acepta or {}

    def nueva(self, fondo):
        self._banda_activa = False
        s = self.prs.slides.add_slide(self.blanco)
        s.background.fill.solid()
        s.background.fill.fore_color.rgb = fondo
        return s

    # -- banda de criterios de aceptación -----------------------
    def _banda(self, s, kicker, oscuro=False):
        crit = self.acepta.get(kicker)
        if not crit:
            return
        self._banda_activa = True
        caja(s, 0, Y_BANDA, W, 1.26, relleno=RGBColor(0x0B, 0x3D, 0x3A) if oscuro else BANDA)
        texto(s, 0.7, Y_BANDA + 0.08, 5.0, 0.3, "CRITERIOS DE ACEPTACIÓN",
              fuente=SANS, tam=CUERPO, bold=True,
              color=VERDE_CLARO if not oscuro else RGBColor(0x8F, 0xC5, 0xBE),
              mayus=True, tracking=0.8)
        lineas = [{"runs": [("•  ", {"color": VERDE if not oscuro else RGBColor(0x8F, 0xC5, 0xBE),
                                      "bold": True}), (c, {})]}
                  for c in crit[:3]]
        texto(s, 0.7, Y_BANDA + 0.4, 12.0, 0.8, lineas, fuente=SANS,
              tam=CUERPO, color=TINTA if not oscuro else HUESO,
              interlineado=1.0, espaciado=1)

    def _encabezado(self, s, kicker, titular, tam=30):
        texto(s, 0.7, 0.36, 10.0, 0.35, kicker, fuente=SANS, tam=CUERPO,
              color=ROJO, bold=True, mayus=True, tracking=1.2)
        texto(s, 0.7, 0.74, 11.9, 1.0, titular, fuente=FUENTE, tam=tam,
              color=TINTA, bold=True, interlineado=0.95)

    def _pie(self, s, pie=None, nota=None):
        if nota and not getattr(self, "_banda_activa", False):
            texto(s, 0.7, 6.58, 11.6, 0.35, nota, fuente=SANS, tam=PIE,
                  color=GRIS, bold=True, italic=True)
        if pie:
            texto(s, 0.7, 7.03, 9.6, 0.3, pie, fuente=SANS, tam=PIE,
                  color=GRIS, bold=True, italic=True)
        texto(s, 9.25, 7.03, 3.4, 0.3, REPO, fuente=SANS, tam=PIE, color=GRIS,
              bold=True, alineacion=PP_ALIGN.RIGHT)

    def _footer_dark(self, s, pie=None, nota=None):
        if nota and not getattr(self, "_banda_activa", False):
            texto(s, 0.7, 6.58, 11.6, 0.35, nota, fuente=SANS, tam=PIE,
                  color=HUESO, bold=True, italic=True)
        if pie:
            texto(s, 0.7, 7.03, 9.6, 0.3, pie, fuente=SANS, tam=PIE,
                  color=GREY_HUESO, bold=True, italic=True)
        texto(s, 9.25, 7.03, 3.4, 0.3, REPO, fuente=SANS, tam=PIE,
              color=GREY_HUESO, bold=True, alineacion=PP_ALIGN.RIGHT)

    # -- 1. portada --------------------------------------------
    def portada(self, numero, titulo, subtema, datos):
        s = self.nueva(TINTA)
        texto(s, 0.8, 0.55, 6.0, 0.35, "MINERÍA DE DATOS · INEC",
              fuente=SANS, tam=CUERPO, color=HUESO, bold=True, mayus=True,
              tracking=1.2)
        texto(s, 0.75, 1.0, 5.0, 2.2, numero, fuente=FUENTE, tam=110,
              color=VERDE, bold=True, interlineado=0.85)
        texto(s, 0.8, 3.35, 7.2, 1.5, titulo, fuente=FUENTE, tam=42,
              color=BLANCO, bold=True, interlineado=0.95)
        texto(s, 0.8, 5.0, 7.4, 0.9, subtema, fuente=SANS, tam=CUERPO, color=HUESO)
        texto(s, 0.8, 5.75, 7.4, 0.6, datos, fuente=SANS, tam=CUERPO,
              color=GREY_HUESO)
        texto(s, 0.8, 6.95, 7.5, 0.3, REPO, fuente=SANS, tam=PIE,
              color=RGBColor(0x7F, 0xB2, 0xAD), bold=True)
        return s

    # -- 2. mapa del bloque -------------------------------------
    def mapa(self, kicker, titular, items, pie=None):
        s = self.nueva(TINTA)
        texto(s, 0.7, 0.36, 10.0, 0.35, kicker, fuente=SANS, tam=CUERPO,
              color=ROJO, bold=True, mayus=True, tracking=1.2)
        texto(s, 0.7, 0.74, 11.9, 0.9, titular, fuente=FUENTE, tam=30,
              color=BLANCO, bold=True, interlineado=0.95)

        n = len(items)
        paso = min(1.25, 3.3 / max(n, 1))
        y = 1.95 + max(0.0, (3.3 - n * paso) / 2)
        for codigo, titulo, pregunta in items:
            texto(s, 0.72, y, 1.5, 0.4, codigo, fuente=SANS, tam=CUERPO,
                  color=VERDE, bold=True)
            texto(s, 2.3, y - 0.03, 4.3, 0.75, titulo, fuente=SANS, tam=CUERPO,
                  color=BLANCO, bold=True, interlineado=1.05)
            texto(s, 6.75, y, 5.8, 0.75, pregunta, fuente=SANS, tam=CUERPO,
                  color=GREY_HUESO, interlineado=1.1)
            caja(s, 0.72, y + 0.6, 11.9, 0.012, relleno=RGBColor(0x2A, 0x3B, 0x38))
            y += paso

        self._banda(s, kicker, oscuro=True)
        self._footer_dark(s, pie)
        return s

    # -- 3. qué es: definición + para qué sirve aquí -------------
    def definicion(self, kicker, titular, definicion, claves, para_que, pie=None):
        s = self.nueva(CREMA)
        self._encabezado(s, kicker, titular)

        texto(s, 0.7, 1.85, 7.3, 1.5, definicion, fuente=SANS, tam=CUERPO,
              color=TINTA, interlineado=1.18)

        y = 3.35
        for clave in claves[:2]:
            caja(s, 0.7, y + 0.09, 0.11, 0.11, relleno=ROJO)
            texto(s, 1.0, y, 6.9, 0.85, clave, fuente=SANS, tam=CUERPO,
                  color=TINTA, interlineado=1.12)
            y += 0.95

        caja(s, 8.3, 1.8, 4.3, 3.4, relleno=PANEL, radio=0.05)
        texto(s, 8.55, 1.98, 3.85, 0.3, "PARA QUÉ SIRVE AQUÍ", fuente=SANS,
              tam=CUERPO, color=VERDE, bold=True, tracking=0.6)
        texto(s, 8.55, 2.32, 3.85, 2.9, para_que, fuente=SANS, tam=CUERPO,
              color=TINTA, interlineado=1.16)

        self._banda(s, kicker)
        self._pie(s, pie)
        return s

    # -- 4. criterios: exige y dónde se rompe --------------------
    def criterios(self, kicker, titular, exige, cuidado, nota=None, pie=None):
        s = self.nueva(CREMA)
        self._encabezado(s, kicker, titular)

        texto(s, 0.7, 1.85, 5.7, 0.3, "LO QUE EXIGE", fuente=SANS, tam=CUERPO,
              color=VERDE, bold=True, tracking=0.6)
        caja(s, 0.7, 2.2, 5.75, 0.03, relleno=VERDE)

        texto(s, 7.1, 1.85, 5.7, 0.3, "DÓNDE SE ROMPE", fuente=SANS, tam=CUERPO,
              color=ROJO, bold=True, tracking=0.6)
        caja(s, 7.1, 2.2, 5.75, 0.03, relleno=ROJO)

        paso = 0.7 if max(len(exige), len(cuidado)) > 3 else 0.92
        for i, item in enumerate(exige[:4]):
            texto(s, 0.7, 2.35 + i * paso, 5.85, 0.8,
                  [{"runs": [(f"{i+1}.  ", {"color": VERDE, "bold": True}),
                             (item, {})]}],
                  fuente=SANS, tam=CUERPO, color=TINTA, interlineado=1.08)
        for i, item in enumerate(cuidado[:4]):
            texto(s, 7.1, 2.35 + i * paso, 5.85, 0.8,
                  [{"runs": [(f"{i+1}.  ", {"color": ROJO, "bold": True}),
                             (item, {})]}],
                  fuente=SANS, tam=CUERPO, color=TINTA, interlineado=1.08)

        self._banda(s, kicker)
        self._pie(s, pie, nota)
        return s

    # -- 5. teoría: ideas y notación ----------------------------
    def teoria(self, kicker, titular, ideas, lineas, nota=None, pie=None):
        s = self.nueva(CREMA)
        self._encabezado(s, kicker, titular)

        ideas = ideas[:3]
        paso = 1.05 if len(ideas) <= 3 else 0.9
        y = 1.95
        for idea in ideas:
            caja(s, 0.7, y + 0.09, 0.11, 0.11, relleno=ROJO)
            texto(s, 1.0, y, 6.2, 0.9, idea, fuente=SANS, tam=CUERPO,
                  color=TINTA, interlineado=1.12)
            y += paso

        caja(s, 7.55, 1.85, 5.05, 3.3, relleno=PANEL, radio=0.05)
        texto(s, 7.8, 2.1, 4.55, 2.95,
              [(ln, {"tam": CUERPO, "fuente": MONO, "espaciado": 8})
               for ln in lineas], color=TINTA, interlineado=1.1)

        self._banda(s, kicker)
        self._pie(s, pie, nota)
        return s

    # -- 6. tabla -----------------------------------------------
    def tabla(self, kicker, titular, encabezados, filas, anchos, pie=None):
        s = self.nueva(CREMA)
        self._encabezado(s, kicker, titular)

        alto = 0.55 * (len(filas) + 1)
        forma = s.shapes.add_table(len(filas) + 1, len(encabezados),
                                   Inches(0.7), Inches(1.72), Inches(sum(anchos)),
                                   Inches(alto))
        t = forma.table
        for i, w in enumerate(anchos):
            t.columns[i].width = Inches(w)
        t.rows[0].height = Inches(0.4)

        for j, h in enumerate(encabezados):
            c = t.cell(0, j)
            c.text = ""
            r = c.text_frame.paragraphs[0].add_run()
            r.text = h
            r.font.size = Pt(CUERPO)
            r.font.bold = True
            r.font.name = SANS
            r.font.color.rgb = BLANCO
            c.fill.solid()
            c.fill.fore_color.rgb = VERDE
            c.vertical_anchor = MSO_ANCHOR.MIDDLE

        for i, fila in enumerate(filas, 1):
            for j, v in enumerate(fila):
                c = t.cell(i, j)
                c.text = ""
                r = c.text_frame.paragraphs[0].add_run()
                r.text = v
                r.font.size = Pt(CUERPO)
                r.font.name = SANS
                r.font.color.rgb = TINTA
                r.font.bold = (j == 0)
                c.fill.solid()
                c.fill.fore_color.rgb = BLANCO if i % 2 else RGBColor(0xF7, 0xF5, 0xEF)
                c.vertical_anchor = MSO_ANCHOR.MIDDLE
                c.margin_left = Inches(0.07)
                c.margin_right = Inches(0.05)

        self._banda(s, kicker)
        self._pie(s, pie)
        return s

    # -- 7. pasos en R ------------------------------------------
    def pasos(self, kicker, titular, secuencia, pie=None, nota_codigo=None):
        s = self.nueva(TINTA)
        texto(s, 0.7, 0.36, 10.0, 0.35, kicker, fuente=SANS, tam=CUERPO,
              color=ROJO, bold=True, mayus=True, tracking=1.2)
        texto(s, 0.7, 0.72, 11.9, 0.85, titular, fuente=FUENTE, tam=30,
              color=BLANCO, bold=True, interlineado=0.95)

        paso = 0.68 if len(secuencia) > 4 else 0.8
        y = 1.8
        for n, (texto_paso, funcion) in enumerate(secuencia, 1):
            texto(s, 0.72, y - 0.04, 0.6, 0.4, f"{n}", fuente=FUENTE, tam=18,
                  color=VERDE, bold=True)
            texto(s, 1.3, y, 6.1, 0.6, texto_paso, fuente=SANS, tam=CUERPO,
                  color=HUESO, interlineado=1.05)
            if funcion:
                texto(s, 7.55, y + 0.02, 5.1, 0.55,
                      [(funcion, {"fuente": MONO, "tam": CUERPO})],
                      color=RGBColor(0xBF, 0xD8, 0xD4), interlineado=1.0)
            y += paso

        self._banda(s, kicker, oscuro=True)
        self._footer_dark(s, pie, nota_codigo)
        return s

    # -- 8. aplicado: figura + lecturas -------------------------
    def aplicacion(self, kicker, titular, imagen_nombre, ideas, pie=None):
        s = self.nueva(CREMA)
        self._encabezado(s, kicker, titular)
        ruta = os.path.join(FIG, "_slide", imagen_nombre)
        if not os.path.exists(ruta):
            ruta = os.path.join(FIG, imagen_nombre)
        with Image.open(ruta) as im:
            ar = im.width / im.height

        if ar >= 1.9:
            imagen(s, ruta, 0.7, 1.75, 11.9, 2.55)
            for i, idea in enumerate(ideas[:3]):
                x = 0.7 + i * 4.0
                caja(s, x, 4.55, 0.11, 0.11, relleno=ROJO)
                texto(s, x + 0.3, 4.45, 3.55, 0.9, idea, fuente=SANS,
                      tam=CUERPO, color=TINTA, interlineado=1.1)
        else:
            imagen(s, ruta, 0.45, 1.75, 7.2, 3.4)
            y = 1.85
            for idea in ideas[:3]:
                caja(s, 7.95, y + 0.09, 0.11, 0.11, relleno=ROJO)
                texto(s, 8.25, y, 4.4, 0.95, idea, fuente=SANS, tam=CUERPO,
                      color=TINTA, interlineado=1.1)
                y += 1.15
        self._banda(s, kicker)
        self._pie(s, pie)
        return s

    # -- 9. cierre ----------------------------------------------
    def cierre(self, pregunta, siguiente):
        s = self.nueva(VERDE)
        texto(s, 0.8, 2.3, 8.5, 1.3, pregunta, fuente=FUENTE, tam=54,
              color=BLANCO, bold=True)
        texto(s, 0.85, 3.8, 8.5, 1.0, siguiente, fuente=SANS, tam=20, color=HUESO)
        caja(s, 0.85, 5.05, 4.4, 0.02, relleno=HUESO)
        texto(s, 0.85, 5.25, 8.0, 0.4, "Todo el material, los scripts y los datos:",
              fuente=SANS, tam=CUERPO, color=HUESO)
        texto(s, 0.85, 5.65, 8.5, 0.4, REPO, fuente=SANS, tam=CUERPO,
              color=BLANCO, bold=True)
        return s

    def guardar(self, ruta):
        self.prs.save(ruta)
