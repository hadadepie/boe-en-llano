"""Pruebas de boe/decretos_ley.py. Sin red: el BOE se simula con documentos de ejemplo."""

import json
import xml.etree.ElementTree as ET
from datetime import date

from boe import decretos_ley, exportar

# Documento oficial recortado, con la estructura real del XML del BOE (RDL 2/2025).
DOCUMENTO = """<?xml version="1.0" encoding="utf-8"?>
<documento>
  <metadatos>
    <identificador>BOE-A-2025-5404</identificador>
    <titulo>Real Decreto-ley 2/2025, de 18 de marzo, por el que se aprueban medidas urgentes para la garantía del interés superior de la infancia y adolescencia.</titulo>
    <rango>Real Decreto-ley</rango>
    <numero_oficial>2/2025</numero_oficial>
    <fecha_publicacion>20250319</fecha_publicacion>
  </metadatos>
  <analisis>
    <materias>
      <materia>Asistencia social</materia>
      <materia>Extranjeros</materia>
      <materia>Menores</materia>
    </materias>
    <referencias>
      <anteriores>
        <anterior referencia="BOE-A-2000-544" orden="2015"><palabra>MODIFICA</palabra><texto>el art. 52</texto></anterior>
        <anterior referencia="BOE-A-2000-544" orden="2020"><palabra>AÑADE</palabra><texto>los arts. 35 bis</texto></anterior>
        <anterior referencia="BOE-A-2015-1" orden="2030"><palabra>PRORROGA</palabra><texto>el plazo</texto></anterior>
        <anterior referencia="BOE-A-1978-31229" orden="2040"><palabra>DE CONFORMIDAD con</palabra><texto>el art. 86</texto></anterior>
      </anteriores>
    </referencias>
  </analisis>
</documento>"""


def test_fecha_del_titulo_completo_en_un_indice_del_congreso():
    textos = ["Votación 12. Real Decreto-ley 2/2025, de 18 de marzo, por el que se aprueban medidas…"]
    assert decretos_ley.fecha_en_textos("2/2025", textos) == date(2025, 3, 18)
    # No confunde 2/2025 con 12/2025.
    assert decretos_ley.fecha_en_textos("2/2025", ["Real Decreto-ley 12/2025, de 4 de noviembre"]) is None


def test_normas_modificadas_cuenta_normas_distintas_y_solo_relaciones_de_cambio():
    raiz = ET.fromstring(DOCUMENTO.encode("utf-8"))
    # BOE-A-2000-544 (modifica y añade) cuenta una vez; «de conformidad con» no es un cambio.
    assert decretos_ley.normas_modificadas(raiz) == 2


def test_varios_temas_solo_si_hay_tres_temas_con_tres_materias_cada_uno():
    pocas = ["Impuesto sobre la Renta de las Personas Físicas", "Empleo", "Viviendas"]
    assert len(decretos_ley.temas_de_materias(pocas)) < decretos_ley.MIN_TEMAS_VARIOS
    muchas = (["Impuesto sobre Sociedades", "Impuesto sobre el Valor Añadido", "Impuestos Especiales"]
              + ["Empleo", "Seguridad Social", "Pensiones"]
              + ["Viviendas", "Arrendamientos urbanos", "Urbanismo"])
    assert len(decretos_ley.temas_de_materias(muchas)) >= decretos_ley.MIN_TEMAS_VARIOS


def test_ficha_con_el_documento_oficial(monkeypatch, tmp_path):
    monkeypatch.setattr(decretos_ley, "fecha_de", lambda rdl, c, p: date(2025, 3, 18))
    monkeypatch.setattr(decretos_ley, "documento", lambda rdl, f, c, p: ET.fromstring(DOCUMENTO.encode("utf-8")))
    f = decretos_ley.ficha("2/2025", tmp_path, pausa=0)
    assert f["encontrado"] and f["id_boe"] == "BOE-A-2025-5404"
    assert f["fecha_publicacion"] == "2025-03-19"
    assert f["normas_modificadas"] == 2
    assert f["materias"] == ["Asistencia social", "Extranjeros", "Menores"]
    assert f["tema"] and f["motivos_tema"]


def test_sin_fecha_ni_documento_queda_como_no_encontrado(monkeypatch, tmp_path):
    monkeypatch.setattr(decretos_ley, "fecha_de", lambda rdl, c, p: None)
    assert decretos_ley.ficha("99/2025", tmp_path, pausa=0) == {"rdl": "99/2025", "encontrado": False, "fecha": None}


def test_la_exportacion_une_tema_tamano_y_titular_a_la_legislatura(tmp_path):
    congreso = tmp_path / "congreso"
    congreso.mkdir()
    (congreso / "legislatura_xv.json").write_text(json.dumps({"decretos_ley": [
        {"rdl": "2/2025", "resultado": "convalidado", "margen": 200},
        {"rdl": "3/2025", "resultado": "derogado", "margen": -5},
    ]}), encoding="utf-8")
    (congreso / "decretos_ley_xv.json").write_text(json.dumps({"decretos": {
        "2/2025": {"encontrado": True, "id_boe": "BOE-A-2025-5404", "tema": "Derechos e igualdad", "normas_modificadas": 2,
                   "fecha_publicacion": "2025-03-19",
                   "titulo": "Real Decreto-ley 2/2025, de 18 de marzo, por el que se aprueban medidas urgentes para la infancia."},
        "3/2025": {"encontrado": False},
    }}), encoding="utf-8")
    L = exportar.leer_legislatura(tmp_path)
    a, b = L["decretos_ley"]
    assert a["tema"] == "Derechos e igualdad" and a["normas_modificadas"] == 2 and a["id_boe"] == "BOE-A-2025-5404"
    assert a["titular"] == "Se aprueban medidas urgentes para la infancia."
    assert "tema" not in b  # sin documento no se inventa nada
