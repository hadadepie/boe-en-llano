"""Paso 5: preparar los archivos que lee la web (carpeta web/datos/).

Uso:
    python -m boe.exportar

Junta datos/recuentos.json y datos/normas/*.json, agrupa las secciones como se
muestran en la web (la V suma V.A + V.B + V.C) y calcula la cabecera.

Para que la portada cargue poco, el resultado se parte en tres niveles:
- web/datos/indice.json: la lista ligera de ediciones (id, etiqueta, fechas,
  archivo, cuántas normas y días con datos) y las cifras de la legislatura.
  No crece con el detalle de cada semana: así la portada carga poco aunque
  haya años de ediciones.
- web/datos/semanas/<semana>.json: lo de una edición: su resumen, «La semana en
  datos», votaciones y seguimiento («edicion»), sus recuentos por día («dias») y
  sus normas, sin el antes y el después y solo con el primer párrafo del preámbulo.
- web/datos/normas/<id>.json: lo que se lee al abrir la ficha (preámbulo
  completo, «cambios» y «cambios_recibidos»).
- web/datos/buscar.json: una línea por norma (id, fecha, titular, tema, impacto)
  para el buscador; la web lo descarga solo cuando alguien busca.
- web/datos/informe.json: las cifras del informe de la legislatura (boe.informe), que
  solo carga «La legislatura».
- web/datos/feed.xml: canal RSS con las últimas normas, para seguir la web sin entrar.
La carpeta web/datos/ es generada: no se versiona (está en .gitignore).
"""

import json
import re
import shutil
from datetime import date, datetime, timezone
from email.utils import format_datetime
from pathlib import Path
from xml.sax.saxutils import escape

from boe import informe
from boe.clasificar import IMPACTOS, TEMAS
from boe.resumir import titular_corto, titulo_simplificado

CARPETA_DATOS = Path("datos")
CARPETA_WEB = Path("web/datos")
URL_WEB = "https://hadadepie.github.io/boe-en-llano/"  # la misma que en las etiquetas para compartir de web/*.html
MAX_RSS = 50

# Sección de la API -> sección que se muestra en la web.
SECCIONES_WEB = [
    ("I", "I. Disposiciones generales", ["1"]),
    ("II.A", "II.A Nombramientos y situaciones", ["2A"]),
    ("II.B", "II.B Oposiciones y concursos", ["2B"]),
    ("III", "III. Otras disposiciones", ["3"]),
    ("IV", "IV. Administración de Justicia", ["4"]),
    ("V", "V. Anuncios", ["5A", "5B", "5C"]),
    # Al final, para que las demás secciones conserven su color en la web (--s1…--s6).
    ("TC", "TC. Sentencias del Tribunal Constitucional", ["T"]),
]
_SECCION_DE_CODIGO = {c: web for web, _, codigos in SECCIONES_WEB for c in codigos}

MESES = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto",
         "septiembre", "octubre", "noviembre", "diciembre"]


def miles(n):
    """1516 -> '1.516' (separador de miles español)."""
    return f"{n:,}".replace(",", ".")


def porcentaje(parte, total):
    """52, 1516 -> '3,4 %'."""
    if not total:
        return "0 %"
    return f"{100 * parte / total:.1f}".replace(".", ",") + " %"


def fecha_larga(iso, con_año=True):
    d = date.fromisoformat(iso)
    texto = f"{d.day} de {MESES[d.month - 1]}"
    return f"{texto} de {d.year}" if con_año else texto


def agrupar_recuento(recuento_api):
    """{'1': 27, '5A': 73, '5B': 62} -> {'I': 27, ..., 'V': 135} (con ceros)."""
    agrupado = {web: 0 for web, _, _ in SECCIONES_WEB}
    for codigo, cantidad in recuento_api.items():
        web = _SECCION_DE_CODIGO.get(codigo)
        if web is None:
            print(f"AVISO: sección desconocida {codigo!r}; no se muestra en el gráfico.")
            continue
        agrupado[web] += cantidad
    return agrupado


def frase_resumen(dias, normas):
    """Frase de cabecera calculada solo a partir de los datos."""
    if not dias:
        return "Todavía no hay días descargados."
    total = sum(sum(d["recuento"].values()) for d in dias)
    generales = sum(d["recuento"]["I"] for d in dias)
    directas = sum(1 for n in normas if n.get("impacto") == "Directo")

    primero, ultimo = dias[0]["fecha"], dias[-1]["fecha"]
    if primero == ultimo:
        cuando = f"El {fecha_larga(primero)}"
    elif primero[:7] == ultimo[:7]:
        cuando = f"Entre el {date.fromisoformat(primero).day} y el {fecha_larga(ultimo)}"
    else:
        cuando = f"Entre el {fecha_larga(primero, con_año=primero[:4] != ultimo[:4])} y el {fecha_larga(ultimo)}"

    frase = f"{cuando}, el BOE publicó {miles(total)} textos. Solo {miles(generales)} ({porcentaje(generales, total)}) "
    if generales == 1:  # semanas de agosto o sueltas
        frase += "es una norma general"
        return frase + (" y cambia algo para mucha gente." if directas else
                        " y no cambia algo para mucha gente de forma directa.")
    frase += "son normas generales"
    if directas == 0:
        return frase + " y ninguna cambia algo para mucha gente de forma directa."
    if directas == 1:
        return frase + " y 1 cambia algo para mucha gente."
    return frase + f" y {miles(directas)} cambian algo para mucha gente."


