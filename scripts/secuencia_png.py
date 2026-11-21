"""Letrero de la secuencia de la actividad final (A2 vertical, 150 ppp)."""
import os

from PIL import Image, ImageDraw, ImageFont

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SALIDA = os.path.join(RAIZ, "docs", "Secuencia_actividad_final.png")

W, H = 2480, 3508          # A2 a 150 ppp
M = 150

TINTA = (0x12, 0x20, 0x1E)
VERDE = (0x0E, 0x5E, 0x5A)
CREMA = (0xF4, 0xF1, 0xEA)
ROJO = (0xC0, 0x39, 0x2B)
GRIS = (0x6E, 0x6A, 0x63)
HUESO = (0xE7, 0xE2, 0xD8)
BLANCO = (0xFF, 0xFF, 0xFF)
VERDE_CLARO = (0x1B, 0x7A, 0x73)

GEORGIA = r"C:\Windows\Fonts\georgia.ttf"
GEORGIA_B = r"C:\Windows\Fonts\georgiab.ttf"
SANS = r"C:\Windows\Fonts\segoeui.ttf"
SANS_B = r"C:\Windows\Fonts\segoeuib.ttf"
SANS_SB = r"C:\Windows\Fonts\seguisb.ttf"
MONO = r"C:\Windows\Fonts\consola.ttf"


def f(ruta, tam):
    return ImageFont.truetype(ruta, tam)


def texto(d, xy, txt, fuente, color, ancho=None, interlineado=1.18):
    """Dibuja texto con salto de línea; devuelve el alto usado."""
    x, y = xy
    if ancho is None:
        d.text((x, y), txt, font=fuente, fill=color)
        return fuente.getbbox("Ág")[3]

    palabras, linea, lineas = txt.split(), "", []
    for p in palabras:
        prueba = (linea + " " + p).strip()
        if d.textlength(prueba, font=fuente) <= ancho:
            linea = prueba
        else:
            lineas.append(linea)
            linea = p
    if linea:
        lineas.append(linea)

    alto = fuente.getbbox("Ág")[3] * interlineado
    for i, ln in enumerate(lineas):
        d.text((x, y + i * alto), ln, font=fuente, fill=color)
    return alto * len(lineas)


def centrado(d, y, txt, fuente, color, ancho=W):
    w = d.textlength(txt, font=fuente)
    d.text(((ancho - w) / 2, y), txt, font=fuente, fill=color)


img = Image.new("RGB", (W, H), CREMA)
d = ImageDraw.Draw(img)

# ------------------------------------------------------------
# Cabecera
# ------------------------------------------------------------
d.rectangle([0, 0, W, 900], fill=TINTA)
d.rectangle([0, 900, W, 908], fill=VERDE)

d.text((M, 130), "MINERÍA DE DATOS CON R  ·  INEC 2025",
       font=f(SANS_B, 42), fill=HUESO)
d.text((M - 8, 210), "Actividad final", font=f(GEORGIA_B, 150), fill=BLANCO)
d.text((M, 410), "La secuencia, en orden", font=f(SANS, 66), fill=HUESO)

d.text((M, 560), "Siete pasos. El que se salta, se nota en la entrega.",
       font=f(SANS, 44), fill=(0x9A, 0xA8, 0xA4))

# sello de fechas
caja_x, caja_y, caja_w, caja_h = 1660, 560, 670, 250
d.rounded_rectangle([caja_x, caja_y, caja_x + caja_w, caja_y + caja_h],
                    radius=18, fill=(0x1B, 0x2E, 0x2B), outline=VERDE, width=3)
d.text((caja_x + 40, caja_y + 30), "ENTREGA", font=f(SANS_B, 30), fill=(0x8F, 0xC5, 0xBE))
d.text((caja_x + 40, caja_y + 78), "dom 29 nov · 23h59", font=f(SANS_B, 50), fill=BLANCO)
d.text((caja_x + 40, caja_y + 152), "Presentación 3 dic", font=f(SANS, 40), fill=HUESO)

