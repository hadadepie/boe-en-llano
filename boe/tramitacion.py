"""Tramitación parlamentaria de los reales decretos-ley tramitados como proyecto de ley.

Uso:
    python -m boe.tramitacion      # añade "tramitacion" a los reales decretos-ley de datos/normas

Cuando el Congreso convalida un real decreto-ley puede acordar tramitarlo como
proyecto de ley (para poder enmendarlo). Esa tramitación aparece en los datos
abiertos de iniciativas del Congreso (fichero "ProyectosDeLey", JSON), con:
  - OBJETO: "… (procedente del Real Decreto-ley 22/2026, de 1 de septiembre)";
  - TRAMITACIONSEGUIDA: los pasos con sus fechas;
  - RESULTADOTRAMITACION: "Caducado 04/11/2026", "Aprobado…", etc.;
  - ENLACESBOCG: el Boletín Oficial de las Cortes (texto y enmiendas).

El enlace al fichero lleva una marca de fecha, así que se saca de la página de
datos abiertos. El fichero se guarda en datos/crudo/congreso/iniciativas/ y se
renueva cada día que se ejecuta.
"""

import argparse
import json
import re
import time
from datetime import date
from pathlib import Path

import requests

BASE = "https://www.congreso.es"
URL_INICIATIVAS = BASE + "/es/opendata/iniciativas"
CARPETA_DATOS = Path("datos")
CABECERAS = {"User-Agent": "boe-en-llano/0.1 (proyecto educativo)"}
PAUSA_SEGUNDOS = 1.0
_RE_RDL = re.compile(r"Real\s+Decreto-ley\s+(\d+/\d{4})")
_RE_FECHAS = re.compile(r"^desde\s+(\d{2}/\d{2}/\d{4})(?:\s+hasta\s+(\d{2}/\d{2}/\d{4}))?", re.IGNORECASE)
_RE_FECHA = re.compile(r"(\d{2})/(\d{2})/(\d{4})")


def _get(url, archivo=None):
    if archivo is not None and Path(archivo).exists():
        return Path(archivo).read_text(encoding="utf-8")
    respuesta = requests.get(url, headers=CABECERAS, timeout=60)
    time.sleep(PAUSA_SEGUNDOS)
    respuesta.raise_for_status()
    texto = respuesta.content.decode("utf-8", errors="replace")
    if archivo is not None:
        Path(archivo).parent.mkdir(parents=True, exist_ok=True)
        Path(archivo).write_text(texto, encoding="utf-8")
    return texto


def fichero_iniciativas(nombre, carpeta_datos=CARPETA_DATOS, hoy=None):
    """Lista de un fichero de iniciativas de la legislatura («ProyectosDeLey», «ProposicionesDeLey»…)."""
    hoy = hoy or date.today()
    carpeta = Path(carpeta_datos) / "crudo" / "congreso" / "iniciativas"
    pagina = _get(URL_INICIATIVAS, carpeta / f"pagina_{hoy:%Y%m%d}.html")
    enlace = re.search(rf"/webpublica/opendata/iniciativas/{nombre}__\d+\.json", pagina)
    if not enlace:
        raise RuntimeError(f"No se encuentra el fichero {nombre} en {URL_INICIATIVAS}")
    datos = json.loads(_get(BASE + enlace.group(0), carpeta / f"{nombre}_{hoy:%Y%m%d}.json"))
    return datos if isinstance(datos, list) else next(v for v in datos.values() if isinstance(v, list))


def proyectos_de_ley(carpeta_datos=CARPETA_DATOS, hoy=None):
    """Lista de proyectos de ley de la legislatura (datos abiertos del Congreso)."""
    return fichero_iniciativas("ProyectosDeLey", carpeta_datos, hoy)


def _iso(ddmmaaaa):
    m = _RE_FECHA.search(ddmmaaaa or "")
    return f"{m.group(3)}-{m.group(2)}-{m.group(1)}" if m else None


def _lineas(texto):
    return [l.strip() for l in (texto or "").splitlines() if l.strip()]


def pasos(tramitacion_seguida):
    """'Comisión X\\nPublicación\\ndesde A hasta B\\n…' -> [{fase, organo, desde, hasta}]."""
    lineas = _lineas(tramitacion_seguida)
    resultado = []
    for i, linea in enumerate(lineas):
        m = _RE_FECHAS.match(linea)
        if not m or i == 0:
            continue
        fase = lineas[i - 1]
        organo = lineas[i - 2] if i >= 2 and not _RE_FECHAS.match(lineas[i - 2]) else None
        resultado.append({"fase": fase, "organo": organo, "desde": _iso(m.group(1)), "hasta": _iso(m.group(2))})
    return resultado


def resumen_proyecto(p):
    resultado = " ".join(_lineas(p.get("RESULTADOTRAMITACION")))
    return {
        "expediente": (p.get("NUMEXPEDIENTE") or "").split("/0000")[0],
        "objeto": " ".join(_lineas(p.get("OBJETO"))),
        "resultado": resultado or None,
        "fecha_resultado": _iso(resultado),
        "situacion": p.get("SITUACIONACTUAL"),
        "comision": p.get("COMISIONCOMPETENTE"),
        "tipo_tramitacion": p.get("TIPOTRAMITACION"),
        "presentado": _iso(p.get("FECHAPRESENTACION")),
        "pasos": pasos(p.get("TRAMITACIONSEGUIDA")),
        "enlaces_bocg": [e.split("#")[0] + ("#" + e.split("#")[1] if "#" in e else "")
                         for e in re.split(r"\s+", (p.get("ENLACESBOCG") or "").strip()) if e.startswith("http")],
    }


def por_rdl(proyectos):
    """{'22/2026': resumen} para los proyectos 'procedentes del Real Decreto-ley…'."""
    resultado = {}
    for p in proyectos:
        objeto = " ".join(_lineas(p.get("OBJETO")))
        if "procedente del" not in objeto.lower():
            continue
        m = _RE_RDL.search(objeto)
        if m:
            resultado[m.group(1)] = resumen_proyecto(p)
    return resultado


def procesar(carpeta_datos=CARPETA_DATOS, hoy=None):
    carpeta_datos = Path(carpeta_datos)
    indice = por_rdl(proyectos_de_ley(carpeta_datos, hoy))
    cambiadas = 0
    for archivo in sorted((carpeta_datos / "normas").glob("*.json")):
        norma = json.loads(archivo.read_text(encoding="utf-8"))
        if norma.get("rango") != "Real Decreto-ley":
            continue
        nuevo = indice.get(norma.get("numero_oficial"))
        if nuevo != norma.get("tramitacion"):
            if nuevo is None:
                norma.pop("tramitacion", None)
            else:
                norma["tramitacion"] = nuevo
            archivo.write_text(json.dumps(norma, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            cambiadas += 1
    return cambiadas


def main():
    argparse.ArgumentParser(description="Tramitación como proyecto de ley de los reales decretos-ley.").parse_args()
    print(f"Reales decretos-ley con tramitación actualizada: {procesar()}")


if __name__ == "__main__":
    main()