# ---------- Relevancia (para elegir titulares) ----------
# Reglas sencillas y explicables. Pesa sobre todo a quién afecta; después, que
# sea estatal (llega a más gente que una autonómica), el rango de la norma y que
# el titular se entienda (corto y sin referencias tipo "Ley 1/2005").
PESO_IMPACTO = {"Directo": 100, "Colectivos": 50, "Técnico": 0}
PESO_RANGO = {"Ley Orgánica": 12, "Ley": 10, "Real Decreto-ley": 9, "Decreto-ley": 8,
              "Real Decreto Legislativo": 7, "Real Decreto": 6, "Orden": 4, "Resolución": 2}
PESO_ESTATAL = 10
PESO_TITULAR_CLARO = 6
MAX_TITULAR_CLARO = 90


def titular_claro(titular):
    """Corto, sin referencias a otras normas ("1/2005") y sin empezar por "Se modifica"."""
    t = (titular or "").strip()
    return (len(t) <= MAX_TITULAR_CLARO
            and not re.search(r"\d+/\d{4}", t)
            and not re.match(r"(se modifica|modificación|corrección)", t, re.IGNORECASE))


def relevancia(n):
    puntos = PESO_IMPACTO.get(n.get("impacto"), 0) + PESO_RANGO.get(n.get("rango"), 0)
    if n.get("ambito") == "Estatal":
        puntos += PESO_ESTATAL
    if titular_claro((n.get("ficha") or {}).get("titulo_llano")):
        puntos += PESO_TITULAR_CLARO
    if (n.get("ficha") or {}).get("estado") == "ok":
        puntos += 1
    return puntos


# ---------- Semanas (ediciones) ----------

def semana_de(iso):
    """'2026-11-20' -> '2026-S47' (semana ISO: de lunes a domingo)."""
    año, semana, _ = date.fromisoformat(iso).isocalendar()
    return f"{año}-S{semana:02d}"


def etiqueta_semana(fechas):
    """Rango de días con BOE de la semana: 'Semana del 16 al 21 de noviembre de 2026'."""
    primero, ultimo = min(fechas), max(fechas)
    if primero == ultimo:
        return f"Edición del {fecha_larga(primero)}"
    if primero[:7] == ultimo[:7]:
        return f"Semana del {date.fromisoformat(primero).day} al {fecha_larga(ultimo)}"
    return f"Semana del {fecha_larga(primero, con_año=primero[:4] != ultimo[:4])} al {fecha_larga(ultimo)}"


def resumen(dias, normas):
    total = sum(sum(d["recuento"].values()) for d in dias)
    generales = sum(d["recuento"]["I"] for d in dias)
    return {
        "frase": frase_resumen(dias, normas),
        "total_publicaciones": total,
        "normas_generales": generales,
        "porcentaje_normas": porcentaje(generales, total),
        "impacto_directo": sum(1 for n in normas if n["impacto"] == "Directo"),
        "fichas_verificadas": sum(1 for n in normas if (n["ficha"] or {}).get("estado") == "ok"),
    }


# ---------- Piezas automáticas ("La semana en datos") ----------
# Datos que se sacan del tipo de norma, del ámbito y del título oficial: no
# hay interpretación ni IA. Cada pieza guarda los identificadores de sus normas
# para poder verlas en la lista.

def _plural(n, singular, plural):
    return singular if n == 1 else plural


def piezas_semana(normas):
    piezas = []

    def anadir(seleccion, texto):
        if seleccion:
            piezas.append({"cifra": len(seleccion), "texto": texto, "ids": [n["id"] for n in seleccion]})

    rdl = [n for n in normas if n.get("rango") == "Real Decreto-ley"]
    anadir(rdl, _plural(len(rdl), "real decreto-ley aprobado por el Gobierno",
                        "reales decretos-ley aprobados por el Gobierno"))

    leyes_estado = [n for n in normas if n.get("rango") in ("Ley", "Ley Orgánica") and n.get("ambito") == "Estatal"]
    anadir(leyes_estado, _plural(len(leyes_estado), "ley aprobada por las Cortes", "leyes aprobadas por las Cortes"))

    leyes_ccaa = [n for n in normas if n.get("rango") in ("Ley", "Ley Orgánica") and n.get("ambito") != "Estatal"]
    if leyes_ccaa:
        por_ccaa = {}
        for n in leyes_ccaa:
            por_ccaa[n["ambito"]] = por_ccaa.get(n["ambito"], 0) + 1
        detalle = ", ".join(f"{c} ({k})" for c, k in sorted(por_ccaa.items(), key=lambda x: (-x[1], x[0])))
        anadir(leyes_ccaa, f"{_plural(len(leyes_ccaa), 'ley autonómica', 'leyes autonómicas')}: {detalle}")

    titulo = lambda n: (n.get("titulo") or "").lower()
    convalidados = [n for n in normas if "acuerdo de convalidación" in titulo(n)]
    anadir(convalidados, _plural(len(convalidados), "real decreto-ley convalidado por el Congreso",
                                 "reales decretos-ley convalidados por el Congreso"))

    derogados = [n for n in normas if "acuerdo de derogación" in titulo(n)]
    anadir(derogados, _plural(len(derogados), "real decreto-ley rechazado (derogado) por el Congreso",
                              "reales decretos-ley rechazados (derogados) por el Congreso"))

    subvenciones = [n for n in normas if "concesión directa" in titulo(n)]
    anadir(subvenciones, _plural(len(subvenciones), "subvención o préstamo directo a entidades concretas",
                                 "subvenciones o préstamos directos a entidades concretas"))

    correcciones = [n for n in normas if n.get("rango") == "Corrección (errores o erratas)"]
    anadir(correcciones, _plural(len(correcciones), "corrección de errores", "correcciones de errores"))
    return piezas


