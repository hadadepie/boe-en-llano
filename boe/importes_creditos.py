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
derogado o sin votación publicada todavía, el mismo importe en otra norma, ejercicio 2027…).

La hoja de revisión (datos/presupuestos/revision_creditos.csv, «;» y UTF-8 con BOM para abrirla en
una hoja de cálculo) tiene tres columnas para la autora: «contar» (sí / no), «importe_revisado» (en
euros) y «nota». Al volver a generarla se conservan. Ninguna suma se publica sin esa revisión, y
siempre como importe concedido, no gastado.
"""

import csv
import difflib
import json
import re
import xml.etree.ElementTree as ET
from collections import Counter
from datetime import date
from decimal import Decimal
from pathlib import Path

from boe import pagina_creditos
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


_LETRA = re.compile(r"^\(?([a-zñ])\)")


def bloque(els, i):
    """El elemento i y su continuación (apartados, guiones, tablas). Un párrafo que no es apartado corta el
    bloque, salvo que unos párrafos más abajo siga la letra siguiente («a) …», explicación, «b) …»: RDL 5/2026)."""
    partes, k, fin = [els[i]], i + 1, min(len(els), i + 60)
    while k < fin:
        clase, t, _ = els[k]
        if clase in _ENCABEZADOS or (clase != "tabla" and _CONCEDE.search(t)):
            break
        if clase != "tabla" and not _CONTINUACION.match(t):
            letras = [m.group(1) for _, tt, _ in partes for m in [_LETRA.match(tt)] if m]
            siguiente = chr(ord(letras[-1]) + 1) if letras else None
            salto = next((j for j in range(k + 1, min(fin, k + 8)) if siguiente and els[j][0] != "tabla"
                          and (m := _LETRA.match(els[j][1])) and m.group(1) == siguiente), None)
            if salto is None:
                break
            partes.extend(els[k:salto])
            k = salto
            continue
        partes.append(els[k])
        k += 1
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
    n_creditos = cuantos_creditos(partes[0][1])
    if valores and len(set(valores)) == 1 and not tablas and (n_creditos == "varios" or n_creditos > 1):
        # «Se aprueban los siguientes créditos…» y un solo importe: falta alguno (o va en otro sitio). Sin cifra.
        return None, None, avisos + ["el texto concede varios créditos y solo se lee un importe: revisar"]
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
        n = n_creditos
        if n == "varios" or n == len(valores):
            return sum(valores), f"suma de {len(valores)} importes", avisos
        return None, None, avisos + [f"{len(valores)} importes para {n} crédito(s): revisar"]
    if de_tabla is not None:
        return de_tabla, "suma de la tabla", avisos
    return None, None, avisos + ["sin importe en el texto ni en una tabla"]


# A dónde va el dinero: la clasificación económica del concepto (tres cifras) de la aplicación
# presupuestaria, la misma que usa Hacienda (y el Sankey de los Presupuestos).
_APLICACION = re.compile(r"\b(\d{2})[.\-\s]\s?\d{2}[.\-\s]\s?\d{3}[A-Z][.\-\s]\s?(\d{3})(?:\d{2})?\b(?:[.\-]\d{2})?\s*(?:«([^»]{3,200})»)?")
_CONCEPTO = re.compile(r"\b(?:conceptos?|subconceptos?)\s+(?:presupuestarios?\s*,?\s*)?(\d{3})(?:\.\d{2})?\b\s*(?:«([^»]{3,200})»)?", re.I)
_SUBCONCEPTO_TABLA = re.compile(r"^(\d{3})\d{2}$")
_SECCION = re.compile(r"\bsecci[óo]n\s+(\d{1,2})\s*,?\s*«([^»]{3,100})»", re.I)
_MINISTERIO = re.compile(r"«(Ministerio[^»]{3,100})»|\b(?:Presupuesto|presupuesto)\s+del\s+(Ministerio\s+(?:de|del|para)\s+[^,.;«»()]{3,100})")
DESTINOS = {
    "1": "Personal", "2": "Compras de bienes y servicios", "3": "Intereses", "5": "Fondo de contingencia",
    "6": "Inversiones del Estado", "8": "Préstamos y aportaciones de capital (activos financieros)",
    "9": "Deuda (pasivos financieros)",
}
DESTINOS_TRANSFERENCIA = {  # segunda cifra de los capítulos 4 (corrientes) y 7 (de capital)
    # 40, 41 y 43: a otro organismo del Estado (p. ej. el FEGA o la CNMC), que es quien lo paga a los destinatarios finales.
    "0": "Organismos del Estado, que lo gestionan o reparten", "1": "Organismos del Estado, que lo gestionan o reparten",
    "2": "Seguridad Social", "3": "Organismos del Estado, que lo gestionan o reparten",
    "4": "Empresas y entes públicos", "5": "Comunidades autónomas", "6": "Entidades locales", "7": "Empresas privadas",
    "8": "Familias e instituciones sin fines de lucro", "9": "Exterior",
}


def destino(concepto):
    """'777' -> 'Empresas privadas' (capítulos 4 y 7: a quién se transfiere; los demás, en qué se gasta)."""
    c = str(concepto)
    if c[0] in "47":
        return DESTINOS_TRANSFERENCIA.get(c[1])
    return DESTINOS.get(c[0])


def conceptos(texto, tablas=()):
    """[(sección o None, concepto de tres cifras, nombre de la aplicación o None)] del texto y las tablas."""
    salida = [(m.group(1), m.group(2), m.group(3)) for m in _APLICACION.finditer(texto)]
    salida += [(None, m.group(1), m.group(2)) for m in _CONCEPTO.finditer(texto)]
    for filas in tablas:
        for f in filas:
            celda = f[0] if f else ""
            m = _APLICACION.match(celda) or _SUBCONCEPTO_TABLA.match(celda)
            if m:
                salida.append((m.group(1), m.group(2), None) if m.re is _APLICACION else (None, m.group(1), None))
    return salida


def _para_que(texto, nombres, titulo):
    for n in nombres:
        if n and not re.match(r"(Ministerio|Secretar[íi]a|Direcci[óo]n|Subsecretar[íi]a|Programa|Servicio)", n):
            return n
    m = re.match(r"^(?:\d+\.\s*)?(?:Asimismo,\s*)?(?:Al objeto de|Con (?:el|la) (?:fin|objeto|finalidad) de|Para|A los efectos de)\s+"
                 r"(.{8,170}?)(?:,\s*(?:se|en el|a los)|\s+se\s+(?:aprueba|concede))", texto, re.I)
    if m and not re.search(r"previstas? en (?:este|esta|el|los)|estas? (?:medidas?|ayudas?|subvenci)|citada", m.group(1), re.I):
        return m.group(1)[0].upper() + m.group(1)[1:]
    return titulo


def anotar_destino(creditos):
    """Pone en cada crédito a dónde va (destinos), el ministerio o sección y para qué."""
    secciones = {}
    for c in creditos:
        for num, nombre in _SECCION.findall(c["texto"]):
            secciones.setdefault(num.zfill(2), nombre)
    for c in creditos:
        completo = c.pop("_completo", c["texto"])
        cs = conceptos(completo, c.pop("_tablas", ()))
        c["destinos"] = list(dict.fromkeys(d for _, con, _ in cs for d in [destino(con)] if d))
        m = _MINISTERIO.search(completo) or _SECCION.search(completo)
        if m:
            c["ministerio"] = next(g for g in m.groups()[::-1] if g and not g.isdigit()).strip() if m.re is _SECCION else (m.group(1) or m.group(2)).strip()
        else:
            c["ministerio"] = next((secciones[s] for s, _, _ in cs if s and s in secciones), None)
        c["para_que"] = _para_que(completo, [n for _, _, n in cs], c["titulo"])


def _localizar(els, texto_credito, usados=()):
    """Primer elemento aún no usado que contiene el inicio del párrafo (dos artículos pueden empezar igual)."""
    inicio = _espacios(texto_credito).rstrip("…").strip()[:100]
    return next((k for k, (clase, t, _) in enumerate(els) if clase != "tabla" and inicio in t and k not in usados), None)


def _redondo(euros):
    return None if euros is None else float(euros.quantize(Decimal("0.01")))


def resultados_decretos_ley(carpeta_datos=CARPETA_DATOS):
    """{«8/2023»: «convalidado» | «derogado» | «sin votación publicada»} de boe.legislatura, el mismo que muestra la
    web: el del BOE cuando discrepa de los datos abiertos del Congreso (RDL 8/2023: empate en el Congreso,
    convalidación en el BOE) y el de la Diputación Permanente, que solo publica el BOE."""
    archivo = Path(carpeta_datos) / "congreso" / "legislatura_xv.json"
    if not archivo.exists():
        return {}
    return {x["rdl"]: x["resultado"] for x in json.loads(archivo.read_text(encoding="utf-8")).get("decretos_ley") or []}


def creditos_de_norma(norma, xml, resultados_rdl):
    """Lista de créditos de una norma con su importe propuesto y avisos. `resultados_rdl`: resultados_decretos_ley()."""
    els = elementos(xml)
    es_rdl = norma.get("rango") == "Real Decreto-ley" and norma.get("origen_legislativo") == "Estatal"
    resultado_conv = (resultados_rdl.get(norma.get("numero_oficial")) or "sin votación publicada") if es_rdl else None
    conv = es_rdl
    salida, usados = [], set()
    for c in norma.get("creditos") or []:
        i = _localizar(els, c["texto"], usados)
        if i is not None:
            usados.add(i)
        avisos = []
        if norma.get("origen_legislativo") != "Estatal":
            avisos.append("norma autonómica: no es dinero del Estado")
        if conv and resultado_conv != "convalidado":
            avisos.append("decreto-ley derogado por el Congreso" if resultado_conv == "derogado"
                          else "decreto-ley sin votación publicada todavía")
        tablas = []
        if i is None:
            importe, como, mas = None, None, ["párrafo no encontrado en el XML"]
            texto = c["texto"]
        else:
            partes = bloque(els, i)
            importe, como, mas = proponer(partes)
            texto = " ".join(t for _, t, _ in partes)
            tablas = [f for clase, _, f in partes if clase == "tabla"]
        avisos += mas
        if _OTRA_NORMA.match(c["texto"]):
            avisos.append("el párrafo cita otra norma: puede no conceder nada")
        if re.search(r"obligaciones\s+de\s+ejercicios\s+anteriores", texto, re.I):
            avisos.append("para pagar obligaciones de ejercicios anteriores")
        m = _EJERCICIO.search(texto)
        situacion = ("autonómica" if norma.get("origen_legislativo") != "Estatal" else
                     ("convalidado" if resultado_conv == "convalidado" else "derogado" if resultado_conv == "derogado"
                      else "sin votación publicada") if conv else "ley")
        salida.append({"id": norma["id"], "parrafo": c["parrafo"], "tipo": c["tipo"], "titulo": norma["titulo"],
                       "fecha": norma.get("fecha_publicacion"), "situacion": situacion, "_tablas": tablas, "_completo": texto,
                       "ejercicio": int(m.group(1)) if m else None,
                       "importe_propuesto": _redondo(importe), "como": como,
                       "importes_en_el_texto": [lit for _, lit in importes(texto)], "avisos": avisos,
                       "texto": texto[:1500]})
    return salida


PARECIDO_MINIMO = 0.8


def parecido(a, b):
    """0–1: cuánto se parecen dos textos (sin contar los números, que en una prórroga cambian)."""
    limpio = lambda t: re.sub(r"\d", "", _espacios(t))[:800]
    return difflib.SequenceMatcher(None, limpio(a), limpio(b)).ratio()


def marcar_repetidos(creditos):
    """Avisa cuando otro crédito tiene el mismo importe y casi el mismo texto (¿prórroga o repetición?).
    El mismo importe con otro texto es casi siempre una cifra redonda que coincide: no se avisa."""
    por_importe = {}
    for c in creditos:
        if c["importe_propuesto"]:
            por_importe.setdefault(c["importe_propuesto"], []).append(c)
    for grupo in por_importe.values():
        for c in grupo:
            gemelos = [o for o in grupo if o is not c and parecido(c["texto"], o["texto"]) >= PARECIDO_MINIMO]
            if any(o["id"] == c["id"] and _espacios(o["texto"]) == _espacios(c["texto"]) for o in gemelos):
                c["avisos"].append("otro crédito de esta norma tiene el mismo importe y el mismo texto")
            otras = sorted({o["id"] for o in gemelos if o["id"] != c["id"]})
            if otras:
                c["avisos"].append("el mismo importe y casi el mismo texto en " + ", ".join(otras))


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
                    "importes_en_el_texto", *COLUMNAS_AUTORA, "titulo", "texto", "clave", "destinos", "ministerio"])
        for c in creditos:
            p = previas.get((c["id"], str(c["parrafo"])), {})
            propuesto = "" if c["importe_propuesto"] is None else f"{c['importe_propuesto']:.2f}".replace(".", ",")
            w.writerow([c["id"], c["parrafo"], c["tipo"], c["fecha"], c["ejercicio"] or "", propuesto, c["como"] or "",
                        " | ".join(c["avisos"]), " | ".join(c["importes_en_el_texto"]),
                        *[p.get(k, "") for k in COLUMNAS_AUTORA], c["titulo"], c["texto"],
                        c.get("clave", ""), " + ".join(c.get("destinos") or []), c.get("ministerio") or ""])


def marcar_cifras_seguras(creditos, revision):
    """`cifra_segura` (la que puede ir en la ficha de la norma): créditos del Estado cuyo importe sale de una regla
    segura y sin dudas, o que la autora ha revisado. Su revisión manda: «no» en «contar» la quita, y un
    «importe_revisado» la pone (en `importe`)."""
    estatales = [c for c in creditos if c["situacion"] != "autonómica"]
    for c in creditos:
        r = revision.get((c["id"], str(c["parrafo"])), {})
        revisado = (r.get("importe_revisado") or "").strip()
        contar = (r.get("contar") or "").strip().lower()
        c["importe"] = c["importe_propuesto"]
        c["cifra_segura"] = (c["situacion"] != "autonómica" and c["importe_propuesto"] is not None
                             and not pagina_creditos.es_dudoso(c, estatales))
        if revisado:
            c["importe"] = float(a_decimal(revisado))
            c["cifra_segura"] = c["situacion"] != "autonómica"
            c["revisado"] = True
        if contar in ("sí", "si"):
            c["revisado"] = True
            c["cifra_segura"] = c["situacion"] != "autonómica" and c["importe"] is not None
        elif contar == "no":
            c["revisado"] = True
            c["cifra_segura"] = False


def poner_claves(creditos):
    """C-001… a los del Estado y A-01… a los autonómicos, por fecha y párrafo (para citarlos en el chat)."""
    orden = sorted(creditos, key=lambda c: (c["fecha"] or "", c["id"], c["parrafo"]))
    estatales = [c for c in orden if c["situacion"] != "autonómica"]
    autonomicos = [c for c in orden if c["situacion"] == "autonómica"]
    for k, c in enumerate(estatales, 1):
        c["clave"] = f"C-{k:03d}"
    for k, c in enumerate(autonomicos, 1):
        c["clave"] = f"A-{k:02d}"
    creditos[:] = estatales + autonomicos


def procesar(carpeta_datos=CARPETA_DATOS):
    carpeta_datos = Path(carpeta_datos)
    resultados_rdl = resultados_decretos_ley(carpeta_datos)
    creditos, sin_xml = [], []
    for archivo in sorted((carpeta_datos / "normas").glob("*.json")):
        norma = json.loads(archivo.read_text(encoding="utf-8"))
        if not norma.get("creditos"):
            continue
        xml = carpeta_datos / "crudo" / "normas" / f"{norma['id']}.xml"
        if not xml.exists():
            sin_xml.append(norma["id"])
            continue
        creditos += creditos_de_norma(norma, xml.read_text(encoding="utf-8"), resultados_rdl)
    marcar_repetidos(creditos)
    anotar_destino(creditos)
    poner_claves(creditos)
    salida = carpeta_datos / "presupuestos"
    marcar_cifras_seguras(creditos, leer_revision(salida / "revision_creditos.csv"))
    salida.mkdir(parents=True, exist_ok=True)
    (salida / "creditos.json").write_text(json.dumps({"aviso": "Importes propuestos con reglas, sin revisar: no sumar sin la hoja de revisión.",
                                                      "sin_xml": sin_xml, "creditos": creditos},
                                                     ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    escribir_revision(salida / "revision_creditos.csv", creditos)
    (salida / "revision_creditos.html").write_text(pagina_creditos.pagina(creditos, date.today().strftime("%d/%m/%Y")), encoding="utf-8")
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
