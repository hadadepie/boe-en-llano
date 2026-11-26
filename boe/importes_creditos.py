"""Importe de cada crédito extraordinario y suplemento de crédito, para revisarlo a mano antes de sumar.

Uso:
    python -m boe.importes_creditos     # escribe datos/presupuestos/creditos.json y la hoja de revisión

De dónde: los créditos que `boe.presupuestos` encontró en cada norma (campo `creditos` de datos/normas)
y el XML oficial guardado en datos/crudo/normas/. Del XML se toma el párrafo que concede el crédito y
su continuación (apartados «a)», «b)»…, guiones y tablas), hasta el siguiente apartado numerado,
artículo u otro crédito.

Los importes se leen con su unidad (euros, miles de euros, millones de euros; también «cuatrocientos
millones (400.000.000) de euros») y se pasan a euros. Se propone una cifra solo con reglas seguras:
  - un único importe distinto en el bloque (si se repite, suele ser el párrafo de financiación);
  - un total y su desglose (el mayor es la suma de los demás): el total;
  - tantos importes distintos como créditos dice el texto («dos créditos extraordinarios»): su suma;
  - una tabla con una columna de importes: la suma de la primera tabla (en las leyes forales navarras,
    la segunda dice de dónde sale el dinero), comprobada con su fila «Total» si la tiene.
En otro caso no se propone nada y se marca para revisar.

Los avisos no cambian la cifra: dicen por qué podría no sumarse (norma autonómica, decreto-ley
derogado o sin convalidación en los datos abiertos, el mismo importe en otra norma, ejercicio 2027…).

La hoja de revisión (datos/presupuestos/revision_creditos.csv, «;» y UTF-8 con BOM para abrirla en
una hoja de cálculo) tiene tres columnas para la autora: «contar» (sí / no), «importe_revisado» (en
euros) y «nota». Al volver a generarla se conservan. Ninguna suma se publica sin esa revisión, y
siempre como importe concedido, no gastado.
"""

import csv
import json
import re
import xml.etree.ElementTree as ET
from collections import Counter
from decimal import Decimal
from pathlib import Path

from boe.presupuestos import _CONCEDE

CARPETA_DATOS = Path("datos")
COLUMNAS_AUTORA = ["contar", "importe_revisado", "nota"]

_NUMERO = r"\d{1,3}(?:\.\d{3})+(?:,\d+)?|\d+(?:,\d+)?"
_IMPORTE = re.compile(rf"({_NUMERO})\)?\s*(miles\s+de\s+euros|millones\s+de\s+euros|millones\s+euros|de\s+euros|euros|€)",
                      re.IGNORECASE)
_SOLO_NUMERO = re.compile(rf"^\s*({_NUMERO})\s*(?:€|euros)?\s*$")
# Continuación del párrafo que concede: apartados «a)», «i)», guiones, «1.º», códigos de aplicación.
_CONTINUACION = re.compile(r"^(?:\(?[a-zñ]{1,2}\)|\(?[ivx]{1,4}\)|[–—\-•·]\s|\d+\.?º|\d{2}[.\s]\d{2}[.\s]|Aplicaci[óo]n|Concepto|Servicio\s)",
                           re.IGNORECASE)
_ENCABEZADOS = {"articulo", "capitulo_num", "capitulo_tit", "seccion", "titulo_num", "titulo_tit", "anexo_num",
                "anexo_tit", "firma_rey", "firma_ministro"}
_NUMEROS_EN_LETRA = {"un": 1, "una": 1, "dos": 2, "tres": 3, "cuatro": 4, "cinco": 5, "seis": 6, "sendos": 2}
_CUANTOS = re.compile(r"\b(un|una|dos|tres|cuatro|cinco|seis|sendos)\s+(?:nuevos?\s+)?(?:cr[ée]ditos?|suplementos?)\b", re.I)
_EJERCICIO = re.compile(r"(?:presupuesto|ejercicio)[^.]{0,40}?\b(20\d\d)\b", re.I)
_OTRA_NORMA = re.compile(r"^(?:\d+\.\s*)?(?:Asimismo,\s*)?(?:La|El)\s+(?:disposici[óo]n|Ley|Real\s+Decreto|Decreto)", re.I)
_UNIDAD_CABECERA = re.compile(r"(miles\s+de\s+euros|millones\s+de\s+euros|euros)", re.I)


