"""Pruebas de boe/congreso.py. Sin red: el índice y las votaciones son copias
reducidas del formato real de los datos abiertos del Congreso."""

import json
from datetime import date

from boe import congreso

INDICE = """
<div>VI. Convalidación o derogación de Reales Decretos-leyes.</div>
<div>Real Decreto-ley 21/2026, de 25 de agosto, de transparencia. (Núm. expte. 130/000052) Si: 2 No: 3</div>
<a href="/webpublica/opendata/votaciones/Leg15/Sesion198/20260916/Votacion016/VOT_20260916195339.pdf">PDF</a>
<a href="/webpublica/opendata/votaciones/Leg15/Sesion198/20260916/Votacion016/VOT_20260916195405.xml">XML</a>
<a href="/webpublica/opendata/votaciones/Leg15/Sesion198/20260916/Votacion016/VOT_20260916195406.json">JSON</a>
<div>Tramitación como Proyecto de Ley del Real Decreto-ley 22/2026. Si: 6 No: 0</div>
<a href="/webpublica/opendata/votaciones/Leg15/Sesion198/20260916/Votacion017/VOT_20260916195410.json">JSON</a>
<a href="/webpublica/opendata/votaciones/Leg15/Sesion198/20260916/Votacion017/VOT_20260916195410.json">JSON repetido</a>
"""

VOT_CONVALIDACION = {
    "informacion": {"sesion": 198, "numeroVotacion": 16, "fecha": "16/9/2026",
                    "titulo": "Convalidación o derogación de Reales Decretos-leyes.",
                    "textoExpediente": "Real Decreto-ley 21/2026, de 25 de agosto, de transparencia."},
    "totales": {"asentimiento": "No", "presentes": 6, "afavor": 2, "enContra": 3, "abstenciones": 1, "noVotan": 0},
    "votaciones": [
        {"asiento": "3603", "diputado": "Uno, Ana", "grupo": "GP", "voto": "No"},
        {"asiento": "3604", "diputado": "Dos, Berta", "grupo": "GP", "voto": "No"},
        {"asiento": "-1", "diputado": "Tres, Carlos", "grupo": "GS", "voto": "Sí"},
        {"asiento": "1201", "diputado": "Cuatro, Dora", "grupo": "GMx", "voto": "Sí"},
        {"asiento": "1202", "diputado": "Cinco, Eva", "grupo": "GMx", "voto": "Abstención"},
        {"asiento": "1203", "diputado": "Seis, Fran", "grupo": "GMx", "voto": "No"},
    ],
}
VOT_TRAMITACION = {
    "informacion": {"sesion": 198, "numeroVotacion": 17, "titulo": "Convalidación o derogación de Reales Decretos-leyes.",
                    "textoExpediente": "Tramitación como Proyecto de Ley por el procedimiento de urgencia del Real Decreto-ley 22/2026."},
    "totales": {"afavor": 6, "enContra": 0, "abstenciones": 0, "noVotan": 0},
    "votaciones": [],
}
LISTAS = {
    "Uno, Ana": ("PP", "Grupo Parlamentario Popular en el Congreso"),
    "Dos, Berta": ("PP", "Grupo Parlamentario Popular en el Congreso"),
    "Tres, Carlos": ("PSOE", "Grupo Parlamentario Socialista"),
    "Cuatro, Dora": ("BNG", "Grupo Parlamentario Mixto"),
    "Cinco, Eva": ("SUMAR", "Grupo Parlamentario Mixto"),
    # "Seis, Fran" no está: debe contar como "Sin dato"
}


def test_enlaces_de_votaciones_y_pdf():
    enlaces = congreso.enlaces_votaciones(INDICE)
    assert len(enlaces) == 2 and enlaces[0].endswith("Votacion016/VOT_20260916195406.json")
    assert congreso.pdf_de(INDICE, enlaces[0]).endswith("Votacion016/VOT_20260916195339.pdf")
    assert congreso.pdf_de(INDICE, enlaces[1]) is None


def test_rdl_de_texto():
    assert congreso.rdl_de_texto("Real Decreto-ley 21/2026, de 25 de agosto, de …") == "21/2026"
    assert congreso.rdl_de_texto("Tramitación como Proyecto de Ley del Real Decreto-ley 22/2026") == "22/2026"
    assert congreso.rdl_de_texto("Proposición de ley orgánica") is None


def test_tipo_de_votacion_distingue_convalidacion_y_tramitacion():
    assert congreso.tipo_de_votacion(VOT_CONVALIDACION["informacion"]) == "convalidacion"
    assert congreso.tipo_de_votacion(VOT_TRAMITACION["informacion"]) == "tramitacion"
    assert congreso.tipo_de_votacion({"titulo": "Proposiciones no de ley", "textoExpediente": "Real Decreto-ley 1/2026"}) is None


def test_resultado():
    assert congreso.resultado_de({"afavor": 2, "enContra": 3}, "convalidacion") == "derogado"
    assert congreso.resultado_de({"afavor": 304, "enContra": 33}, "convalidacion") == "convalidado"
    assert congreso.resultado_de({"afavor": 6, "enContra": 0}, "tramitacion") == "se tramita como proyecto de ley"