# ------------------------------------------------------------
# Los siete pasos
# ------------------------------------------------------------
PASOS = [
    ("1", "Elige la pregunta",
     "Una de las cuatro: P1 seguridad social, P2 empleo protegido, P3 pluriempleo, "
     "P4 brecha de ingreso. Se responde con las variables que ya están en la carpeta.",
     "Criterio: no hace falta buscar datos por fuera."),
    ("2", "Descarga el insumo",
     "Del repositorio, carpeta actividad/: los datos comprimidos, el diccionario de "
     "variables, el de códigos y la plantilla del script.",
     "Criterio: trabajas sobre la misma versión que se califica."),
    ("3", "Calcula tu semilla",
     "Se deriva de tu correo institucional con la función de la plantilla. No se escribe "
     "a mano: así cada equipo tiene su propio corte de entrenamiento y prueba.",
     "Criterio: dos equipos con el mismo código no dan la misma cifra."),
    ("4", "Recodifica con el diccionario",
     "Los códigos vienen sin etiqueta a propósito. Antes de usarlos, revisa qué significa "
     "cada valor y conviértelos en factores con nombre.",
     "Criterio: ningún modelo se ajusta sobre códigos 1, 2, 3."),
    ("5", "Analiza y verifica",
     "Aplica la técnica que corresponde a tu pregunta. Después repite el corte con otra "
     "semilla y mira cuánto se mueve la métrica.",
     "Criterio: un solo corte es una muestra, no el resultado."),
    ("6", "Escribe",
     "Doscientas cincuenta palabras: una cifra propia, qué significa y cuál es su límite. "
     "Sin adjetivos, sin promesas.",
     "Criterio: cada número del texto sale del script."),
    ("7", "Entrega",
     "Un ZIP con el script, la tabla de resultados, las seis láminas y el resumen. "
     "Nombra la carpeta con tu apellido.",
     "Criterio: el script corre de cero en otra máquina."),
]

def envolver(txt, fuente, ancho):
    lineas, linea = [], ""
    for palabra in txt.split():
        prueba = (linea + " " + palabra).strip()
        if d.textlength(prueba, font=fuente) <= ancho:
            linea = prueba
        else:
            lineas.append(linea)
            linea = palabra
    if linea:
        lineas.append(linea)
    return lineas


FU_TIT, FU_CUE, FU_CRI = f(SANS_B, 56), f(SANS, 37), f(SANS_B, 36)
LH_CUE = 46
ANCHO_TXT = 1330

# Dos pasadas: primero se mide, después se reparte el alto sobrante
# entre los siete pasos para que el letrero no quede con un hueco abajo.
alturas = []
for _, _, cuerpo, _ in PASOS:
    n = len(envolver(cuerpo, FU_CUE, ANCHO_TXT))
    alturas.append(74 + n * LH_CUE + 12 + 40)

TOPE, BASE = 1005, 3280
sobra = (BASE - TOPE - sum(alturas)) / len(PASOS)
sobra = max(sobra, 56)

y = TOPE
for (num, titulo, cuerpo, criterio), alto_bloque in zip(PASOS, alturas):
    lineas = envolver(cuerpo, FU_CUE, ANCHO_TXT)
    alto = len(lineas) * LH_CUE

    d.ellipse([M, y + 4, M + 110, y + 114], fill=VERDE)
    wnum = d.textlength(num, font=f(GEORGIA_B, 58))
    d.text((M + 55 - wnum / 2, y + 22), num, font=f(GEORGIA_B, 58), fill=BLANCO)

    d.text((M + 150, y), titulo, font=FU_TIT, fill=TINTA)
    for i, ln in enumerate(lineas):
        d.text((M + 150, y + 74 + i * LH_CUE), ln, font=FU_CUE, fill=(0x3A, 0x38, 0x33))
    d.text((M + 150, y + 74 + alto + 12), criterio, font=FU_CRI, fill=VERDE)

    y += alto_bloque + sobra
    if num != "7":
        d.line([(M + 150, y - sobra / 2 - 8), (W - M, y - sobra / 2 - 8)],
               fill=(0xD8, 0xD2, 0xC4), width=2)

# ------------------------------------------------------------
# Banda de reglas y cierre
# ------------------------------------------------------------
banda_y = 3310
d.rectangle([0, banda_y, W, H], fill=TINTA)
d.rectangle([0, banda_y, W, banda_y + 8], fill=ROJO)

d.text((M, banda_y + 46), "LA REGLA QUE NO SE NEGOCIA",
       font=f(SANS_B, 32), fill=(0x8F, 0xC5, 0xBE))
d.text((M, banda_y + 92), "Si no está en el script, no ocurrió.",
       font=f(GEORGIA_B, 62), fill=BLANCO)

d.text((1560, banda_y + 46), "TODO EL MATERIAL", font=f(SANS_B, 32),
       fill=(0x8F, 0xC5, 0xBE))
d.text((1560, banda_y + 92), "github.com/jbarrosn/mineria-datos-inec",
       font=f(MONO, 34), fill=BLANCO)

img.save(SALIDA, dpi=(150, 150))
print(SALIDA, img.size)