def a_decimal(texto):
    """'1.273.495,50' -> Decimal('1273495.50')."""
    return Decimal(texto.replace(".", "").replace(",", "."))


def factor(unidad):
    u = " ".join(unidad.lower().split())
    return Decimal(1000) if u.startswith("miles") else Decimal(1_000_000) if u.startswith("millones") else Decimal(1)


def importes(texto):
    """[(euros, literal)] de cada importe con unidad que aparece en un texto, en orden."""
    return [(a_decimal(m.group(1)) * factor(m.group(2)), " ".join(m.group(0).split())) for m in _IMPORTE.finditer(texto or "")]


def _espacios(texto):
    return " ".join((texto or "").split())


def elementos(xml):
    """[(clase, texto, filas)] de los hijos de <texto>: párrafos con su clase y tablas con sus filas."""
    nodo = ET.fromstring(xml).find("texto")
    salida = []
    for h in (nodo if nodo is not None else []):
        if h.tag == "table":
            filas = [[_espacios("".join(c.itertext())) for c in tr] for tr in h.iter("tr")]
            filas = [f for f in filas if any(f)]
            salida.append(("tabla", " // ".join(" | ".join(f) for f in filas), filas))
        else:
            t = _espacios("".join(h.itertext()))
            if t:
                salida.append((h.attrib.get("class") or h.tag, t, None))
    return salida


def bloque(els, i):
    """El elemento i y su continuación (apartados, guiones, tablas)."""
    partes = [els[i]]
    for el in els[i + 1:i + 40]:
        clase, t, _ = el
        if clase in _ENCABEZADOS or (clase != "tabla" and (_CONCEDE.search(t) or not _CONTINUACION.match(t))):
            break
        partes.append(el)
    return partes


def suma_de_tabla(filas, unidad_del_texto=None):
    """(euros, aviso) de una tabla: en cada fila, la última celda que es solo un número; la unidad, de
    una celda de cabecera («Importe (miles de euros)») o, si la tabla no la dice, del párrafo. Las filas
    «Total» no se suman: se comparan con la suma."""
    unidad = next((m.group(1) for f in filas[:3] for c in f for m in [_UNIDAD_CABECERA.search(c)] if m), None)
    unidad = unidad or unidad_del_texto
    if unidad is None:
        return None, "tabla sin unidad (euros, miles o millones)"
    total, filas_total = Decimal(0), []
    for f in filas:
        k = next((k for k in range(len(f) - 1, -1, -1) if _SOLO_NUMERO.match(f[k])), None)
        if k is None or k == 0:  # sin número, o solo un código en la primera celda
            continue
        valor = a_decimal(_SOLO_NUMERO.match(f[k]).group(1))
        if re.match(r"^\s*total", " ".join(f[:k]), re.I):
            filas_total.append(valor)
        else:
            total += valor
    euros = total * factor(unidad)
    if filas_total and filas_total[-1] * factor(unidad) != euros:
        return filas_total[-1] * factor(unidad), "la fila «Total» no coincide con la suma de la tabla"
    return (euros, None) if total else (None, "tabla sin importes legibles")


_PLURAL = re.compile(r"\b(?:los\s+siguientes|las\s+siguientes|cr[ée]ditos\s+extraordinarios|suplementos\s+de\s+cr[ée]dito)\b", re.I)
_UNO = re.compile(r"\b(?:un|una)\s+(?:suplemento\s+de\s+cr[ée]dito|cr[ée]dito\s+extraordinario)\b", re.I)
_EN_LETRA = re.compile(r"\b[a-záéíóúñ]+\s+(?:mil\s+)?millones\s+de\s+euros\b", re.I)
_CAPITULO_8 = re.compile(r"\b\d{2}[.\-]\d{2}[.\-]\s?\d{3}[A-Z][.\-]\s?8\d{2}\b")


