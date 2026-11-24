"""Genera las imágenes de la web (sin dependencias): web/imagen-compartir.png
(1200×630, vista previa al compartir) y web/icono-180.png (icono táctil).
Dibujan el mosaico de la portada: un cuadrado por norma, en los tres colores de
impacto. Se ejecuta a mano si cambia el diseño: python herramientas/imagen_compartir.py"""

import struct
import zlib
from pathlib import Path

WEB = Path(__file__).resolve().parent.parent / "web"
FONDO = (249, 249, 247)
DIRECTO, COLECTIVOS, TECNICO = (37, 106, 191), (109, 167, 236), (205, 226, 251)
ACENTO = (11, 11, 11)


def png(ruta: Path, ancho: int, alto: int, pixeles: bytearray) -> None:
    filas = b"".join(b"\x00" + bytes(pixeles[y * ancho * 3:(y + 1) * ancho * 3]) for y in range(alto))

    def trozo(tipo: bytes, datos: bytes) -> bytes:
        cuerpo = tipo + datos
        return struct.pack(">I", len(datos)) + cuerpo + struct.pack(">I", zlib.crc32(cuerpo))

    ruta.write_bytes(b"\x89PNG\r\n\x1a\n" + trozo(b"IHDR", struct.pack(">IIBBBBB", ancho, alto, 8, 2, 0, 0, 0))
                     + trozo(b"IDAT", zlib.compress(filas, 9)) + trozo(b"IEND", b""))


def lienzo(ancho: int, alto: int, color) -> bytearray:
    return bytearray(bytes(color) * (ancho * alto))


def rect(px, ancho, x, y, w, h, color) -> None:
    for fila in range(y, y + h):
        px[(fila * ancho + x) * 3:(fila * ancho + x + w) * 3] = bytes(color) * w


def mosaico(ancho, alto, margen, lado, hueco, patron) -> bytearray:
    """patron: filas de letras D (directo), C (colectivos), T (técnico), '.' (vacío)."""
    px = lienzo(ancho, alto, FONDO)
    colores = {"D": DIRECTO, "C": COLECTIVOS, "T": TECNICO}
    for j, fila in enumerate(patron):
        for i, letra in enumerate(fila):
            if letra in colores:
                rect(px, ancho, margen + i * (lado + hueco), margen + j * (lado + hueco), lado, lado, colores[letra])
    return px


# Una mancha de «normas» con pocas que te afectan directamente, como en la portada.
PATRON = [
    "DDCCCTTTCTTCTTTTCC",
    "DCCCTTTTCCTTTTTCTT",
    "CCCTTTCCTTTTTTCTTT",
    "CCTTCCTTTTTTTTTTTT",
    "CTTTTTTTTTTTTTTT..",
]

if __name__ == "__main__":
    # 18 columnas × 5 filas de cuadrados de 52 px con huecos de 8 px.
    ancho, alto = 1200, 630
    px = mosaico(ancho, alto, 64, 52, 8, PATRON)
    # Barra inferior oscura (equivale a la mancheta de la web).
    rect(px, ancho, 0, alto - 48, ancho, 48, ACENTO)
    png(WEB / "imagen-compartir.png", ancho, alto, px)
    # Icono táctil: 3×3 cuadrados.
    icono = mosaico(180, 180, 18, 36, 9, ["DCT", "CTT", "TTT"])
    png(WEB / "icono-180.png", 180, 180, icono)
    print("imágenes generadas en", WEB)
