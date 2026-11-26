"""Página de revisión de los créditos (para la autora, no para la web publicada).

    python -m boe.importes_creditos   # la escribe en datos/presupuestos/revision_creditos.html

Una línea legible por crédito: norma, importe propuesto, a dónde va (clasificación económica),
ministerio y para qué, con el enlace al BOE. Arriba, un resumen por destino y situación de la norma,
marcado como «sin revisar». Primero los dudosos, con el motivo en castellano; después los que salen de
reglas seguras; al final, aparte, los autonómicos. Cada crédito del Estado tiene una clave (C-001…)
para decir en el chat cuál está mal.
"""

import re
from html import escape

# Avisos que hacen dudoso un crédito (el resto informa, pero la cifra sale de una regla segura).
_DUDOSOS = ("revisar", "no coincide", "cita otra norma", "mismo texto", "casi el mismo texto", "capítulo 8", "tabla sin",
            "letra", "repetido en el párrafo", "no encontrado", "sin importe")
SITUACIONES = [("vigente", "Ley o decreto-ley convalidado"),
               ("sin votación publicada", "Decreto-ley sin votación publicada todavía"),
               ("derogado", "Decreto-ley derogado por el Congreso")]


def euros(v):
    if v is None:
        return "sin propuesta"
    if abs(v) >= 1_000_000:
        texto = f"{v / 1_000_000:,.1f}".replace(",", " ").replace(".", ",").replace(" ", ".")
        return f"{texto} M€"
    return f"{v:,.0f}".replace(",", ".") + " €"


def norma_corta(titulo):
    m = re.match(r"^(.*?\d+/\d{4})", titulo or "")
    return m.group(1) if m else (titulo or "")[:60]


def situacion_resumen(c):
    return "vigente" if c["situacion"] in ("convalidado", "ley") else c["situacion"]


def es_dudoso(c, estatales):
    if c["importe_propuesto"] is None or not c["destinos"]:
        return True
    return any(d in a for a in c["avisos"] for d in _DUDOSOS)


def motivos(c, estatales):
    nombres = {o["id"]: norma_corta(o["titulo"]) for o in estatales}
    legibles = []
    for a in c["avisos"]:
        if not any(d in a for d in _DUDOSOS):
            continue
        if "casi el mismo texto en " in a:
            otras = [nombres.get(i, i) for i in a.split(" en ", 1)[1].split(", ")]
            a = "el mismo importe y casi el mismo texto en " + ", ".join(otras) + " (¿prórroga o repetición? no contarlo dos veces)"
        legibles.append(a)
    salida = []
    if legibles:
        texto = "; ".join(legibles)
        if c["importe_propuesto"] is None:
            texto = "No hay una cifra segura: " + texto
        salida.append(texto[0].upper() + texto[1:] + ".")
    elif c["importe_propuesto"] is None:
        salida.append("No hay una cifra segura.")
    if not c["destinos"]:
        salida.append("No se reconoce el código de la aplicación presupuestaria: no se sabe a dónde va.")
    return salida


def _linea(c, estatales, dudoso):
    destino = " + ".join(c["destinos"]) if c["destinos"] else "¿?"
    situacion = {"convalidado": "convalidado", "ley": "ley", "derogado": "derogado",
                 "sin votación publicada": "sin votación publicada"}.get(c["situacion"], c["situacion"])
    partes = [f'<div class="credito{" dudoso" if dudoso else ""}" id="{c["clave"]}">',
              f'<div class="cab"><span class="clave">{c["clave"]}</span> '
              f'<a href="https://www.boe.es/diario_boe/txt.php?id={c["id"]}" target="_blank" rel="noopener">{escape(norma_corta(c["titulo"]))}</a>'
              f' <span class="sit sit-{situacion_resumen(c).split()[0]}">{escape(situacion)}</span>'
              f'{" · ejercicio " + str(c["ejercicio"]) if c.get("ejercicio") else ""}</div>',
              f'<div class="cifra"><strong>{euros(c["importe_propuesto"])}</strong> → <span class="destino">{escape(destino)}</span></div>',
              f'<div class="para">{escape(c["para_que"] or "")}</div>']
    if c.get("ministerio"):
        partes.append(f'<div class="mini">{escape(c["ministerio"])} · {escape(c["tipo"].lower())}</div>')
    else:
        partes.append(f'<div class="mini">{escape(c["tipo"])}</div>')
    if dudoso:
        partes += [f'<p class="motivo">{escape(m)}</p>' for m in motivos(c, estatales)]
        if c["importes_en_el_texto"]:
            partes.append(f'<p class="leidos">Importes leídos: {escape(" · ".join(c["importes_en_el_texto"]))}</p>')
    partes.append(f'<details><summary>Texto oficial</summary><p>{escape(c["texto"])}</p></details></div>')
    return "\n".join(partes)


