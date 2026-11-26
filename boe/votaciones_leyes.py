"""Cómo votó el Pleno del Congreso cada ley (votación final y, si la hubo, la del paso por el Senado).

Uso:
    python -m boe.votaciones_leyes      # escribe datos/congreso/votaciones_leyes.json

De qué leyes: las que el Senado recibió del Congreso (boe.senado, datos/senado.json), que son todas
las leyes de la legislatura. Su expediente en el Congreso se saca del boletín que cita la ficha del
Senado: en la serie A (proyectos de ley) el número es el del expediente (A-5 = 121/000005); en la
serie B (proposiciones), no, y se traduce con los enlaces al boletín del fichero «ProposicionesDeLey»
del Congreso. Si el boletín no está en ese fichero (las reformas de la Constitución, expedientes 100 y
101, no salen en ningún fichero de iniciativas del Congreso: «PropuestasDeReforma» son de Estatutos de
Autonomía), se lee el expediente de la portada del propio boletín (PDF, una vez).

Las votaciones: los índices diarios de votaciones del Congreso (boe.congreso) enlazan el JSON de
cada votación; se asigna a la ley la votación cuyo enlace sigue a la mención de su expediente. Qué
votación es lo dice el propio JSON (sin reglas sobre texto libre):
  - parte del orden del día «Dictámenes…» y «Votación del dictamen» → aprobación en el Congreso;
    «Votación de conjunto» → la de las leyes orgánicas, que necesita mayoría absoluta;
  - «Enmiendas del Senado» → una votación por enmienda o bloque; si es orgánica, otra de conjunto;
  - «Veto del Senado» → la votación para levantar el veto.
Las votaciones públicas por llamamiento no tienen JSON: solo sus totales, del índice.

Siempre agregado por grupo parlamentario (congreso.resumir_votacion); el voto de cada diputado queda
en datos/crudo/. Una ley ya guardada no se vuelve a buscar (la búsqueda recorre los índices de toda
la legislatura: en la Action, solo si llega una ley nueva).
"""

import argparse
import io
import json
import re
import time
from datetime import date, timedelta
from html import unescape
from pathlib import Path

import requests

from boe import congreso, tramitacion
from boe.clasificar import normalizar

CARPETA_DATOS = Path("datos")
INICIO = date(2023, 8, 17)  # constitución de las Cortes de la XV legislatura
FIN = date(2026, 10, 6)     # disolución
_RE_EXPEDIENTE = re.compile(r"expte\.\s*(\d{3}/\d{6})")
_RE_TOTALES = re.compile(r"Si:\s*(\d+)\s*No:\s*(\d+)\s*Abstenciones:\s*(\d+)")


def expediente_congreso(boletin, b_a_expediente):
    """'121/000005' a partir del boletín que cita el Senado ({'serie': 'A', 'numero': 5})."""
    if not boletin:
        return None
    if boletin["serie"] == "A":
        return f"121/{boletin['numero']:06d}"
    return b_a_expediente.get(boletin["numero"])


def boletines_de_proposiciones(proposiciones):
    """{número en la serie B del boletín: expediente} según ENLACESBOCG de cada proposición."""
    resultado = {}
    for p in proposiciones:
        m = re.match(r"(\d{3}/\d{6})", p.get("NUMEXPEDIENTE") or "")
        if not m:
            continue
        for b in re.finditer(r"BOCG-\d+-B-(\d+)-", p.get("ENLACESBOCG") or ""):
            resultado.setdefault(int(b.group(1)), m.group(1))
    return resultado


_RE_NUM_EXPEDIENTE = re.compile(r"\b(\d{3}/\d{6})\b")
URL_BOCG_B = "https://www.congreso.es/public_oficiales/L15/CONG/BOCG/B/BOCG-15-B-{}-1.PDF"


def expediente_de_portada(texto):
    """Primer número de expediente de la portada de un boletín (el de la iniciativa publicada; los que
    siguen son los de otras legislaturas a los que «corresponde»)."""
    m = _RE_NUM_EXPEDIENTE.search(texto or "")
    return m.group(1) if m else None


def expediente_del_boletin_b(numero, carpeta_datos=CARPETA_DATOS):
    """Expediente de una iniciativa de la serie B leyendo la portada de su boletín (BOCG-15-B-N-1)."""
    import pypdf
    archivo = Path(carpeta_datos) / "crudo" / "congreso" / "bocg" / f"BOCG-15-B-{numero}-1.PDF"
    if not archivo.exists():
        respuesta = requests.get(URL_BOCG_B.format(numero), headers=tramitacion.CABECERAS, timeout=60)
        time.sleep(tramitacion.PAUSA_SEGUNDOS)
        respuesta.raise_for_status()
        archivo.parent.mkdir(parents=True, exist_ok=True)
        archivo.write_bytes(respuesta.content)
    return expediente_de_portada(pypdf.PdfReader(io.BytesIO(archivo.read_bytes())).pages[0].extract_text())


