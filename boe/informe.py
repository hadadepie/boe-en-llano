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

Qué pasó después (parte 2, sin la «vida» de las normas antiguas):

    tramitados_como_ley  decretos-ley que el Congreso tramitó también como proyecto de ley
                         (boe.tramitacion: fase en que se quedó y cuánto tardó)
    tribunales           lo que el BOE publica de los tribunales sobre normas (boe.tribunales):
                         tipo de asunto, quién recurre, qué normas y qué decide el Supremo
    senado               conflictos entre órganos constitucionales (Senado, Gobierno, Congreso)
                         admitidos por el Tribunal Constitucional: quién, frente a quién y por qué
    correcciones         correcciones de errores por órgano: cuántas, de qué normas y la tasa por cada
                         100 normas que publica ese órgano
    sin_presupuestos     gobernar con los Presupuestos prorrogados: leyes de Presupuestos, órdenes
                         para elaborarlos, normas que conceden créditos (boe.presupuestos) y el
                         conflicto ante el Tribunal Constitucional

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


# Fases de la tramitación de un proyecto de ley en el Congreso, en palabras llanas.
FASES_TRAMITACION = {"Enmiendas": "Plazo de enmiendas", "Informe": "Informe de la ponencia",
                     "Mesa - Calificación": "Calificación de la Mesa", "Publicación": "Publicación"}
_NOMBRE_NORMA = re.compile(r"^(Real Decreto-ley \d+/\d{4})")


