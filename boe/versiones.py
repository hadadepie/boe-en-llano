"""Qué cambia en concreto: el antes y el después de cada artículo modificado.

Uso:
    python -m boe.versiones      # calcula los cambios de las normas que modifican otras

Para cada norma nuestra que MODIFICA o AÑADE algo en otra (según su análisis de
legislación consolidada, campo "vida.modifica"):
  1. se consulta el índice del texto consolidado de la norma modificada, que da
     la fecha de última actualización de cada artículo (bloque);
  2. de los bloques actualizados desde la publicación de nuestra norma, se
     descargan sus versiones (XML) y se busca la versión que creó nuestra norma;
  3. "antes" es la versión anterior y "después", la suya. Si existe una versión
     posterior, se indica hasta cuándo estuvo en vigor esa redacción.

El resultado se guarda comparado (párrafos iguales resumidos, cambios marcados
palabra a palabra) en el campo "cambios" de la norma. Se calcula una sola vez
por pareja (norma, norma modificada): las versiones pasadas no cambian.
Fuente: API de legislación consolidada del BOE (índice en JSON, bloques en XML).
"""

import argparse
import difflib
import json
import re
import time
import xml.etree.ElementTree as ET
from pathlib import Path

import requests

BASE = "https://www.boe.es/datosabiertos/api/legislacion-consolidada/id/{id}/texto"
CARPETA_DATOS = Path("datos")
PAUSA_SEGUNDOS = 1.0
AGENTE = "boe-en-llano/0.1 (proyecto educativo)"
MAX_BLOQUES_POR_NORMA = 25        # tope de artículos a revisar por norma modificada
MAX_CARACTERES_POR_PARRAFO = 1500  # se recortan párrafos enormes (tablas)
RELACIONES = ("Modifica", "Añade")


def _lista(x):
    return x if isinstance(x, list) else ([] if x is None else [x])


def _get(url, aceptar, archivo):
    archivo = Path(archivo)
    if archivo.exists():
        return archivo.read_text(encoding="utf-8")
    respuesta = requests.get(url, headers={"Accept": aceptar, "User-Agent": AGENTE}, timeout=60)
    time.sleep(PAUSA_SEGUNDOS)
    if respuesta.status_code == 404:
        return None
    respuesta.raise_for_status()
    texto = respuesta.content.decode("utf-8", errors="replace")
    archivo.parent.mkdir(parents=True, exist_ok=True)
    archivo.write_text(texto, encoding="utf-8")
    return texto


def indice(identificador, carpeta_datos, marca):
    """Bloques del texto consolidado [{id, titulo, fecha_actualizacion}] (o None).

    `marca` (fecha de nuestra norma) forma parte del nombre de la caché: un
    índice consultado antes de esa fecha no serviría.
    """
    archivo = Path(carpeta_datos) / "crudo" / "consolidada" / "indices" / f"{identificador}_{marca}.json"
    texto = _get(BASE.format(id=identificador) + "/indice", "application/json", archivo)
    if texto is None:
        return None
    datos = json.loads(texto).get("data")
    datos = datos[0] if isinstance(datos, list) and datos else (datos or {})
    return [b for b in _lista(datos.get("bloque")) if isinstance(b, dict)]


def versiones(identificador, bloque, actualizado, carpeta_datos):
    """Versiones de un bloque: [{id_norma, fecha_publicacion, fecha_vigencia, parrafos}]."""
    archivo = Path(carpeta_datos) / "crudo" / "consolidada" / "bloques" / f"{identificador}_{bloque}_{actualizado}.xml"
    texto = _get(BASE.format(id=identificador) + f"/bloque/{bloque}", "application/xml", archivo)
    if texto is None:
        return []
    raiz = ET.fromstring(texto)
    resultado = []
    for v in raiz.iter("version"):
        parrafos = []
        for p in v:
            if (p.get("class") or "").startswith("nota") or p.tag == "blockquote" and all(
                    (h.get("class") or "").startswith("nota") for h in p):
                continue  # notas editoriales del BOE ("Se modifica el apartado 2 por…"), a veces en <blockquote>
            t = re.sub(r"\s+", " ", "".join(p.itertext())).strip()
            if t:
                parrafos.append(t[:MAX_CARACTERES_POR_PARRAFO])
        resultado.append({"id_norma": v.get("id_norma"), "fecha_publicacion": v.get("fecha_publicacion"),
                          "fecha_vigencia": v.get("fecha_vigencia"), "parrafos": parrafos})
    return resultado


