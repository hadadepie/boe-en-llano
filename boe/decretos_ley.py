"""De qué trata cada real decreto-ley de la legislatura y cuántas normas modifica.

Uso:
    python -m boe.decretos_ley            # completa lo que falte
    python -m boe.decretos_ley --rehacer  # vuelve a calcularlo todo (usa lo guardado)

Parte de la lista de boe.legislatura (número, resultado y votos). Para cada
real decreto-ley se lee su DOCUMENTO OFICIAL en el BOE, tal como se publicó,
por su dirección ELI (https://www.boe.es/eli/es/rdl/AAAA/MM/DD/N/dof/spa/xml).
Es la misma fuente para todos: la legislación consolidada no incluye muchos
decretos-ley (sobre todo los que solo modifican otras normas).

La dirección ELI necesita la fecha del decreto-ley, que se toma de:
1. la búsqueda de legislación consolidada del BOE (si lo tiene);
2. el título completo en los índices de votaciones del Congreso ya guardados
   («Real Decreto-ley 2/2025, de 18 de marzo, por el que…»);
3. los títulos de nuestras normas guardadas (el propio decreto-ley o la
   resolución que publica su convalidación).

Del documento se calcula:
- `normas_modificadas`: cuántas normas DISTINTAS cambia según su propio análisis
  (relaciones «modifica», «añade», «deroga», «prorroga»…). Mide el tamaño del
  decreto-ley (lo que en el debate público se llama «ómnibus»), no su importancia.
- `tema`: el tema de la web con las reglas de boe.clasificar (título y materias).
- `temas_materias`: temas a los que apuntan al menos MIN_MATERIAS_TEMA materias.
  Con MIN_TEMAS_VARIOS o más, se muestra «Varios temas» en vez de forzar uno.

Todo se guarda en datos/crudo/decretos_ley/ y no se vuelve a pedir. El resultado
va a datos/congreso/decretos_ley_xv.json (aparte de las votaciones).
"""

import argparse
import json
import re
import time
import xml.etree.ElementTree as ET
from datetime import date
from pathlib import Path

import requests

from boe import consolidada
from boe.clasificar import PALABRAS_TEMA, TEMAS, _contiene, clasificar_tema, normalizar

CARPETA_DATOS = Path("datos")
URL_BUSQUEDA = "https://www.boe.es/datosabiertos/api/legislacion-consolidada"
URL_ELI = "https://www.boe.es/eli/es/rdl/{a}/{m:02d}/{d:02d}/{n}/dof/spa/xml"
PAUSA_SEGUNDOS = 1.0
MIN_MATERIAS_TEMA = 3
MIN_TEMAS_VARIOS = 3
VARIOS_TEMAS = "Varios temas"
MESES = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto",
         "septiembre", "octubre", "noviembre", "diciembre"]


def _crudo(carpeta_datos):
    return Path(carpeta_datos) / "crudo" / "decretos_ley"


def _pedir(url, archivo, pausa, accept="application/json"):
    """Respuesta guardada o pedida (una sola vez). None si el BOE responde 404."""
    if archivo.exists():
        return archivo.read_bytes() or None
    respuesta = requests.get(url, headers={**consolidada.CABECERAS, "Accept": accept}, timeout=30)
    time.sleep(pausa)
    archivo.parent.mkdir(parents=True, exist_ok=True)
    if respuesta.status_code == 404:
        archivo.write_bytes(b"")
        return None
    respuesta.raise_for_status()
    archivo.write_bytes(respuesta.content)
    return respuesta.content


# ---------- Fecha del decreto-ley ----------

def _patron_fecha(rdl):
    return re.compile(rf"Real Decreto-ley {re.escape(rdl)}, de (\d{{1,2}}) de ({'|'.join(MESES)})", re.IGNORECASE)


def fecha_por_busqueda(rdl, carpeta_datos=CARPETA_DATOS, pausa=PAUSA_SEGUNDOS):
    n, a = rdl.split("/")
    consulta = {"query": {"query_string": {"query": f'titulo:"Real Decreto-ley {rdl}"'}}}
    url = requests.Request("GET", URL_BUSQUEDA, params={"query": json.dumps(consulta), "limit": 10}).prepare().url
    contenido = _pedir(url, _crudo(carpeta_datos) / f"busqueda_{a}_{int(n):03d}.json", pausa)
    datos = json.loads(contenido) if contenido else {}
    for d in consolidada._lista(datos.get("data")):
        if isinstance(d, dict) and (d.get("rango") or {}).get("texto") == "Real Decreto-ley" and d.get("numero_oficial") == rdl:
            f = d.get("fecha_disposicion") or ""
            return date(int(f[:4]), int(f[4:6]), int(f[6:8])) if len(f) >= 8 else None
    return None


def fecha_en_textos(rdl, textos):
    """Fecha del decreto-ley a partir de un título completo en alguno de los textos."""
    patron = _patron_fecha(rdl)
    anio = int(rdl.split("/")[1])
    for texto in textos:
        m = patron.search(re.sub(r"\s+", " ", texto))
        if m:
            return date(anio, MESES.index(m.group(2).lower()) + 1, int(m.group(1)))
    return None


def _textos_indices(carpeta_datos):
    for archivo in sorted((Path(carpeta_datos) / "crudo" / "congreso" / "indices").glob("*.html")):
        yield re.sub(r"<[^>]+>", " ", archivo.read_text(encoding="utf-8", errors="replace"))


def _titulos_normas(carpeta_datos):
    for archivo in (Path(carpeta_datos) / "normas").glob("*.json"):
        yield json.loads(archivo.read_text(encoding="utf-8")).get("titulo") or ""