def tramitados_como_ley(normas, legislatura=None):
    """Decretos-ley que, además de convalidarse, se tramitaron como proyecto de ley (None si no hay)."""
    filas = []
    for n in normas:
        t = n.get("tramitacion")
        if not t or n.get("rango") != "Real Decreto-ley":
            continue
        pasos = [p["fase"] for p in t.get("pasos", []) if not p["fase"].startswith("Concluido")]
        fase = pasos[-1] if pasos else None
        dias = ((date.fromisoformat(t["fecha_resultado"]) - date.fromisoformat(t["presentado"])).days
                if t.get("fecha_resultado") and t.get("presentado") else None)
        m = _NOMBRE_NORMA.match(n.get("titulo") or "")
        filas.append({"id": n["id"], "nombre": m.group(1) if m else n.get("titulo"), "tema": n.get("tema"),
                      "presentado": t.get("presentado"), "resultado": t.get("resultado"),
                      "fecha_resultado": t.get("fecha_resultado"), "fase": FASES_TRAMITACION.get(fase, fase),
                      "dias": dias, "comision": t.get("comision")})
    if not filas:
        return None
    filas.sort(key=lambda x: (x["presentado"] or "", x["id"]))
    dias = sorted(x["dias"] for x in filas if x["dias"] is not None)
    resultados = Counter((x["resultado"] or "Sin resultado").split(" ")[0] for x in filas)
    return {"n": len(filas), "convalidados": ((legislatura or {}).get("resumen") or {}).get("convalidado"),
            "resultados": dict(resultados.most_common()),
            "fases": dict(Counter(x["fase"] for x in filas).most_common()),
            "dias": {"mediana": dias[len(dias) // 2], "min": dias[0], "max": dias[-1]} if dias else None,
            "lista": filas}


# Quien recurre, en el orden en que se muestra; lo que no consta se junta.
_SIN_PROMOTOR = "No consta en el BOE"
MAS_RECURRIDAS = 10


def tribunales(normas):
    """Lo que el BOE (sección I) publica de los tribunales sobre normas, contado (None si no hay).

    Ojo al leerlo: el BOE no publica todo. Del Constitucional, la sección I recoge sobre todo la
    admisión de recursos y cuestiones (sus sentencias van en un suplemento aparte); del Supremo,
    sobre todo las sentencias que anulan una norma, porque la ley obliga a publicarlas."""
    filas = [n["tribunal"] for n in normas if n.get("tribunal")]
    if not filas:
        return None
    tc = [t for t in filas if t["tribunal"] == "Tribunal Constitucional"]
    ts = [t for t in filas if t["tribunal"].startswith("Tribunal Supremo")]
    promotores = Counter(c if (c := (t.get("promotor") or {}).get("categoria")) not in (None, "No consta") else _SIN_PROMOTOR
                         for t in filas)
    # La misma norma se cita con títulos de distinta longitud: se agrupa por rango, número y fecha
    # (la fecha separa leyes autonómicas con el mismo número).
    recurridas, texto_de = Counter(), {}
    for t in filas:
        a = t.get("norma_afectada") or {}
        if a.get("texto"):
            clave = (a.get("rango"), a.get("numero"), a.get("fecha")) if a.get("numero") else (a.get("rango"), a["texto"])
            recurridas[clave] += 1
            if clave not in texto_de or len(a["texto"]) < len(texto_de[clave]):
                texto_de[clave] = a["texto"]
    return {
        "total": len(filas), "constitucional": len(tc), "supremo": len(ts),
        "tipos_tc": dict(Counter(t.get("tipo") or "Otro" for t in tc).most_common()),
        "decisiones_ts": dict(Counter(t.get("decision") or "Otra" for t in ts).most_common()),
        "suspension_161_2": sum(1 for t in tc if t.get("suspension_161_2")),
        "promotores": [{"categoria": k, "n": v} for k, v in promotores.most_common() if k != _SIN_PROMOTOR]
                      + [{"categoria": _SIN_PROMOTOR, "n": promotores[_SIN_PROMOTOR]}] * bool(promotores[_SIN_PROMOTOR]),
        "mas_recurridas": [{"norma": texto_de[k], "rango": k[0], "n": v} for k, v in recurridas.most_common(MAS_RECURRIDAS) if v >= 3],
        "sin_norma": len(filas) - sum(recurridas.values()),
    }


_LEY_PGE = re.compile(r"de Presupuestos Generales del Estado para (?:el (?:año|ejercicio) )?(\d{4})", re.IGNORECASE)
_ELABORACION_PGE = re.compile(r"normas para la elaboraci[óo]n de los Presupuestos Generales del Estado para (\d{4})", re.IGNORECASE)
_PRESUPUESTOS = re.compile(r"Presupuestos Generales del Estado", re.IGNORECASE)


def _nombre(n):
    m = re.match(r"^(.*?\d+/\d{4})", n.get("titulo") or "")  # «Real Decreto-ley 8/2023», «Orden HFP/1254/2023»
    return m.group(1) if m else n.get("titulo")


def sin_presupuestos(normas):
    """Gobernar con los Presupuestos prorrogados, contado con lo que publicó el BOE (None si no hay normas)."""
    estatales = [n for n in normas if n.get("origen_legislativo", "Estatal") == "Estatal"]
    if not estatales:
        return None
    leyes = sorted(({"id": n["id"], "fecha": n["fecha_publicacion"], "ejercicio": m.group(1), "titulo": n["titulo"]}
                    for n in estatales if n.get("rango") == "Ley" and (m := _LEY_PGE.search(n.get("titulo") or ""))),
                   key=lambda x: x["fecha"])
    ordenes = sorted(({"id": n["id"], "fecha": n["fecha_publicacion"], "ejercicio": m.group(1), "nombre": _nombre(n)}
                      for n in estatales if n.get("rango") == "Orden" and (m := _ELABORACION_PGE.search(n.get("titulo") or ""))),
                     key=lambda x: x["fecha"])
    conflictos = sorted(({"id": n["id"], "fecha": n["fecha_publicacion"], "titulo": n["titulo"],
                          "promotor": ((n["tribunal"].get("promotor") or {}).get("texto"))}
                         for n in estatales if (n.get("tribunal") or {}).get("tipo") == "Conflicto entre órganos constitucionales"
                         and _PRESUPUESTOS.search(n.get("titulo") or "")), key=lambda x: x["fecha"])
    con_creditos = sorted((n for n in estatales if n.get("creditos")), key=lambda n: (n["fecha_publicacion"], n["id"]))
    rdl = [n for n in estatales if n.get("rango") == "Real Decreto-ley"]
    anios = sorted({n["fecha_publicacion"][:4] for n in rdl})
    por_anio = [{"anio": a, "rdl": sum(1 for n in rdl if n["fecha_publicacion"][:4] == a),
                 "con_creditos": sum(1 for n in rdl if n["fecha_publicacion"][:4] == a and n.get("creditos"))} for a in anios]
    return {
        "leyes": leyes, "ordenes_elaboracion": ordenes, "conflictos": conflictos,
        "rdl": len(rdl), "rdl_con_creditos": sum(1 for n in rdl if n.get("creditos")), "por_anio": por_anio,
        "creditos": [{"id": n["id"], "nombre": _nombre(n), "rango": n["rango"], "fecha": n["fecha_publicacion"],
                      "tema": n.get("tema"),
                      # Párrafos que los conceden (un párrafo puede conceder varios créditos).
                      "tipos": sorted({c["tipo"] for c in n["creditos"]})}
                     for n in con_creditos],
    }


# Conflictos entre órganos constitucionales: de qué tratan, por reglas sobre el título oficial
# (en orden: la primera que encaja). Etiquetas descriptivas, sin valorar quién tiene razón.
MOTIVOS_CONFLICTO = [
    (re.compile(r"134\.6|veto presupuestario|disconformidad", re.I), "Enmiendas con gasto: el Gobierno se opone a tramitarlas (art. 134.6)"),
    (re.compile(r"Presupuestos Generales del Estado", re.I), "Presentar los Presupuestos"),
    (re.compile(r"comparecencia", re.I), "Comparecencia del presidente del Gobierno"),
    (re.compile(r"correcci[óo]n de errores|Bolet[íi]n Oficial de las Cortes Generales", re.I), "Corrección y publicación del texto de una ley"),
    (re.compile(r"Mesa del Congreso", re.I), "Acuerdos de la Mesa del Congreso sobre textos del Senado"),
]
_ORGANOS = (("Senado", "el Senado"), ("Congreso", "el Congreso"), ("Gobierno", "el Gobierno"),
            ("Consejo General del Poder Judicial", "el Consejo General del Poder Judicial"))


def _organo(texto):
    return next((nombre for clave, nombre in _ORGANOS if clave.lower() in (texto or "").lower()), None)


def _frente_a(promotor, titulo, quien):
    """Contra quién: lo dice el BOE («el Senado frente al Gobierno») o, si no, el acuerdo recurrido."""
    if " frente a" in (promotor or ""):
        return _organo(promotor.split(" frente a", 1)[1])
    for patron, organo in ((r"Mesa del Congreso", "el Congreso"), (r"Mesa del Senado|Presidente del Senado", "el Senado"),
                           (r"Gobierno|Consejo de Ministros", "el Gobierno")):
        if organo != quien and re.search(patron, titulo or "", re.I):
            return organo
    return None


def senado(normas):
    """Conflictos entre órganos constitucionales publicados en el BOE (None si no hay)."""
    filas = []
    for n in normas:
        t = n.get("tribunal") or {}
        if t.get("tipo") != "Conflicto entre órganos constitucionales":
            continue
        promotor = (t.get("promotor") or {}).get("texto") or ""
        quien = _organo(promotor.split(" frente a", 1)[0])
        m = re.search(r"\ben relaci[óo]n (?:con|al?) (.+)$", n.get("titulo") or "")
        filas.append({"id": n["id"], "fecha": n["fecha_publicacion"], "asunto_tc": t.get("asunto"),
                      "decision": t.get("decision"), "quien": quien, "frente_a": _frente_a(promotor, n.get("titulo"), quien),
                      "motivo": next((e for r, e in MOTIVOS_CONFLICTO if r.search(n.get("titulo") or "")), "Otros"),
                      "sobre": (m.group(1) if m else n.get("titulo") or "").rstrip(".")})
    if not filas:
        return None
    filas.sort(key=lambda x: (x["fecha"], x["id"]))
    parejas = Counter(f"{x['quien']} frente a {x['frente_a']}" if x["frente_a"] else x["quien"] for x in filas)
    return {"n": len(filas), "por_quien": dict(Counter(x["quien"] for x in filas).most_common()),
            "parejas": dict(parejas.most_common()), "motivos": dict(Counter(x["motivo"] for x in filas).most_common()),
            "lista": filas}


# Correcciones de errores: se enlazan con la norma corregida por el título oficial (lo que va
# tras «Corrección de errores del…») y el órgano, que es el mismo que publicó la norma.
_PREFIJO_CORRECCION = re.compile(
    r"^Correcci[óo]n de (?:errores|erratas)(?: y erratas)? (?:del|de la|de las|de los|de|en la|en el|a las|a la|al)\s+", re.I)
_RANGO_EN_TITULO = re.compile(r"^(Real Decreto-ley|Real Decreto Legislativo|Real Decreto|Ley Orgánica|Ley|Orden|Resolución|"
                              r"Circular|Instrucción|Decreto-ley|Decreto Legislativo|Decreto|Sentencia|Acuerdo)")
_INTERNACIONAL = ("Acuerdo Internacional", "Nota Diplomática")
MINIMO_NORMAS_TASA = 50  # por debajo, una o dos correcciones bastan para mover mucho la tasa
EJEMPLOS_CORRECCIONES = 8


def _clave_titulo(t):
    return re.sub(r"\s+", " ", t or "").strip(" .").lower()


def _que_corrige(c, corregida):
    """Tipo de lo corregido: el rango de la norma enlazada o, si no está entre las guardadas, el que
    nombra el título. Exteriores publica sin rango en el título los tratados, enmiendas y estatutos."""
    if corregida:
        return "internacional" if corregida.get("rango") in _INTERNACIONAL else "otra"
    resto = _PREFIJO_CORRECCION.sub("", c.get("titulo") or "")
    if not _RANGO_EN_TITULO.match(resto) and (c.get("departamento") or "").startswith("Ministerio de Asuntos Exteriores"):
        return "internacional"
    return "otra"


def correcciones(normas, minimo=MINIMO_NORMAS_TASA):
    """Correcciones de errores por órgano y tasa por cada 100 normas que publica (None si no hay).

    Los órganos se cuentan con el nombre que les da el BOE, sin juntar los ministerios de antes y
    después de la reestructuración de noviembre de 2023 (no siempre son el mismo ministerio)."""
    cor = [n for n in normas if n.get("rango") == CORRECCION]
    if not cor:
        return None
    resto = [n for n in normas if n.get("rango") != CORRECCION]
    por_titulo = {}
    for n in resto:
        por_titulo.setdefault((n.get("departamento"), _clave_titulo(n.get("titulo"))), n)
    filas = []
    for c in cor:
        corregida = por_titulo.get((c.get("departamento"), _clave_titulo(_PREFIJO_CORRECCION.sub("", c.get("titulo") or ""))))
        filas.append((c, corregida))

    estatales = [(c, o) for c, o in filas if c.get("origen_legislativo") == "Estatal"]
    publicadas = Counter(n.get("departamento") for n in resto if n.get("origen_legislativo") == "Estatal")
    cuenta, internacional = Counter(), Counter()
    for c, o in estatales:
        cuenta[c.get("departamento")] += 1
        internacional[c.get("departamento")] += _que_corrige(c, o) == "internacional"
    organos = [{"organo": d, "normas": publicadas[d], "correcciones": cuenta[d],
                "de_acuerdos_internacionales": internacional[d],
                "tasa": round(cuenta[d] * 100 / publicadas[d], 1)}
               # Ordenados por lo que publican, no por la tasa: es una comparación, no una clasificación.
               for d in sorted(publicadas, key=lambda d: (-publicadas[d], d)) if publicadas[d] >= minimo]

    enlazadas = [(c, o) for c, o in filas if o]
    dias = sorted((date.fromisoformat(c["fecha_publicacion"]) - date.fromisoformat(o["fecha_publicacion"])).days
                  for c, o in enlazadas)
    por_norma = defaultdict(list)
    for c, o in enlazadas:
        por_norma[o["id"]].append(c)
    corregidas = {o["id"]: o for _, o in enlazadas}
    # Normas del Estado con más correcciones y, a igualdad, las más recientes.
    ejemplos = sorted((i for i in por_norma if corregidas[i].get("origen_legislativo") == "Estatal"),
                      key=lambda i: (-len(por_norma[i]), -_ordinal(corregidas[i]), i))[:EJEMPLOS_CORRECCIONES]
    return {
        "total": len(cor), "estatales": len(estatales), "autonomicas": len(cor) - len(estatales),
        "de_acuerdos_internacionales": sum(internacional.values()),
        "enlazadas": len(enlazadas), "normas_corregidas": len(por_norma),
        "normas_estatales": sum(publicadas.values()), "minimo_normas": minimo,
        "dias": {"mediana": dias[len(dias) // 2], "hasta_7": sum(1 for d in dias if d <= 7),
                 "mas_de_180": sum(1 for d in dias if d > 180)} if dias else None,
        "organos": organos,
        "ejemplos": [{"id": i, "nombre": _nombre(corregidas[i]), "titulo": corregidas[i]["titulo"],
                      "rango": corregidas[i].get("rango"), "organo": corregidas[i].get("departamento"),
                      "fecha": corregidas[i]["fecha_publicacion"],
                      "correcciones": [{"id": c["id"], "fecha": c["fecha_publicacion"],
                                        "dias": (date.fromisoformat(c["fecha_publicacion"]) - date.fromisoformat(corregidas[i]["fecha_publicacion"])).days}
                                       for c in sorted(por_norma[i], key=lambda c: (c["fecha_publicacion"], c["id"]))]}
                     for i in ejemplos],
    }


def _ordinal(n):
    return date.fromisoformat(n["fecha_publicacion"]).toordinal()


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
        "tramitados_como_ley": tramitados_como_ley(normas, legislatura),
        "tribunales": tribunales(normas),
        "sin_presupuestos": sin_presupuestos(normas),
        "senado": senado(normas),
        "correcciones_por_organo": correcciones(normas),
    }