def pieza_votaciones(votaciones, normas_semana):
    if not votaciones:
        return None
    resultados = [v["convalidacion"]["resultado"] for v in votaciones]
    partes = []
    if resultados.count("convalidado"):
        partes.append(f"{resultados.count('convalidado')} {_plural(resultados.count('convalidado'), 'convalidado', 'convalidados')}")
    if resultados.count("derogado"):
        partes.append(f"{resultados.count('derogado')} {_plural(resultados.count('derogado'), 'derogado', 'derogados')}")
    ids_semana = {n["id"] for n in normas_semana}
    return {"cifra": len(votaciones),
            "texto": f"{_plural(len(votaciones), 'real decreto-ley votado', 'reales decretos-ley votados')} "
                     f"en el Pleno del Congreso ({' y '.join(partes)})",
            "ids": sorted({i for v in votaciones for i in v["ids"] if i in ids_semana}),
            # Los votados de otras semanas: la portada enlaza a su ficha (la semana se deduce del id).
            "otras": [{"id": v["ids"][0], "rdl": v["rdl"], "titulo": v["titulo"], "resultado": v["convalidacion"]["resultado"]}
                      for v in votaciones if v["ids"] and v["ids"][0] not in ids_semana],
            "votaciones": True}


def ediciones(dias, normas, hoy=None, convalidaciones=None):
    """Una edición por semana, de la más reciente a la más antigua."""
    hoy = hoy or date.today()
    # El domingo no hay BOE: ese día la semana ya está completa.
    semana_actual = None if hoy.isoweekday() == 7 else semana_de(hoy.isoformat())
    resultado = []
    for clave in sorted({semana_de(d["fecha"]) for d in dias}, reverse=True):
        dias_semana = [d for d in dias if semana_de(d["fecha"]) == clave]
        normas_semana = [n for n in normas if n["semana"] == clave]
        resultado.append({
            "id": clave,
            "etiqueta": etiqueta_semana([d["fecha"] for d in dias_semana]),
            "desde": dias_semana[0]["fecha"],
            "hasta": dias_semana[-1]["fecha"],
            "en_curso": clave == semana_actual,
            "resumen": resumen(dias_semana, normas_semana),
            "piezas": piezas_semana(normas_semana),
            "votaciones": votaciones_semana(convalidaciones or {}, normas, dias_semana[0]["fecha"], dias_semana[-1]["fecha"]),
        })
        pieza = pieza_votaciones(resultado[-1]["votaciones"], normas_semana)
        if pieza:
            resultado[-1]["piezas"].insert(0, pieza)
    return resultado


# ---------- Seguimiento: qué pasa esta semana con normas de semanas anteriores ----------
# Quien lee cada semana ve las normas cuando se publican, no lo que les pasa después.
# Cada edición recoge los hechos con fecha en esa semana sobre normas publicadas antes
# (en semanas anteriores o días antes en la misma semana):
# votaciones del Pleno y acuerdos de la Diputación Permanente sobre reales decretos-ley
# (boe.legislatura) y cambios que registra la legislación consolidada (vida de la norma).

# Relaciones de «vida de la norma» que cuentan como novedad (no las correcciones de erratas).
RELACIONES_SEGUIMIENTO = {"Se modifica": "Modificada", "Se deroga": "Derogada", "Se deja sin efecto": "Sin efecto",
                          "Se suspende": "Suspendida", "Se anula": "Anulada", "Se declara nulo": "Anulada"}
# Lo que ya cuentan las votaciones de los decretos-ley (se omite para no repetirlo).
def _es_acuerdo_del_congreso(h):
    """«Se publica acuerdo de convalidación…» o «Se deroga por Resolución…» (del Congreso)."""
    return ("acuerdo de convalidaci" in (h.get("relacion") or "").lower()
            or (h.get("texto") or "").lower().startswith("por resolución"))


