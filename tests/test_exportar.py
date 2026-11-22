"""Pruebas del paso 5 (boe/exportar.py)."""

import json

from boe import exportar


def test_agrupar_recuento_suma_la_seccion_v_y_rellena_ceros():
    agrupado = exportar.agrupar_recuento({"1": 27, "2A": 12, "3": 72, "5A": 73, "5B": 62, "5C": 1})
    assert agrupado == {"I": 27, "II.A": 12, "II.B": 0, "III": 72, "IV": 0, "V": 136}


def test_formato_espanol():
    assert exportar.miles(1516) == "1.516"
    assert exportar.porcentaje(52, 1516) == "3,4 %"
    assert exportar.porcentaje(1, 0) == "0 %"
    assert exportar.fecha_larga("2026-11-20") == "20 de noviembre de 2026"


def _dia(fecha, i, total_resto):
    return {"fecha": fecha, "recuento": {"I": i, "II.A": 0, "II.B": 0, "III": total_resto, "IV": 0, "V": 0}}


def test_frase_resumen_rango_del_mismo_mes():
    dias = [_dia("2026-11-16", 4, 269), _dia("2026-11-21", 5, 280)]
    normas = [{"impacto": "Directo"}, {"impacto": "Técnico"}, {"impacto": "Directo"}]
    assert exportar.frase_resumen(dias, normas) == (
        "Entre el 16 y el 21 de noviembre de 2026, el BOE publicó 558 textos. "
        "Solo 9 (1,6 %) son normas generales y 2 cambian algo para mucha gente.")


def test_frase_resumen_un_dia_y_singular():
    frase = exportar.frase_resumen([_dia("2026-11-20", 27, 255)], [{"impacto": "Directo"}])
    assert frase.startswith("El 20 de noviembre de 2026, el BOE publicó 282 textos.")
    assert frase.endswith("y 1 cambia algo para mucha gente.")


def test_frase_resumen_entre_meses_y_sin_datos():
    dias = [_dia("2026-10-30", 1, 9), _dia("2026-11-02", 1, 9)]
    assert exportar.frase_resumen(dias, []).startswith("Entre el 30 de octubre y el 2 de noviembre de 2026")
    assert exportar.frase_resumen([], []) == "Todavía no hay días descargados."


def test_construir_junta_recuentos_y_normas(tmp_path):
    (tmp_path / "normas").mkdir()
    (tmp_path / "recuentos.json").write_text(json.dumps({"2026-11-20": {"1": 2, "5A": 3}}), encoding="utf-8")
    for i, impacto in enumerate(["Directo", "Técnico"]):
        norma = {"id": f"BOE-A-2026-0000{i}", "fecha_publicacion": "2026-11-20", "titulo": "T",
                 "impacto": impacto, "tema": "Trabajo y empleo", "ambito": "Estatal",
                 "ficha": {"estado": "ok" if i == 0 else "pendiente"}}
        (tmp_path / "normas" / f"{norma['id']}.json").write_text(json.dumps(norma), encoding="utf-8")

    datos = exportar.construir(tmp_path)
    assert datos["dias"] == [{"fecha": "2026-11-20", "recuento": {"I": 2, "II.A": 0, "II.B": 0, "III": 0, "IV": 0, "V": 3}}]
    assert datos["resumen"]["total_publicaciones"] == 5
    assert datos["resumen"]["porcentaje_normas"] == "40,0 %"
    assert datos["resumen"]["impacto_directo"] == 1
    assert datos["resumen"]["fichas_verificadas"] == 1
    assert [s["codigo"] for s in datos["secciones"]] == ["I", "II.A", "II.B", "III", "IV", "V"]


# ---------- Edición semanal ----------

from datetime import date as _date


def _norma(**c):
    base = {"id": "BOE-A-2026-00001", "fecha": "2026-11-20", "titulo": "T", "rango": "Real Decreto",
            "impacto": "Directo", "ambito": "Estatal", "tema": "Trabajo y empleo",
            "ficha": {"estado": "pendiente", "titulo_llano": "Se fija el salario mínimo para 2027."}}
    return base | c


