"""Qué dicen los tribunales sobre las normas, a partir de lo que publica el BOE (sección I).

Sin IA: reglas sobre el título, el epígrafe y la primera frase del texto, que en
estas publicaciones es muy regular:

- Tribunal Constitucional (providencias y autos): «El Pleno del Tribunal
  Constitucional, por providencia de …, ha acordado admitir a trámite el recurso de
  inconstitucionalidad número …, promovido por …, contra … de la Ley …».
- Tribunal Supremo, Sala Tercera (sentencias y autos): «Sentencia de …, de la Sala
  Tercera del Tribunal Supremo, que estima parcialmente el recurso
  contencioso-administrativo … contra el Real Decreto …».

Se queda en los hechos (quién, qué tipo de asunto, qué decide, sobre qué norma y
cuándo); no resume argumentos. Quien recurre se guarda por categoría institucional
(«Gobierno de España», «Gobierno autonómico», «50 o más diputados»…); si es una
persona particular no se guarda su nombre.

`clasificar(norma, texto)` devuelve un diccionario o None si la publicación no es
una decisión de un tribunal sobre normas (p. ej. instrucciones del Tribunal de Cuentas).
"""

import re

MESES = "enero|febrero|marzo|abril|mayo|junio|julio|agosto|septiembre|octubre|noviembre|diciembre"
_FECHA = rf"\d{{1,2}} de (?:{MESES}) de \d{{4}}"

# ---------- Tipo de asunto ----------

TIPOS_TC = [
    (r"recursos? de inconstitucionalidad", "Recurso de inconstitucionalidad"),
    (r"cuesti[óo]n(?:es)? de inconstitucionalidad", "Cuestión de inconstitucionalidad"),
    (r"conflicto positivo de competencia", "Conflicto positivo de competencia"),
    (r"conflicto negativo de competencia", "Conflicto negativo de competencia"),
    (r"conflicto entre [óo]rganos constitucionales", "Conflicto entre órganos constitucionales"),
    (r"conflicto en defensa de la autonom[íi]a local", "Conflicto en defensa de la autonomía local"),
    (r"impugnaci[óo]n de disposiciones auton[óo]micas", "Impugnación de disposiciones autonómicas"),
    (r"cuesti[óo]n prejudicial", "Cuestión prejudicial sobre normas forales"),
]
TIPOS_TS = [
    (r"cuesti[óo]n de ilegalidad", "Cuestión de ilegalidad"),
    (r"recurso de casaci[óo]n", "Recurso de casación"),
    (r"recurso contencioso-administrativo|recurso (?:n[úu]mero|n\.º|ordinario)", "Recurso contencioso-administrativo"),
]

# ---------- Qué decide ----------

DECISIONES_TC = [
    (r"admitir a tr[áa]mite", "Admite a trámite"),
    (r"inadmitir", "Inadmite"),
    (r"tener por desistid|desistimiento", "Desistimiento"),
    (r"levantar la suspensi[óo]n", "Levanta la suspensión"),
    (r"mantener la suspensi[óo]n", "Mantiene la suspensión"),
    (r"extinci[óo]n|declarar extinguid", "Extinción del proceso"),
]
DECISIONES_TS = [
    (r"\bestima(?:r)? (?:parcialmente|en parte)", "Estima en parte"),
    (r"\bdesestima", "Desestima"),
    (r"\binadmit", "Inadmite"),
    (r"\bestima", "Estima"),
    (r"suspender cautelarmente|suspensi[óo]n cautelar", "Suspende cautelarmente"),
    (r"rectifica(?:r|ci[óo]n)? (?:de )?(?:el |los )?error|aclara", "Corrige o aclara una resolución anterior"),
    (r"ejecuci[óo]n", "Ejecución de sentencia"),
]

# ---------- Quién lo promueve ----------

_PROMOTOR = re.compile(r"\b(?:promovid[oa]|planteada|interpuest[oa])\s+(?:en nombre y representaci[óo]n de|por)\s+(.+?)"
                       r"(?:,\s+(?:frente|contra|en relaci[óo]n|respecto|en el|ha acordado|la Sala|representad[oa]|bajo la)\b"
                       r"|\s+(?:contra|frente a|en relaci[óo]n con|respecto de|ante el)\s)",
                       re.IGNORECASE)