def test_resumen_agrega_por_grupo_y_por_lista_y_cuenta_telematicos():
    r = congreso.resumir_votacion(VOT_CONVALIDACION, LISTAS)
    assert r["por_grupo"]["GP"] == {"No": 2}
    assert r["por_grupo"]["GMx"] == {"Sí": 1, "Abstención": 1, "No": 1}
    assert r["por_lista"]["GMx"] == {"BNG": {"Sí": 1}, "SUMAR": {"Abstención": 1}, "Sin dato": {"No": 1}}
    assert r["telematicos"] == 1
    assert r["diputados_sin_lista"] == 1
    assert r["nombres_grupo"]["GMx"] == "Grupo Parlamentario Mixto"
    # Lo publicado es agregado: no aparece ningún nombre de diputado.
    assert "Uno, Ana" not in json.dumps(r, ensure_ascii=False)


def _simular(monkeypatch, indices, votaciones):
    monkeypatch.setattr(congreso, "indice_del_dia", lambda dia, carpeta, hoy: indices.get(dia, ""))
    monkeypatch.setattr(congreso, "votacion", lambda ruta, carpeta: votaciones[ruta])


def test_convalidacion_de_encuentra_la_votacion(monkeypatch, tmp_path):
    ruta = congreso.enlaces_votaciones(INDICE)[0]
    _simular(monkeypatch, {date(2026, 9, 16): INDICE}, {ruta: VOT_CONVALIDACION,
             congreso.enlaces_votaciones(INDICE)[1]: VOT_TRAMITACION})
    norma = {"id": "BOE-A-2026-1", "numero_oficial": "21/2026", "fecha_publicacion": "2026-08-26",
             "titulo": "Real Decreto-ley 21/2026, de 25 de agosto"}
    r = congreso.convalidacion_de(norma, LISTAS, tmp_path, hoy=date(2026, 11, 22))
    assert r["estado"] == "derogado"
    assert r["convalidacion"]["fecha"] == "2026-09-16"
    assert r["convalidacion"]["fuente_pdf"].endswith(".pdf")
    assert "tramitacion" not in r  # la votación de tramitación era de otro real decreto-ley


def test_sin_votacion_en_el_pleno(monkeypatch, tmp_path):
    _simular(monkeypatch, {}, {})
    norma = {"id": "BOE-A-2026-2", "numero_oficial": "37/2026", "fecha_publicacion": "2026-10-20", "titulo": "…"}
    assert congreso.convalidacion_de(norma, LISTAS, tmp_path, hoy=date(2026, 12, 30))["estado"] == "sin datos"
    assert congreso.convalidacion_de(norma, LISTAS, tmp_path, hoy=date(2026, 11, 5))["estado"] == "pendiente de votación"


def test_filtro_previo_por_texto_del_indice():
    rutas = congreso.enlaces_votaciones(INDICE)
    assert congreso._menciona_rdl(INDICE, rutas[0], "21/2026")
    assert not congreso._menciona_rdl(INDICE, rutas[0], "99/2026")


# Corrección (22/11/2026): la sesión del 2-oct-2026 votó los RDL 26 y 27/2026
# "por llamamiento" y el Congreso solo publicó imágenes: no hay JSON.
INDICE_LLAMAMIENTO = """
<div>Sesión Plenaria número 203 Fecha : 02/10/2026</div>
<div>Convalidación o derogación de Reales Decretos-leyes.</div>
<div>Real Decreto-ley 26/2026, de 29 de septiembre, por el que se adoptan medidas urgentes para la vivienda.
(Pública por llamamiento) (Núm. expte. 130/000055) Si: 172 No: 178 Abstenciones: 0 <a>Detalle</a></div>
<div>Real Decreto-ley 27/2026, de 29 de septiembre, de arrendamientos. (Pública por llamamiento)
(Núm. expte. 130/000056) Si: 166 No: 184 Abstenciones: 0 <a>Detalle</a></div>
<a href="/webpublica/opendata/votaciones/Leg15/Sesion203/20261002/Votacion001/VOT_20261002175800.png">PNG</a>
"""


def test_totales_del_indice_sin_json():
    assert congreso.totales_del_indice(INDICE_LLAMAMIENTO, "26/2026") == {
        "afavor": 172, "enContra": 178, "abstenciones": 0, "llamamiento": True}
    assert congreso.totales_del_indice(INDICE_LLAMAMIENTO, "27/2026")["enContra"] == 184
    assert congreso.totales_del_indice(INDICE_LLAMAMIENTO, "99/2026") is None


def test_convalidacion_con_solo_totales(monkeypatch, tmp_path):
    _simular(monkeypatch, {date(2026, 10, 2): INDICE_LLAMAMIENTO}, {})
    norma = {"id": "BOE-A-2026-20266", "numero_oficial": "26/2026", "fecha_publicacion": "2026-09-30", "titulo": "…"}
    r = congreso.convalidacion_de(norma, LISTAS, tmp_path, hoy=date(2026, 11, 22))
    assert r["estado"] == "derogado"
    assert r["convalidacion"]["solo_totales"] is True and r["convalidacion"]["por_grupo"] == {}
    assert "llamamiento" in r["convalidacion"]["nota"]
