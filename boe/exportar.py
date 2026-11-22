"""Paso 5: preparar el único archivo que lee la web (web/datos.json).

Uso:
    python -m boe.exportar

Junta datos/recuentos.json y datos/normas/*.json, agrupa las secciones como se
muestran en la web (la V suma V.A + V.B + V.C) y calcula la cabecera.
web/datos.json es un archivo generado: no se versiona (está en .gitignore).
"""

import json
import re
from datetime import date, datetime, timezone
from pathlib import Path

from boe.clasificar import IMPACTOS, TEMAS

CARPETA_DATOS = Path("datos")
ARCHIVO_WEB = Path("web/datos.json")

# Sección de la API -> sección que se muestra en la web.
SECCIONES_WEB = [
    ("I", "I. Disposiciones generales", ["1"]),
    ("II.A", "II.A Nombramientos y situaciones", ["2A"]),
    ("II.B", "II.B Oposiciones y concursos", ["2B"]),
    ("III", "III. Otras disposiciones", ["3"]),
    ("IV", "IV. Administración de Justicia", ["4"]),
    ("V", "V. Anuncios", ["5A", "5B", "5C"]),
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

    frase = (f"{cuando}, el BOE publicó {miles(total)} textos. "
             f"Solo {miles(generales)} ({porcentaje(generales, total)}) son normas generales")
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


# ---------- Votaciones del Congreso (convalidación de reales decretos-ley) ----------

NOMBRE_CORTO_GRUPO = {
    "GP": "PP", "GS": "PSOE", "GVOX": "Vox", "GSUMAR": "Sumar", "GMx": "Mixto",
    "GJxCAT": "Junts", "GR": "ERC", "GEH Bildu": "EH Bildu", "GV (EAJ-PNV)": "PNV",
}
_RE_RDL_TITULO = re.compile(r"Real Decreto-ley (\d+/\d{4})")


def leer_convalidaciones(carpeta_datos):
    archivo = Path(carpeta_datos) / "congreso" / "convalidaciones.json"
    return json.loads(archivo.read_text(encoding="utf-8")) if archivo.exists() else {}


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


def enlazar_votaciones(normas, convalidaciones):
    """Añade 'congreso' a cada real decreto-ley y a las resoluciones que publican su convalidación."""
    por_rdl = {r["rdl"]: votacion_para_web(r) for r in convalidaciones.values() if r.get("rdl")}
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


def norma_para_web(n):
    return {
        "id": n["id"],
        "fecha": n["fecha_publicacion"],
        "rango": n.get("rango"),
        "organo": n.get("departamento") or n.get("departamento_sumario"),
        "titulo": n["titulo"],
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
    }


def construir(carpeta_datos=CARPETA_DATOS):
    carpeta_datos = Path(carpeta_datos)
    archivo_recuentos = carpeta_datos / "recuentos.json"
    recuentos = json.loads(archivo_recuentos.read_text(encoding="utf-8")) if archivo_recuentos.exists() else {}
    dias = [{"fecha": f, "recuento": agrupar_recuento(r)} for f, r in sorted(recuentos.items())]

    normas = [json.loads(p.read_text(encoding="utf-8")) for p in sorted((carpeta_datos / "normas").glob("*.json"))]
    normas = [norma_para_web(n) for n in normas]
    normas.sort(key=lambda n: (n["fecha"], n["id"]), reverse=True)
    convalidaciones = leer_convalidaciones(carpeta_datos)
    enlazar_votaciones(normas, convalidaciones)

    return {
        "generado": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "secciones": [{"codigo": c, "nombre": nombre} for c, nombre, _ in SECCIONES_WEB],
        "temas": TEMAS,
        "impactos": IMPACTOS,
        "resumen": resumen(dias, normas),
        "ediciones": ediciones(dias, normas, convalidaciones=convalidaciones),
        "dias": dias,
        "normas": normas,
    }


def main():
    datos = construir()
    ARCHIVO_WEB.parent.mkdir(parents=True, exist_ok=True)
    ARCHIVO_WEB.write_text(json.dumps(datos, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{ARCHIVO_WEB}: {len(datos['dias'])} días, {len(datos['normas'])} normas, "
          f"{len(datos['ediciones'])} ediciones semanales.")
    for e in datos["ediciones"]:
        print(f"  {e['id']}: {e['etiqueta']}. {e['resumen']['frase']}")


if __name__ == "__main__":
    main()