def resumen(estatales):
    """{destino: {situación: (euros, n)}}; los de varios destinos, en «Varios destinos»."""
    tabla = {}
    for c in estatales:
        if c["importe_propuesto"] is None:
            continue
        d = c["destinos"][0] if len(c["destinos"]) == 1 else ("Varios destinos" if c["destinos"] else "Sin identificar")
        celda = tabla.setdefault(d, {}).setdefault(situacion_resumen(c), [0.0, 0])
        celda[0] += c["importe_propuesto"]
        celda[1] += 1
    return tabla


def pagina(creditos, fecha):
    estatales = [c for c in creditos if c["situacion"] != "autonómica"]
    autonomicos = [c for c in creditos if c["situacion"] == "autonómica"]
    dudosos = [c for c in estatales if es_dudoso(c, estatales)]
    seguros = [c for c in estatales if c not in dudosos]
    tabla = resumen(estatales)
    orden = sorted(tabla, key=lambda d: -sum(v[0] for v in tabla[d].values()))
    filas = []
    for d in orden:
        celdas = "".join(f'<td>{euros(tabla[d][s][0])}<br><small>{tabla[d][s][1]} créd.</small></td>' if s in tabla[d] else "<td>—</td>"
                         for s, _ in SITUACIONES)
        filas.append(f"<tr><th>{escape(d)}</th>{celdas}</tr>")
    totales = "".join(f'<td><strong>{euros(sum(tabla[d][s][0] for d in tabla if s in tabla[d]))}</strong></td>' for s, _ in SITUACIONES)
    por_norma = {}
    for c in seguros:
        por_norma.setdefault(c["id"], []).append(c)
    bloques_seguros = "\n".join(
        f'<h3>{escape(norma_corta(cs[0]["titulo"]))} <small>{escape(cs[0]["fecha"] or "")}</small></h3>\n'
        + "\n".join(_linea(c, estatales, False) for c in cs) for cs in por_norma.values())
    lineas_auto = "\n".join(
        f'<li><a href="https://www.boe.es/diario_boe/txt.php?id={c["id"]}" target="_blank" rel="noopener">{escape(norma_corta(c["titulo"]))}</a>'
        f' · {euros(c["importe_propuesto"])}</li>' for c in autonomicos)
    return f"""<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Revisión de créditos</title>
<style>
:root {{ --fondo:#fbfaf7; --texto:#1f2328; --suave:#5d6670; --borde:#dedad2; --caja:#ffffff; --duda:#fff4e0; --duda-borde:#e0a13a;
        --ok:#2f7d4f; --mal:#b3261e; --gris:#6b7280; --enlace:#1d5fa8; }}
@media (prefers-color-scheme: dark) {{ :root {{ --fondo:#17191c; --texto:#e6e6e6; --suave:#a3a9b1; --borde:#33373d; --caja:#1f2226;
        --duda:#33280f; --duda-borde:#b8832b; --ok:#6cc08b; --mal:#f2867d; --gris:#9aa1ab; --enlace:#7fb3ee; }} }}
* {{ box-sizing:border-box; }}
body {{ margin:0; background:var(--fondo); color:var(--texto); font:16px/1.5 system-ui, -apple-system, "Segoe UI", sans-serif; }}
main {{ max-width:900px; margin:0 auto; padding:24px 16px 64px; }}
h1 {{ font-size:1.6rem; margin:0 0 4px; }} h2 {{ margin-top:40px; border-bottom:1px solid var(--borde); padding-bottom:4px; }}
h3 {{ font-size:1.05rem; margin:24px 0 8px; }} h3 small {{ color:var(--suave); font-weight:normal; }}
a {{ color:var(--enlace); }} .aviso {{ background:var(--duda); border-left:4px solid var(--duda-borde); padding:10px 14px; border-radius:4px; }}
.tabla {{ overflow-x:auto; }} table {{ border-collapse:collapse; width:100%; font-size:.92rem; }}
th, td {{ border-bottom:1px solid var(--borde); padding:6px 8px; text-align:right; vertical-align:top; }}
th:first-child {{ text-align:left; }} thead th {{ text-align:right; color:var(--suave); font-weight:600; }} small {{ color:var(--suave); }}
.credito {{ background:var(--caja); border:1px solid var(--borde); border-radius:6px; padding:10px 14px; margin:8px 0; }}
.credito.dudoso {{ border-left:4px solid var(--duda-borde); }}
.cab {{ font-size:.9rem; color:var(--suave); }} .clave {{ font-family:ui-monospace, monospace; font-weight:700; color:var(--texto); }}
.cifra {{ font-size:1.1rem; margin:2px 0; }} .destino {{ font-weight:600; }}
.para {{ }} .mini {{ font-size:.85rem; color:var(--suave); }}
.sit {{ font-size:.78rem; padding:1px 6px; border-radius:10px; border:1px solid currentColor; }}
.sit-vigente {{ color:var(--ok); }} .sit-derogado {{ color:var(--mal); }} .sit-sin {{ color:var(--gris); }}
.motivo {{ margin:6px 0 0; }} .leidos {{ margin:4px 0 0; font-size:.85rem; color:var(--suave); }}
details {{ margin-top:6px; font-size:.88rem; }} details p {{ color:var(--suave); }}
</style>
</head>
<body><main>
<h1>Créditos extraordinarios y suplementos de crédito</h1>
<p><small>Generada el {escape(fecha)} con <code>python -m boe.importes_creditos</code>. Solo para revisar: no es parte de la web.</small></p>
<p class="aviso"><strong>Cifras sin revisar.</strong> Importes <em>concedidos</em> (dinero que se autoriza a gastar fuera del presupuesto), no gastados.
Salen del texto oficial con reglas; «a dónde va» sale del código de cada aplicación presupuestaria (clasificación económica).
Para corregir uno, di en el chat su clave y qué está mal (p. ej. «C-012: son 2,5 M€»).</p>

<h2>Resumen: a dónde va</h2>
<p>{len(estatales)} créditos del Estado en {len({c["id"] for c in estatales})} normas. {sum(1 for c in estatales if c["importe_propuesto"] is not None)} tienen importe propuesto
(los suma esta tabla); de ellos, {sum(1 for c in estatales if c.get("cifra_segura"))} salen de una regla segura y sin dudas, y son los que muestra la ficha de cada norma en la web.
Los que van a varios destinos no se reparten (el texto no siempre dice cuánto a cada uno).</p>
<p class="aviso"><strong>Ojo al sumar.</strong> Los decretos-ley derogados estuvieron en vigor hasta su derogación, y el RDL 2/2026 repite lo del 16/2025.
«Préstamos y aportaciones de capital» no es gasto: se presta o se invierte y puede volver. La web no muestra ningún total.</p>
<div class="tabla"><table>
<thead><tr><th>Destino</th>{"".join(f"<th>{escape(t)}</th>" for _, t in SITUACIONES)}</tr></thead>
<tbody>{"".join(filas)}<tr><th>Total</th>{totales}</tr></tbody>
</table></div>

<h2>Para revisar ({len(dudosos)})</h2>
<p>La cifra o el destino no salen de una regla segura, o el mismo importe aparece en otra norma.</p>
{"".join(_linea(c, estatales, True) for c in dudosos)}

<h2>Con regla segura ({len(seguros)})</h2>
<p>Para repasar en diagonal. Si ves algo raro, di su clave.</p>
{bloques_seguros}

<h2>Normas autonómicas ({len(autonomicos)})</h2>
<p>Créditos de los presupuestos de cada comunidad, publicados también en el BOE. No son dinero del Estado: no entran en el resumen.</p>
<ul>{lineas_auto}</ul>
</main></body></html>
"""
