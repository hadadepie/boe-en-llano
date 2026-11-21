"""Pruebas del paso 2 (boe/guardar.py). Sin red: se simulan las descargas."""

import json
from datetime import date
from pathlib import Path

from boe import descargar, guardar

CARPETA = Path(__file__).parent / "datos"
SUMARIO_MINI = json.loads((CARPETA / "sumario_mini.json").read_text(encoding="utf-8"))
XML_MINI = (CARPETA / "norma_mini.xml").read_text(encoding="utf-8")


def test_normas_seccion_i_conserva_departamento_y_epigrafe():
    normas = guardar.normas_seccion_i(SUMARIO_MINI)
    assert [n["id"] for n in normas] == ["BOE-A-2026-00001", "BOE-A-2026-00002", "BOE-A-2026-00003"]
    assert normas[0]["departamento_sumario"] == "CORTES GENERALES"
    assert normas[2]["epigrafe"] == "Un solo epígrafe, que llega suelto"
    assert normas[0]["fecha_publicacion"] == "2026-11-20"


def test_metadatos_de_xml():
    meta = guardar.metadatos_de_xml(XML_MINI)
    assert meta["rango"] == "Resolución"
    assert meta["origen_legislativo"] == "Estatal"
    assert meta["fecha_disposicion"] == "2026-11-18"
    assert meta["fecha_vigencia"] is None
    assert meta["numero_oficial"] is None
    assert meta["materias"] == ["Ceuta", "Subvenciones"]


def test_texto_de_xml_usa_solo_el_texto_principal():
    texto = guardar.texto_de_xml(XML_MINI)
    assert texto == "Primer párrafo con negrita.\nSegundo párrafo."
    assert "NO es el texto" not in texto


def _simular_api(monkeypatch, llamadas):
    def sumario(fecha, carpeta):
        llamadas.append(("sumario", fecha))
        return SUMARIO_MINI

    def norma(identificador, carpeta):
        llamadas.append(("norma", identificador))
        return XML_MINI

    monkeypatch.setattr(descargar, "descargar_sumario", sumario)
    monkeypatch.setattr(descargar, "descargar_norma_xml", norma)


def test_procesar_dia_guarda_recuentos_y_normas(tmp_path, monkeypatch):
    llamadas = []
    _simular_api(monkeypatch, llamadas)

    assert guardar.procesar_dia(date(2026, 11, 20), tmp_path) == "hecho"

    recuentos = json.loads((tmp_path / "recuentos.json").read_text(encoding="utf-8"))
    assert recuentos == {"2026-11-20": {"1": 3, "5A": 2, "5C": 1}}
    norma = json.loads((tmp_path / "normas" / "BOE-A-2026-00001.json").read_text(encoding="utf-8"))
    assert norma["rango"] == "Resolución" and norma["titulo"] == "Norma uno"
    assert len(list((tmp_path / "normas").iterdir())) == 3


def test_procesar_dos_veces_no_vuelve_a_descargar(tmp_path, monkeypatch):
    llamadas = []
    _simular_api(monkeypatch, llamadas)
    guardar.procesar_dia(date(2026, 11, 20), tmp_path)
    llamadas.clear()

    assert guardar.procesar_dia(date(2026, 11, 20), tmp_path) == "ya_estaba"
    assert llamadas == []


def test_dia_sin_boe_no_se_marca_como_procesado(tmp_path, monkeypatch):
    monkeypatch.setattr(descargar, "descargar_sumario", lambda fecha, carpeta: None)
    assert guardar.procesar_dia(date(2026, 11, 22), tmp_path) == "sin_boe"
    assert guardar.leer_recuentos(tmp_path) == {}
