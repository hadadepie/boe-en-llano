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


def ediciones(dias, normas, hoy=None):
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
        })
    return resultado


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
    }


def construir(carpeta_datos=CARPETA_DATOS):
    carpeta_datos = Path(carpeta_datos)
    archivo_recuentos = carpeta_datos / "recuentos.json"
    recuentos = json.loads(archivo_recuentos.read_text(encoding="utf-8")) if archivo_recuentos.exists() else {}
    dias = [{"fecha": f, "recuento": agrupar_recuento(r)} for f, r in sorted(recuentos.items())]

    normas = [json.loads(p.read_text(encoding="utf-8")) for p in sorted((carpeta_datos / "normas").glob("*.json"))]
    normas = [norma_para_web(n) for n in normas]
    normas.sort(key=lambda n: (n["fecha"], n["id"]), reverse=True)

    return {
        "generado": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "secciones": [{"codigo": c, "nombre": nombre} for c, nombre, _ in SECCIONES_WEB],
        "temas": TEMAS,
        "impactos": IMPACTOS,
        "resumen": resumen(dias, normas),
        "ediciones": ediciones(dias, normas),
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
