"""Votaciones del Congreso sobre los reales decretos-ley (convalidación).

Uso:
    python -m boe.congreso                     # todos los reales decretos-ley guardados
    python -m boe.congreso --desde 2026-09-01  # solo los publicados desde esa fecha

Qué hace: para cada real decreto-ley de datos/normas busca, en los datos abiertos
del Congreso, la votación del Pleno que lo convalidó o derogó (el Congreso tiene
30 días desde su publicación) y, si existe, la votación sobre tramitarlo como
proyecto de ley. Guarda en datos/congreso/convalidaciones.json:
  - los totales oficiales y el resultado (convalidado / derogado);
  - el voto AGREGADO por grupo parlamentario y por lista electoral dentro de
    cada grupo, y cuántos votos fueron telemáticos.

Decisiones (ver CLAUDE.md):
  - No se versiona el voto de cada diputado: queda solo en datos/crudo/ (los
    ficheros oficiales tal cual). Lo publicado es siempre agregado.
  - El voto telemático cuenta como voto emitido.
  - La lista electoral sale del dato oficial FORMACIONELECTORAL del Congreso;
    no distingue partidos dentro de una coalición (p. ej. dentro de SUMAR).

Fuente: https://www.congreso.es/es/opendata/votaciones (índice por fecha, con
un JSON por votación) y https://www.congreso.es/es/opendata/diputados.
Las votaciones de la Diputación Permanente (con las Cortes disueltas) no están
en los datos abiertos: esos reales decretos-ley quedan "sin datos".
"""

import argparse
import json
import re
import time
from collections import Counter, defaultdict
from datetime import date, timedelta
from html import unescape
from pathlib import Path

import requests

from boe.clasificar import normalizar

BASE = "https://www.congreso.es"
URL_INDICE = (BASE + "/es/opendata/votaciones?p_p_id=votaciones&p_p_lifecycle=0&p_p_state=normal"
              "&p_p_mode=view&targetLegislatura={legislatura}&targetDate={dia:02d}%2F{mes:02d}%2F{anio}")
URL_DIPUTADOS = BASE + "/es/opendata/diputados"
CARPETA_DATOS = Path("datos")
PAUSA_SEGUNDOS = 1.0
CABECERAS = {"User-Agent": "boe-en-llano/0.1 (proyecto educativo)"}
DIAS_PLAZO = 60  # el plazo de 30 días es en días hábiles: agosto y festivos no cuentan (RDL 9/2025, publicado el 30/07, votado el 09/09)
LEGISLATURA = "XV"
ASIENTO_TELEMATICO = "-1"  # así marca el Congreso el voto telemático

_RE_JSON = re.compile(r"/webpublica/opendata/votaciones/Leg\d+/Sesion\d+/\d{8}/Votacion\d+/VOT_\d+\.json")
_RE_RDL = re.compile(r"real decreto-ley (\d+)/(\d{4})")


# ---------- Descargas (con caché en datos/crudo/congreso) ----------

def _get(url, archivo, cachear=True, binario=False):
    archivo = Path(archivo)
    if cachear and archivo.exists():
        return archivo.read_bytes() if binario else archivo.read_text(encoding="utf-8")
    respuesta = requests.get(url, headers=CABECERAS, timeout=30)
    time.sleep(PAUSA_SEGUNDOS)
    respuesta.raise_for_status()
    archivo.parent.mkdir(parents=True, exist_ok=True)
    if binario:
        archivo.write_bytes(respuesta.content)
        return respuesta.content
    # Los JSON del Congreso son UTF-8 (con escapes \u); en el HTML solo usamos enlaces.
    texto = respuesta.content.decode("utf-8", errors="replace")
    if cachear:
        archivo.write_text(texto, encoding="utf-8")
    return texto


def indice_del_dia(dia, carpeta_datos=CARPETA_DATOS, hoy=None):
    """HTML del índice de votaciones de un día. Los días ya pasados se guardan."""
    hoy = hoy or date.today()
    archivo = Path(carpeta_datos) / "crudo" / "congreso" / "indices" / f"{dia:%Y%m%d}.html"
    url = URL_INDICE.format(legislatura=LEGISLATURA, dia=dia.day, mes=dia.month, anio=dia.year)
    return _get(url, archivo, cachear=dia < hoy)


