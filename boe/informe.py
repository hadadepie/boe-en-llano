"""Informe de la legislatura: quién decidió, cuándo y con cuánto tiempo para adaptarse.

Sin IA ni fuentes nuevas: cuenta las normas de la sección I guardadas en datos/normas/
(del 17/08/2023 en adelante) por quién las aprueba, según su rango y su departamento:

    cortes         leyes, leyes orgánicas y reformas de la Constitución (Cortes Generales)
    rdl            reales decretos-ley (Gobierno; el Congreso los convalida o deroga)
    rd             reales decretos (Consejo de Ministros)
    ministerios    órdenes, resoluciones, instrucciones y circulares de un ministerio
    otros_organos  organismos independientes y otros órganos (Banco de España, CNMC,
                   Junta Electoral Central, CGPJ, reglamentos internos de las Cortes…)
    internacional  tratados, acuerdos internacionales y notas diplomáticas
    tribunales     providencias, sentencias y autos (Tribunal Constitucional, Supremo)

No cuentan como decisiones: las correcciones de errores y las resoluciones de las Cortes
que publican la convalidación o derogación de un decreto-ley (ya están en su decreto-ley).
Las normas autonómicas que se publican también en el BOE se cuentan aparte.
"""

import re
from collections import Counter, defaultdict
from datetime import date

from boe import vigencia

CATEGORIAS = [
    ("cortes", "Leyes de las Cortes", "Leyes, leyes orgánicas y reformas de la Constitución, aprobadas por las Cortes Generales."),
    ("rdl", "Reales decretos-ley", "Los aprueba el Gobierno por urgencia, con fuerza de ley; el Congreso los convalida o deroga después."),
    ("rd", "Reales decretos", "Los aprueba el Consejo de Ministros, sin votación en las Cortes."),
    ("ministerios", "Órdenes y resoluciones", "Órdenes, resoluciones, instrucciones y circulares de un ministerio."),
    ("otros_organos", "Otros órganos del Estado", "Organismos independientes (Banco de España, CNMC, CNMV, Consejo de Seguridad Nuclear), "
                                                  "Junta Electoral Central, Consejo General del Poder Judicial, Tribunal de Cuentas y "
                                                  "reglamentos internos del Congreso y el Senado."),
    ("internacional", "Acuerdos internacionales", "Tratados, acuerdos internacionales y notas diplomáticas que obligan a España."),
    ("tribunales", "Decisiones de tribunales", "Providencias, sentencias y autos del Tribunal Constitucional y del Supremo sobre normas."),
]
DECIDEN_LEYES = ("cortes", "rdl", "rd")  # las tres vías que se comparan por mes y por tema

_RANGO = {"Ley": "cortes", "Ley Orgánica": "cortes", "Reforma": "cortes",
          "Real Decreto-ley": "rdl", "Real Decreto": "rd",
          "Acuerdo Internacional": "internacional", "Nota Diplomática": "internacional",
          "Providencia": "tribunales", "Sentencia": "tribunales", "Auto": "tribunales"}
CORRECCION = "Corrección (errores o erratas)"

# Entrada en vigor por tipo de norma (boe.vigencia); «otro» junta lo poco frecuente.
GRUPOS_VIGENCIA = [("Leyes", ("Ley", "Ley Orgánica")), ("Reales decretos-ley", ("Real Decreto-ley",)),
                   ("Reales decretos", ("Real Decreto",)), ("Órdenes", ("Orden",)),
                   ("Resoluciones de ministerios", ("Resolución",))]
TIPOS_VIGENCIA = ["mismo_dia", "dia_siguiente", "plazo", "fecha", "otro"]
_TIPO_AGRUPADO = {"mes_siguiente": "otro", "condicion": "otro"}

_NUEVO_GOBIERNO = re.compile(r"por el que se reestructuran los departamentos ministeriales", re.IGNORECASE)
_SUBVENCION_DIRECTA = re.compile(r"concesi[óo]n directa", re.IGNORECASE)


