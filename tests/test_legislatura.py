"""Pruebas de boe/legislatura.py. Sin red: índices reducidos con el texto real."""

from datetime import date

from boe import legislatura

INDICE = """
<div>V. Proposiciones no de ley. Proposición no de ley sobre el Real Decreto-ley 3/2026. Si: 200 No: 150 Abstenciones: 0 Detalle XML JSON</div>
<div>VI. Convalidación o derogación de Reales Decretos-leyes.</div>
<div>Real Decreto-ley 21/2026, de 25 de agosto, de transparencia. (Núm. expte. 130/000052) Si: 155 No: 179 Abstenciones: 12 Detalle XML JSON</div>
<div>Real Decreto-ley 22/2026, de 1 de septiembre, de Ceuta. (Núm. expte. 130/000053) Si: 304 No: 33 Abstenciones: 7 Detalle XML JSON</div>
<div>Tramitación como Proyecto de Ley por el procedimiento de urgencia del Real Decreto-ley 22/2026. Si: 345 No: 0 Abstenciones: 0 Detalle XML JSON</div>
<div>VII. Dictámenes de comisiones sobre iniciativas legislativas.</div>
<div>Proyecto de Ley de Ceuta (procedente del Real Decreto-ley 9/2025). Si: 300 No: 40 Abstenciones: 0 Detalle XML JSON</div>
"""
LLAMAMIENTO = """
<div>PUNTO UNICO. Convalidación o derogación de Reales Decretos-leyes.</div>
<div>Real Decreto-ley 26/2026, de 29 de septiembre. (Pública por llamamiento) (Núm. expte. 130/000055) Si: 172 No: 178 Abstenciones: 0 Detalle</div>
<div>Real Decreto-ley 27/2026, de 29 de septiembre. (Pública por llamamiento) (Núm. expte. 130/000056) Si: 166 No: 184 Abstenciones: 0 Detalle</div>
"""


def test_solo_cuenta_los_puntos_de_convalidacion():
    r = legislatura.convalidaciones_del_indice(INDICE)
    assert [x["rdl"] for x in r] == ["21/2026", "22/2026"]  # ni la PNL, ni la tramitación, ni el «procedente del»
    assert r[0]["afavor"] == 155 and r[0]["enContra"] == 179 and not r[0]["llamamiento"]


def test_votacion_por_llamamiento_y_punto_unico():
    r = legislatura.convalidaciones_del_indice(LLAMAMIENTO)
    assert [(x["rdl"], x["llamamiento"]) for x in r] == [("26/2026", True), ("27/2026", True)]


def test_recorrer_solo_dias_laborables_y_hasta_la_disolucion(monkeypatch, tmp_path):
    consultados = []
    def indice(dia, carpeta, hoy):
        consultados.append(dia)
        return INDICE if dia == date(2026, 9, 16) else ""
    monkeypatch.setattr(legislatura.congreso, "indice_del_dia", indice)
    votaciones, dias = legislatura.recorrer(date(2026, 9, 14), date(2026, 10, 20), tmp_path, hoy=date(2026, 11, 22))
    assert all(d.isoweekday() <= 5 for d in consultados)
    assert max(consultados) == legislatura.FIN_PLENO  # no consulta después de la disolución
    assert votaciones["21/2026"]["fecha"] == "2026-09-16"


def test_cifras_y_huecos_de_numeracion():
    votaciones = {"21/2026": {"afavor": 155, "enContra": 179, "abstenciones": 12, "llamamiento": False, "fecha": "2026-09-16"},
                  "23/2026": {"afavor": 300, "enContra": 38, "abstenciones": 10, "llamamiento": False, "fecha": "2026-09-23"}}
    resumen, lista = legislatura.cifras(votaciones, {"21/2026", "22/2026", "23/2026", "30/2026"},
                                        {"30/2026": {"resultado": "convalidado", "id": "BOE-A-2026-24291", "fecha": "2026-11-20"}})
    assert resumen == {"convalidado": 2, "derogado": 1, "sin votación publicada": 1, "pleno": 2,
                       "diputacion_permanente": 1, "empates": 0}
    assert lista[-1]["organo"] == "Diputación Permanente"
    assert [x["rdl"] for x in lista] == ["21/2026", "22/2026", "23/2026", "30/2026"]
    assert lista[0]["margen"] == -24


def test_no_vuelve_a_recorrer_una_legislatura_cerrada(monkeypatch, tmp_path):
    (tmp_path / "congreso").mkdir()
    (tmp_path / "congreso" / "legislatura_xv.json").write_text('{"consultado": "2026-11-22", "resumen": {}}', encoding="utf-8")
    monkeypatch.setattr(legislatura, "recorrer", lambda **k: (_ for _ in ()).throw(AssertionError("no debe recorrer")))
    assert legislatura.procesar(tmp_path, hoy=date(2026, 11, 29))["consultado"] == "2026-11-22"


def test_empate_cuenta_como_derogado_y_se_marca():
    resumen, lista = legislatura.cifras({"8/2023": {"afavor": 171, "enContra": 171, "abstenciones": 0, "llamamiento": False, "fecha": "2024-01-10"}}, set())
    assert lista[0]["resultado"] == "derogado" and lista[0]["empate"] is True and resumen["empates"] == 1
