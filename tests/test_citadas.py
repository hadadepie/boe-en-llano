"""Pruebas de boe/citadas.py: títulos de las normas anteriores más cambiadas. Sin red."""

import json

from boe import citadas, descargar, guardar


def _xml(titulo, fecha="20061129", rango="Ley"):
    return (f"<documento><metadatos><titulo>{titulo}</titulo><rango codigo='1300'>{rango}</rango>"
            f"<fecha_publicacion>{fecha}</fecha_publicacion></metadatos></documento>")


def test_ficha_de_los_metadatos_del_diario():
    assert citadas.ficha_de(_xml("Ley 35/2006, de 28 de noviembre, del Impuesto sobre la Renta.")) == {
        "titulo": "Ley 35/2006, de 28 de noviembre, del Impuesto sobre la Renta", "rango": "Ley", "fecha_publicacion": "2006-11-29"}
    assert citadas.ficha_de("<documento><metadatos/></documento>") is None


def test_procesar_pide_solo_las_que_faltan(tmp_path, monkeypatch):
    norma = {"id": "BOE-A-2024-1", "fecha_publicacion": "2024-01-10", "rango": "Ley", "departamento": "Jefatura del Estado",
             "origen_legislativo": "Estatal", "titulo": "Ley 1/2024.", "cambia": [
                 {"id": "BOE-A-2006-20764", "relacion": "Modifica"}, {"id": "BOE-A-1882-6036", "relacion": "Modifica"}]}
    guardar.escribir_json(tmp_path / "normas" / "BOE-A-2024-1.json", norma)
    (tmp_path / "normas_citadas.json").write_text(json.dumps({"BOE-A-2006-20764": {"titulo": "Ley 35/2006"}}), encoding="utf-8")
    pedidas = []
    monkeypatch.setattr(descargar, "descargar_norma_xml",
                        lambda i, carpeta, pausa: pedidas.append(i) or _xml("Ley de Enjuiciamiento Criminal", "18820917", "Real Decreto"))
    assert citadas.procesar(tmp_path) == 1 and pedidas == ["BOE-A-1882-6036"]
    assert citadas.leer(tmp_path)["BOE-A-1882-6036"]["fecha_publicacion"] == "1882-09-17"
    assert citadas.procesar(tmp_path) == 0
