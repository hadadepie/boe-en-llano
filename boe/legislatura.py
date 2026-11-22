"""Cifras de la legislatura: todas las convalidaciones de reales decretos-ley en el Pleno.

Uso:
    python -m boe.legislatura            # recorre la XV legislatura y guarda las cifras

Fuente: índice de votaciones del Pleno del Congreso por fecha (datos abiertos).
El calendario de días con votaciones se carga con JavaScript, así que se
consulta cada día laborable; los índices de días pasados quedan guardados en
datos/crudo/congreso/indices/ (los mismos que usa boe.congreso).

De cada índice se leen los puntos de la sección «Convalidación o derogación de
Reales Decretos-leyes» que EMPIEZAN por «Real Decreto-ley N/AAAA» (no la
tramitación como proyecto de ley ni las votaciones de proyectos «procedentes
de» un decreto-ley), con sus totales Sí / No / Abstenciones.

Límite conocido: lo que votó la Diputación Permanente (con las Cortes
disueltas) no está en los datos abiertos; esos números aparecen «sin votación
del Pleno publicada».
"""

import argparse
import json
import re
from datetime import date, timedelta
from pathlib import Path

from boe import congreso

CARPETA_DATOS = Path("datos")
LEGISLATURA = "XV"
INICIO = date(2023, 8, 17)      # constitución de las Cortes de la XV legislatura
FIN_PLENO = date(2026, 10, 6)   # disolución: después, no hay votaciones del Pleno

_SECCION = "Convalidación o derogación de Reales Decretos-leyes"
_INICIO_PUNTO = re.compile(r"(Reales Decretos-leyes\.|Detalle(?:\s+XML)?(?:\s+JSON)?(?:\s+PDF)?)\s*$")
_OTRA_SECCION = re.compile(r"\b(?:[IVXL]+|PUNTO [A-ZÚÑ]+)\.\s+[A-ZÁÉÍÓÚ][a-záéíóúñ]")
_RDL = re.compile(r"Real Decreto-ley\s+(\d+)/(\d{4})")


def convalidaciones_del_indice(html):
    """[{rdl, afavor, enContra, abstenciones, llamamiento}] de un índice de votaciones."""
    texto = congreso._texto_visible(html)
    resultado = []
    for m in _RDL.finditer(texto):
        antes = texto[max(0, m.start() - 80):m.start()]
        if not _INICIO_PUNTO.search(antes):
            continue  # la mención no empieza un punto (tramitación, «procedente del…», etc.)
        cabecera = texto.rfind(_SECCION, 0, m.start())
        if cabecera < 0 or _OTRA_SECCION.search(texto[cabecera + len(_SECCION):m.start()]):
            continue  # no está en la sección de convalidaciones
        tramo = texto[m.end():m.end() + 900]
        t = congreso._RE_TOTALES.search(tramo)
        if not t or _RDL.search(tramo[:t.start()]):
            continue
        resultado.append({"rdl": f"{m.group(1)}/{m.group(2)}", "afavor": int(t.group(1)), "enContra": int(t.group(2)),
                          "abstenciones": int(t.group(3)), "llamamiento": "por llamamiento" in tramo[:t.start()].lower()})
    return resultado


def recorrer(desde=INICIO, hasta=None, carpeta_datos=CARPETA_DATOS, hoy=None):
    """Convalidaciones del Pleno entre `desde` y `hasta` (días laborables)."""
    hoy = hoy or date.today()
    hasta = min(hasta or FIN_PLENO, FIN_PLENO, hoy)
    votaciones, dias = {}, 0
    dia = desde
    while dia <= hasta:
        if dia.isoweekday() <= 5:
            dias += 1
            for v in convalidaciones_del_indice(congreso.indice_del_dia(dia, carpeta_datos, hoy)):
                votaciones.setdefault(v["rdl"], {**v, "fecha": dia.isoformat()})
        dia += timedelta(days=1)
    return votaciones, dias


def numero(rdl):
    n, a = rdl.split("/")
    return int(a), int(n)


_ACUERDO = re.compile(r"Acuerdo de (convalidación|derogación) del Real Decreto-ley (\d+/\d{4})", re.IGNORECASE)


def acuerdos_boe(carpeta_datos=CARPETA_DATOS):
    """{rdl: {"resultado", "id", "fecha"}} de las resoluciones del BOE que publican una convalidación o derogación."""
    resultado = {}
    for archivo in (Path(carpeta_datos) / "normas").glob("*.json"):
        n = json.loads(archivo.read_text(encoding="utf-8"))
        m = _ACUERDO.search(n.get("titulo") or "")
        if m:
            resultado[m.group(2)] = {"resultado": "convalidado" if m.group(1).lower() == "convalidación" else "derogado",
                                     "id": n["id"], "fecha": n.get("fecha_publicacion")}
    return resultado