def seguimiento_semanas(normas, legislatura):
    """{semana: [hecho, …]} con lo ocurrido en cada semana a normas publicadas antes (aunque sea esa misma semana)."""
    propias = {n["id"]: n for n in normas}
    rdl_con_votacion = {}  # número -> resultado
    por_semana = {}

    def anadir(fecha, publicada, hecho):
        if fecha and publicada and fecha > publicada:
            por_semana.setdefault(semana_de(fecha), []).append({"fecha": fecha, "publicada": publicada, **hecho})

    for x in (legislatura or {}).get("decretos_ley") or []:
        if x.get("resultado") not in ("convalidado", "derogado") or not x.get("fecha_publicacion"):
            continue
        rdl_con_votacion[x["rdl"]] = x["resultado"]
        verbo = "convalidó" if x["resultado"] == "convalidado" else "derogó"
        if x.get("organo") == "Pleno":
            fecha = x.get("fecha")
            texto = (f"El Congreso {verbo} el Real Decreto-ley {x['rdl']}, según el acuerdo publicado en el BOE "
                     f"(los datos abiertos del Congreso registran {x['afavor']} sí y {x['enContra']} no)." if x.get("discrepancia")
                     else f"El Congreso {verbo} el Real Decreto-ley {x['rdl']}: {x['afavor']} sí, {x['enContra']} no"
                     + (" (empate)." if x.get("empate") else "."))
        else:
            fecha = x.get("publicado_boe")
            texto = f"La Diputación Permanente del Congreso {verbo} el Real Decreto-ley {x['rdl']} (acuerdo publicado en el BOE)."
        anadir(fecha, x["fecha_publicacion"], {
            "tipo": x["resultado"], "etiqueta": "Convalidado" if x["resultado"] == "convalidado" else "Derogado",
            "texto": texto, "id": x.get("id_boe"), "titular": x.get("titular") or f"Real Decreto-ley {x['rdl']}",
            "en_web": x.get("id_boe") in propias})

    for n in normas:
        votacion = rdl_con_votacion.get(n.get("numero_oficial")) if n.get("rango") == "Real Decreto-ley" else None
        for h in (n.get("vida") or {}).get("despues") or []:
            etiqueta = RELACIONES_SEGUIMIENTO.get(h.get("relacion"))
            if not etiqueta or (votacion and _es_acuerdo_del_congreso(h)):
                continue
            # Lo que el BOE deja «sin efecto» al derogarse un decreto-ley ya lo cuenta la derogación.
            if votacion == "derogado" and h.get("relacion") == "Se deja sin efecto":
                continue
            anadir(h.get("fecha"), n["fecha"], {
                "tipo": "cambio", "etiqueta": etiqueta, "texto": f"{h['relacion']} {h.get('texto') or ''}".strip() + ".",
                "id": n["id"], "titular": n.get("titular") or n["titulo"], "en_web": True, "por": h.get("id")})

    for hechos in por_semana.values():
        hechos.sort(key=lambda h: (h["fecha"], h["titular"]), reverse=True)
    return por_semana


# ---------- Votaciones del Congreso (convalidación de reales decretos-ley) ----------

NOMBRE_CORTO_GRUPO = {
    "GP": "PP", "GS": "PSOE", "GVOX": "Vox", "GSUMAR": "Sumar", "GMx": "Mixto",
    "GJxCAT": "Junts", "GR": "ERC", "GEH Bildu": "EH Bildu", "GV (EAJ-PNV)": "PNV",
}
_RE_RDL_TITULO = re.compile(r"Real Decreto-ley (\d+/\d{4})")


# De cada real decreto-ley de la legislatura, lo que necesita la web (boe.decretos_ley).
CAMPOS_DECRETO = ("id_boe", "tema", "normas_modificadas", "fecha_publicacion")


def leer_legislatura(carpeta_datos):
    """Cifras de convalidación de la legislatura (boe.legislatura) con el tema y el tamaño
    de cada decreto-ley (boe.decretos_ley), si existen."""
    archivo = Path(carpeta_datos) / "congreso" / "legislatura_xv.json"
    if not archivo.exists():
        return None
    legislatura = json.loads(archivo.read_text(encoding="utf-8"))
    extra = Path(carpeta_datos) / "congreso" / "decretos_ley_xv.json"
    if extra.exists():
        decretos = json.loads(extra.read_text(encoding="utf-8")).get("decretos") or {}
        for x in legislatura["decretos_ley"]:
            d = decretos.get(x["rdl"]) or {}
            if d.get("encontrado"):
                x.update({k: d.get(k) for k in CAMPOS_DECRETO})
                x["titular"] = titular_corto(titulo_simplificado(d["titulo"]))
    return legislatura


def leer_convalidaciones(carpeta_datos):
    archivo = Path(carpeta_datos) / "congreso" / "convalidaciones.json"
    return json.loads(archivo.read_text(encoding="utf-8")) if archivo.exists() else {}


def leer_senado(carpeta_datos):
    """Iniciativas que el Senado recibió del Congreso (boe.senado), o [] si no se han descargado."""
    archivo = Path(carpeta_datos) / "senado.json"
    return json.loads(archivo.read_text(encoding="utf-8"))["iniciativas"] if archivo.exists() else []


def enlazar_senado(normas, iniciativas):
    """Pone en cada ley lo que hizo con ella el Senado (por su id del BOE)."""
    por_id = {n["id"]: n for n in normas}
    for i in iniciativas:
        for id_boe in i.get("boe") or []:
            if id_boe in por_id:
                p = i.get("presentadas") or {}
                por_id[id_boe]["senado"] = {
                    "expediente": i["expediente"], "resultado": i["resultado"], "congreso": i.get("congreso"),
                    "enmiendas_presentadas": p.get("enmiendas"), "vetos_presentados": p.get("vetos"), "url": i.get("url")}


def leer_sentencias_tc(carpeta_datos):
    """Sentencias y autos del Tribunal Constitucional sobre normas (boe.sentencias_tc), o []."""
    archivo = Path(carpeta_datos) / "sentencias_tc.json"
    return json.loads(archivo.read_text(encoding="utf-8"))["sentencias"] if archivo.exists() else []


