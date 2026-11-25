"""El dinero de los Presupuestos Generales del Estado (backlog 3.2, pieza 1: el Sankey).

Fuente: «Estadísticas de los Presupuestos Generales del Estado» de la Secretaría de Estado de
Presupuestos y Gastos (Ministerio de Hacienda), en Excel. Aviso legal de la web: «Se autoriza la
reproducción total o parcial de los contenidos del Portal, siempre que se cite expresamente su origen».

Uso (desde la raíz del proyecto):
    python -m boe.hacienda                 # edición 2025-P (los de 2023, prorrogados)
    python -m boe.hacienda --ediciones     # qué ediciones ofrece hoy la web

Qué se comprobó con los archivos reales (25/11/2026, edición «Enero 2026», 2025-P):
- El capítulo 1 de ingresos se llama «Impuestos directos» en la tabla, pero en la clasificación
  económica es «Impuestos directos y cotizaciones sociales». En el consolidado (269.000 M€) suma
  exactamente el del Estado (86.429, impuestos), las cotizaciones de la Seguridad Social (152.075) y
  el capítulo 1 de los organismos autónomos (30.497). Por eso se leen también esos tres archivos.
- Los impuestos indirectos del consolidado (57.809) son los del Estado: los demás organismos no tienen.
  Son la parte que se queda el Estado; lo cedido a comunidades y entidades locales no pasa por aquí.
- El consolidado quita lo que se pasan entre sí Estado, Seguridad Social y organismos (artículos 41 a
  43 de transferencias): no se cuenta dos veces.
- Los ingresos solo llegan al capítulo 8: la deuda nueva (capítulo 9) no aparece; lo que falta para
  cubrir los gastos de los capítulos 1 a 8 se calcula aquí como diferencia y se dice que es calculado.
- No hay edición 2026-P: la última es 2025-P (la web anuncia la «Prórroga del Presupuesto para 2026»).

Nada de personas: solo agregados por capítulo, artículo y política de gasto.
"""

import argparse
import json
import re
import unicodedata
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path
from urllib.parse import quote, urlparse

from boe.descargar import pedir

DOMINIO = "www.sepg.pap.hacienda.gob.es"
PAGINA = (f"https://{DOMINIO}/sitios/sepg/es-ES/Presupuestos/DocumentacionEstadisticas/"
          "Estadisticas/Paginas/Estadisticas.aspx")
BASE = f"https://{DOMINIO}/sitios/sepg/es-ES/Presupuestos/accesodocumentacion/DocumentacionEstadisticas/Estadisticas/Documents"
AVISO_LEGAL = f"https://{DOMINIO}/sitios/sepg/es-ES/Ayuda/Paginas/AvisoLegal.aspx"
EDICION = "2025-P"
ARCHIVOS = {
    "consolidado": "01 Presupuestos Generales del Estado Consolidados.xlsx",
    "estado": "02 Presupuestos del Estado.xlsx",
    "seguridad_social": "03 Presupuesto de la Seguridad Social.xlsx",
    "organismos": "04 Presupuesto de los Organismos Autónomos.xlsx",
}
CARPETA_CRUDO = Path("datos/crudo/hacienda")
SALIDA = Path("datos/hacienda/presupuestos.json")
CABECERAS = {"User-Agent": "boe-en-llano/0.1 (proyecto educativo)"}
LICENCIA = ("Se autoriza la reproducción total o parcial de los contenidos del Portal, siempre que se cite "
            "expresamente su origen (aviso legal de la Secretaría de Estado de Presupuestos y Gastos).")

M = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"
R = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}"

# Destinatarios de las transferencias (artículos 4x y 7x de la clasificación económica).
DESTINATARIOS = {
    "44": "Empresas y entes del sector público",
    "45": "Comunidades autónomas",
    "46": "Entidades locales",
    "47": "Empresas privadas",
    "48": "Familias e instituciones sin fines de lucro",
    "49": "Exterior",
}