def es_reforma_constitucional(expediente):
    """100: de grupos parlamentarios; 101: de comunidades autónomas; 102: del Gobierno."""
    return bool(expediente) and expediente[:4] in ("100/", "101/", "102/")


def etapa(info):
    """Qué votación es, según el JSON oficial: dictamen | conjunto | senado_enmienda | senado_conjunto |
    senado_veto | totalidad | otra."""
    seccion = normalizar(info.get("titulo"))
    texto = " ".join(normalizar(info.get(k)) for k in ("textoExpediente", "tituloSubGrupo", "textoSubGrupo"))
    if "veto" in seccion:
        return "senado_veto"
    if "enmiendas del senado" in seccion:
        return "senado_conjunto" if "votacion de conjunto" in texto else "senado_enmienda"
    if "totalidad" in seccion:
        return "totalidad"
    if "lectura unica" in seccion and "acuerdo" not in seccion:
        # «Tramitación directa y en lectura única»: el Pleno vota el texto entero una sola vez
        # (no el «Acuerdo de tramitación directa…», que solo decide tramitarla así).
        return "conjunto" if "votacion de conjunto" in texto else "dictamen" if "votacion" in texto else "otra"
    if "dictamen" in seccion:
        if "votacion de conjunto" in texto:
            return "conjunto"
        if re.search(r"votacion del (?:nuevo )?dictamen", texto):
            return "dictamen"
    return "otra"


def _limpio(html):
    return re.sub(r"\s+", " ", unescape(re.sub(r"<[^>]+>", " ", html)))


def votaciones_de_un_dia(html, expedientes):
    """[(expediente, ruta JSON o None, texto)] del índice de un día, solo de los expedientes pedidos.

    Cada enlace a un JSON se asigna al último expediente mencionado antes. Las votaciones por
    llamamiento no tienen enlace: se devuelven con ruta None y el texto con sus totales."""
    menciones = [(m.start(), m.group(1)) for m in _RE_EXPEDIENTE.finditer(html)]
    if not any(e in expedientes for _, e in menciones):
        return []
    resultado = []
    for m in congreso._RE_JSON.finditer(html):
        previo = [e for pos, e in menciones if pos < m.start()]
        if previo and previo[-1] in expedientes:
            resultado.append((previo[-1], m.group(0), None))
    for i, (pos, e) in enumerate(menciones):
        if e not in expedientes:
            continue
        hasta = menciones[i + 1][0] if i + 1 < len(menciones) else len(html)
        # Desde un poco antes de la mención: «(Pública por llamamiento)» puede ir delante del número.
        desde = max(menciones[i - 1][0] if i else 0, pos - 2000)
        tramo = _limpio(html[desde:hasta])
        if "llamamiento" not in tramo.lower():
            continue
        marca = tramo.find(f"expte. {e}")
        seccion = _seccion(_limpio(html[max(0, pos - 20000):pos]))
        inicio = 0
        for t in _RE_TOTALES.finditer(tramo):
            # Por llamamiento: «(Pública por llamamiento) … Si: … Detalle», sin enlace «XML JSON» detrás.
            antes, despues = tramo[inicio:t.start()], tramo[t.end():t.end() + 40]
            if t.start() > marca and "llamamiento" in antes.lower() and "JSON" not in despues:
                resultado.append((e, None, f"{seccion} {antes}{t.group(0)}"))
            inicio = t.end()
    return resultado


_RE_SECCION = re.compile(r"\b[IVXL]+\.\s+([A-ZÁÉÍÓÚ][^.]{3,90})\.")


def _seccion(texto):
    """Último encabezado de parte del orden del día («IX. Veto del Senado.») antes de una mención."""
    encabezados = _RE_SECCION.findall(texto)
    return encabezados[-1] if encabezados else ""


def _iso(ddmmaaaa):
    d, m, a = (ddmmaaaa or "").split("/")
    return f"{a}-{int(m):02d}-{int(d):02d}"  # el Congreso escribe «14/3/2024»


def votacion_resumida(ruta, carpeta_datos, listas):
    datos = congreso.votacion(ruta, carpeta_datos)
    info = datos["informacion"]
    return {"etapa": etapa(info), "fecha": _iso(info.get("fecha")), "titulo": " ".join((info.get("textoSubGrupo") or info.get("textoExpediente") or "").split()),
            "fuente": congreso.BASE + ruta, **congreso.resumir_votacion(datos, listas)}


