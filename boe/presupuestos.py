"""Gasto aprobado fuera del presupuesto: créditos extraordinarios y suplementos de crédito.

Sin IA: reglas sobre el texto oficial. Cuando hace falta gastar en algo que el presupuesto
no prevé (crédito extraordinario) o para lo que no basta lo previsto (suplemento de crédito),
la norma lo dice en la parte que manda, con una forma muy regular:

    «Se concede un crédito extraordinario en el presupuesto de la sección 17 … por importe de …»
    «1. Se conceden suplementos de crédito en el concepto 451 …»
    «Para financiar …, se aprueba un crédito extraordinario por importe de 250 millones de euros …»

Solo se mira la parte que manda (desde «En su virtud» o «DISPONGO»): el preámbulo lo explica
y contaría dos veces. Se copia el párrafo literal (como `boe.extractos`), no se suman importes:
vienen en euros, miles o millones de euros y a veces en tablas, y una suma automática podría dar
cifras falsas.

`creditos(texto)` devuelve [{"tipo", "parrafo", "texto"}] (vacía si no hay).
"""

import re

MAX_CARACTERES = 900
_CREDITO = r"(cr[ée]ditos?\s+extraordinarios?|suplementos?\s+de\s+cr[ée]ditos?)"
_CONCEDE = re.compile(
    r"\bse\s+(?:conceden?|aprueban?|autorizan?)\s+(?:la\s+concesi[óo]n\s+de\s+)?"
    r"(?:(?:un|una|dos|tres|cuatro|cinco|seis|siete|ocho|nueve|diez|los|las|varios|diversos|siguientes|"
    r"nuevos?|sendos)\s+){0,3}" + _CREDITO, re.IGNORECASE)
_DISPOSITIVA = re.compile(r"^(En su virtud|DISPONGO)", re.IGNORECASE)


def _tipo(texto):
    return "Suplemento de crédito" if texto.lower().startswith("suplemento") else "Crédito extraordinario"


def creditos(texto):
    lineas = [p.strip() for p in (texto or "").splitlines() if p.strip()]
    inicio = next((i for i, p in enumerate(lineas) if _DISPOSITIVA.match(p)), 0)
    encontrados = []
    for i, parrafo in enumerate(lineas[inicio:], start=inicio + 1):
        m = _CONCEDE.search(parrafo)
        if m:
            corto = parrafo if len(parrafo) <= MAX_CARACTERES else parrafo[:MAX_CARACTERES].rsplit(" ", 1)[0] + "…"
            encontrados.append({"tipo": _tipo(m.group(1)), "parrafo": i, "texto": corto})
    return encontrados