def categoria(n):
    """Clave de CATEGORIAS, «autonomica», o None si no es una decisión (corrección, convalidación publicada)."""
    rango, departamento = n.get("rango") or "", n.get("departamento") or ""
    if rango == CORRECCION:
        return None
    if n.get("origen_legislativo") != "Estatal":
        return "autonomica"
    if rango in _RANGO:
        return _RANGO[rango]
    if departamento == "Cortes Generales":
        return None if rango == "Resolución" else "otros_organos"
    if departamento.startswith("Ministerio"):
        return "ministerios"
    return "otros_organos"


def _meses(desde, hasta):
    a, m = int(desde[:4]), int(desde[5:7])
    while f"{a:04d}-{m:02d}" <= hasta[:7]:
        yield f"{a:04d}-{m:02d}"
        a, m = (a + 1, 1) if m == 12 else (a, m + 1)


def _ritmo(normas, desde, hasta):
    """Normas de cada vía cada 30 días entre dos fechas (hasta excluida)."""
    dias = (date.fromisoformat(hasta) - date.fromisoformat(desde)).days
    cuenta = Counter(c for n, c in normas if desde <= n["fecha_publicacion"] < hasta)
    return {"desde": desde, "hasta": hasta, "dias": dias,
            **{c: cuenta[c] for c in DECIDEN_LEYES},
            "rd_cada_30_dias": round(cuenta["rd"] * 30 / dias, 1) if dias else None}


def vigencia_por_grupo(normas):
    grupos = []
    for etiqueta, rangos in GRUPOS_VIGENCIA:
        tipos, sin_parrafo, total = Counter(), 0, 0
        for n, c in normas:
            if n.get("rango") not in rangos or c not in ("cortes", "rdl", "rd", "ministerios"):
                continue
            total += 1
            parrafo = ((n.get("textos_oficiales") or {}).get("entrada_en_vigor") or {}).get("texto")
            if not parrafo:
                sin_parrafo += 1
                continue
            tipo = vigencia.clasificar(parrafo)["tipo"]
            tipos[_TIPO_AGRUPADO.get(tipo, tipo)] += 1
        grupos.append({"grupo": etiqueta, "total": total, "sin_parrafo": sin_parrafo,
                       "tipos": {t: tipos[t] for t in TIPOS_VIGENCIA}})
    return grupos


# Cómo votó cada grupo parlamentario las convalidaciones del Pleno (boe.congreso).
POSICIONES = ["Sí", "No", "Abstención", "No vota", "Dividido"]
NOMBRE_CORTO_GRUPO = {
    "GP": "PP", "GS": "PSOE", "GVOX": "Vox", "GSUMAR": "Sumar", "GMx": "Mixto",
    "GJxCAT": "Junts", "GR": "ERC", "GEH Bildu": "EH Bildu", "GV (EAJ-PNV)": "PNV",
}


def posicion(votos):
    """Lo que votó la mayoría de los diputados del grupo; «Dividido» si empatan dos opciones."""
    if not votos:
        return None
    orden = sorted(votos.items(), key=lambda kv: -kv[1])
    return "Dividido" if len(orden) > 1 and orden[0][1] == orden[1][1] else orden[0][0]


def votos_por_grupo(convalidaciones):
    """Posición de cada grupo en cada convalidación con voto por grupos, contada por grupo.

    Siempre agregado: el Grupo Mixto va como grupo (sus listas de un solo diputado serían, sumadas
    a lo largo de la legislatura, el historial de una persona); su desglose sigue en cada ficha.
    Orden: por número de diputados del grupo, no por cómo votó."""
    detalle = [r for r in (convalidaciones or {}).values() if (r.get("convalidacion") or {}).get("por_grupo")]
    if not detalle:
        return None
    cuenta, diputados, nombres = defaultdict(Counter), Counter(), {}
    for r in detalle:
        v = r["convalidacion"]
        for g, votos in v["por_grupo"].items():
            p = posicion(votos)
            if p:
                cuenta[g][p] += 1
            diputados[g] = max(diputados[g], sum(votos.values()))
            nombres[g] = (v.get("nombres_grupo") or {}).get(g, g)
    grupos = [{"codigo": g, "nombre": NOMBRE_CORTO_GRUPO.get(g, nombres[g]), "nombre_completo": nombres[g],
               "diputados": diputados[g], "votaciones": sum(cuenta[g].values()),
               "posiciones": {p: cuenta[g][p] for p in POSICIONES}}
              for g in sorted(cuenta, key=lambda g: (-diputados[g], g))]
    solo_totales = sum(1 for r in convalidaciones.values() if (r.get("convalidacion") or {}).get("solo_totales"))
    return {"votaciones": len(detalle), "solo_totales": solo_totales, "grupos": grupos}