# «el procurador don X, en representación de las entidades Y» -> Y
_REPRESENTANTE = re.compile(r"^(?:el|la) (?:procurador|procuradora|abogad[oa]|letrad[oa])\b.*?\ben representaci[óo]n de"
                            r"(?:l| la| las entidades| la entidad| los)?\s+(.+)$", re.IGNORECASE)
CATEGORIAS_PROMOTOR = [
    (r"presidente del gobierno|gobierno de la naci[óo]n|abogac[íi]a del estado|abogado del estado", "Gobierno de España"),
    (r"defensor del pueblo", "Defensor del Pueblo"),
    (r"^(?:el |la )?(?:senado|congreso de los diputados|consejo general del poder judicial)\b", "Un órgano constitucional"),
    (r"diputados", "50 o más diputados"),
    (r"senadores", "50 o más senadores"),
    (r"parlamento|cortes de|asamblea|junta general|corts", "Parlamento autonómico"),
    (r"consejo de gobierno|gobierno de|govern|xunta|junta de|generalitat|diputaci[óo]n general|consell", "Gobierno autonómico"),
    (r"juzgado|tribunal|sala de lo|secci[óo]n \d|audiencia", "Un órgano judicial"),
    (r"ayuntamiento|municipio|diputaci[óo]n provincial|cabildo|consell insular|federaci[óo]n espa[ñn]ola de municipios", "Administración local"),
    (r"comisi[óo]n nacional|agencia estatal|banco de espa[ñn]a|ministerio fiscal|autoridad independiente", "Un organismo público"),
]
_PERSONA = re.compile(r"^(?:la representaci[óo]n (?:procesal )?de\s+)?(?:don|doña|d\.ª?|dña\.)\s", re.IGNORECASE)


def categoria_promotor(texto):
    t = (texto or "").strip()
    if not t:
        return None
    for patron, nombre in CATEGORIAS_PROMOTOR:
        if re.search(patron, t, re.IGNORECASE):
            return nombre
    if _PERSONA.search(t):
        return "Una persona particular"
    return "Empresas, asociaciones u otras entidades"


def promotor(texto):
    """{"categoria": …, "texto": …}; el texto literal solo si no es una persona particular."""
    m = _PROMOTOR.search(texto or "")
    if not m:
        return None
    literal = re.sub(r"^(?:la )?representaci[óo]n (?:procesal )?de(?:l| la)?\s+", "", m.group(1).strip(), flags=re.IGNORECASE)
    representado = _REPRESENTANTE.search(literal)
    if representado:
        literal = representado.group(1)
    elif re.match(r"^(?:el|la) (?:procurador|procuradora)\b", literal, re.IGNORECASE):
        return {"categoria": "No consta"}  # solo se nombra al procurador
    categoria = categoria_promotor(literal)
    resultado = {"categoria": categoria}
    if categoria != "Una persona particular":
        resultado["texto"] = literal[:200]
    return resultado


# ---------- Sobre qué norma ----------

_RANGOS = (r"Real Decreto Legislativo|Real Decreto-ley|Real Decreto|Decreto Legislativo|Decreto-ley|Decreto Foral|Decreto|"
           r"Ley Org[áa]nica|Ley Foral|Ley|Norma Foral|Orden|Resoluci[óo]n|Acuerdo")
_NORMA = re.compile(rf"\b({_RANGOS})\s+(?:(?:de[l]?\s+)?[A-Z][\w\s]*?\s)?((?:[A-Z]{{2,5}}/)?\d+/\d{{4}})(?:,?\s+de\s+(\d{{1,2}} de (?:{MESES})))?",
                    re.IGNORECASE)
_TRAS_CONTRA = re.compile(r"\b(?:contra|en relaci[óo]n con|respecto de|frente a)\b", re.IGNORECASE)