def cuantos_creditos(parrafo):
    """Cuántos créditos dice conceder el párrafo: un número («dos créditos»), «varios» (forma plural
    sin número: «los siguientes suplementos») o las veces que dice «un suplemento de crédito»."""
    p = _espacios(parrafo)
    m = _CUANTOS.search(p)
    if m and m.group(1).lower() not in ("un", "una"):
        return _NUMEROS_EN_LETRA[m.group(1).lower()]
    if _PLURAL.search(p):
        return "varios"
    return max(1, len(_UNO.findall(p)))


def proponer(partes):
    """(importe propuesto en euros o None, cómo, avisos) para el bloque de un crédito."""
    texto = " ".join(t for clase, t, _ in partes if clase != "tabla")
    tablas = [f for clase, _, f in partes if clase == "tabla"]
    avisos = []
    valores = [v for v, _ in importes(texto)]
    if _CAPITULO_8.search(texto):
        avisos.append("capítulo 8 (activos financieros: préstamos o aportaciones de capital, no gasto)")
    if not valores and _EN_LETRA.search(texto):
        avisos.append("importe escrito solo en letra")
    de_tabla = None
    if tablas:
        unidad = next((m.group(1) for m in [_UNIDAD_CABECERA.search(texto)] if m), None)
        de_tabla, aviso = suma_de_tabla(tablas[0], unidad)
        if aviso:
            avisos.append(aviso)
        if len(tablas) > 1:
            avisos.append(f"{len(tablas)} tablas: se usa la primera")
    if valores and len(set(valores)) == 1:
        if len(valores) > 1:
            avisos.append("el mismo importe repetido en el párrafo (se cuenta una vez)")
        if de_tabla is not None and de_tabla != valores[0]:
            avisos.append("el importe del texto no coincide con la tabla")
        return valores[0], "único importe", avisos
    if len(valores) > 1:
        mayor = max(valores)
        if sum(valores) - mayor == mayor and valores.count(mayor) == 1:
            return mayor, "total con desglose", avisos
        if len(set(valores)) < len(valores):
            return None, None, avisos + ["importes repetidos y distintos a la vez: revisar"]
        n = cuantos_creditos(partes[0][1])
        if n == "varios" or n == len(valores):
            return sum(valores), f"suma de {len(valores)} importes", avisos
        return None, None, avisos + [f"{len(valores)} importes para {n} crédito(s): revisar"]
    if de_tabla is not None:
        return de_tabla, "suma de la tabla", avisos
    return None, None, avisos + ["sin importe en el texto ni en una tabla"]


def _localizar(els, texto_credito):
    inicio = _espacios(texto_credito).rstrip("…").strip()[:100]
    return next((k for k, (clase, t, _) in enumerate(els) if clase != "tabla" and inicio in t), None)


def _redondo(euros):
    return None if euros is None else float(euros.quantize(Decimal("0.01")))


def creditos_de_norma(norma, xml, convalidaciones):
    """Lista de créditos de una norma con su importe propuesto y avisos."""
    els = elementos(xml)
    conv = (convalidaciones.get(norma["id"]) or {})
    resultado_conv = (conv.get("convalidacion") or {}).get("resultado") if conv else None
    salida = []
    for c in norma.get("creditos") or []:
        i = _localizar(els, c["texto"])
        avisos = []
        if norma.get("origen_legislativo") != "Estatal":
            avisos.append("norma autonómica: no es dinero del Estado")
        if conv and resultado_conv != "convalidado":
            avisos.append("decreto-ley derogado por el Congreso" if resultado_conv == "derogado"
                          else "decreto-ley sin convalidación en los datos abiertos")
        if i is None:
            importe, como, mas = None, None, ["párrafo no encontrado en el XML"]
            texto = c["texto"]
        else:
            partes = bloque(els, i)
            importe, como, mas = proponer(partes)
            texto = " ".join(t for _, t, _ in partes)
        avisos += mas
        if _OTRA_NORMA.match(c["texto"]):
            avisos.append("el párrafo cita otra norma: puede no conceder nada")
        if re.search(r"obligaciones\s+de\s+ejercicios\s+anteriores", texto, re.I):
            avisos.append("para pagar obligaciones de ejercicios anteriores")
        m = _EJERCICIO.search(texto)
        salida.append({"id": norma["id"], "parrafo": c["parrafo"], "tipo": c["tipo"], "titulo": norma["titulo"],
                       "fecha": norma.get("fecha_publicacion"), "ejercicio": int(m.group(1)) if m else None,
                       "importe_propuesto": _redondo(importe), "como": como,
                       "importes_en_el_texto": [lit for _, lit in importes(texto)], "avisos": avisos,
                       "texto": texto[:1500]})
    return salida


