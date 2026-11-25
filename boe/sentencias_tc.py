"""Sentencias y autos del Tribunal Constitucional sobre normas (sección T del BOE).

Uso:
    python -m boe.sentencias_tc      # añade a datos/sentencias_tc.json las de los sumarios guardados

El BOE publica las sentencias del Constitucional en su propia sección («T»). De cada sumario
guardado (datos/crudo/sumarios/) se toman las de asuntos sobre normas: recursos y cuestiones de
inconstitucionalidad, conflictos de competencia y entre órganos constitucionales, impugnaciones
de disposiciones autonómicas y cuestiones forales. Los recursos de amparo (casos de personas)
no se recogen.

Sin IA ni reglas sobre el texto de la sentencia: el XML oficial trae en su análisis las
referencias que pone el propio BOE:
  - «DICTADA en el Recurso 3726/2023» → la admisión a trámite (publicada en la sección I);
  - «DECLARA la inconstitucionalidad y nulidad de…», «la desestimación en relación con…», «la
    pérdida sobrevenida del objeto…» → cada norma juzgada y qué se decidió sobre ella (un «,» quiere
    decir «lo mismo que la anterior»).

Lo extraído se guarda en datos/sentencias_tc.json (en Git: la Action no conserva datos/crudo/);
el XML de cada sentencia, en datos/crudo/sentencias_tc/. No se vuelve a pedir lo ya guardado.
"""

import argparse
import json
import re
import xml.etree.ElementTree as ET
from pathlib import Path

from boe import descargar, tribunales

CARPETA_DATOS = Path("datos")
URL_XML = "https://www.boe.es/diario_boe/xml.php?id={id}"
_AMPARO = re.compile(r"recursos? de amparo", re.IGNORECASE)
_RECURSO = re.compile(r"(?:Recurso|Cuesti[óo]n|Conflicto|Impugnaci[óo]n) .{0,90}?(\d{1,5}-\d{4})", re.IGNORECASE)

# Qué decidió el Tribunal sobre cada norma, según el texto corto de la referencia «DECLARA».
# En orden: la primera que encaja.
RESULTADOS = [
    (re.compile(r"sin (?:declaraci[óo]n de )?nulidad", re.I), "inconstitucional_sin_nulidad"),
    (re.compile(r"\bnul[oai]s?\b|nulidad", re.I), "nulidad"),
    (re.compile(r"p[ée]rdida", re.I), "pierde_objeto"),
    (re.compile(r"extinci|extingui", re.I), "extinguido"),
    (re.compile(r"inadmisi|inadmisible", re.I), "inadmite"),
    (re.compile(r"desestim", re.I), "desestima"),
    # «el mantenimiento de suspensión de lo indicado… y el levantamiento del resto»: se mantiene en parte.
    (re.compile(r"mantenimiento de (?:la )?suspensi", re.I), "mantiene_suspension"),
    (re.compile(r"levantamiento de (?:la )?suspensi", re.I), "levanta_suspension"),
    (re.compile(r"inconstitucional", re.I), "inconstitucional_sin_nulidad"),
    (re.compile(r"interpretaci[óo]n conforme|constitucionalidad", re.I), "constitucional"),
]


def tipo_de(titulo):
    """Tipo de asunto (como boe.tribunales) o None si no es sobre normas (amparo, corrección…)."""
    if _AMPARO.search(titulo or ""):
        return None
    return next((e for r, e in tribunales.TIPOS_TC if re.search(r, titulo or "", re.IGNORECASE)), None)


def resultado_de(texto, anterior=None):
    t = " ".join((texto or "").split()).strip(" ,.")
    if not t:
        return anterior or "otro"  # «,»: lo mismo que la referencia anterior
    return next((e for r, e in RESULTADOS if r.search(t)), "otro")


def items_t(sumario):
    """Publicaciones de la sección T de un sumario: [(id, título)]."""
    return [(i["identificador"], " ".join(i["titulo"].split()))
            for s in descargar.secciones(sumario) if s.get("codigo") == "T"
            for i in descargar.extraer_items(s)]


def leer_xml(xml, titulo=None):
    e = ET.fromstring(xml)
    md = e.find("metadatos")
    titulo = " ".join((md.findtext("titulo") or titulo or "").split())
    fecha = md.findtext("fecha_publicacion") or ""
    admisiones, normas, anterior = [], [], None
    for a in e.iter("anterior"):
        palabra, texto = (a.findtext("palabra") or "").strip(), " ".join((a.findtext("texto") or "").split())
        if palabra == "DICTADA" and a.get("referencia"):
            admisiones.append(a.get("referencia"))
        elif palabra == "DECLARA" and a.get("referencia"):
            anterior = resultado_de(texto, anterior)
            normas.append({"id": a.get("referencia"), "resultado": anterior, "texto": texto.strip(" ,") or None})
    m = _RECURSO.search(titulo)
    return {"rango": md.findtext("rango"), "numero": md.findtext("numero_oficial"),
            "fecha": f"{fecha[:4]}-{fecha[4:6]}-{fecha[6:]}" if len(fecha) == 8 else None,
            "tipo": tipo_de(titulo), "asunto": m.group(1) if m else None,
            "sala": titulo.split(".", 1)[0] if titulo.startswith(("Pleno", "Sala")) else None,
            "titulo": titulo, "admisiones": admisiones, "normas": normas}


def procesar(carpeta_datos=CARPETA_DATOS, pausa=descargar.PAUSA_SEGUNDOS):
    carpeta_datos = Path(carpeta_datos)
    salida = carpeta_datos / "sentencias_tc.json"
    guardadas = {s["id"]: s for s in (json.loads(salida.read_text(encoding="utf-8"))["sentencias"]
                                      if salida.exists() else [])}
    nuevas = 0
    for archivo in sorted((carpeta_datos / "crudo" / "sumarios").glob("*.json")):
        for id_, titulo in items_t(json.loads(archivo.read_text(encoding="utf-8"))):
            if id_ in guardadas or not tipo_de(titulo):
                continue
            crudo = carpeta_datos / "crudo" / "sentencias_tc" / f"{id_}.xml"
            if not crudo.exists():
                respuesta = descargar.pedir(URL_XML.format(id=id_), descargar.CABECERAS, pausa)
                respuesta.raise_for_status()
                crudo.parent.mkdir(parents=True, exist_ok=True)
                crudo.write_bytes(respuesta.content)
            datos = leer_xml(crudo.read_bytes(), titulo)
            if datos["rango"] in ("Sentencia", "Auto"):
                guardadas[id_] = {"id": id_, **datos}
                nuevas += 1
    if nuevas or not salida.exists():
        lista = sorted(guardadas.values(), key=lambda s: (s["fecha"] or "", s["id"]))
        salida.write_text(json.dumps({"fuente": "BOE, sección T (Tribunal Constitucional)", "sentencias": lista},
                                     ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return nuevas


def main():
    argparse.ArgumentParser(description="Sentencias del Tribunal Constitucional sobre normas (sección T del BOE).").parse_args()
    print(f"Sentencias y autos nuevos del Tribunal Constitucional: {procesar()}")


if __name__ == "__main__":
    main()