def enlazar_sentencias_tc(normas, sentencias):
    """En cada norma juzgada, lo que decidió el Constitucional; en cada admisión a trámite, qué la resolvió."""
    por_id = {n["id"]: n for n in normas}
    for s in sentencias:
        base = {"id": s["id"], "rango": s["rango"], "numero": s["numero"], "fecha": s["fecha"], "tipo": s["tipo"], "asunto": s["asunto"]}
        for j in s["normas"]:
            if j["id"] in por_id:
                por_id[j["id"]].setdefault("sentencias_tc", []).append({**base, "resultado": j["resultado"], "texto": j["texto"]})
        for a in s["admisiones"]:
            if a in por_id and s["rango"] == "Sentencia":
                por_id[a]["resuelto_por"] = {**base, "resultados": sorted({j["resultado"] for j in s["normas"]})}
    # En «qué ha pasado después» (legislación consolidada) las sentencias salen sin fecha: se la ponemos.
    fecha_de = {s["id"]: s["fecha"] for s in sentencias}
    for n in normas:
        despues = (n.get("vida") or {}).get("despues") or []
        if any(h.get("id") in fecha_de and not h.get("fecha") for h in despues):
            for h in despues:
                if h.get("id") in fecha_de and not h.get("fecha"):
                    h["fecha"] = fecha_de[h["id"]]
            despues.sort(key=lambda h: (h.get("fecha") or "9999", h["relacion"]))


def corregir_con_legislatura(convalidaciones, legislatura):
    """Si boe.legislatura detectó que el BOE publicó otro resultado (discrepancia), la votación
    con detalle por grupos toma ese resultado y lleva la explicación."""
    discrepancias = {x["rdl"]: x for x in (legislatura or {}).get("decretos_ley") or [] if x.get("discrepancia")}
    for r in convalidaciones.values():
        x = discrepancias.get(r.get("rdl"))
        if x and r.get("convalidacion"):
            r["estado"] = r["convalidacion"]["resultado"] = x["resultado"]
            r["discrepancia"] = x["discrepancia"]
    return convalidaciones


def listas_divididas(por_lista):
    """¿Las listas electorales de un grupo votaron mayoritariamente distinto?

    Así el desglose aparece en grupos como el Mixto (BNG sí, UPN no) y no en
    grupos cuyas listas son marcas territoriales que votan igual (PSC y PSOE).
    """
    if not por_lista or len(por_lista) < 2:
        return False
    mayoritario = {lista: max(votos, key=votos.get) for lista, votos in por_lista.items() if votos}
    return len(set(mayoritario.values())) > 1


def votacion_para_web(registro):
    """Lo que la web necesita de una convalidación (siempre agregado, sin nombres)."""
    web = {"rdl": registro.get("rdl"), "estado": registro.get("estado"), "nota": registro.get("nota")}
    if registro.get("discrepancia"):
        web["discrepancia"] = registro["discrepancia"]
    v = registro.get("convalidacion")
    if v:
        web["convalidacion"] = {
            "fecha": v["fecha"], "resultado": v["resultado"], "totales": v["totales"],
            "telematicos": v["telematicos"], "fuente_pdf": v.get("fuente_pdf"), "fuente": v.get("fuente"),
            "solo_totales": v.get("solo_totales", False), "nota": v.get("nota"),
            "grupos": [{"codigo": g, "nombre": NOMBRE_CORTO_GRUPO.get(g, v["nombres_grupo"].get(g, g)),
                        "nombre_completo": v["nombres_grupo"].get(g, g), "votos": votos,
                        "por_lista": v["por_lista"].get(g) if listas_divididas(v["por_lista"].get(g)) else None}
                       for g, votos in v["por_grupo"].items()],
        }
    t = registro.get("tramitacion")
    if t:
        web["tramitacion"] = {"resultado": t["resultado"], "totales": t["totales"], "fecha": t["fecha"]}
    return web


def acuerdo_diputacion_permanente(x):
    """Lo que se sabe de un decreto-ley convalidado o derogado por la Diputación Permanente
    (boe.legislatura, por la resolución publicada en el BOE): resultado, sin cifras."""
    verbo = "convalidó" if x["resultado"] == "convalidado" else "derogó"
    publicado = f", publicado en el BOE el {fecha_larga(x['publicado_boe'])}" if x.get("publicado_boe") else ""
    return {"rdl": x["rdl"], "estado": x["resultado"], "organo": "Diputación Permanente",
            "nota": f"Lo {verbo} la Diputación Permanente del Congreso, con las Cortes disueltas (acuerdo{publicado}). "
                    "Sus votaciones no están en los datos abiertos: no hay cifras ni voto por grupos."}


