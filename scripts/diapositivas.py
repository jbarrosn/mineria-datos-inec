"""Genera los juegos de diapositivas del curso (16:9, sin plantilla).

Diseño propio: fondo crema para contenido, tinta verde para portada y
cierre, tipografía grande y una sola idea por lámina. Cuatro láminas
por script en lugar de siete.
"""
import os

from PIL import Image, ImageFont
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.util import Emu, Inches, Pt

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

FUENTE = "Georgia"
SANS = "Segoe UI"
REPO = "github.com/jbarrosn/mineria-datos-inec"


def _f(tam):
    return ImageFont.truetype(r"C:\Windows\Fonts\georgia.ttf", int(tam * 96 / 72))


def cabe(texto, tam, ancho_in, fuente=SANS):
    """True si el texto cabe en una línea del ancho dado."""
    ruta = {"Georgia": r"C:\Windows\Fonts\georgia.ttf",
            "Segoe UI": r"C:\Windows\Fonts\segoeui.ttf",
            "Segoe UI Semibold": r"C:\Windows\Fonts\segoeuisb.ttf",
            "Consolas": r"C:\Windows\Fonts\consola.ttf"}.get(fuente)
    f = ImageFont.truetype(ruta, int(tam * 96 / 72))
    return f.getlength(texto) <= ancho_in * 96


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
          bold=False, italic=False, alineacion=PP_ALIGN.LEFT,
          espaciado=6, interlineado=1.0, ancla=MSO_ANCHOR.TOP, mayus=False,
          tracking=None):
    tb = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(ancho), Inches(alto))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = ancla
    tf.margin_left = 0
    tf.margin_right = 0
    tf.margin_top = 0
    tf.margin_bottom = 0
    if isinstance(lineas, str):
        lineas = [lineas]
    for i, item in enumerate(lineas):
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
            from pptx.oxml.ns import qn
            rPr = r._r.get_or_add_rPr()
            rPr.set("spc", str(int(tracking * 100)))
    return tb


def imagen(slide, ruta, x, y, ancho, alto, ajuste="contain"):
    with Image.open(ruta) as im:
        ar = im.width / im.height
    if ajuste == "contain":
        if ancho / alto > ar:
            h, w = alto, alto * ar
        else:
            w, h = ancho, ancho / ar
        x += (ancho - w) / 2
        y += (alto - h) / 2
    else:
        w, h = ancho, alto
    slide.shapes.add_picture(ruta, Inches(x), Inches(y), Inches(w), Inches(h))


class Deck:
    def __init__(self):
        self.prs = Presentation()
        self.prs.slide_width = Inches(W)
        self.prs.slide_height = Inches(H)
        self.blanco = self.prs.slide_layouts[6]

    def nueva(self, fondo):
        s = self.prs.slides.add_slide(self.blanco)
        fondo_shape = s.background
        fondo_shape.fill.solid()
        fondo_shape.fill.fore_color.rgb = fondo
        return s

    # -- lámina 1: portada -------------------------------------
    def portada(self, numero, titulo, subtema, datos):
        s = self.nueva(TINTA)
        texto(s, 0.85, 0.85, 1.6, 0.4, "MINERÍA DE DATOS · INEC",
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

    # -- lámina 2 y 3: figura + lectura ------------------------
    def figura(self, kicker, titular, imagen_nombre, ideas, fuente_texto=None,
               fondo=CREMA):
        s = self.nueva(fondo)
        ruta = os.path.join(FIG, imagen_nombre)
        with Image.open(ruta) as im:
            ar = im.width / im.height

        texto(s, 0.75, 0.5, 8.0, 0.3, kicker, fuente=SANS, tam=10, color=ROJO,
              bold=True, mayus=True, tracking=1.6)
        texto(s, 0.75, 0.82, 11.6, 1.2, titular, fuente=FUENTE, tam=32,
              color=TINTA, bold=True, interlineado=0.98)

        if ar >= 1.9:
            # figura apaisada: ocupa el ancho y las ideas van en fila
            imagen(s, ruta, 0.75, 2.12, 11.85, 3.3)
            for i, idea in enumerate(ideas):
                x = 0.75 + i * 3.95
                caja(s, x, 5.62, 0.1, 0.1, relleno=ROJO)
                texto(s, x + 0.28, 5.55, 3.4, 0.9, idea, fuente=SANS, tam=12.5,
                      color=TINTA, interlineado=1.15)
        else:
            imagen(s, ruta, 0.55, 2.12, 7.25, 4.7)
            y = 2.3
            for idea in ideas:
                caja(s, 8.15, y + 0.08, 0.1, 0.1, relleno=ROJO)
                texto(s, 8.45, y, 4.15, 0.95, idea, fuente=SANS, tam=13,
                      color=TINTA, interlineado=1.15)
                y += 1.18

        if fuente_texto:
            texto(s, 0.75, 7.02, 9.4, 0.3, fuente_texto, fuente=SANS, tam=9,
                  color=GRIS, italic=True)
        texto(s, 10.7, 7.02, 1.9, 0.3, REPO, fuente=SANS, tam=8.5, color=GRIS,
              alineacion=PP_ALIGN.RIGHT)
        return s
    # -- lámina 3 alternativa: código --------------------------
    def codigo(self, kicker, titular, lineas, remate):
        s = self.nueva(TINTA)
        texto(s, 0.8, 0.75, 5.0, 0.3, kicker, fuente=SANS, tam=10, color=ROJO,
              bold=True, mayus=True, tracking=1.6)
        texto(s, 0.8, 1.1, 5.2, 1.6, titular, fuente=FUENTE, tam=32,
              color=BLANCO, bold=True, interlineado=0.98)
        caja(s, 0.8, 3.05, 7.4, 3.05, relleno=RGBColor(0x0A, 0x1A, 0x18), radio=0.03)
        texto(s, 1.15, 3.35, 6.9, 2.6,
              [(ln, {"tam": 14, "fuente": "Consolas", "espaciado": 2})
               for ln in lineas], color=RGBColor(0xD8, 0xE6, 0xE3),
              interlineado=1.25)
        texto(s, 8.6, 3.05, 4.0, 2.6, remate, fuente=FUENTE, tam=20,
              color=HUESO, italic=True, interlineado=1.2)
        texto(s, 0.8, 6.85, 9.0, 0.3, REPO, fuente=SANS, tam=8.5, color=GRIS)
        return s

    # -- lámina 4: cierre --------------------------------------
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


GREY_HUESO = RGBColor(0x9A, 0xA8, 0xA4)
