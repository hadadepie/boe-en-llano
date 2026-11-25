"""Títulos oficiales de las normas anteriores a la legislatura que más cambió (para «La legislatura»).

Uso:
    python -m boe.citadas

El campo «cambia» de cada norma solo trae el identificador de la norma cambiada (p. ej.
BOE-A-2006-20764). Para que la web diga «Ley 35/2006, de 28 de noviembre, del Impuesto sobre la
Renta de las Personas Físicas…», se leen los metadatos de su XML del diario oficial
(https://www.boe.es/diario_boe/xml.php?id={id}; sirve también para las que el BOE no consolida),
solo para las que salen en la lista del informe (`informe.anteriores_cambiadas`) y solo si faltan:
el título de una norma no cambia. El XML queda en datos/crudo/citadas/ (fuera de Git); los títulos,
en datos/normas_citadas.json (versionado):

    {"BOE-A-2006-20764": {"titulo": "Ley 35/2006…", "rango": "Ley", "fecha_publicacion": "2006-11-29"}, …}
"""

import json
import xml.etree.ElementTree as ET
from pathlib import Path

from boe import descargar, informe

CARPETA_DATOS = Path("datos")
ARCHIVO = "normas_citadas.json"
PAUSA_SEGUNDOS = 1.0


def leer(carpeta_datos=CARPETA_DATOS):
    archivo = Path(carpeta_datos) / ARCHIVO
    return json.loads(archivo.read_text(encoding="utf-8")) if archivo.exists() else {}


def ficha_de(xml):
    """{"titulo", "rango", "fecha_publicacion"} de los metadatos del XML del diario, o None."""
    meta = ET.fromstring(xml).find("metadatos")
    titulo = (meta.findtext("titulo") or "").strip() if meta is not None else ""
    if not titulo:
        return None
    f = (meta.findtext("fecha_publicacion") or "").strip()
    return {"titulo": titulo.rstrip("."), "rango": (meta.findtext("rango") or "").strip() or None,
            "fecha_publicacion": f"{f[:4]}-{f[4:6]}-{f[6:8]}" if len(f) == 8 else None}


def procesar(carpeta_datos=CARPETA_DATOS, pausa=PAUSA_SEGUNDOS):
    """Añade a datos/normas_citadas.json las que falten de la lista del informe. Devuelve cuántas añade."""
    carpeta_datos = Path(carpeta_datos)
    normas = [json.loads(p.read_text(encoding="utf-8")) for p in sorted((carpeta_datos / "normas").glob("*.json"))]
    anteriores = informe.anteriores_cambiadas(normas)
    if not anteriores:
        return 0
    citadas = leer(carpeta_datos)
    ids = [x["id"] for x in anteriores["lista"]] + ([anteriores["mas_antigua"]["id"]] if anteriores["mas_antigua"] else [])
    nuevas = 0
    for i in dict.fromkeys(ids):
        if i in citadas:
            continue
        xml = descargar.descargar_norma_xml(i, carpeta=carpeta_datos / "crudo" / "citadas", pausa=pausa)
        ficha = ficha_de(xml)
        if ficha:
            citadas[i] = ficha
            nuevas += 1
    if nuevas:
        (carpeta_datos / ARCHIVO).write_text(json.dumps(dict(sorted(citadas.items())), ensure_ascii=False, indent=2) + "\n",
                                             encoding="utf-8")
    return nuevas


def main():
    print(f"Títulos nuevos de normas citadas: {procesar()}")


if __name__ == "__main__":
    main()
