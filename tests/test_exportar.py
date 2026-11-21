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