def url_archivo(edicion, nombre):
    url = f"{BASE}/{quote(edicion)}/{quote(nombre)}"
    _comprobar_url(url)
    return url


def _comprobar_url(url):
    partes = urlparse(url)
    if partes.scheme != "https" or partes.hostname != DOMINIO:
        raise ValueError(f"URL fuera del dominio oficial de Hacienda: {url}")


def descargar(edicion=EDICION, carpeta=CARPETA_CRUDO, pausa=1.0):
    """Baja los XLSX de la edición a `carpeta/edicion/` (si ya están, no los vuelve a pedir)."""
    rutas = {}
    for clave, nombre in ARCHIVOS.items():
        destino = Path(carpeta) / edicion / nombre
        if not destino.exists():
            url = url_archivo(edicion, nombre)
            respuesta = pedir(url, CABECERAS, pausa=pausa)
            respuesta.raise_for_status()
            if not respuesta.content.startswith(b"PK"):
                raise ValueError(f"{nombre}: no parece un XLSX ({respuesta.headers.get('Content-Type')})")
            destino.parent.mkdir(parents=True, exist_ok=True)
            destino.write_bytes(respuesta.content)
            print(f"  descargado {nombre} ({len(respuesta.content) // 1024} KB)")
        rutas[clave] = destino
    return rutas


def ediciones(html):
    """Ediciones (p. ej. «2025-P», «2023») con Excel en la página de estadísticas."""
    encontradas = set(re.findall(r"Documents/(\d{4}(?:-P)?)/[^\"']+\.xlsx", html))
    return sorted(encontradas, key=lambda e: (e[:4], e.endswith("-P")))


# --- Lectura del XLSX sin dependencias (un .xlsx es un ZIP con XML) ---

def _columna(ref):
    return re.match(r"[A-Z]+", ref).group()


def leer_xlsx(ruta):
    """{título de la hoja (celda A4): [{columna: valor}, …]} con las filas que tienen algo."""
    with zipfile.ZipFile(ruta) as z:
        compartidas = []
        if "xl/sharedStrings.xml" in z.namelist():
            raiz = ET.fromstring(z.read("xl/sharedStrings.xml"))
            compartidas = ["".join(t.text or "" for t in si.iter(f"{M}t")) for si in raiz.findall(f"{M}si")]
        libro = ET.fromstring(z.read("xl/workbook.xml"))
        rels = {r.get("Id"): r.get("Target") for r in ET.fromstring(z.read("xl/_rels/workbook.xml.rels"))}
        hojas = {}
        for hoja in libro.find(f"{M}sheets"):
            objetivo = rels[hoja.get(f"{R}id")].lstrip("/")
            objetivo = objetivo if objetivo.startswith("xl/") else f"xl/{objetivo}"
            filas = []
            for fila in ET.fromstring(z.read(objetivo)).iter(f"{M}row"):
                celdas = {}
                for c in fila.findall(f"{M}c"):
                    v = c.find(f"{M}v")
                    if v is not None and v.text is not None:
                        celdas[_columna(c.get("r"))] = compartidas[int(v.text)] if c.get("t") == "s" else v.text
                    elif c.find(f"{M}is/{M}t") is not None:
                        celdas[_columna(c.get("r"))] = c.find(f"{M}is/{M}t").text
                if celdas:
                    filas.append(celdas)
            titulo = next((f["A"].strip() for f in filas if re.match(r"\d+(\.\d+)*\. ", f.get("A", "").strip())), hoja.get("name"))
            hojas[titulo] = filas
    return hojas


def _sin_tildes(texto):
    return "".join(c for c in unicodedata.normalize("NFD", texto) if unicodedata.category(c) != "Mn").lower()