def enlaces_votaciones(html):
    """Rutas de los JSON de cada votación que aparecen en un índice (sin repetir)."""
    return list(dict.fromkeys(_RE_JSON.findall(html or "")))


def _menciona_rdl(html, ruta_json, rdl, ventana=3000):
    """¿El texto del índice justo antes del enlace menciona ese real decreto-ley?

    Es un filtro previo para no descargar todas las votaciones del día; la
    comprobación definitiva se hace después con el JSON oficial.
    """
    pos = (html or "").find(ruta_json)
    if pos < 0:
        return True
    numero = re.escape(rdl or "")
    return re.search(rf"Decreto-ley\s+{numero}\b", html[max(0, pos - ventana):pos], re.IGNORECASE) is not None


def _texto_visible(html):
    html = re.sub(r"<script.*?</script>|<style.*?</style>", " ", html or "", flags=re.S)
    return re.sub(r"\s+", " ", unescape(re.sub(r"<[^>]+>", " ", html)))


_RE_TOTALES = re.compile(r"Si:\s*(\d+)\s*No:\s*(\d+)\s*Abstenciones:\s*(\d+)")


def totales_del_indice(html, rdl):
    """Totales de la convalidación de `rdl` leídos del texto del índice.

    Para votaciones sin fichero JSON (p. ej. las públicas por llamamiento, en las
    que cada diputado vota de viva voz, el Congreso solo publica una imagen).
    Devuelve {"afavor", "enContra", "abstenciones", "llamamiento"} o None.
    """
    texto = _texto_visible(html)
    for m in re.finditer(rf"Real Decreto-ley\s+{re.escape(rdl)}\b", texto):
        if "tramitación como proyecto de ley" in texto[max(0, m.start() - 120):m.start()].lower():
            continue  # es la votación de tramitación, no la de convalidación
        tramo = texto[m.end():m.end() + 900]
        t = _RE_TOTALES.search(tramo)
        if not t or "Real Decreto-ley" in tramo[:t.start()]:
            continue  # los totales que siguen son de otra votación
        return {"afavor": int(t.group(1)), "enContra": int(t.group(2)), "abstenciones": int(t.group(3)),
                "llamamiento": "por llamamiento" in tramo[:t.start()].lower()}
    return None


def pdf_de(html, ruta_json):
    """Ruta del PDF oficial de la misma votación (está en la misma carpeta)."""
    carpeta = ruta_json.rsplit("/", 1)[0]
    m = re.search(re.escape(carpeta) + r"/VOT_\d+\.pdf", html or "")
    return m.group(0) if m else None


def votacion(ruta, carpeta_datos=CARPETA_DATOS):
    """JSON oficial de una votación (se guarda en crudo)."""
    nombre = "_".join(ruta.split("/")[-5:-1]) + ".json"  # Leg15_Sesion198_20260916_Votacion016.json
    archivo = Path(carpeta_datos) / "crudo" / "congreso" / "votaciones" / nombre
    return json.loads(_get(BASE + ruta, archivo))


def listas_electorales(carpeta_datos=CARPETA_DATOS):
    """{nombre del diputado: (lista electoral, grupo parlamentario)} de la legislatura.

    Junta los diputados en activo y los de baja (con las Cortes disueltas, casi
    todos están "de baja"). Los enlaces llevan una marca de fecha, así que se
    sacan de la página de datos abiertos.
    """
    carpeta = Path(carpeta_datos) / "crudo" / "congreso" / "diputados"
    pagina = _get(URL_DIPUTADOS, carpeta / f"pagina_{date.today():%Y%m%d}.html")
    resultado = {}
    for clave in ("DiputadosDeBaja", "DiputadosActivos"):  # los activos, al final, mandan
        enlace = re.search(rf"/webpublica/opendata/diputados/{clave}__\d+\.json", pagina)
        if not enlace:
            raise RuntimeError(f"No se encuentra el fichero {clave} en {URL_DIPUTADOS}")
        datos = json.loads(_get(BASE + enlace.group(0), carpeta / f"{clave}_{date.today():%Y%m%d}.json"))
        filas = datos if isinstance(datos, list) else next(v for v in datos.values() if isinstance(v, list))
        for f in filas:
            resultado[f["NOMBRE"]] = (f.get("FORMACIONELECTORAL"), f.get("GRUPOPARLAMENTARIO"))
    return resultado