def enlazar_votaciones(normas, convalidaciones, legislatura=None):
    """Añade 'congreso' a cada real decreto-ley y a las resoluciones que publican su convalidación.

    Las votaciones del Pleno salen de boe.congreso; lo que acordó la Diputación Permanente,
    que no está en los datos abiertos de votaciones, de boe.legislatura."""
    por_rdl = {r["rdl"]: votacion_para_web(r) for r in convalidaciones.values() if r.get("rdl")}
    for x in (legislatura or {}).get("decretos_ley") or []:
        resuelto = (por_rdl.get(x["rdl"]) or {}).get("estado") in ("convalidado", "derogado")
        if not resuelto and x.get("organo") == "Diputación Permanente" and x.get("resultado") in ("convalidado", "derogado"):
            por_rdl[x["rdl"]] = acuerdo_diputacion_permanente(x)
    for n in normas:
        if n.get("rango") == "Real Decreto-ley":
            rdl = n.get("numero_oficial") or (_RE_RDL_TITULO.search(n["titulo"]) or [None, None])[1]
        elif re.search(r"acuerdo de (convalidación|derogación)", n["titulo"], re.IGNORECASE):
            m = _RE_RDL_TITULO.search(n["titulo"])
            rdl = m.group(1) if m else None
        else:
            continue
        if rdl in por_rdl:
            n["congreso"] = por_rdl[rdl]


# ---------- ¿Quién decidió? ¿Se votó? ----------
# Separa lo que se vota en un parlamento de lo que decide el Gobierno, un tribunal o otra
# administración. Solo se afirma lo que se sabe por el tipo de norma y los datos del Congreso.
DECISIONES = ["votada", "pendiente", "gobierno", "autonomica", "tribunal", "otra"]
_RANGOS_GOBIERNO = {"Real Decreto", "Decreto", "Orden", "Resolución", "Circular", "Instrucción"}


def decision_de(n):
    """Clave de DECISIONES de una norma ya enlazada con las votaciones del Congreso.

    votada: ley estatal (Cortes) o real decreto-ley con votación de convalidación registrada
            (también las resoluciones que publican esa votación).
    pendiente: real decreto-ley sin votación conocida (aún en plazo, o votado en la Diputación
            Permanente, cuyas votaciones no están en los datos abiertos).
    gobierno: norma estatal del Gobierno o la Administración, sin votación parlamentaria.
    autonomica: cualquier norma de una comunidad autónoma (no recogemos sus votaciones).
    tribunal: sentencias y providencias.
    otra: acuerdos internacionales, correcciones de errores y el resto."""
    rango = n.get("rango")
    if rango in ("Sentencia", "Providencia"):
        return "tribunal"
    if n.get("ambito") not in (None, "Estatal"):
        return "autonomica"
    congreso = n.get("congreso") or {}
    if rango == "Real Decreto-ley":
        return "votada" if congreso.get("estado") in ("convalidado", "derogado") else "pendiente"
    if congreso.get("convalidacion"):
        return "votada"
    if rango in ("Ley", "Ley Orgánica"):
        return "votada"
    if rango in _RANGOS_GOBIERNO:
        return "gobierno"
    return "otra"


def asignar_decision(normas):
    for n in normas:
        n["decision"] = decision_de(n)


def votaciones_semana(convalidaciones, normas, desde, hasta):
    """Votaciones de convalidación celebradas entre `desde` y `hasta` (ambos incluidos)."""
    resultado = []
    for r in convalidaciones.values():
        v = r.get("convalidacion")
        if not v or not (desde <= v["fecha"] <= hasta):
            continue
        ids = [n["id"] for n in normas if (n.get("congreso") or {}).get("rdl") == r["rdl"]]
        resultado.append({**votacion_para_web(r), "titulo": r["titulo"], "id_norma": r["id"], "ids": ids})
    return sorted(resultado, key=lambda x: (x["convalidacion"]["fecha"], x["rdl"]))


def fechar_vida(normas):
    """Pone fecha a los hechos posteriores cuya norma tenemos guardada.

    El BOE describe los hechos posteriores con texto ("por Real Decreto-ley
    38/2026, de 17 de noviembre"), a veces sin año: si la norma que los causa
    está en nuestros datos, se usa su fecha de publicación.
    """
    fecha_de = {n["id"]: n["fecha"] for n in normas}
    for n in normas:
        for hecho in (n.get("vida") or {}).get("despues", []):
            if hecho.get("id") in fecha_de:
                hecho["fecha"] = fecha_de[hecho["id"]]
        if n.get("vida") and n["vida"].get("despues"):
            n["vida"]["despues"].sort(key=lambda h: (h.get("fecha") or "9999", h["relacion"]))


def enlazar_cambios_recibidos(normas, guardados):
    """Une el antes y el después calculado desde los dos lados.

    - Desde la modificadora ("cambios"): se añade a la modificada como recibido.
    - Desde la modificada ("cambios_recibidos" guardados): se añade a la
      modificadora como cambio, con la referencia del análisis.
    """
    por_id = {n["id"]: n for n in normas}
    for n in normas:
        n["cambios_recibidos"] = []
    for n in normas:
        for c in n.get("cambios") or []:
            destino = por_id.get(c["norma"])
            if destino is not None and c.get("bloques"):
                destino["cambios_recibidos"].append({"por": n["id"], "bloques": c["bloques"]})
    for id_destino, recibidos in guardados.items():
        destino = por_id.get(id_destino)
        for r in recibidos:
            if not r.get("bloques") or destino is None:
                continue
            if not any(x["por"] == r["por"] for x in destino["cambios_recibidos"]):
                destino["cambios_recibidos"].append({"por": r["por"], "bloques": r["bloques"]})
            origen = por_id.get(r["por"])
            if origen is not None and not any(c["norma"] == id_destino for c in origen.get("cambios") or []):
                origen["cambios"] = (origen.get("cambios") or []) + [{
                    "norma": id_destino, "relacion": "Modifica", "consolidada": True, "bloques": r["bloques"],
                    "referencia": f"{destino['titulo'][:160]}"}]


