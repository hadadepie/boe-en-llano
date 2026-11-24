"""Cuándo empieza a aplicarse una norma (vacatio legis), a partir de su párrafo de entrada en vigor.

Sin IA: reglas sobre el párrafo que copia `boe.extractos` («Este real decreto entrará
en vigor el día siguiente al de su publicación en el «Boletín Oficial del Estado»»).
Se clasifica la regla general (la primera frase); si la norma prevé excepciones
(«No obstante…», «Se exceptúa…», otros apartados), se marca, sin detallarlas.

Tipos:
    mismo_dia      el mismo día de su publicación
    dia_siguiente  el día siguiente
    plazo          a los N días o meses de publicarse (`plazo`: {"cantidad", "unidad"})
    fecha          en una fecha concreta (`fecha`: «1 de enero de 2025»)
    mes_siguiente  el primer día del mes siguiente al de su publicación
    condicion      depende de otro hecho (p. ej. acuerdos internacionales: tras la última notificación)
    otro           no se ha podido clasificar
"""

import re

from boe.resumir import numeros_con_letra

MESES = "enero|febrero|marzo|abril|mayo|junio|julio|agosto|septiembre|octubre|noviembre|diciembre"
ETIQUETAS = {
    "mismo_dia": "El mismo día de su publicación",
    "dia_siguiente": "Al día siguiente de su publicación",
    "plazo": "Tiempo de espera tras su publicación",
    "fecha": "En una fecha concreta",
    "mes_siguiente": "El primer día del mes siguiente a su publicación",
    "condicion": "Depende de otro hecho",
    "otro": "Sin clasificar",
}

_NUMERO = r"(\d+|[a-záéíóúñ]+(?:\s+y\s+[a-záéíóúñ]+)?)"
_PLAZO = re.compile(rf"(?:a\s+los|transcurridos|al\s+cabo\s+de|pasados)?\s*{_NUMERO}\s+(d[íi]as|mes(?:es)?)"
                    rf"(?:\s+(naturales|h[áa]biles))?\s+(?:de|despu[ée]s\s+de|desde|siguientes\s+al?(?:\s+de)?|contados\s+(?:a\s+partir\s+de|desde))"
                    rf"\s+(?:el\s+d[íi]a\s+de\s+)?(?:la\s+|su\s+)?publicaci[óo]n",
                    re.IGNORECASE)
_AL_MES = re.compile(r"\b(?:al\s+mes|un\s+mes\s+despu[ée]s)\s+de\s+(?:su\s+|la\s+)?publicaci[óo]n", re.IGNORECASE)
_FECHA = re.compile(rf"\bel\s+(?:d[íi]a\s+)?(\d{{1,2}}\s+de\s+(?:{MESES})\s+(?:de|del\s+a[ñn]o)\s+\d{{4}})", re.IGNORECASE)
_MES_SIGUIENTE = re.compile(r"\b(?:el\s+)?(?:primer\s+d[íi]a|d[íi]a\s+(?:primero|uno|1))\s+del\s+mes\s+siguiente", re.IGNORECASE)
_CONDICION = re.compile(r"despu[ée]s\s+de\s+la\s+fecha\s+en\s+que|en\s+la\s+fecha\s+(?:en\s+)?que|a\s+partir\s+de\s+la\s+fecha\s+en\s+que|"
                        r"fecha\s+de\s+(?:su\s+)?firma|"
                        r"cuando\s+|[úu]ltima\s+(?:notificaci[óo]n|nota)|instrumento\s+de\s+ratificaci[óo]n|canje\s+de", re.IGNORECASE)
_EXCEPCIONES = re.compile(r"\bno\s+obstante\b|se\s+except[úu]a|\bexcepto\b|\bsalvo\b|con\s+efectos\s+(?:desde|a\s+partir)|"
                          r"ser[áa]n?\s+de\s+aplicaci[óo]n|ser[áa]\s+aplicable", re.IGNORECASE)
_BOLETIN = re.compile(r"publicaci[óo]n\s+en\s+(?:el\s+)?[«\"]?((?:Bolet[íi]n|Diario|Diari)\s+Oficial[^»\".,;]*)", re.IGNORECASE)


def _primera_frase(texto):
    t = re.sub(r"^\s*(?:\d+\.|[a-z]\)|Uno\.)\s*", "", (texto or "").split("\n")[0]).replace("\xa0", " ").replace(" ", " ")
    m = re.search(r"\.\s+(?=[A-ZÁÉÍÓÚ])", t)  # fin de la primera frase
    return t[: m.start() + 1] if m else t


def _cantidad(palabra):
    if palabra.isdigit():
        return int(palabra)
    if palabra.lower() in ("un", "uno", "una"):
        return 1
    valores = numeros_con_letra(palabra)
    return int(next(iter(valores))) if len(valores) == 1 else None


def clasificar(texto):
    """{"tipo", "etiqueta", "excepciones", y según el tipo "plazo", "fecha", "boletin"}; None sin texto."""
    if not (texto or "").strip():
        return None
    frase = _primera_frase(texto)
    resultado = {"tipo": "otro"}
    plazo = _PLAZO.search(frase)
    if re.search(r"\bmismo\s+d[íi]a\b|\bel\s+d[íi]a\s+de\s+su\s+publicaci[óo]n", frase, re.IGNORECASE) and not plazo:
        resultado["tipo"] = "mismo_dia"
    elif re.search(r"\b(?:el|al|del)\s+d[íi]a\s+siguiente\b", frase, re.IGNORECASE):
        resultado["tipo"] = "dia_siguiente"
    elif _MES_SIGUIENTE.search(frase):
        resultado["tipo"] = "mes_siguiente"
    elif _AL_MES.search(frase):
        resultado.update(tipo="plazo", plazo={"cantidad": 1, "unidad": "meses"})
    elif plazo and _cantidad(plazo.group(1)):
        unidad = "días" if plazo.group(2).lower().startswith("d") else "meses"
        if unidad == "días" and plazo.group(3) and plazo.group(3).lower().startswith("h"):
            unidad = "días hábiles"
        resultado.update(tipo="plazo", plazo={"cantidad": _cantidad(plazo.group(1)), "unidad": unidad})
    elif _CONDICION.search(frase) and not _FECHA.search(frase):
        resultado["tipo"] = "condicion"
    elif _FECHA.search(frase):
        resultado.update(tipo="fecha", fecha=_FECHA.search(frase).group(1))
    elif _CONDICION.search(frase):
        resultado["tipo"] = "condicion"
    resultado["etiqueta"] = ETIQUETAS[resultado["tipo"]]
    if resultado["tipo"] == "plazo":
        p = resultado["plazo"]
        singular = {"días": "día", "días hábiles": "día hábil", "meses": "mes"}[p["unidad"]]
        resultado["etiqueta"] = (f"Al {singular} de su publicación" if p["cantidad"] == 1
                                 else f"A los {p['cantidad']} {p['unidad']} de su publicación")
    boletin = _BOLETIN.search(frase)
    if boletin:
        resultado["boletin"] = boletin.group(1).strip()
    resto = texto[len(frase):] if texto.startswith(frase) else texto.replace(frase, "", 1)
    resultado["excepciones"] = bool(_EXCEPCIONES.search(texto) or re.search(r"(?:^|\n)\s*2\.\s", resto))
    return resultado
