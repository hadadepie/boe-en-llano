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
import re
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
        for item, departamento, epigrafe in descargar.recorrer_items(seccion):
            normas.append({
                "id": item["identificador"],
                "fecha_publicacion": f"{fecha[:4]}-{fecha[4:6]}-{fecha[6:]}",
                "departamento_sumario": departamento,
                "epigrafe": epigrafe,
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


# ---------- Preámbulo: por qué se aprueba, según el propio texto ----------

# Donde acaba el preámbulo y empieza la parte que manda.
_FIN_PREAMBULO = re.compile(
    r"^(En su virtud|DISPONGO|Artículo (único|primero|1)\b|T[IÍ]TULO\s|CAP[IÍ]TULO\s)|"
    r"(ha resuelto|resuelvo|dispongo|acuerdo|ha acordado)( lo siguiente)?:\s*$", re.IGNORECASE)
# Fórmulas de promulgación y encabezados que no explican nada.
_FORMULA = re.compile(r"a todos los que la presente vieren|sepades|sea notorio|en nombre del rey|promulgo|"
                      r"han aprobado y (yo|nos)|vengo en sancionar", re.IGNORECASE)
_ENCABEZADO = re.compile(r"^(EXPOSICI[OÓ]N DE MOTIVOS|PRE[AÁ]MBULO|[IVXL]+\.?)$", re.IGNORECASE)
_SECCION_ROMANA = re.compile(r"^[IVXL]+\.?$")
_INDICE = re.compile(r"^[IÍ]NDICE\.?$", re.IGNORECASE)
_ENCABEZADO_PREAMBULO = re.compile(r"^(PRE[AÁ]MBULO|EXPOSICI[OÓ]N DE MOTIVOS)\.?$", re.IGNORECASE)
# Párrafos de trámite habituales en todos los preámbulos.
_TRAMITE = re.compile(r"principios de buena regulación|al amparo de lo dispuesto en el artículo 149|"
                      r"se dicta al amparo|(norma|ley|real decreto|orden)[\w\s-]{0,20} (consta|se estructura) (de|en)|"
                      r"trámite(s)? de (audiencia|información pública)|ha sido sometid[oa]|"
                      r"memoria del análisis de impacto", re.IGNORECASE)
MAX_PARRAFOS_PREAMBULO = 5
MAX_CARACTERES_PREAMBULO = 3500
MIN_CARACTERES_PARRAFO = 100


def preambulo_de_texto(texto):
    """Primeros párrafos del preámbulo que explican por qué se aprueba la norma.

    Copia literal del texto oficial (sin resumir ni reescribir). Si el preámbulo
    está dividido en partes (I, II…), se queda con la primera, que suele ser la
    motivación; se saltan fórmulas, encabezados y párrafos de trámite.
    Devuelve {"parrafos": [...], "recortado": bool} o None si no hay preámbulo útil.
    """
    parrafos, recortado, secciones = [], False, 0
    lineas = [p.strip() for p in (texto or "").splitlines() if p.strip()]
    # Algunas leyes llevan un índice al principio ("Preámbulo. / Título I / Artículo 1…"):
    # se salta hasta el encabezado del preámbulo que va seguido de un párrafo de verdad.
    if any(_INDICE.match(p) for p in lineas):
        for j, p in enumerate(lineas[:-1]):
            siguiente = lineas[j + 1]
            if (_ENCABEZADO_PREAMBULO.match(p) and len(siguiente) >= MIN_CARACTERES_PARRAFO
                    and not _FIN_PREAMBULO.search(siguiente)):
                lineas = lineas[j:]
                break
    for p in lineas:
        if _FIN_PREAMBULO.search(p):
            break
        if _SECCION_ROMANA.match(p):
            secciones += 1
            if secciones > 1 and parrafos:
                recortado = True
                break
            continue
        if _ENCABEZADO.match(p) or _FORMULA.search(p) or _TRAMITE.search(p) or len(p) < MIN_CARACTERES_PARRAFO:
            continue
        if len(parrafos) == MAX_PARRAFOS_PREAMBULO or sum(map(len, parrafos)) + len(p) > MAX_CARACTERES_PREAMBULO:
            recortado = True
            break
        parrafos.append(p)
    return {"parrafos": parrafos, "recortado": recortado} if parrafos else None


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


def guardar_normas(sumario, carpeta_datos=CARPETA_DATOS):
    """Guarda las normas de la sección I que aún no estén. Devuelve cuántas añade."""
    carpeta_datos = Path(carpeta_datos)
    nuevas = 0
    for norma in normas_seccion_i(sumario):
        archivo = carpeta_datos / "normas" / f"{norma['id']}.json"
        if archivo.exists():
            continue
        xml = descargar.descargar_norma_xml(norma["id"], carpeta=carpeta_datos / "crudo" / "normas")
        escribir_json(archivo, {**norma, **metadatos_de_xml(xml), "preambulo": preambulo_de_texto(texto_de_xml(xml))})
        nuevas += 1
    return nuevas


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

    guardar_normas(sumario, carpeta_datos)
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


def revisar(carpeta_datos=CARPETA_DATOS):
    """Vuelve a leer los sumarios ya descargados y corrige recuentos y normas.

    Útil cuando se mejora la lectura del sumario (p. ej. una estructura nueva):
    no pide nada a la API salvo el XML de las normas que falten. Devuelve
    {fecha: (recuento_anterior, recuento_nuevo, normas_añadidas)} de los días cambiados.
    """
    carpeta_datos = Path(carpeta_datos)
    recuentos = leer_recuentos(carpeta_datos)
    cambios = {}
    for clave in sorted(recuentos):
        archivo = carpeta_datos / "crudo" / "sumarios" / f"{clave.replace('-', '')}.json"
        if not archivo.exists():
            continue  # sin el sumario en crudo no se puede revisar (no se vuelve a descargar)
        sumario = json.loads(archivo.read_text(encoding="utf-8"))
        nuevo = descargar.contar_por_seccion(sumario)
        anadidas = guardar_normas(sumario, carpeta_datos)
        if nuevo != recuentos[clave] or anadidas:
            cambios[clave] = (recuentos[clave], nuevo, anadidas)
            recuentos[clave] = nuevo
    escribir_json(carpeta_datos / "recuentos.json", dict(sorted(recuentos.items())))
    completar_preambulos(carpeta_datos)
    return cambios


def completar_preambulos(carpeta_datos=CARPETA_DATOS):
    """Añade el preámbulo a las normas guardadas antes de que existiera ese campo.

    Usa el XML en crudo (solo lo descarga si falta). Devuelve cuántas completa.
    """
    carpeta_datos = Path(carpeta_datos)
    completadas = 0
    for archivo in sorted((carpeta_datos / "normas").glob("*.json")):
        norma = json.loads(archivo.read_text(encoding="utf-8"))
        if "preambulo" in norma:
            continue
        xml = descargar.descargar_norma_xml(norma["id"], carpeta=carpeta_datos / "crudo" / "normas")
        norma["preambulo"] = preambulo_de_texto(texto_de_xml(xml))
        escribir_json(archivo, norma)
        completadas += 1
    return completadas


def main():
    parser = argparse.ArgumentParser(description="Descarga y guarda días del BOE.")
    parser.add_argument("desde", nargs="?", help="AAAA-MM-DD")
    parser.add_argument("hasta", nargs="?", help="AAAA-MM-DD (por defecto, igual que desde)")
    parser.add_argument("--revisar", action="store_true",
                        help="releer los sumarios ya guardados y corregir recuentos y normas")
    args = parser.parse_args()
    if args.revisar:
        cambios = revisar()
        print(f"Días corregidos: {len(cambios)}")
        for fecha, (antes, despues, anadidas) in cambios.items():
            print(f"  {fecha}: sección I {antes.get('1', 0)} -> {despues.get('1', 0)}; normas añadidas: {anadidas}")
        return
    if not args.desde:
        parser.error("indica una fecha o usa --revisar")
    desde = date.fromisoformat(args.desde)
    hasta = date.fromisoformat(args.hasta) if args.hasta else desde

    resultado = procesar_rango(desde, hasta)
    print("\nResumen:", {estado: list(resultado.values()).count(estado)
                         for estado in sorted(set(resultado.values()))})


if __name__ == "__main__":
    main()
