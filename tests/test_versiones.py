"""Pruebas de boe/versiones.py (antes y después). Sin red."""

import json

from boe import versiones

ANTES = [
    "Artículo 15. Plan ICEX de fomento de la internacionalización de las empresas de Ceuta.",
    "1. ICEX promoverá un plan de fomento de la internacionalización.",
    "b) Una jornada a celebrar en la ciudad con las empresas exportadoras.",
    "El Plan Ceuta Exporta se ejecutará durante los seis meses siguientes a la fecha de este real decreto-ley.",
]
DESPUES = [
    "Artículo 15. Plan ICEX de fomento de la internacionalización de las empresas de Ceuta.",
    "1. ICEX promoverá un plan de fomento de la internacionalización.",
    "b) Una jornada a celebrar en la ciudad con las empresas exportadoras.",
    "c) Ayudas, de acuerdo con lo dispuesto en la Ley 38/2003, General de Subvenciones.",
    "El Plan Ceuta Exporta se ejecutará hasta el 31 de diciembre de 2027.",
]


def test_comparar_resume_iguales_y_marca_cambios():
    r = versiones.comparar(ANTES, DESPUES)
    assert r[0] == {"iguales": 3}
    assert r[1] == {"añadido": DESPUES[3]}
    # El párrafo parecido se empareja como cambio palabra a palabra
    cambio = r[2]["cambiado"]
    assert ["-", "durante los seis meses siguientes a la fecha"] in cambio
    assert ["+", "hasta el 31"] in cambio


def test_parrafo_distinto_no_se_empareja():
    r = versiones.comparar(["Texto antiguo totalmente distinto."], ["Una redacción nueva sin relación alguna con la anterior."])
    assert {"eliminado": "Texto antiguo totalmente distinto."} in r
    assert {"añadido": "Una redacción nueva sin relación alguna con la anterior."} in r


def test_bloque_nuevo_no_tiene_antes():
    assert versiones.comparar([], ["Artículo 95 ter. Nuevo."]) == [{"añadido": "Artículo 95 ter. Nuevo."}]


def test_cambios_en_toma_la_version_de_la_norma_y_la_anterior(monkeypatch, tmp_path):
    monkeypatch.setattr(versiones, "indice", lambda destino, carpeta, marca: [
        {"id": "a14", "titulo": "Artículo 14", "fecha_actualizacion": "20260902"},   # no tocado
        {"id": "a1-7", "titulo": "Artículo\xa015", "fecha_actualizacion": "20261118"},
    ])
    pedidos = []
    def vers(destino, bloque, actualizado, carpeta):
        pedidos.append(bloque)
        return [
            {"id_norma": "BOE-A-2026-18429", "fecha_publicacion": "20260902", "fecha_vigencia": "20260903", "parrafos": ANTES},
            {"id_norma": "BOE-A-2026-24120", "fecha_publicacion": "20261118", "fecha_vigencia": "20261119", "parrafos": DESPUES},
            {"id_norma": "BOE-A-2026-99999", "fecha_publicacion": "20261201", "fecha_vigencia": "20261202", "parrafos": DESPUES},
        ]
    monkeypatch.setattr(versiones, "versiones", vers)
    c = versiones.cambios_en("BOE-A-2026-24120", "20261118", "BOE-A-2026-18429", tmp_path)
    assert pedidos == ["a1-7"]  # solo los bloques actualizados desde la fecha de la norma
    b = c["bloques"][0]
    assert b["titulo"] == "Artículo 15" and b["en_vigor_desde"] == "2026-11-19"
    assert b["hasta"] == "2026-12-02" and b["cambiado_despues_por"] == "BOE-A-2026-99999"
    assert b["comparacion"][0] == {"iguales": 3}


def test_procesar_calcula_una_vez_por_pareja(monkeypatch, tmp_path):
    llamadas = []
    monkeypatch.setattr(versiones, "cambios_en", lambda mod, fecha, destino, carpeta: llamadas.append(destino) or {"consolidada": True, "bloques": []})
    (tmp_path / "normas").mkdir()
    norma = {"id": "BOE-A-2026-24120", "fecha_publicacion": "2026-11-18",
             "vida": {"modifica": [{"relacion": "Modifica", "texto": "el art. 15.2…", "id": "BOE-A-2026-18429"},
                                   {"relacion": "Deroga", "texto": "la orden…", "id": "BOE-A-2020-1"}]}}
    (tmp_path / "normas" / "n.json").write_text(json.dumps(norma), encoding="utf-8")
    versiones.procesar(tmp_path)
    versiones.procesar(tmp_path)
    assert llamadas == ["BOE-A-2026-18429"]  # las derogaciones no se comparan; la pareja se calcula una vez