def por_llamamiento(texto, dia):
    t = list(_RE_TOTALES.finditer(texto))[-1]
    tramo = normalizar(texto[:t.start()])
    e = ("senado_veto" if "veto" in tramo else "senado_conjunto" if "senado" in tramo and "conjunto" in tramo
         else "conjunto" if "conjunto" in tramo else "dictamen" if "dictamen" in tramo else "otra")
    return {"etapa": e, "fecha": dia.isoformat(), "titulo": "Votación pública por llamamiento", "solo_totales": True,
            "totales": {"afavor": int(t.group(1)), "enContra": int(t.group(2)), "abstenciones": int(t.group(3))}}


def resumen_ley(votaciones):
    """La votación final en el Congreso y la del paso por el Senado (la última de cada tipo)."""
    def ultima(*etapas):
        v = [x for x in votaciones if x["etapa"] in etapas]
        return v[-1] if v else None
    final = ultima("conjunto") or ultima("dictamen")  # en las orgánicas decide la de conjunto
    senado = ultima("senado_veto") or ultima("senado_conjunto")
    return {"final": final, "tras_senado": senado,
            "votaciones_enmiendas_senado": sum(1 for x in votaciones if x["etapa"] == "senado_enmienda")}


def procesar(carpeta_datos=CARPETA_DATOS, hoy=None):
    carpeta_datos = Path(carpeta_datos)
    hoy = hoy or date.today()
    salida = carpeta_datos / "congreso" / "votaciones_leyes.json"
    guardadas = {x["senado"]: x for x in (json.loads(salida.read_text(encoding="utf-8"))["leyes"] if salida.exists() else [])}
    senado = json.loads((carpeta_datos / "senado.json").read_text(encoding="utf-8"))["iniciativas"]
    pendientes = [i for i in senado if i.get("boe") and i["expediente"] not in guardadas]
    if not pendientes:
        return 0
    proposiciones = tramitacion.fichero_iniciativas("ProposicionesDeLey", carpeta_datos, hoy)
    b_a_exp = boletines_de_proposiciones(proposiciones)
    # Tipo de tramitación («Urgente», «Lectura Única», «Competencia Legislativa Plena»…): con competencia
    # legislativa plena la aprueba una comisión y no hay votación final en el Pleno.
    tipo_de = {m.group(1): " ".join((x.get("TIPOTRAMITACION") or "").split()) or None
               for x in tramitacion.proyectos_de_ley(carpeta_datos, hoy) + proposiciones
               for m in [re.match(r"(\d{3}/\d{6})", x.get("NUMEXPEDIENTE") or "")] if m}
    for i in pendientes:
        b = i.get("boletin_congreso")
        if b and b["serie"] == "B" and b["numero"] not in b_a_exp:
            b_a_exp[b["numero"]] = expediente_del_boletin_b(b["numero"], carpeta_datos)
    expediente_de = {i["expediente"]: expediente_congreso(i.get("boletin_congreso"), b_a_exp) for i in pendientes}
    buscados = {e for e in expediente_de.values() if e}
    encontradas = {e: [] for e in buscados}
    listas = congreso.listas_electorales(carpeta_datos)
    dia = INICIO
    while dia <= min(FIN, hoy):
        if dia.weekday() < 5:
            html = congreso.indice_del_dia(dia, carpeta_datos, hoy)
            for e, ruta, texto in votaciones_de_un_dia(html or "", buscados):
                encontradas[e].append(votacion_resumida(ruta, carpeta_datos, listas) if ruta else por_llamamiento(texto, dia))
        dia += timedelta(days=1)
    for i in pendientes:
        e = expediente_de[i["expediente"]]
        votaciones = sorted(encontradas.get(e, []), key=lambda v: v["fecha"])
        guardadas[i["expediente"]] = {"senado": i["expediente"], "congreso": e, "boe": i["boe"], "titulo": i["titulo"],
                                      "tramitacion": tipo_de.get(e),
                                      **({"reforma_constitucional": True} if es_reforma_constitucional(e) else {}),
                                      **resumen_ley(votaciones)}
    lista = sorted(guardadas.values(), key=lambda x: x["senado"])
    salida.parent.mkdir(parents=True, exist_ok=True)
    salida.write_text(json.dumps({"fuente": "https://www.congreso.es/es/opendata/votaciones", "leyes": lista},
                                 ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return len(pendientes)


def main():
    argparse.ArgumentParser(description="Votación final de cada ley en el Pleno del Congreso.").parse_args()
    print(f"Leyes con la votación buscada: {procesar()}")


if __name__ == "__main__":
    main()