def fecha_de(rdl, carpeta_datos=CARPETA_DATOS, pausa=PAUSA_SEGUNDOS):
    return (fecha_por_busqueda(rdl, carpeta_datos, pausa)
            or fecha_en_textos(rdl, _textos_indices(carpeta_datos))
            or fecha_en_textos(rdl, _titulos_normas(carpeta_datos)))


# ---------- Documento oficial ----------

def documento(rdl, fecha, carpeta_datos=CARPETA_DATOS, pausa=PAUSA_SEGUNDOS):
    n, a = rdl.split("/")
    url = URL_ELI.format(a=fecha.year, m=fecha.month, d=fecha.day, n=int(n))
    contenido = _pedir(url, _crudo(carpeta_datos) / f"documento_{a}_{int(n):03d}.xml", pausa, "application/xml")
    return ET.fromstring(contenido) if contenido else None


def normas_modificadas(raiz):
    """Normas distintas que cambia según su propio análisis."""
    ids = {a.get("referencia") or a.findtext("texto")
           for a in raiz.findall("analisis/referencias/anteriores/anterior")
           if (a.findtext("palabra") or "").strip().upper().startswith(consolidada.CAMBIOS)}
    return len(ids)


def temas_de_materias(materias):
    """Temas de la web a los que apuntan al menos MIN_MATERIAS_TEMA materias (en el orden de TEMAS)."""
    normalizadas = [normalizar(m) for m in materias]
    return [t for t in TEMAS
            if sum(1 for m in normalizadas if any(_contiene(m, p) for p in PALABRAS_TEMA.get(t, []))) >= MIN_MATERIAS_TEMA]


def ficha(rdl, carpeta_datos=CARPETA_DATOS, pausa=PAUSA_SEGUNDOS):
    fecha = fecha_de(rdl, carpeta_datos, pausa)
    raiz = documento(rdl, fecha, carpeta_datos, pausa) if fecha else None
    if raiz is None:
        return {"rdl": rdl, "encontrado": False, "fecha": fecha.isoformat() if fecha else None}
    titulo = (raiz.findtext("metadatos/titulo") or "").strip()
    materias = [m.text.strip() for m in raiz.findall("analisis/materias/materia") if m.text and m.text.strip()]
    tema, motivos = clasificar_tema({"titulo": titulo, "materias": materias})
    temas_materias = temas_de_materias(materias)
    publicacion = raiz.findtext("metadatos/fecha_publicacion") or ""
    return {
        "rdl": rdl, "encontrado": True, "id_boe": raiz.findtext("metadatos/identificador"),
        "titulo": titulo, "fecha": fecha.isoformat(),
        "fecha_publicacion": f"{publicacion[:4]}-{publicacion[4:6]}-{publicacion[6:8]}" if len(publicacion) >= 8 else None,
        "materias": materias, "normas_modificadas": normas_modificadas(raiz),
        "tema": VARIOS_TEMAS if len(temas_materias) >= MIN_TEMAS_VARIOS else tema,
        "tema_reglas": tema, "motivos_tema": motivos, "temas_materias": temas_materias,
    }


def procesar(carpeta_datos=CARPETA_DATOS, hoy=None, rehacer=False, pausa=PAUSA_SEGUNDOS):
    hoy = hoy or date.today()
    legislatura = Path(carpeta_datos) / "congreso" / "legislatura_xv.json"
    if not legislatura.exists():
        return None
    lista = json.loads(legislatura.read_text(encoding="utf-8"))["decretos_ley"]
    salida = Path(carpeta_datos) / "congreso" / "decretos_ley_xv.json"
    previo = json.loads(salida.read_text(encoding="utf-8")) if salida.exists() and not rehacer else {}
    decretos = dict(previo.get("decretos") or {})
    pendientes = [x["rdl"] for x in lista if not (decretos.get(x["rdl"]) or {}).get("encontrado")]
    if not pendientes and previo:
        return previo
    for rdl in pendientes:
        decretos[rdl] = ficha(rdl, carpeta_datos, pausa)
    resultado = {
        "consultado": hoy.isoformat(),
        "fuente": "https://www.boe.es/eli/es/rdl/",
        "nota": ("Título, materias y normas modificadas según el documento oficial de cada real decreto-ley en el BOE "
                 "(su análisis en el momento de publicarse). «Normas modificadas» cuenta normas distintas con relación "
                 "expresa (modifica, añade, deroga, prorroga…): mide el tamaño del decreto-ley, no su importancia."),
        "decretos": dict(sorted(decretos.items(), key=lambda kv: tuple(int(p) for p in kv[0].split("/")[::-1]))),
    }
    salida.parent.mkdir(parents=True, exist_ok=True)
    salida.write_text(json.dumps(resultado, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return resultado


def main():
    parser = argparse.ArgumentParser(description="Tema y tamaño de los reales decretos-ley de la legislatura.")
    parser.add_argument("--rehacer", action="store_true", help="recalcular todo (usa las respuestas guardadas)")
    r = procesar(rehacer=parser.parse_args().rehacer)
    if not r:
        print("Falta datos/congreso/legislatura_xv.json: ejecuta antes python -m boe.legislatura.")
        return
    d = list(r["decretos"].values())
    print(f"{len(d)} decretos-ley · {sum(1 for x in d if x.get('encontrado'))} leídos del BOE")
    for x in d:
        if not x.get("encontrado"):
            print(f"  sin documento: {x['rdl']} (fecha: {x.get('fecha')})")


if __name__ == "__main__":
    main()