def construir(normas, legislatura=None, convalidaciones=None):
    """Cifras del informe a partir de las normas tal como están en datos/normas/ (None si no hay)."""
    if not normas:
        return None
    clasificadas = [(n, categoria(n)) for n in normas]
    fechas = sorted(n["fecha_publicacion"] for n in normas)
    desde, hasta = fechas[0], fechas[-1]
    cuenta = Counter(c for _, c in clasificadas)
    estatales = [(n, c) for n, c in clasificadas if c not in (None, "autonomica")]

    por_mes = {c: Counter() for c in DECIDEN_LEYES}
    por_tema = defaultdict(Counter)
    for n, c in estatales:
        if c in DECIDEN_LEYES:
            por_mes[c][n["fecha_publicacion"][:7]] += 1
            por_tema[n.get("tema") or "Sin tema"][c] += 1
    meses = list(_meses(desde, hasta))

    leyes = sorted(({"id": n["id"], "fecha": n["fecha_publicacion"], "rango": n["rango"], "titulo": n["titulo"],
                     "tema": n.get("tema")} for n, c in estatales if c == "cortes"), key=lambda x: (x["fecha"], x["id"]))
    rd = [n for n, c in estatales if c == "rd"]
    gobierno = sorted((n for n, c in estatales if c == "rd" and _NUEVO_GOBIERNO.search(n["titulo"])
                       and "modifica" not in n["titulo"][:60].lower()), key=lambda n: n["fecha_publicacion"])
    nuevo_gobierno = ({"id": gobierno[0]["id"], "fecha": gobierno[0]["fecha_publicacion"], "titulo": gobierno[0]["titulo"]}
                      if gobierno else None)
    disolucion = (legislatura or {}).get("hasta_pleno")

    return {
        "desde": desde, "hasta": hasta, "total": len(normas),
        "correcciones": sum(1 for n in normas if n.get("rango") == CORRECCION),
        "convalidaciones_publicadas": sum(1 for n, c in clasificadas if c is None and n.get("rango") != CORRECCION),
        "autonomicas": cuenta["autonomica"],
        "estatales": len(estatales),
        "categorias": [{"clave": k, "etiqueta": e, "explicacion": x, "n": cuenta[k]} for k, e, x in CATEGORIAS],
        "leyes": leyes,
        "subvenciones_directas": {"n": sum(1 for n in rd if _SUBVENCION_DIRECTA.search(n["titulo"])), "de": len(rd)},
        "nuevo_gobierno": nuevo_gobierno,
        "disolucion": disolucion,
        "ritmo": ({"en_funciones": _ritmo(estatales, desde, nuevo_gobierno["fecha"]),
                   "con_gobierno": _ritmo(estatales, nuevo_gobierno["fecha"], disolucion or hasta)}
                  if nuevo_gobierno else None),
        "por_mes": {"meses": meses, **{c: [por_mes[c][m] for m in meses] for c in DECIDEN_LEYES}},
        "por_tema": sorted(({"tema": t, **{c: v[c] for c in DECIDEN_LEYES}} for t, v in por_tema.items()),
                           key=lambda x: -sum(x[c] for c in DECIDEN_LEYES)),
        "vigencia": vigencia_por_grupo(estatales),
        "votos_grupos": votos_por_grupo(convalidaciones),
    }
