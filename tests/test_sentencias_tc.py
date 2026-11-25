"""Pruebas de boe.sentencias_tc con XML como los del BOE (recortados)."""

import json

from boe import sentencias_tc

TITULO = ("Pleno. Sentencia 127/2023, de 27 de septiembre de 2023. Recurso de inconstitucionalidad 3726-2023. "
          "Interpuesto por el presidente del Gobierno en relación con diversos preceptos del Decreto-ley 5/2022.")


def _xml(titulo=TITULO, rango="Sentencia", anteriores=()):
    refs = "".join(f'<anterior referencia="{r}"><palabra>{p}</palabra><texto>{t}</texto></anterior>' for r, p, t in anteriores)
    return (f"<?xml version='1.0' encoding='UTF-8'?><documento><metadatos><rango>{rango}</rango>"
            f"<numero_oficial>127/2023</numero_oficial><titulo>{titulo}</titulo><fecha_publicacion>20231101</fecha_publicacion>"
            f"</metadatos><analisis><referencias><anteriores>{refs}</anteriores></referencias></analisis>"
            f"<texto><p>FALLO</p></texto></documento>").encode("utf-8")


def test_lee_admision_normas_y_resultado():
    s = sentencias_tc.leer_xml(_xml(anteriores=[
        ("BOE-A-2023-15069", "DICTADA", "en el Recurso 3726/2023"),
        ("BOE-A-2022-16900", "DECLARA", "la inconstitucionalidad y nulidad de los arts. 2, 3 y 4 del Decreto-ley 5/2022"),
        ("BOE-A-2022-1", "DECLARA", ","),  # «,»: lo mismo que la anterior
        ("BOE-A-2021-2", "DECLARA", "la desestimación en relación con el art. 1 de la Ley 2/2021"),
    ]))
    assert s["fecha"] == "2023-11-01" and s["asunto"] == "3726-2023" and s["sala"] == "Pleno"
    assert s["tipo"] == "Recurso de inconstitucionalidad" and s["admisiones"] == ["BOE-A-2023-15069"]
    assert [(n["id"], n["resultado"]) for n in s["normas"]] == [
        ("BOE-A-2022-16900", "nulidad"), ("BOE-A-2022-1", "nulidad"), ("BOE-A-2021-2", "desestima")]


def test_resultados():
    r = sentencias_tc.resultado_de
    assert r("inconstitucional y nulo el art. 4 de la Ley 1/2004") == "nulidad"
    assert r("la perdida del objeto en relación con el Decreto-ley 3/2023") == "pierde_objeto"
    assert r("su extinción, por la pérdida sobrevenida de objeto") == "pierde_objeto"
    assert r("la inadmisión en relación con el art. 3 del Decreto-ley 2/2018") == "inadmite"
    assert r("en el Recurso 6243/2023, el mantenimiento de suspensión de lo indicado del art. 10.1 y el levantamiento del resto") == "mantiene_suspension"
    assert r("en el Recurso 8042/2023, el levantamiento de suspensión de vigencia") == "levanta_suspension"
    assert r("la inconstitucionalidad, sin nulidad, del art. 5") == "inconstitucional_sin_nulidad"


def test_los_amparos_no_se_recogen():
    assert sentencias_tc.tipo_de("Sala Primera. Sentencia 86/2023. Recurso de amparo 4650-2021. Promovido por don …") is None
    assert sentencias_tc.tipo_de("Pleno. Sentencia 16/2024. Cuestión de inconstitucionalidad núm. 2847-2023.") == "Cuestión de inconstitucionalidad"


def test_procesar_toma_la_seccion_t_y_no_repite(tmp_path, monkeypatch):
    sumario = {"data": {"sumario": {"diario": [{"seccion": [
        {"codigo": "T", "nombre": "Tribunal Constitucional", "departamento": {"nombre": "TRIBUNAL CONSTITUCIONAL", "item": [
            {"identificador": "BOE-A-2023-22422", "titulo": TITULO},
            {"identificador": "BOE-A-2023-22423", "titulo": "Sala Primera. Sentencia 86/2023. Recurso de amparo 4650-2021."}]}},
        {"codigo": "1", "nombre": "I", "departamento": {"nombre": "X", "item": [{"identificador": "BOE-A-2023-1", "titulo": TITULO}]}},
    ]}]}}}
    (tmp_path / "crudo" / "sumarios").mkdir(parents=True)
    (tmp_path / "crudo" / "sumarios" / "20231101.json").write_text(json.dumps(sumario), encoding="utf-8")
    pedidas = []

    class R:
        status_code, content = 200, _xml(anteriores=[("BOE-A-2022-16900", "DECLARA", "la desestimación")])

        def raise_for_status(self):
            pass

    monkeypatch.setattr(sentencias_tc.descargar, "pedir", lambda url, cab, pausa: pedidas.append(url) or R())
    assert sentencias_tc.procesar(tmp_path, pausa=0) == 1  # ni el amparo ni lo que no es sección T
    assert pedidas == ["https://www.boe.es/diario_boe/xml.php?id=BOE-A-2023-22422"]
    guardado = json.loads((tmp_path / "sentencias_tc.json").read_text(encoding="utf-8"))["sentencias"]
    assert guardado[0]["id"] == "BOE-A-2023-22422" and guardado[0]["normas"][0]["resultado"] == "desestima"
    assert sentencias_tc.procesar(tmp_path, pausa=0) == 0 and len(pedidas) == 1
