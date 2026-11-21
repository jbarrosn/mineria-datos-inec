"""Motor de las diapositivas del curso (16:9, sin plantilla).

Cada bloque se arma con cuatro pantallas de contenido:
  qué es  →  antes de aplicarla  →  cómo se hace  →  aplicado a la ENEMDU
más portada y cierre.
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
CREMA = RGBColor(0xF4, 0xF1, 0xEA)
ROJO = RGBColor(0xC0, 0x39, 0x2B)
GRIS = RGBColor(0x6E, 0x6A, 0x63)
BLANCO = RGBColor(0xFF, 0xFF, 0xFF)
HUESO = RGBColor(0xE7, 0xE2, 0xD8)
PANEL = RGBColor(0xEA, 0xE4, 0xD8)
GREY_HUESO = RGBColor(0x9A, 0xA8, 0xA4)

FUENTE = "Georgia"
SANS = "Segoe UI"
MONO = "Consolas"
REPO = "github.com/jbarrosn/mineria-datos-inec"


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


def texto(slide, x, y, ancho, alto, lineas, fuente=FUENTE, tam=20, color=TINTA,
          bold=False, italic=False, alineacion=PP_ALIGN.LEFT, espaciado=6,
          interlineado=1.0, ancla=MSO_ANCHOR.TOP, mayus=False, tracking=0):
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
    def __init__(self):
        self.prs = Presentation()
        self.prs.slide_width = Inches(W)
        self.prs.slide_height = Inches(H)
        self.blanco = self.prs.slide_layouts[6]

    def nueva(self, fondo):
        s = self.prs.slides.add_slide(self.blanco)
        s.background.fill.solid()
        s.background.fill.fore_color.rgb = fondo
        return s

    def _encabezado(self, s, kicker, titular, ancho=11.6, tam=30):
        texto(s, 0.75, 0.48, 9.0, 0.3, kicker, fuente=SANS, tam=9.5, color=ROJO,
              bold=True, mayus=True, tracking=1.6)
        texto(s, 0.75, 0.78, ancho, 1.15, titular, fuente=FUENTE, tam=tam,
              color=TINTA, bold=True, interlineado=0.98)

    def _pie(self, s, pie, nota_codigo=None):
        if nota_codigo:
            texto(s, 0.75, 6.42, 11.0, 0.35, nota_codigo, fuente=SANS, tam=10,
                  color=GRIS, italic=True)
        if pie:
            texto(s, 0.75, 7.02, 9.4, 0.3, pie, fuente=SANS, tam=8.5, color=GRIS,
                  italic=True)
        texto(s, 10.7, 7.02, 1.9, 0.3, REPO, fuente=SANS, tam=8, color=GRIS,
              alineacion=PP_ALIGN.RIGHT)

    # -- 1. portada --------------------------------------------
    def portada(self, numero, titulo, subtema, datos):
        s = self.nueva(TINTA)
        texto(s, 0.85, 0.85, 6.0, 0.4, "MINERÍA DE DATOS · INEC",
              fuente=SANS, tam=10, color=HUESO, mayus=True, tracking=1.6)
        texto(s, 0.8, 1.1, 4.6, 2.0, numero, fuente=FUENTE, tam=120,
              color=VERDE, bold=True, interlineado=0.85)
        texto(s, 0.85, 3.15, 6.6, 1.5, titulo, fuente=FUENTE, tam=44,
              color=BLANCO, bold=True, interlineado=0.95)
        texto(s, 0.85, 4.85, 6.4, 0.6, subtema, fuente=SANS, tam=15, color=HUESO)
        texto(s, 0.85, 5.35, 6.4, 0.9, datos, fuente=SANS, tam=12, color=GREY_HUESO)
        texto(s, 0.85, 6.75, 7.5, 0.4, REPO, fuente=SANS, tam=11,
              color=RGBColor(0x7F, 0xB2, 0xAD))
        return s

    # -- 2. qué es: definición + para qué sirve aquí -------------
    def definicion(self, kicker, titular, definicion, claves, para_que, pie=None):
        s = self.nueva(CREMA)
        self._encabezado(s, kicker, titular)

        texto(s, 0.75, 2.15, 7.1, 1.5, definicion, fuente=SANS, tam=14,
              color=TINTA, interlineado=1.25)

        y = 4.05
        for clave in claves:
            caja(s, 0.75, y + 0.08, 0.1, 0.1, relleno=ROJO)
            texto(s, 1.05, y, 6.6, 0.6, clave, fuente=SANS, tam=12,
                  color=TINTA, interlineado=1.15)
            y += 0.78

        caja(s, 8.15, 2.05, 4.45, 3.9, relleno=PANEL, radio=0.05)
        texto(s, 8.45, 2.3, 3.85, 0.3, "PARA QUÉ SIRVE AQUÍ", fuente=SANS,
              tam=9, color=VERDE, bold=True, tracking=1.4)
        texto(s, 8.45, 2.65, 3.85, 3.1, para_que, fuente=SANS, tam=11.5,
              color=TINTA, interlineado=1.22)
        self._pie(s, pie)
        return s

    # -- 3. antes de aplicarla: criterios y cuidados -------------
    def criterios(self, kicker, titular, exige, cuidado, nota=None, pie=None):
        s = self.nueva(CREMA)
        self._encabezado(s, kicker, titular)

        texto(s, 0.75, 2.05, 5.6, 0.3, "LO QUE EXIGE", fuente=SANS, tam=9,
              color=VERDE, bold=True, tracking=1.4)
        caja(s, 0.75, 2.38, 5.6, 0.03, relleno=VERDE)

        texto(s, 7.0, 2.05, 5.6, 0.3, "DÓNDE SE ROMPE", fuente=SANS, tam=9,
              color=ROJO, bold=True, tracking=1.4)
        caja(s, 7.0, 2.38, 5.6, 0.03, relleno=ROJO)

        for i, item in enumerate(exige[:4]):
            texto(s, 0.75, 2.55 + i * 0.95, 5.5, 0.85,
                  [{"runs": [(f"{i+1}.  ", {"color": VERDE, "bold": True}), (item, {})]}],
                  fuente=SANS, tam=11.5, color=TINTA, interlineado=1.15)
        for i, item in enumerate(cuidado[:4]):
            texto(s, 7.0, 2.55 + i * 0.95, 5.5, 0.85,
                  [{"runs": [(f"{i+1}.  ", {"color": ROJO, "bold": True}), (item, {})]}],
                  fuente=SANS, tam=11.5, color=TINTA, interlineado=1.15)

        if nota:
            texto(s, 0.75, 6.45, 11.2, 0.4, nota, fuente=SANS, tam=10.5,
                  color=GRIS, italic=True)
        self._pie(s, pie)
        return s

    # -- 4. cómo se hace: pasos + función ------------------------
    def pasos(self, kicker, titular, secuencia, pie=None, nota_codigo=None):
        s = self.nueva(TINTA)
        texto(s, 0.75, 0.48, 9.0, 0.3, kicker, fuente=SANS, tam=9.5, color=ROJO,
              bold=True, mayus=True, tracking=1.6)
        texto(s, 0.75, 0.78, 11.6, 1.0, titular, fuente=FUENTE, tam=30,
              color=BLANCO, bold=True, interlineado=0.98)

        y = 2.15
        for n, (paso, funcion) in enumerate(secuencia, 1):
            texto(s, 0.78, y - 0.04, 0.6, 0.5, f"{n}", fuente=FUENTE, tam=22,
                  color=VERDE, bold=True)
            texto(s, 1.45, y, 6.6, 0.7, paso, fuente=SANS, tam=12, color=HUESO,
                  interlineado=1.15)
            if funcion:
                texto(s, 8.25, y + 0.02, 4.35, 0.6,
                      [(funcion, {"fuente": MONO, "tam": 9.5})],
                      color=RGBColor(0xBF, 0xD8, 0xD4), interlineado=1.1)
            y += 0.85

        if nota_codigo:
            texto(s, 0.75, 6.42, 11.0, 0.35, nota_codigo, fuente=SANS, tam=10,
                  color=HUESO, italic=True)
        texto(s, 0.75, 7.02, 9.4, 0.3, pie or "", fuente=SANS, tam=8.5,
              color=GREY_HUESO, italic=True)
        texto(s, 10.7, 7.02, 1.9, 0.3, REPO, fuente=SANS, tam=8,
              color=GREY_HUESO, alineacion=PP_ALIGN.RIGHT)
        return s

    # -- 5. aplicado: figura + lecturas --------------------------
    def aplicacion(self, kicker, titular, imagen_nombre, ideas, pie=None):
        s = self.nueva(CREMA)
        self._encabezado(s, kicker, titular)
        ruta = os.path.join(FIG, imagen_nombre)
        with Image.open(ruta) as im:
            ar = im.width / im.height

        if ar >= 1.9:
            imagen(s, ruta, 0.75, 2.1, 11.85, 3.3)
            for i, idea in enumerate(ideas[:3]):
                x = 0.75 + i * 3.95
                caja(s, x, 5.62, 0.1, 0.1, relleno=ROJO)
                texto(s, x + 0.28, 5.55, 3.4, 0.9, idea, fuente=SANS, tam=12,
                      color=TINTA, interlineado=1.15)
        else:
            imagen(s, ruta, 0.55, 2.1, 7.25, 4.6)
            y = 2.3
            for idea in ideas[:3]:
                caja(s, 8.15, y + 0.08, 0.1, 0.1, relleno=ROJO)
                texto(s, 8.45, y, 4.15, 0.95, idea, fuente=SANS, tam=12.5,
                      color=TINTA, interlineado=1.15)
                y += 1.2
        self._pie(s, pie)
        return s

    # -- 6. cierre ----------------------------------------------
    def cierre(self, pregunta, siguiente):
        s = self.nueva(VERDE)
        texto(s, 0.85, 2.35, 8.0, 1.3, pregunta, fuente=FUENTE, tam=54,
              color=BLANCO, bold=True)
        texto(s, 0.9, 3.75, 8.0, 1.0, siguiente, fuente=SANS, tam=17, color=HUESO)
        caja(s, 0.9, 5.0, 4.4, 0.02, relleno=HUESO)
        texto(s, 0.9, 5.2, 8.0, 0.4, "Todo el material, los scripts y los datos:",
              fuente=SANS, tam=12, color=HUESO)
        texto(s, 0.9, 5.55, 8.0, 0.4, REPO, fuente=SANS, tam=14, color=BLANCO,
              bold=True)
        return s

    def guardar(self, ruta):
        self.prs.save(ruta)