def norma_afectada(texto):
    """Primera norma citada tras «contra / en relación con / respecto de».

    {"rango": "Ley", "numero": "12/2023", "fecha": "24 de mayo", "texto": "Ley 12/2023, de 24 de mayo, por el derecho a la vivienda"}
    """
    t = (texto or "").replace("\xa0", " ")
    m = _TRAS_CONTRA.search(t)
    resto = t[m.end():] if m else t
    n = _NORMA.search(resto)
    if not n:
        return None
    cola = resto[n.end():]
    corte = re.search(r"[.;]\s|,\s+(?:por posible|en cuanto|y,? de conformidad|cuya parte)|\s+y\s+(?:el|la|los|las)\s+(?:art|disp|Real|Ley|Decreto|Orden|Resoluci)|$", cola)
    descripcion = cola[: corte.start()] if corte else cola
    rango = n.group(1)
    rango = {"ley organica": "Ley Orgánica", "resolucion": "Resolución"}.get(rango.lower().replace("á", "a").replace("ó", "o"), rango[:1].upper() + rango[1:])
    return {"rango": rango, "numero": n.group(2), "fecha": n.group(3) or None,
            "texto": (resto[n.start():n.end()] + descripcion).strip(" ,")[:300]}


# ---------- Clasificación ----------

def _primero(patrones, texto):
    for patron, nombre in patrones:
        if re.search(patron, texto or "", re.IGNORECASE):
            return nombre
    return None


def _fecha_decision(titulo, texto):
    m = re.search(rf"(?:providencia|auto|sentencia)\s+(?:de|con fecha)\s+({_FECHA})", f"{titulo} {texto}", re.IGNORECASE)
    return m.group(1) if m else None


def _documento(norma, texto):
    rango = (norma.get("rango") or "").lower()
    if rango in ("providencia", "auto", "sentencia"):
        return rango.capitalize()
    m = re.search(r"\bpor (providencia|auto)\b|ha dictado (sentencia|auto)", texto or "", re.IGNORECASE)
    return (m.group(1) or m.group(2)).capitalize() if m else None


def clasificar(norma, texto):
    """Ficha de hechos de una decisión judicial sobre normas, o None."""
    departamento = (norma.get("departamento_sumario") or norma.get("departamento") or "").upper()
    titulo = norma.get("titulo") or ""
    epigrafe = norma.get("epigrafe") or ""
    parrafos = [p.strip() for p in (texto or "").splitlines() if p.strip()]
    primera = parrafos[0] if parrafos else ""
    if "TRIBUNAL CONSTITUCIONAL" in departamento:
        tribunal, tipos, decisiones = "Tribunal Constitucional", TIPOS_TC, DECISIONES_TC
        # A veces el primer párrafo repite el título y la decisión va en el segundo.
        primera = next((p for p in parrafos if re.search(r"Tribunal Constitucional|ha acordado", p)), primera)
        decision_de = primera
    elif "TRIBUNAL SUPREMO" in departamento:
        sala = re.search(r"\bSala (Primera|Segunda|Tercera|Cuarta|Quinta)\b", f"{titulo} {primera}")
        tribunal = f"Tribunal Supremo (Sala {sala.group(1)})" if sala else "Tribunal Supremo"
        tipos, decisiones = TIPOS_TS, DECISIONES_TS
        decision_de = titulo  # «…, que estima parcialmente el recurso…»
    else:
        return None
    resultado = {
        "tribunal": tribunal,
        "documento": _documento(norma, primera),
        "tipo": _primero(tipos, f"{epigrafe} {titulo} {primera}"),
        "decision": _primero(decisiones, decision_de) or _primero(decisiones, primera),
        "fecha_decision": _fecha_decision(titulo, primera),
        "promotor": promotor(primera) or promotor(titulo),
        "norma_afectada": norma_afectada(titulo) or norma_afectada(primera),
    }
    if tribunal == "Tribunal Constitucional":
        resultado["suspension_161_2"] = bool(re.search(r"161\.2", texto or ""))
    asunto = re.search(r"(?:n\.º|n[úu]mero|núm\.)\s*(\d+[-/]\d{4})", f"{titulo} {primera}")
    if asunto:
        resultado["asunto"] = asunto.group(1)
    return resultado