# ---------- Lectura de una votación ----------

def rdl_de_texto(texto):
    """'Real Decreto-ley 21/2026, de 25 de agosto…' -> '21/2026' (o None)."""
    m = _RE_RDL.search(normalizar(texto))
    return f"{m.group(1)}/{m.group(2)}" if m else None


def tipo_de_votacion(info):
    """'convalidacion', 'tramitacion' o None, según el título y el expediente."""
    titulo = normalizar(info.get("titulo"))
    expediente = normalizar(info.get("textoExpediente"))
    if "convalidacion o derogacion" not in titulo:
        return None
    if expediente.startswith("tramitacion como proyecto de ley"):
        return "tramitacion"
    if expediente.startswith("real decreto-ley"):
        return "convalidacion"
    return None


def resultado_de(totales, tipo):
    si, no = totales.get("afavor", 0), totales.get("enContra", 0)
    if tipo == "convalidacion":
        return "convalidado" if si > no else "derogado"
    return "se tramita como proyecto de ley" if si > no else "no se tramita como proyecto de ley"


def resumir_votacion(datos, listas):
    """Totales oficiales y voto AGREGADO por grupo y por lista electoral."""
    por_grupo = defaultdict(Counter)
    por_lista = defaultdict(lambda: defaultdict(Counter))
    nombres_grupo = defaultdict(Counter)
    telematicos = 0
    sin_lista = 0
    for fila in datos["votaciones"]:
        grupo, voto = fila["grupo"], fila["voto"]
        por_grupo[grupo][voto] += 1
        if str(fila.get("asiento")) == ASIENTO_TELEMATICO:
            telematicos += 1
        lista, nombre_grupo = listas.get(fila["diputado"], (None, None))
        if lista is None:
            sin_lista += 1
            lista = "Sin dato"
        por_lista[grupo][lista][voto] += 1
        if nombre_grupo:
            nombres_grupo[grupo][nombre_grupo] += 1
    return {
        "totales": datos["totales"],
        "telematicos": telematicos,
        "por_grupo": {g: dict(c) for g, c in sorted(por_grupo.items(), key=lambda kv: -sum(kv[1].values()))},
        "por_lista": {g: {l: dict(c) for l, c in listas_g.items()} for g, listas_g in por_lista.items()},
        "nombres_grupo": {g: c.most_common(1)[0][0] for g, c in nombres_grupo.items()},
        "diputados_sin_lista": sin_lista,
    }


# ---------- Búsqueda de la convalidación de un real decreto-ley ----------

def buscar_votaciones(rdl, publicado, carpeta_datos=CARPETA_DATOS, hoy=None, dias=DIAS_PLAZO):
    """Busca las votaciones del Pleno sobre `rdl` ('21/2026') en los días siguientes a su publicación."""
    hoy = hoy or date.today()
    encontradas = {}
    dia = publicado + timedelta(days=1)
    while dia <= min(publicado + timedelta(days=dias), hoy) and "convalidacion" not in encontradas:
        if dia.isoweekday() <= 5:  # el Pleno vota de lunes a viernes
            html = indice_del_dia(dia, carpeta_datos, hoy)
            for ruta in enlaces_votaciones(html):
                if not _menciona_rdl(html, ruta, rdl):
                    continue  # ahorra descargar las votaciones de otros asuntos
                datos = votacion(ruta, carpeta_datos)
                info = datos.get("informacion", {})
                tipo = tipo_de_votacion(info)
                if tipo and rdl_de_texto(info.get("textoExpediente")) == rdl:
                    encontradas[tipo] = {"fecha": dia.isoformat(), "ruta_json": ruta, "ruta_pdf": pdf_de(html, ruta),
                                         "info": info, "datos": datos}
            if "convalidacion" not in encontradas:
                totales = totales_del_indice(html, rdl)
                if totales:  # votación sin fichero de detalle: solo totales
                    encontradas["convalidacion"] = {"fecha": dia.isoformat(), "solo_totales": totales,
                                                    "fuente_indice": URL_INDICE.format(legislatura=LEGISLATURA,
                                                                                       dia=dia.day, mes=dia.month, anio=dia.year)}
        dia += timedelta(days=1)
    return encontradas