def norma_para_web(n):
    return {
        "id": n["id"],
        "fecha": n["fecha_publicacion"],
        "rango": n.get("rango"),
        "organo": n.get("departamento") or n.get("departamento_sumario"),
        "titulo": n["titulo"],
        # Titular recortado para portada y listas; la ficha usa ficha.titulo_llano completo.
        "titular": titular_corto((n.get("ficha") or {}).get("titulo_llano") or n["titulo"]),
        "url_html": n.get("url_html"),
        "url_pdf": n.get("url_pdf"),
        "fecha_vigencia": n.get("fecha_vigencia"),
        "tema": n.get("tema"),
        "impacto": n.get("impacto"),
        "ambito": n.get("ambito"),
        "clasificacion": n.get("clasificacion"),
        "ficha": n.get("ficha"),
        "semana": semana_de(n["fecha_publicacion"]),
        "relevancia": relevancia(n),
        "numero_oficial": n.get("numero_oficial"),
        "preambulo": n.get("preambulo"),
        "textos_oficiales": n.get("textos_oficiales") or {},
        "creditos": n.get("creditos") or [],
        "vida": n.get("vida"),
        "cambios": n.get("cambios"),
        "tramitacion": n.get("tramitacion"),
    }


def construir(carpeta_datos=CARPETA_DATOS):
    carpeta_datos = Path(carpeta_datos)
    archivo_recuentos = carpeta_datos / "recuentos.json"
    recuentos = json.loads(archivo_recuentos.read_text(encoding="utf-8")) if archivo_recuentos.exists() else {}
    dias = [{"fecha": f, "recuento": agrupar_recuento(r)} for f, r in sorted(recuentos.items())]

    normas = [json.loads(p.read_text(encoding="utf-8")) for p in sorted((carpeta_datos / "normas").glob("*.json"))]
    guardados = {n["id"]: n.get("cambios_recibidos") or [] for n in normas}
    crudas = normas
    normas = [norma_para_web(n) for n in normas]
    normas.sort(key=lambda n: (n["fecha"], n["id"]), reverse=True)
    legislatura = leer_legislatura(carpeta_datos)
    convalidaciones = corregir_con_legislatura(leer_convalidaciones(carpeta_datos), legislatura)
    enlazar_votaciones(normas, convalidaciones, legislatura)
    asignar_decision(normas)
    fechar_vida(normas)
    enlazar_cambios_recibidos(normas, guardados)
    senado = leer_senado(carpeta_datos)
    enlazar_senado(normas, senado)
    sentencias = leer_sentencias_tc(carpeta_datos)
    enlazar_sentencias_tc(normas, sentencias)

    lista_ediciones = ediciones(dias, normas, convalidaciones=convalidaciones)
    seguimiento = seguimiento_semanas(normas, legislatura)
    for e in lista_ediciones:
        e["seguimiento"] = seguimiento.get(e["id"], [])

    return {
        "generado": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "secciones": [{"codigo": c, "nombre": nombre} for c, nombre, _ in SECCIONES_WEB],
        "temas": TEMAS,
        "impactos": IMPACTOS,
        "decisiones": DECISIONES,
        "resumen": resumen(dias, normas),
        "ediciones": lista_ediciones,
        "legislatura": legislatura,
        "informe": informe.construir(crudas, legislatura, convalidaciones, senado, sentencias),
        "dias": dias,
        "normas": normas,
    }


# ---------- Partir en archivos pequeños ----------
# Lo que solo hace falta al abrir la ficha: se quita del archivo de la semana.
CAMPOS_DETALLE = ("cambios", "cambios_recibidos", "textos_oficiales", "creditos")


def resumen_cambios(n):
    """Cuántas normas y artículos cambia (y cuántos cambios recibe), para la ficha sin cargar el detalle."""
    con_bloques = [c for c in n.get("cambios") or [] if c.get("bloques")]
    return {"normas": len(con_bloques), "articulos": sum(len(c["bloques"]) for c in con_bloques),
            "recibidos": len([c for c in n.get("cambios_recibidos") or [] if c.get("bloques")])}


def norma_ligera(n):
    """La norma tal como va en el archivo de su semana."""
    ligera = {k: v for k, v in n.items() if k not in CAMPOS_DETALLE}
    p = n.get("preambulo")
    if p and p.get("parrafos"):
        ligera["preambulo"] = {**p, "parrafos": p["parrafos"][:1], "total_parrafos": len(p["parrafos"])}
    ligera["resumen_cambios"] = resumen_cambios(n)
    return ligera


def norma_detalle(n):
    listas = {k: n.get(k) or [] for k in CAMPOS_DETALLE if k != "textos_oficiales"}
    return {"id": n["id"], "preambulo": n.get("preambulo"), **listas, "textos_oficiales": n.get("textos_oficiales") or {}}