def marcar_repetidos(creditos):
    """Avisa cuando el mismo importe aparece en otro crédito de la misma norma o en otra norma."""
    por_importe = {}
    for c in creditos:
        if c["importe_propuesto"]:
            por_importe.setdefault(c["importe_propuesto"], []).append(c)
    for grupo in por_importe.values():
        if len(grupo) < 2:
            continue
        for c in grupo:
            otros = [o for o in grupo if o is not c]
            if any(o["id"] == c["id"] for o in otros):
                c["avisos"].append("el mismo importe en otro crédito de esta norma")
            otras = sorted({o["id"] for o in otros if o["id"] != c["id"]})
            if otras:
                c["avisos"].append("el mismo importe en " + ", ".join(otras))


def leer_revision(archivo):
    if not archivo.exists():
        return {}
    with archivo.open(encoding="utf-8-sig", newline="") as f:
        return {(fila["id"], fila["parrafo"]): {k: fila.get(k, "") for k in COLUMNAS_AUTORA} for fila in csv.DictReader(f, delimiter=";")}


def escribir_revision(archivo, creditos):
    """Hoja para la autora; conserva lo que ya hubiera escrito en sus columnas."""
    previas = leer_revision(archivo)
    archivo.parent.mkdir(parents=True, exist_ok=True)
    with archivo.open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f, delimiter=";")
        w.writerow(["id", "parrafo", "tipo", "fecha", "ejercicio", "importe_propuesto", "como", "avisos",
                    "importes_en_el_texto", *COLUMNAS_AUTORA, "titulo", "texto"])
        for c in creditos:
            p = previas.get((c["id"], str(c["parrafo"])), {})
            propuesto = "" if c["importe_propuesto"] is None else f"{c['importe_propuesto']:.2f}".replace(".", ",")
            w.writerow([c["id"], c["parrafo"], c["tipo"], c["fecha"], c["ejercicio"] or "", propuesto, c["como"] or "",
                        " | ".join(c["avisos"]), " | ".join(c["importes_en_el_texto"]),
                        *[p.get(k, "") for k in COLUMNAS_AUTORA], c["titulo"], c["texto"]])


def procesar(carpeta_datos=CARPETA_DATOS):
    carpeta_datos = Path(carpeta_datos)
    conv_archivo = carpeta_datos / "congreso" / "convalidaciones.json"
    convalidaciones = json.loads(conv_archivo.read_text(encoding="utf-8")) if conv_archivo.exists() else {}
    creditos, sin_xml = [], []
    for archivo in sorted((carpeta_datos / "normas").glob("*.json")):
        norma = json.loads(archivo.read_text(encoding="utf-8"))
        if not norma.get("creditos"):
            continue
        xml = carpeta_datos / "crudo" / "normas" / f"{norma['id']}.xml"
        if not xml.exists():
            sin_xml.append(norma["id"])
            continue
        creditos += creditos_de_norma(norma, xml.read_text(encoding="utf-8"), convalidaciones)
    marcar_repetidos(creditos)
    salida = carpeta_datos / "presupuestos"
    salida.mkdir(parents=True, exist_ok=True)
    (salida / "creditos.json").write_text(json.dumps({"aviso": "Importes propuestos con reglas, sin revisar: no sumar sin la hoja de revisión.",
                                                      "sin_xml": sin_xml, "creditos": creditos},
                                                     ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    escribir_revision(salida / "revision_creditos.csv", creditos)
    return creditos, sin_xml


def main():
    creditos, sin_xml = procesar()
    con = sum(1 for c in creditos if c["importe_propuesto"] is not None)
    print(f"Créditos: {len(creditos)} en {len({c['id'] for c in creditos})} normas; con importe propuesto: {con}; "
          f"sin XML guardado: {len(sin_xml)}.")
    for como, n in Counter(c["como"] or "sin propuesta" for c in creditos).most_common():
        print(f"  {como}: {n}")


if __name__ == "__main__":
    main()