def test_semana_de_y_etiqueta():
    assert exportar.semana_de("2026-11-16") == exportar.semana_de("2026-11-21") == "2026-S47"
    assert exportar.semana_de("2026-11-23") == "2026-S48"
    assert exportar.etiqueta_semana(["2026-11-16", "2026-11-21"]) == "Semana del 16 al 21 de noviembre de 2026"
    assert exportar.etiqueta_semana(["2026-11-30", "2026-12-05"]) == "Semana del 30 de noviembre al 5 de diciembre de 2026"
    assert exportar.etiqueta_semana(["2026-11-20"]) == "Edición del 20 de noviembre de 2026"


def test_relevancia_prioriza_impacto_estatal_y_titular_claro():
    smi = _norma()
    ley_ccaa = _norma(rango="Ley", ambito="Cataluña", ficha={"titulo_llano": "Presupuestos de la Generalitat para 2026."})
    rdl_oscuro = _norma(rango="Real Decreto-ley", ficha={"titulo_llano": "Se modifica la Ley 1/2005, de 9 de marzo."})
    tramite = _norma(impacto="Técnico", rango="Ley")
    orden = sorted([tramite, ley_ccaa, rdl_oscuro, smi], key=exportar.relevancia, reverse=True)
    assert orden[0] is smi and orden[-1] is tramite


def test_titular_claro():
    assert exportar.titular_claro("Se fija el salario mínimo para 2027.")
    assert not exportar.titular_claro("Se modifica la Ley 1/2005, de 9 de marzo.")
    assert not exportar.titular_claro("Corrección de errores: Decreto-ley 4/2026.")
    assert not exportar.titular_claro("x" * 120)


def test_piezas_semana_cuentan_por_tipo_ambito_y_titulo():
    normas = [
        _norma(id="a", rango="Real Decreto-ley"),
        _norma(id="b", rango="Real Decreto-ley"),
        _norma(id="c", rango="Ley", ambito="Cataluña"),
        _norma(id="d", rango="Resolución", titulo="Resolución por la que se ordena la publicación del Acuerdo de convalidación del Real Decreto-ley 30/2026."),
        _norma(id="e", rango="Resolución", titulo="Resolución por la que se ordena la publicación del Acuerdo de derogación del Real Decreto-ley 31/2026."),
        _norma(id="f", titulo="Real Decreto por el que se regula la concesión directa de una subvención."),
    ]
    piezas = {p["texto"]: (p["cifra"], p["ids"]) for p in exportar.piezas_semana(normas)}
    assert piezas["reales decretos-ley aprobados por el Gobierno"] == (2, ["a", "b"])
    assert piezas["ley autonómica: Cataluña (1)"] == (1, ["c"])
    assert piezas["real decreto-ley convalidado por el Congreso"] == (1, ["d"])
    assert piezas["real decreto-ley rechazado (derogado) por el Congreso"] == (1, ["e"])
    assert piezas["subvención o préstamo directo a entidades concretas"] == (1, ["f"])
    assert not any("leyes aprobadas por las Cortes" in t or "ley aprobada" in t for t in piezas)


def test_ediciones_por_semana_y_en_curso():
    dias = [{"fecha": f, "recuento": {"I": 1, "II.A": 0, "II.B": 0, "III": 0, "IV": 0, "V": 0}}
            for f in ["2026-11-20", "2026-11-21", "2026-11-23"]]
    normas = [_norma(semana="2026-S47"), _norma(id="x", fecha="2026-11-23", semana="2026-S48")]
    ed = exportar.ediciones(dias, normas, hoy=_date(2026, 11, 24))  # martes de la S48
    assert [e["id"] for e in ed] == ["2026-S48", "2026-S47"]
    assert ed[0]["en_curso"] is True and ed[1]["en_curso"] is False
    assert ed[1]["resumen"]["normas_generales"] == 2
    domingo = exportar.ediciones(dias, normas, hoy=_date(2026, 11, 29))
    assert domingo[0]["en_curso"] is False  # el domingo no hay BOE: la semana está completa
