"""Frases del texto oficial que responden a preguntas de la ficha, sin IA.

Copia literal (no se resume ni se reescribe) de tres cosas que casi todas las
normas dicen de sí mismas:
- objeto: «Este real decreto tiene por objeto…»;
- entrada en vigor: el párrafo de la disposición «Entrada en vigor»;
- competencia: el párrafo de la disposición «Título competencial» («se dicta al
  amparo del artículo 149.1.13.ª de la Constitución…»). Es la competencia que la
  norma DICE usar; una comunidad puede discutirla ante el Tribunal Constitucional.

Cada extracto es {"parrafo": n (1 = primer párrafo del texto), "texto": "..."}; la
competencia lleva además "articulos" (["149.1.13.ª", ...]) si cita el artículo 149.1.
Si no se encuentra, el campo no aparece.
"""

import re

MAX_CARACTERES = 900  # suficiente para un párrafo largo; el resto, en el texto oficial
MAX_APARTADOS = 4     # «1. …», «2. …» que siguen a un encabezado

# Sujeto: la propia norma («Este real decreto», «La presente orden ministerial», «El presente Acuerdo»),
# no otra cosa («Estas ayudas tienen por finalidad…» no dice qué es la norma).
_TIPO_NORMA = (r"(?:real\s+decreto(?:-ley|\s+legislativo)?|decreto(?:-ley|\s+legislativo|\s+foral)?|"
               r"ley(?:\s+org[áa]nica|\s+foral)?|orden(?:\s+ministerial)?|resoluci[óo]n|circular|instrucci[óo]n|"
               r"acuerdo|convenio|protocolo|tratado|canje\s+de\s+notas|enmiendas?|reglamento|disposici[óo]n|norma)")
_SUJETO = rf"(?:(?:El|La|Los|Las)\s+)?(?:presente|presentes|este|esta|estos|estas)\s+{_TIPO_NORMA}"
_NUMERACION = r"(?:\d+\.\s*|[a-z]\)\s*)?"
_OBJETO = re.compile(
    rf"^{_NUMERACION}(?:{_SUJETO}\s+(?:tiene|tienen|tendrá|tendrán)\s+(?:por|como)\s+(?:objeto|finalidad)"
    rf"|(?:El|Es)\s+objeto\s+de\s+(?:el|la|los|las)?\s*(?:presente|este|esta)\b)", re.IGNORECASE)

_ENCABEZADO_VIGOR = re.compile(r"\bentrada en vigor\.?$", re.IGNORECASE)
_VIGOR = re.compile(rf"^{_NUMERACION}{_SUJETO}\s+(?:entrará|entrarán)\s+en\s+vigor", re.IGNORECASE)

_ENCABEZADO_COMPETENCIA = re.compile(
    r"\b(?:t[íi]tulos?\s+competencial(?:es)?|habilitaci[óo]n\s+competencial|fundamento\s+constitucional"
    r"|competencias?\s+(?:estatal(?:es)?|del\s+Estado))\.?$", re.IGNORECASE)
_AMPARO = re.compile(rf"^{_NUMERACION}{_SUJETO}\s+se\s+dicta(?:n)?\s+(?:al\s+amparo|en\s+(?:virtud|ejercicio)|de\s+conformidad)",
                     re.IGNORECASE)
_ARTICULO_149 = re.compile(r"149\.\s*1\.?\s*(\d{1,2})\.?\s*[ªa]")
# Otras formas: «regla 14.ª del artículo 149.1», «149.1 …, cláusula 19.ª», «149.1.6.ª y 18.ª».
_ORDINAL_SUELTO = re.compile(r"(?<![\d.])(\d{1,2})\.?\s*ª")
_APARTADO = re.compile(r"^(?:\d+\.|[a-z]\))\s")
MAX_ENCABEZADO = 120  # «Disposición final quinta. Título competencial.»


def _extracto(lista, i):
    """El párrafo i (y los apartados «1.», «2.»… que le siguen si acaba en «:» o empieza uno)."""
    partes = [lista[i]]
    j = i + 1
    if lista[i].rstrip().endswith(":") or _APARTADO.match(lista[i]):
        while j < len(lista) and len(partes) <= MAX_APARTADOS and _APARTADO.match(lista[j]):
            partes.append(lista[j])
            j += 1
    texto = "\n".join(partes)
    if len(texto) > MAX_CARACTERES:
        texto = texto[:MAX_CARACTERES].rsplit(" ", 1)[0] + "…"
    return {"parrafo": i + 1, "texto": texto}


def _tras_encabezado(lista, patron):
    """Párrafo que sigue al ÚLTIMO encabezado corto que cumple `patron`.

    El último, porque una norma que modifica otra puede citar antes, entre
    comillas, las disposiciones de la norma modificada.
    """
    for i in range(len(lista) - 2, -1, -1):
        if len(lista[i]) <= MAX_ENCABEZADO and patron.search(lista[i]):
            return i + 1
    return None


def _ultimo(lista, patron):
    for i in range(len(lista) - 1, -1, -1):
        if patron.search(lista[i]):
            return i
    return None


def objeto(lista):
    for i, p in enumerate(lista):
        if _OBJETO.search(p):
            return _extracto(lista, i)
    return None


def entrada_en_vigor(lista):
    i = _tras_encabezado(lista, _ENCABEZADO_VIGOR)
    if i is None or not re.search(r"vigor|efectos|aplicar|aplicación", lista[i], re.IGNORECASE):
        i = _ultimo(lista, _VIGOR)
    return _extracto(lista, i) if i is not None else None


def articulos_149(texto):
    """'…artículos 149.1.13.ª y 149.1.21.ª…' -> ['149.1.13.ª', '149.1.21.ª'] (sin repetir, en orden).

    Si el párrafo cita el artículo 149.1, también cuentan los ordinales sueltos
    («regla 14.ª del artículo 149.1», «149.1.6.ª y 18.ª»).
    """
    texto = texto.replace("\xa0", " ")
    numeros = _ARTICULO_149.findall(texto)
    if re.search(r"149\.\s*1\b", texto):
        numeros += _ORDINAL_SUELTO.findall(texto)
    vistos = []
    for n in numeros:
        clave = f"149.1.{int(n)}.ª"
        if clave not in vistos and 1 <= int(n) <= 32:
            vistos.append(clave)
    if re.search(r"149\.\s*2\b", texto):  # el servicio de la cultura
        vistos.append("149.2")
    return vistos


def competencia(lista):
    i = _tras_encabezado(lista, _ENCABEZADO_COMPETENCIA)
    if i is None or not re.search(r"amparo|competencia|149|Estatuto|dicta", lista[i], re.IGNORECASE):
        # Sin encabezado, solo si habla de la Constitución o un Estatuto: «se dicta al
        # amparo del artículo 26.1 de la Ley 3/2013» es una habilitación legal, no una competencia.
        i = _ultimo(lista, _AMPARO)
        if i is not None and not re.search(r"Constituci[óo]n|Estatuto", lista[i]):
            i = None
    if i is None:
        return None
    extracto = _extracto(lista, i)
    articulos = articulos_149(extracto["texto"])
    if articulos:
        extracto["articulos"] = articulos
    return extracto


def extractos_de_texto(texto):
    """{"objeto": …, "entrada_en_vigor": …, "competencia": …} con los que se encuentren."""
    lista = [p.strip() for p in (texto or "").splitlines() if p.strip()]
    encontrados = {"objeto": objeto(lista), "entrada_en_vigor": entrada_en_vigor(lista),
                   "competencia": competencia(lista)}
    return {k: v for k, v in encontrados.items() if v}