def tabla(hojas, titulo):
    """Primera tabla de la hoja cuyo título contiene `titulo`: (años, {fila: {año: millones}}).

    La cabecera es la fila con años («2023», «2023-P»…); se para en «Fuente:» (algunas hojas
    traen debajo otra tabla antigua, en pesetas).
    """
    buscado = _sin_tildes(titulo)
    nombre = next((t for t in hojas if buscado in _sin_tildes(t)), None)
    if nombre is None:
        raise KeyError(f"No hay hoja «{titulo}»: {list(hojas)}")
    años, filas, dentro = {}, {}, False
    for fila in hojas[nombre]:
        valores = {c: str(v).strip() for c, v in fila.items() if c != "A"}
        if not dentro:
            if valores and all(re.fullmatch(r"\d{4}(-P)?", v) for v in valores.values()):
                años, dentro = valores, True
            continue
        etiqueta = str(fila.get("A", "")).strip()
        if etiqueta.startswith("Fuente"):
            break
        if etiqueta:
            filas[etiqueta] = {años[c]: round(float(v), 2) for c, v in valores.items() if c in años}
    if not años:
        raise ValueError(f"Hoja «{nombre}» sin fila de años")
    return list(años.values()), filas


def _fila(filas, empieza):
    buscado = _sin_tildes(empieza)
    for etiqueta, valores in filas.items():
        if _sin_tildes(etiqueta).startswith(buscado):
            return valores
    raise KeyError(f"No hay fila «{empieza}»: {list(filas)}")


def _articulos(filas, capital=False):
    """{"45": {año: v}, …} a partir de etiquetas como «45 y 75 Comunidades Autónomas» o «75 …».

    Los de capital (7x) se guardan con la clave del corriente (4x) para que casen.
    """
    salida = {}
    for etiqueta, valores in filas.items():
        m = re.match(r"([47])(\d)\b", etiqueta)
        if m and m.group(1) == ("7" if capital else "4") and f"4{m.group(2)}" in DESTINATARIOS:
            salida[f"4{m.group(2)}"] = valores
    return salida


def _cerca(a, b, margen=1.0):
    return abs(a - b) <= margen


