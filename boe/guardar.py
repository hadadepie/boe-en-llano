"""Paso 2: extraer y guardar los datos de cada día.

Uso:
    python -m boe.guardar 2026-11-20              # un día
    python -m boe.guardar 2026-11-16 2026-11-20   # un rango (ambos incluidos)

Qué se guarda (versionado en Git):
    datos/recuentos.json          {"2026-11-20": {"1": 27, "2A": 12, ...}, ...}
    datos/normas/BOE-A-….json     una por norma de la sección I

Qué es temporal (en .gitignore): datos/crudo/ (sumarios y XML tal cual).
El texto completo de cada norma NO se guarda en el JSON: se lee del XML en crudo
cuando hace falta (clasificar/resumir) con `texto_de_norma`.

Un día se considera procesado cuando está en recuentos.json. Ese dato se
escribe al final, así que si el proceso se corta a medias, se repite entero
(las normas ya guardadas no se vuelven a descargar).
"""

import argparse
import json
import xml.etree.ElementTree as ET
from datetime import date, timedelta
from pathlib import Path

from boe import descargar
from boe.descargar import como_lista

CARPETA_DATOS = Path("datos")
SECCION_DISPOSICIONES_GENERALES = "1"


# ---------- Lectura del sumario ----------

def normas_seccion_i(sumario):
    """Lista de normas de la sección I con su departamento y epígrafe."""
    fecha = sumario["data"]["sumario"]["metadatos"]["fecha_publicacion"]
    normas = []
    for seccion in descargar.secciones(sumario):
        if seccion["codigo"] != SECCION_DISPOSICIONES_GENERALES:
            continue
        for departamento in como_lista(seccion.get("departamento")):
            for epigrafe in como_lista(departamento.get("epigrafe")):
                for item in como_lista(epigrafe.get("item")):
                    normas.append({
                        "id": item["identificador"],
                        "fecha_publicacion": f"{fecha[:4]}-{fecha[4:6]}-{fecha[6:]}",
                        "departamento_sumario": departamento.get("nombre"),
                        "epigrafe": epigrafe.get("nombre"),
                        "titulo": item["titulo"],
                        "url_html": item.get("url_html"),
                        "url_pdf": (item.get("url_pdf") or {}).get("texto"),
                    })
    return normas


# ---------- Lectura del XML de una norma ----------

def _texto(elemento, ruta):
    nodo = elemento.find(ruta)
    if nodo is None or not (nodo.text or "").strip():
        return None
    return nodo.text.strip()


def _fecha(valor):
    """'20261118' -> '2026-11-18' (o None)."""
    if not valor or len(valor) != 8:
        return None
    return f"{valor[:4]}-{valor[4:6]}-{valor[6:]}"


def metadatos_de_xml(xml):
    """Extrae del XML de una norma los metadatos que usaremos para clasificar."""
    raiz = ET.fromstring(xml)
    meta = raiz.find("metadatos")
    return {
        "rango": _texto(meta, "rango"),                        # tipo: Ley, Real Decreto...
        "departamento": _texto(meta, "departamento"),          # órgano emisor
        "origen_legislativo": _texto(meta, "origen_legislativo"),  # Estatal / Autonómico
        "numero_oficial": _texto(meta, "numero_oficial"),
        "fecha_disposicion": _fecha(_texto(meta, "fecha_disposicion")),
        "fecha_vigencia": _fecha(_texto(meta, "fecha_vigencia")),
        "url_eli": _texto(meta, "url_eli"),
        "materias": [m.text.strip() for m in raiz.findall("analisis/materias/materia") if m.text],
    }


def texto_de_xml(xml):
    """Texto completo de la norma: un párrafo por línea.

    Ojo: hay otras etiquetas <texto> dentro de <analisis>/<referencias>; la buena
    es la que cuelga directamente de <documento>.
    """
    nodo = ET.fromstring(xml).find("texto")
    if nodo is None:
        return ""
    parrafos = ("".join(p.itertext()).strip() for p in nodo)
    return "\n".join(p for p in parrafos if p)


def texto_de_norma(identificador):
    """Texto completo de una norma (lo descarga si no está en datos/crudo/)."""
    return texto_de_xml(descargar.descargar_norma_xml(identificador))


# ---------- Guardado ----------

def leer_recuentos(carpeta_datos=CARPETA_DATOS):
    archivo = Path(carpeta_datos) / "recuentos.json"
    if not archivo.exists():
        return {}
    return json.loads(archivo.read_text(encoding="utf-8"))


def escribir_json(archivo, datos):
    archivo.parent.mkdir(parents=True, exist_ok=True)
    archivo.write_text(
        json.dumps(datos, ensure_ascii=False, indent=2, sort_keys=False) + "\n",
        encoding="utf-8",
    )


def procesar_dia(fecha, carpeta_datos=CARPETA_DATOS):
    """Descarga y guarda un día. Devuelve 'hecho', 'ya_estaba' o 'sin_boe'."""
    carpeta_datos = Path(carpeta_datos)
    recuentos = leer_recuentos(carpeta_datos)
    clave = fecha.isoformat()
    if clave in recuentos:
        print(f"  {fecha}: ya procesado.")
        return "ya_estaba"

    sumario = descargar.descargar_sumario(fecha, carpeta=carpeta_datos / "crudo" / "sumarios")
    if sumario is None:
        return "sin_boe"

    for norma in normas_seccion_i(sumario):
        archivo = carpeta_datos / "normas" / f"{norma['id']}.json"
        if archivo.exists():
            continue
        xml = descargar.descargar_norma_xml(norma["id"], carpeta=carpeta_datos / "crudo" / "normas")
        escribir_json(archivo, {**norma, **metadatos_de_xml(xml)})

    recuentos[clave] = descargar.contar_por_seccion(sumario)
    escribir_json(carpeta_datos / "recuentos.json", dict(sorted(recuentos.items())))
    return "hecho"


def procesar_rango(desde, hasta, carpeta_datos=CARPETA_DATOS):
    resultado = {}
    dia = desde
    while dia <= hasta:
        resultado[dia.isoformat()] = procesar_dia(dia, carpeta_datos)
        dia += timedelta(days=1)
    return resultado


def main():
    parser = argparse.ArgumentParser(description="Descarga y guarda días del BOE.")
    parser.add_argument("desde", help="AAAA-MM-DD")
    parser.add_argument("hasta", nargs="?", help="AAAA-MM-DD (por defecto, igual que desde)")
    args = parser.parse_args()
    desde = date.fromisoformat(args.desde)
    hasta = date.fromisoformat(args.hasta) if args.hasta else desde

    resultado = procesar_rango(desde, hasta)
    print("\nResumen:", {estado: list(resultado.values()).count(estado)
                         for estado in sorted(set(resultado.values()))})


if __name__ == "__main__":
    main()