def cifras(votaciones, numeros_conocidos, acuerdos=None):
    """Resumen y lista ordenada.

    `numeros_conocidos`: RDL de la legislatura que constan (votados o en nuestros datos).
    `acuerdos`: resoluciones del BOE (para los que no votó el Pleno: Diputación Permanente).
    Un empate en el Pleno cuenta como derogado (no se convalida) y se marca.
    """
    acuerdos = acuerdos or {}
    lista = []
    for rdl in sorted(set(votaciones) | set(numeros_conocidos), key=numero):
        v = votaciones.get(rdl)
        if v:
            lista.append({"rdl": rdl, "fecha": v["fecha"], "organo": "Pleno",
                          "resultado": "convalidado" if v["afavor"] > v["enContra"] else "derogado",
                          "empate": v["afavor"] == v["enContra"],
                          "afavor": v["afavor"], "enContra": v["enContra"], "abstenciones": v["abstenciones"],
                          "margen": v["afavor"] - v["enContra"], "llamamiento": v["llamamiento"]})
        elif rdl in acuerdos:
            a = acuerdos[rdl]
            lista.append({"rdl": rdl, "organo": "Diputación Permanente", "resultado": a["resultado"],
                          "publicado_boe": a["fecha"], "id_boe": a["id"]})
        else:
            lista.append({"rdl": rdl, "resultado": "sin votación publicada"})
    cuenta = lambda **f: sum(1 for x in lista if all(x.get(k) == val for k, val in f.items()))
    resumen = {
        "convalidado": cuenta(resultado="convalidado"), "derogado": cuenta(resultado="derogado"),
        "sin votación publicada": cuenta(resultado="sin votación publicada"),
        "pleno": cuenta(organo="Pleno"), "diputacion_permanente": cuenta(organo="Diputación Permanente"),
        "empates": cuenta(empate=True),
    }
    return resumen, lista


def numeros_de_la_legislatura(votaciones, carpeta_datos=CARPETA_DATOS):
    """Números de RDL que sabemos que existen en el periodo: los votados y los de nuestras normas,
    más los huecos de numeración entre el primero y el último de cada año (la numeración es correlativa)."""
    conocidos = set(votaciones)
    for archivo in (Path(carpeta_datos) / "normas").glob("*.json"):
        n = json.loads(archivo.read_text(encoding="utf-8"))
        if n.get("rango") == "Real Decreto-ley" and n.get("numero_oficial"):
            conocidos.add(n["numero_oficial"])
    por_anio = {}
    for rdl in conocidos:
        a, n = numero(rdl)
        por_anio.setdefault(a, set()).add(n)
    completos = set()
    for a, ns in por_anio.items():
        completos |= {f"{k}/{a}" for k in range(min(ns), max(ns) + 1)}
    return completos


def procesar(carpeta_datos=CARPETA_DATOS, hoy=None, rehacer=False):
    hoy = hoy or date.today()
    archivo = Path(carpeta_datos) / "congreso" / f"legislatura_{LEGISLATURA.lower()}.json"
    if archivo.exists() and not rehacer:
        previo = json.loads(archivo.read_text(encoding="utf-8"))
        # Si ya se consultó tras la disolución, el Pleno no puede haber votado nada más.
        if previo.get("consultado", "") > FIN_PLENO.isoformat():
            return previo
    votaciones, dias = recorrer(carpeta_datos=carpeta_datos, hoy=hoy)
    resumen, lista = cifras(votaciones, numeros_de_la_legislatura(votaciones, carpeta_datos), acuerdos_boe(carpeta_datos))
    salida = {
        "legislatura": LEGISLATURA, "desde": INICIO.isoformat(), "hasta_pleno": FIN_PLENO.isoformat(),
        "consultado": hoy.isoformat(), "dias_consultados": dias, "resumen": resumen, "decretos_ley": lista,
        "fuente": "https://www.congreso.es/es/opendata/votaciones",
        "nota": ("Votaciones del Pleno leídas del índice de votaciones de cada día. Lo que votó la Diputación "
                 "Permanente (con las Cortes disueltas) no está en los datos abiertos: su resultado se toma de la "
                 "resolución publicada en el BOE cuando la tenemos. Un empate no convalida el decreto-ley."),
    }
    archivo = Path(carpeta_datos) / "congreso" / f"legislatura_{LEGISLATURA.lower()}.json"
    archivo.parent.mkdir(parents=True, exist_ok=True)
    archivo.write_text(json.dumps(salida, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return salida


def main():
    parser = argparse.ArgumentParser(description="Cifras de convalidación de reales decretos-ley en la legislatura.")
    parser.add_argument("--rehacer", action="store_true", help="recalcular aunque ya exista (usa los índices guardados)")
    s = procesar(rehacer=parser.parse_args().rehacer)
    print(f"Días consultados: {s['dias_consultados']} · {s['resumen']}")


if __name__ == "__main__":
    main()