def construir(rutas, edicion=EDICION):
    """Datos para la web a partir de los XLSX ya descargados (sin red)."""
    cons = leer_xlsx(rutas["consolidado"])
    años, ingresos = tabla(cons, "Ingresos. Clasificación económica")
    _, gastos = tabla(cons, "Gastos. Clasificación económica")
    _, politicas = tabla(cons, "Políticas de gasto")
    _, transf = tabla(cons, "Total transferencias por artículos")
    _, transf_c = tabla(cons, "Transferencias corrientes por artículos")
    _, transf_k = tabla(cons, "Transferencias de capital por artículos")
    _, ing_estado = tabla(leer_xlsx(rutas["estado"]), "Ingresos. Clasificación económica")
    _, ing_ss = tabla(leer_xlsx(rutas["seguridad_social"]), "Ingresos. Clasificación económica")
    _, ing_oa = tabla(leer_xlsx(rutas["organismos"]), "Ingresos. Clasificación económica")

    avisos = []
    cap1 = {
        "consolidado": _fila(ingresos, "Impuestos directos"),
        "estado_impuestos": _fila(ing_estado, "Impuestos directos"),
        "seguridad_social_cotizaciones": _fila(ing_ss, "Cotizaciones sociales"),
        "organismos_capitulo1": _fila(ing_oa, "Impuestos directos"),
    }
    for año in años:
        suma = sum(cap1[k].get(año, 0) for k in ("estado_impuestos", "seguridad_social_cotizaciones", "organismos_capitulo1"))
        if not _cerca(suma, cap1["consolidado"].get(año, 0)):
            avisos.append(f"{año}: el capítulo 1 consolidado ({cap1['consolidado'].get(año)}) no es la suma de sus partes ({suma:.2f})")
    for año in años:
        if not _cerca(_fila(ingresos, "Impuestos indirectos").get(año, 0), _fila(ing_estado, "Impuestos indirectos").get(año, 0)):
            avisos.append(f"{año}: los impuestos indirectos consolidados no son solo los del Estado")
        total_pol = _fila(politicas, "CAPÍTULOS 1 a 8").get(año, 0)
        gastos_1a8 = _fila(gastos, "TOTAL PRESUPUESTO").get(año, 0) - _fila(gastos, "Pasivos financieros").get(año, 0)
        if not _cerca(total_pol, gastos_1a8, margen=10):
            avisos.append(f"{año}: las políticas ({total_pol}) no suman los gastos de los capítulos 1 a 8 ({gastos_1a8:.2f})")
        total_tr = _fila(transf, "TOTAL TRANSFERENCIAS").get(año, 0)
        cap47 = _fila(gastos, "Transferencias corrientes").get(año, 0) + _fila(gastos, "Transferencias de capital").get(año, 0)
        if not _cerca(total_tr, cap47, margen=10):
            avisos.append(f"{año}: las transferencias por artículos ({total_tr}) no suman los capítulos 4 y 7 ({cap47:.2f})")

    deuda = {}
    for año in años:
        gastos_1a8 = _fila(gastos, "TOTAL PRESUPUESTO").get(año, 0) - _fila(gastos, "Pasivos financieros").get(año, 0)
        deuda[año] = round(gastos_1a8 - _fila(ingresos, "TOTAL CAPÍTULOS 1 a 8").get(año, 0), 2)

    return {
        "fuente": {
            "organismo": "Secretaría de Estado de Presupuestos y Gastos (Ministerio de Hacienda)",
            "publicacion": "Estadísticas de los Presupuestos Generales del Estado",
            "pagina": PAGINA,
            "archivos": {k: url_archivo(edicion, n) for k, n in ARCHIVOS.items()},
            "licencia": LICENCIA,
            "aviso_legal": AVISO_LEGAL,
        },
        "edicion": edicion,
        "prorrogado": edicion.endswith("-P"),
        "unidad": "millones de euros",
        "nota": ("Cifras presupuestadas (no ejecutadas), consolidadas: Estado, Seguridad Social, organismos "
                 "autónomos y resto de entidades con presupuesto limitativo, sin las transferencias entre ellos. "
                 "«-P» = presupuesto prorrogado: en 2024, 2025 y 2026 rigen los de 2023."),
        "años": años,
        "ingresos": ingresos,
        "capitulo1_ingresos": cap1,
        "deuda_calculada": deuda,
        "gastos": gastos,
        "politicas": politicas,
        "transferencias": {
            "destinatarios": DESTINATARIOS,
            "total": _articulos(transf),
            "corrientes": _articulos(transf_c),
            "capital": _articulos(transf_k, capital=True),
        },
        "avisos": avisos,
    }


def procesar(edicion=EDICION, carpeta=CARPETA_CRUDO, salida=SALIDA):
    datos = construir(descargar(edicion, carpeta), edicion)
    salida = Path(salida)
    salida.parent.mkdir(parents=True, exist_ok=True)
    salida.write_text(json.dumps(datos, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    return datos


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--edicion", default=EDICION)
    parser.add_argument("--ediciones", action="store_true", help="lista las ediciones con Excel de la web")
    args = parser.parse_args()
    if args.ediciones:
        print(", ".join(ediciones(pedir(PAGINA, CABECERAS).text)))
        return
    datos = procesar(args.edicion)
    año = args.edicion
    ing = datos["ingresos"]
    print(f"Edición {año} ({'prorrogado' if datos['prorrogado'] else 'aprobado'}), millones de euros:")
    print(f"  ingresos capítulos 1 a 8: {ing['TOTAL CAPÍTULOS 1 a 8'][año]:,.0f}; deuda calculada: {datos['deuda_calculada'][año]:,.0f}")
    for k, v in datos["capitulo1_ingresos"].items():
        print(f"  capítulo 1 · {k}: {v[año]:,.0f}")
    for art, v in datos["transferencias"]["total"].items():
        print(f"  transferencias {art} {DESTINATARIOS[art]}: {v[año]:,.0f}")
    print(f"  avisos: {datos['avisos'] or 'ninguno'} → {SALIDA}")


if __name__ == "__main__":
    main()
