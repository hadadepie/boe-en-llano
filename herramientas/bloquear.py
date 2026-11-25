"""Escribe `requirements-ci.txt`: las librerías de `requirements.txt` y las que estas arrastran,
con versión exacta y hash, para que la Action instale con `pip install --require-hashes`.

Uso (tras cambiar `requirements.txt`):
    python herramientas/bloquear.py

Resuelve las dependencias como en la Action (Linux x86_64, Python 3.11) y toma de PyPI los hashes
de todos los archivos publicados de cada versión. Si alguien sustituyera un paquete en PyPI o en el
camino, el hash no coincidiría y la Action se pararía en vez de instalarlo. `requirements.txt` se
queda sin hashes para instalar a mano en cualquier equipo.
"""

import json
import subprocess
import sys
import tempfile
import time
from pathlib import Path

import requests

RAIZ = Path(__file__).resolve().parent.parent
ORIGEN = RAIZ / "requirements.txt"
DESTINO = RAIZ / "requirements-ci.txt"
PYTHON = "3.11"  # el de la Action (.github/workflows/diario.yml)


def resolver():
    """[(nombre, versión)] que pip instalaría en la Action."""
    with tempfile.TemporaryDirectory() as tmp:
        informe = Path(tmp) / "informe.json"
        subprocess.run([sys.executable, "-m", "pip", "install", "--dry-run", "--ignore-installed", "--quiet",
                        "--python-version", PYTHON, "--platform", "manylinux2014_x86_64", "--only-binary=:all:",
                        "--target", str(Path(tmp) / "t"), "--report", str(informe), "-r", str(ORIGEN)], check=True)
        datos = json.loads(informe.read_text(encoding="utf-8"))
    return sorted((i["metadata"]["name"].lower(), i["metadata"]["version"]) for i in datos["install"])


def hashes(nombre, version):
    r = requests.get(f"https://pypi.org/pypi/{nombre}/{version}/json", timeout=30)
    r.raise_for_status()
    return sorted(f["digests"]["sha256"] for f in r.json()["urls"])


def main():
    lineas = ["# Generado por `python herramientas/bloquear.py` a partir de requirements.txt: no editar a mano.",
              "# Lo usa la Action: pip install --require-hashes -r requirements-ci.txt"]
    for nombre, version in resolver():
        # pytest solo pide colorama en Windows: con la marca, el archivo vale también para probarlo aquí
        marca = '; sys_platform == "win32"' if nombre == "colorama" else ""
        lineas.append(f"{nombre}=={version}{marca} \\")
        lista = hashes(nombre, version)
        lineas += [f"    --hash=sha256:{h}" + (" \\" if i < len(lista) - 1 else "") for i, h in enumerate(lista)]
        time.sleep(1)
    DESTINO.write_text("\n".join(lineas) + "\n", encoding="utf-8")
    print(f"{DESTINO.name}: {sum(1 for l in lineas if '==' in l)} librerías")


if __name__ == "__main__":
    main()
