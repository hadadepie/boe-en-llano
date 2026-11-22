"""La vida de cada norma, según la legislación consolidada del BOE.

Uso:
    python -m boe.consolidada        # actualiza el campo "vida" de datos/normas

Para cada norma consulta el análisis jurídico oficial del BOE
(https://www.boe.es/datosabiertos/api/legislacion-consolidada/id/{id}/analisis):
  - nota de entrada en vigor (redactada por el BOE, p. ej. "Entrada en vigor el
    3 de septiembre de 2026"), que da un "desde cuándo" oficial sin IA;
  - referencias anteriores: qué cambia esta norma en otras (MODIFICA, AÑADE…);
  - referencias posteriores: qué le ha pasado después (SE MODIFICA, SE DEROGA,
    SE PUBLICA Acuerdo de convalidación, corrección de errores…).

Las referencias posteriores cambian con el tiempo, así que la respuesta en crudo
se renueva cada DIAS_CACHE días. Las normas que el BOE no consolida (muchas
resoluciones y órdenes de trámite) devuelven 404: no tienen "vida".
Solo se reflejan las relaciones expresas que recoge el BOE.
"""

import argparse
import json
import re
import time
from datetime import date, datetime
from pathlib import Path

import requests

URL_ANALISIS = "https://www.boe.es/datosabiertos/api/legislacion-consolidada/id/{id}/analisis"
URL_NORMA = "https://www.boe.es/buscar/act.php?id={id}"
CARPETA_DATOS = Path("datos")
PAUSA_SEGUNDOS = 1.0
DIAS_CACHE = 7
CABECERAS = {"Accept": "application/json", "User-Agent": "boe-en-llano/0.1 (proyecto educativo)"}

# Relaciones de "anteriores" que indican un cambio real en otra norma (no meras citas).
CAMBIOS = ("MODIFICA", "AÑADE", "DEROGA", "SUPRIME", "SUSTITUYE", "DEJA SIN EFECTO", "PRORROGA", "SUSPENDE")
_MESES = "enero|febrero|marzo|abril|mayo|junio|julio|agosto|septiembre|octubre|noviembre|diciembre"
_RE_FECHA = re.compile(rf"de (\d{{1,2}}) de ({_MESES}) de (\d{{4}})")


def _lista(x):
    return x if isinstance(x, list) else ([] if x is None else [x])


def _textos(valor, clave):
    """Textos bajo `clave` en una estructura que puede ser dict, lista o texto suelto."""
    if valor is None:
        return []
    if isinstance(valor, str):
        return [valor]
    if isinstance(valor, list):
        return [t for v in valor for t in _textos(v, clave)]
    if isinstance(valor, dict):
        return _textos(valor.get(clave), clave) if clave in valor else []
    return []


def _unir(valor):
    """Un dict a partir de un dict, una lista de dicts o nada (la API usa las tres formas)."""
    if isinstance(valor, dict):
        return valor
    resultado = {}
    for v in _lista(valor):
        if isinstance(v, dict):
            for k, x in v.items():
                resultado[k] = _lista(resultado.get(k)) + _lista(x)
    return resultado


def _limpiar(texto):
    return re.sub(r"\s+", " ", (texto or "")).strip().lstrip(",").strip()


def _fecha_iso(texto):
    m = _RE_FECHA.search(texto or "")
    if not m:
        return None
    mes = _MESES.split("|").index(m.group(2)) + 1
    return f"{m.group(3)}-{mes:02d}-{int(m.group(1)):02d}"


def descargar_analisis(identificador, carpeta_datos=CARPETA_DATOS, hoy=None, pausa=PAUSA_SEGUNDOS):
    """Análisis oficial de una norma (dict) o None si el BOE no la consolida.

    Se guarda en datos/crudo/consolidada/ y se reutiliza durante DIAS_CACHE días.
    """
    hoy = hoy or date.today()
    archivo = Path(carpeta_datos) / "crudo" / "consolidada" / f"{identificador}.json"
    if archivo.exists():
        antiguedad = (hoy - datetime.fromtimestamp(archivo.stat().st_mtime).date()).days
        if antiguedad < DIAS_CACHE:
            guardado = json.loads(archivo.read_text(encoding="utf-8"))
            return None if guardado.get("no_consolidada") else guardado
    respuesta = requests.get(URL_ANALISIS.format(id=identificador), headers=CABECERAS, timeout=30)
    time.sleep(pausa)
    archivo.parent.mkdir(parents=True, exist_ok=True)
    if respuesta.status_code == 404:
        archivo.write_text(json.dumps({"no_consolidada": True}), encoding="utf-8")
        return None
    respuesta.raise_for_status()
    datos = respuesta.json()
    archivo.write_text(json.dumps(datos, ensure_ascii=False), encoding="utf-8")
    return datos


def leer_analisis(datos):
    """Convierte la respuesta oficial en lo que muestra la web."""
    bloque = (datos or {}).get("data")
    bloque = bloque[0] if isinstance(bloque, list) and bloque else (bloque or {})
    notas = [_limpiar(n) for n in _textos(bloque.get("notas"), "nota") if n]
    referencias = _unir(bloque.get("referencias"))

    def filas(clave, sub):
        return [r for b in _lista(referencias.get(clave)) for r in _lista((b or {}).get(sub))]

    modifica = []
    for r in filas("anteriores", "anterior"):
        relacion = _limpiar((r.get("relacion") or {}).get("texto")).upper()
        if relacion.startswith(CAMBIOS):
            modifica.append({"relacion": relacion.capitalize(), "texto": _limpiar(r.get("texto")),
                             "id": r.get("id_norma")})
    despues = []
    for r in filas("posteriores", "posterior"):
        relacion = _limpiar((r.get("relacion") or {}).get("texto"))
        texto = _limpiar(r.get("texto"))
        despues.append({"relacion": relacion[:1].upper() + relacion[1:].lower(), "texto": texto,
                        "id": r.get("id_norma"), "fecha": _fecha_iso(texto)})
    despues.sort(key=lambda x: (x["fecha"] or "9999", x["relacion"]))
    vigor = next((n for n in notas if re.search(r"vigor|efectos", n, re.IGNORECASE)), None)
    return {"entrada_en_vigor": vigor, "notas": notas, "modifica": modifica, "despues": despues}


def vida_de(norma, carpeta_datos=CARPETA_DATOS, hoy=None):
    datos = descargar_analisis(norma["id"], carpeta_datos, hoy)
    if datos is None:
        return {"consolidada": False, "consultado": (hoy or date.today()).isoformat()}
    return {"consolidada": True, "consultado": (hoy or date.today()).isoformat(),
            "enlace": URL_NORMA.format(id=norma["id"]), **leer_analisis(datos)}


def procesar(carpeta_datos=CARPETA_DATOS, hoy=None):
    carpeta_datos = Path(carpeta_datos)
    cambiadas = 0
    for archivo in sorted((carpeta_datos / "normas").glob("*.json")):
        norma = json.loads(archivo.read_text(encoding="utf-8"))
        nueva = vida_de(norma, carpeta_datos, hoy)
        anterior = {k: v for k, v in (norma.get("vida") or {}).items() if k != "consultado"}
        if {k: v for k, v in nueva.items() if k != "consultado"} != anterior:
            norma["vida"] = nueva
            archivo.write_text(json.dumps(norma, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            cambiadas += 1
    return cambiadas


def main():
    argparse.ArgumentParser(description="Vida de cada norma según la legislación consolidada del BOE.").parse_args()
    print(f"Normas con la vida actualizada: {procesar()}")


if __name__ == "__main__":
    main()