def convalidacion_de(norma, listas, carpeta_datos=CARPETA_DATOS, hoy=None):
    """Registro publicable sobre la convalidación de un real decreto-ley."""
    rdl = norma.get("numero_oficial") or rdl_de_texto(norma.get("titulo"))
    publicado = date.fromisoformat(norma["fecha_publicacion"])
    registro = {"id": norma["id"], "rdl": rdl, "titulo": norma["titulo"], "publicado": publicado.isoformat()}
    encontradas = buscar_votaciones(rdl, publicado, carpeta_datos, hoy)
    if "convalidacion" not in encontradas:
        plazo_abierto = (hoy or date.today()) <= publicado + timedelta(days=30)
        registro["estado"] = "pendiente de votación" if plazo_abierto else "sin datos"
        registro["nota"] = ("Aún dentro del plazo de 30 días." if plazo_abierto else
                            "No aparece en los datos abiertos de votaciones del Pleno en los 60 días siguientes a su "
                            "publicación. Si las Cortes estaban disueltas, la habrá votado la Diputación Permanente, "
                            "cuyas votaciones no se publican ahí.")
        return registro
    for tipo, v in encontradas.items():
        if v.get("solo_totales"):
            t = v["solo_totales"]
            totales = {"afavor": t["afavor"], "enContra": t["enContra"], "abstenciones": t["abstenciones"], "noVotan": None}
            registro[tipo] = {
                "fecha": v["fecha"], "resultado": resultado_de(totales, tipo), "totales": totales,
                "telematicos": None, "por_grupo": {}, "por_lista": {}, "nombres_grupo": {},
                "solo_totales": True, "fuente": v["fuente_indice"], "fuente_pdf": None,
                "nota": ("Votación pública por llamamiento (cada diputado votó de viva voz). " if t["llamamiento"] else "")
                        + "El Congreso solo ha publicado los totales en sus datos abiertos, sin el voto por grupos.",
            }
            continue
        info = v["info"]
        registro[tipo] = {
            "fecha": v["fecha"],
            "sesion": info.get("sesion"),
            "numero_votacion": info.get("numeroVotacion"),
            "resultado": resultado_de(v["datos"]["totales"], tipo),
            "fuente": BASE + v["ruta_json"],
            "fuente_pdf": BASE + v["ruta_pdf"] if v.get("ruta_pdf") else None,
            **resumir_votacion(v["datos"], listas),
        }
    registro["estado"] = registro["convalidacion"]["resultado"]
    return registro


def procesar(carpeta_datos=CARPETA_DATOS, desde=None, hoy=None):
    carpeta_datos = Path(carpeta_datos)
    rdls = []
    for archivo in sorted((carpeta_datos / "normas").glob("*.json")):
        n = json.loads(archivo.read_text(encoding="utf-8"))
        if n.get("rango") == "Real Decreto-ley" and (not desde or n["fecha_publicacion"] >= desde.isoformat()):
            rdls.append(n)
    if not rdls:
        print("No hay reales decretos-ley en datos/normas para ese periodo.")
        return {}
    listas = listas_electorales(carpeta_datos)
    salida_archivo = carpeta_datos / "congreso" / "convalidaciones.json"
    previas = json.loads(salida_archivo.read_text(encoding="utf-8")) if salida_archivo.exists() else {}
    for n in rdls:
        previa = previas.get(n["id"], {})
        if previa.get("estado") in ("convalidado", "derogado"):
            continue  # ya resuelto: no se vuelve a buscar
        print(f"  {n['id']} (RDL {n.get('numero_oficial')}): buscando votación…")
        previas[n["id"]] = convalidacion_de(n, listas, carpeta_datos, hoy)
        print(f"    -> {previas[n['id']]['estado']}")
    salida_archivo.parent.mkdir(parents=True, exist_ok=True)
    salida_archivo.write_text(json.dumps(dict(sorted(previas.items())), ensure_ascii=False, indent=2) + "\n",
                              encoding="utf-8")
    return previas


def main():
    parser = argparse.ArgumentParser(description="Votaciones de convalidación de los reales decretos-ley.")
    parser.add_argument("--desde", help="AAAA-MM-DD: solo reales decretos-ley publicados desde esa fecha")
    args = parser.parse_args()
    resultado = procesar(desde=date.fromisoformat(args.desde) if args.desde else None)
    estados = Counter(r["estado"] for r in resultado.values())
    print("\nResumen:", dict(estados))


if __name__ == "__main__":
    main()
