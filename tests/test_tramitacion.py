"""Pruebas de boe/tramitacion.py. Sin red: registro reducido copiado del
fichero real ProyectosDeLey de los datos abiertos del Congreso."""

import json

from boe import tramitacion

PROYECTO = {
    "TIPO": "Proyecto de ley",
    "OBJETO": "Proyecto de Ley por la que se aprueban medidas urgentes de carácter \nsocial y económico de apoyo a la ciudad de Ceuta (procedente del Real \nDecreto-ley 22/2026, de 1 de septiembre).",
    "NUMEXPEDIENTE": "121/000114/0000",
    "FECHAPRESENTACION": "16/09/2026",
    "TIPOTRAMITACION": "Competencia Legislativa Plena; Urgente",
    "RESULTADOTRAMITACION": "Caducado \n04/11/2026",
    "SITUACIONACTUAL": "Cerrado",
    "COMISIONCOMPETENTE": "Comisión de Política Territorial",
    "TRAMITACIONSEGUIDA": "Comisión de Política Territorial \nPublicación \ndesde 22/09/2026 hasta 25/09/2026 \nComisión de Política Territorial \nEnmiendas \ndesde 25/09/2026 hasta 06/10/2026 \nConcluido - (Caducado) \ndesde 06/10/2026 hasta 04/11/2026",
    "ENLACESBOCG": "https://www.congreso.es/public_oficiales/L15/CONG/BOCG/A/BOCG-15-A-115-1.PDF#page=1 \n https://www.congreso.es/public_oficiales/L15/CONG/BOCG/D/BOCG-15-D-610.PDF#page=51",
}
OTRO = {"OBJETO": "Proyecto de Ley de presupuestos.", "NUMEXPEDIENTE": "121/000100/0000"}


def test_pasos():
    p = tramitacion.pasos(PROYECTO["TRAMITACIONSEGUIDA"])
    assert p == [
        {"fase": "Publicación", "organo": "Comisión de Política Territorial", "desde": "2026-09-22", "hasta": "2026-09-25"},
        {"fase": "Enmiendas", "organo": "Comisión de Política Territorial", "desde": "2026-09-25", "hasta": "2026-10-06"},
        {"fase": "Concluido - (Caducado)", "organo": None, "desde": "2026-10-06", "hasta": "2026-11-04"},
    ]


def test_por_rdl_solo_los_procedentes_de_un_real_decreto_ley():
    indice = tramitacion.por_rdl([PROYECTO, OTRO])
    assert list(indice) == ["22/2026"]
    r = indice["22/2026"]
    assert r["expediente"] == "121/000114" and r["resultado"] == "Caducado 04/11/2026"
    assert r["fecha_resultado"] == "2026-11-04" and r["presentado"] == "2026-09-16"
    assert len(r["enlaces_bocg"]) == 2 and r["enlaces_bocg"][0].endswith("#page=1")


def test_procesar_anade_y_quita(tmp_path, monkeypatch):
    monkeypatch.setattr(tramitacion, "proyectos_de_ley", lambda carpeta, hoy=None: [PROYECTO])
    (tmp_path / "normas").mkdir()
    rdl = tmp_path / "normas" / "rdl.json"
    rdl.write_text(json.dumps({"id": "x", "rango": "Real Decreto-ley", "numero_oficial": "22/2026"}), encoding="utf-8")
    otra = tmp_path / "normas" / "otra.json"
    otra.write_text(json.dumps({"id": "y", "rango": "Real Decreto-ley", "numero_oficial": "37/2026"}), encoding="utf-8")
    assert tramitacion.procesar(tmp_path) == 1
    assert json.loads(rdl.read_text(encoding="utf-8"))["tramitacion"]["expediente"] == "121/000114"
    assert "tramitacion" not in json.loads(otra.read_text(encoding="utf-8"))
    assert tramitacion.procesar(tmp_path) == 0  # sin cambios, no reescribe