# ---------- Comparación ----------

def _palabras(antes, despues):
    """Diferencias palabra a palabra: [["=", texto], ["-", texto], ["+", texto]]."""
    a, b = antes.split(" "), despues.split(" ")
    segmentos = []
    for op, i1, i2, j1, j2 in difflib.SequenceMatcher(a=a, b=b, autojunk=False).get_opcodes():
        if op == "equal":
            segmentos.append(["=", " ".join(a[i1:i2])])
        else:
            if i2 > i1:
                segmentos.append(["-", " ".join(a[i1:i2])])
            if j2 > j1:
                segmentos.append(["+", " ".join(b[j1:j2])])
    return segmentos


def comparar(antes, despues):
    """Compara dos listas de párrafos. Los iguales se resumen en {"iguales": n}."""
    clave = lambda p: re.sub(r"\s+", " ", p.replace("\xa0", " ")).strip()
    a, b = [clave(p) for p in antes], [clave(p) for p in despues]
    resultado = []
    for op, i1, i2, j1, j2 in difflib.SequenceMatcher(a=a, b=b, autojunk=False).get_opcodes():
        if op == "equal":
            resultado.append({"iguales": i2 - i1})
        else:
            resultado.extend(_emparejar(a[i1:i2], b[j1:j2]))
    return resultado


PARECIDO_MINIMO = 0.5


def _emparejar(quitados, puestos):
    """Empareja párrafos quitados y puestos que se parecen (→ "cambiado").

    Mantiene el orden del texto nuevo; los quitados sin pareja van delante de
    donde estaban, los puestos sin pareja quedan como "añadido".
    """
    usados, resultado = set(), []
    for y in puestos:
        mejor, indice_mejor = 0.0, None
        for k, x in enumerate(quitados):
            if k in usados:
                continue
            r = difflib.SequenceMatcher(a=x, b=y, autojunk=False).ratio()
            if r > mejor:
                mejor, indice_mejor = r, k
        if indice_mejor is not None and mejor >= PARECIDO_MINIMO:
            # los quitados anteriores sin pareja, como eliminados, antes de este cambio
            for k in range(indice_mejor):
                if k not in usados:
                    resultado.append({"eliminado": quitados[k]})
                    usados.add(k)
            resultado.append({"cambiado": _palabras(quitados[indice_mejor], y)})
            usados.add(indice_mejor)
        else:
            resultado.append({"añadido": y})
    resultado.extend({"eliminado": x} for k, x in enumerate(quitados) if k not in usados)
    return resultado


def _iso(aaaammdd):
    return f"{aaaammdd[:4]}-{aaaammdd[4:6]}-{aaaammdd[6:]}" if aaaammdd and len(aaaammdd) == 8 else None


def cambios_en(modificadora, fecha, destino, carpeta_datos=CARPETA_DATOS):
    """Bloques de `destino` que cambió la norma `modificadora` (publicada en `fecha`, AAAAMMDD)."""
    bloques = indice(destino, carpeta_datos, fecha)
    if bloques is None:
        return {"consolidada": False, "bloques": []}
    candidatos = [b for b in bloques if (b.get("fecha_actualizacion") or "") >= fecha and b.get("id")]
    resultado, recortado = [], len(candidatos) > MAX_BLOQUES_POR_NORMA
    for b in candidatos[:MAX_BLOQUES_POR_NORMA]:
        vs = versiones(destino, b["id"], b.get("fecha_actualizacion"), carpeta_datos)
        for k, v in enumerate(vs):
            if v["id_norma"] != modificadora:
                continue
            anterior = vs[k - 1]["parrafos"] if k > 0 else []
            siguiente = vs[k + 1] if k + 1 < len(vs) else None
            resultado.append({
                "bloque": b["id"], "titulo": re.sub(r"\s+", " ", b.get("titulo") or "").strip(),
                "nuevo": k == 0,
                "en_vigor_desde": _iso(v["fecha_vigencia"]),
                "hasta": _iso(siguiente["fecha_vigencia"]) if siguiente else None,
                "cambiado_despues_por": siguiente["id_norma"] if siguiente else None,
                "comparacion": comparar(anterior, v["parrafos"]),
            })
            break
    return {"consolidada": True, "bloques": resultado, "recortado": recortado}


