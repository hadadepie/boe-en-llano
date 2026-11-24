"""Pone en los HTML de web/ el `?v=` de cada .js y .css según su contenido (caché del navegador).

Uso (tras cambiar cualquier .js de web/ o web/estilos.css):
    python herramientas/versionar.py

El `?v=` es el principio del SHA-1 del archivo: cambia solo si el archivo cambia, así que el
navegador vuelve a descargarlo justo cuando hace falta. `tests/test_web.py` falla si algún HTML
lleva un `?v=` que no corresponde al contenido actual (es decir, si se olvidó pasar este script).
"""

import hashlib
import re
from pathlib import Path

WEB = Path(__file__).resolve().parent.parent / "web"
_ENLACE = re.compile(r'((?:src|href)="([\w.-]+\.(?:js|css))\?v=)([\w-]+)(")')


def version(archivo):
    return hashlib.sha1(archivo.read_bytes().replace(b"\r\n", b"\n")).hexdigest()[:10]


def enlaces(html):
    """[(recurso, versión que lleva)] de un HTML."""
    return [(m.group(2), m.group(3)) for m in _ENLACE.finditer(html)]


def versionar(carpeta=WEB):
    cambiados = []
    for pagina in sorted(carpeta.glob("*.html")):
        texto = pagina.read_text(encoding="utf-8")
        nuevo = _ENLACE.sub(lambda m: m.group(1) + version(carpeta / m.group(2)) + m.group(4), texto)
        if nuevo != texto:
            pagina.write_text(nuevo, encoding="utf-8")
            cambiados.append(pagina.name)
    return cambiados


if __name__ == "__main__":
    print("Actualizados:", ", ".join(versionar()) or "ninguno")