def indice_busqueda(datos):
    """Lo mínimo para buscar por palabras del titular en todas las semanas.

    Cada norma es [id, fecha, titular, posición del tema en `temas` (-1 si no tiene), impacto],
    de la más reciente a la más antigua. Crece unos 16 KB por cada 100 normas (unos 4 KB al servirse comprimido)."""
    temas = datos.get("temas") or []
    filas = [[n["id"], n.get("fecha"), n.get("titular") or n.get("titulo") or "",
              temas.index(n["tema"]) if n.get("tema") in temas else -1, n.get("impacto")]
             for n in datos["normas"]]
    filas.sort(key=lambda f: (f[1] or "", f[0]), reverse=True)
    return {"generado": datos.get("generado"), "normas": filas}


# Lo que se queda de cada edición en indice.json; el resto viaja en su archivo de semana.
CAMPOS_EDICION_INDICE = ("id", "etiqueta", "desde", "hasta", "en_curso")


def partir(datos):
    """{ruta dentro de web/datos/: contenido} a partir de lo que devuelve construir()."""
    archivos = {}
    ediciones = []
    for e in datos["ediciones"]:
        normas = [n for n in datos["normas"] if n["semana"] == e["id"]]
        dias = [d for d in datos["dias"] if e["desde"] <= d["fecha"] <= e["hasta"]]
        ruta = f"semanas/{e['id']}.json"
        archivos[ruta] = {"id": e["id"], "edicion": {k: v for k, v in e.items() if k not in CAMPOS_EDICION_INDICE},
                          "dias": dias, "normas": [norma_ligera(n) for n in normas]}
        ediciones.append({**{k: e[k] for k in CAMPOS_EDICION_INDICE if k in e},
                          "archivo": ruta, "num_normas": len(normas), "dias_con_datos": len(dias)})
    for n in datos["normas"]:
        archivos[f"normas/{n['id']}.json"] = norma_detalle(n)
    # Sin «dias» ni el mapa norma → semana: la web deduce la semana de una norma por
    # su fecha (en buscar.json) y las fechas de cada edición.
    indice = {k: v for k, v in datos.items() if k not in ("normas", "ediciones", "dias", "informe")}
    indice["ediciones"] = ediciones
    indice["num_normas"] = len(datos["normas"])
    archivos["indice.json"] = indice
    archivos["buscar.json"] = indice_busqueda(datos)
    if datos.get("informe"):
        archivos["informe.json"] = datos["informe"]
    archivos["feed.xml"] = canal_rss(datos)
    return archivos


def canal_rss(datos, maximo=MAX_RSS):
    """RSS 2.0 con las últimas normas: titular, enlace a su ficha y, si la norma
    dice su objeto, esa frase copiada del texto oficial (si no, el título oficial)."""
    elementos = []
    for n in datos["normas"][:maximo]:  # construir() las deja de la más reciente a la más antigua
        objeto = (n.get("textos_oficiales") or {}).get("objeto")
        texto = f"Según la propia norma: «{objeto['texto']}»" if objeto else f"Título oficial: {n['titulo']}"
        a, m, d = map(int, n["fecha"].split("-"))
        elementos.append("\n".join([
            "    <item>",
            f"      <title>{escape(n['titular'])}</title>",
            f"      <link>{URL_WEB}#{n['id']}</link>",
            f'      <guid isPermaLink="false">{n["id"]}</guid>',
            f"      <pubDate>{format_datetime(datetime(a, m, d, tzinfo=timezone.utc))}</pubDate>",
            f"      <category>{escape(n.get('tema') or '')}</category>",
            f"      <description>{escape(texto + ' Resumen orientativo, no es asesoramiento jurídico. Consulta el texto oficial.')}</description>",
            "    </item>",
        ]))
    return "\n".join([
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<rss version="2.0">',
        "  <channel>",
        "    <title>El BOE en llano</title>",
        f"    <link>{URL_WEB}</link>",
        "    <description>Las normas generales que publica el Boletín Oficial del Estado, clasificadas y explicadas. Proyecto no oficial.</description>",
        "    <language>es-es</language>",
        *elementos,
        "  </channel>",
        "</rss>",
        "",
    ])


def escribir(archivos, carpeta=CARPETA_WEB):
    """Escribe los archivos desde cero (así no quedan semanas o normas que ya no existen)."""
    carpeta = Path(carpeta)
    if carpeta.exists():
        shutil.rmtree(carpeta)
    for ruta, contenido in archivos.items():
        destino = carpeta / ruta
        destino.parent.mkdir(parents=True, exist_ok=True)
        texto = contenido if isinstance(contenido, str) else json.dumps(contenido, ensure_ascii=False, separators=(",", ":"))
        destino.write_text(texto, encoding="utf-8")


def main():
    datos = construir()
    archivos = partir(datos)
    escribir(archivos)
    kb = lambda r: round((CARPETA_WEB / r).stat().st_size / 1024)
    semanas = [kb(r) for r in archivos if r.startswith("semanas/")]
    fichas = [kb(r) for r in archivos if r.startswith("normas/")]
    print(f"{CARPETA_WEB}: {len(datos['dias'])} días, {len(datos['normas'])} normas, "
          f"{len(datos['ediciones'])} ediciones semanales.")
    print(f"  indice.json {kb('indice.json')} KB · semanas {min(semanas, default=0)}-{max(semanas, default=0)} KB"
          f" · fichas {min(fichas, default=0)}-{max(fichas, default=0)} KB")
    for e in datos["ediciones"]:
        print(f"  {e['id']}: {e['etiqueta']}. {e['resumen']['frase']}")


if __name__ == "__main__":
    main()