def procesar(carpeta_datos=CARPETA_DATOS, desde=None):
    """desde (AAAA-MM-DD): solo normas publicadas desde esa fecha (la Action no calcula el antes y
    el después de las antiguas: ocupa ~12 KB por norma con cambios)."""
    carpeta_datos = Path(carpeta_datos)
    actualizadas = 0
    for archivo in sorted((carpeta_datos / "normas").glob("*.json")):
        norma = json.loads(archivo.read_text(encoding="utf-8"))
        if desde and norma.get("fecha_publicacion", "") < desde:
            continue
        refs = [m for m in (norma.get("vida") or {}).get("modifica", []) if m.get("relacion") in RELACIONES and m.get("id")]
        if not refs:
            continue
        hechos = {c["norma"] for c in norma.get("cambios", [])}
        pendientes = [m for m in refs if m["id"] not in hechos]
        if not pendientes:
            continue
        fecha = norma["fecha_publicacion"].replace("-", "")
        print(f"  {norma['id']}: {len(pendientes)} normas modificadas")
        for m in pendientes:
            c = cambios_en(norma["id"], fecha, m["id"], carpeta_datos)
            norma.setdefault("cambios", []).append({"norma": m["id"], "relacion": m["relacion"], "referencia": m["texto"], **c})
        archivo.write_text(json.dumps(norma, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        actualizadas += 1
    return actualizadas


def procesar_recibidos(carpeta_datos=CARPETA_DATOS, desde=None):
    """Calcula el antes y el después desde la norma MODIFICADA.

    Sirve cuando la norma que modifica aún no está consolidada (el BOE tarda
    unos días) pero el análisis de la modificada ya registra el cambio
    ("Se modifica el art. 15.2, por Real Decreto-ley 38/2026"). Solo para
    modificadoras que están en nuestros datos (necesitamos su fecha) y, con
    `desde`, publicadas desde esa fecha.
    """
    carpeta_datos = Path(carpeta_datos)
    archivos = sorted((carpeta_datos / "normas").glob("*.json"))
    fecha_de = {}
    for archivo in archivos:
        n = json.loads(archivo.read_text(encoding="utf-8"))
        fecha_de[n["id"]] = n["fecha_publicacion"].replace("-", "")
    actualizadas = 0
    for archivo in archivos:
        norma = json.loads(archivo.read_text(encoding="utf-8"))
        hechos = {c["por"] for c in norma.get("cambios_recibidos", [])}
        pendientes = [h for h in (norma.get("vida") or {}).get("despues", [])
                      if re.match(r"se (modifica|añade)", h.get("relacion", ""), re.IGNORECASE)
                      and h.get("id") in fecha_de and h["id"] not in hechos
                      and (not desde or fecha_de[h["id"]] >= desde.replace("-", ""))]
        if not pendientes:
            continue
        for h in pendientes:
            c = cambios_en(h["id"], fecha_de[h["id"]], norma["id"], carpeta_datos)
            norma.setdefault("cambios_recibidos", []).append({"por": h["id"], "referencia": h.get("texto"), **c})
        archivo.write_text(json.dumps(norma, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        actualizadas += 1
    return actualizadas


def main():
    argparse.ArgumentParser(description="Antes y después de los artículos que cambia cada norma.").parse_args()
    print(f"Normas con cambios calculados: {procesar()} (desde la modificadora), "
          f"{procesar_recibidos()} (desde la modificada)")


if __name__ == "__main__":
    main()
