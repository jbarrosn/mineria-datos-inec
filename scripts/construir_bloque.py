"""Construye un bloque suelto y lo guarda donde se indique (para saltar bloqueos)."""
import sys

from contenido_bloques import bloque_31, bloque_32, bloque_34

BLOQUES = {"31": bloque_31, "32": bloque_32, "34": bloque_34}

if __name__ == "__main__":
    clave, destino = sys.argv[1], sys.argv[2]
    BLOQUES[clave]().guardar(destino)
    print("OK", destino)
