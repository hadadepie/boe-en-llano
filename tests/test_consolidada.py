"""Pruebas de boe/consolidada.py (vida de la norma). Sin red: respuestas
reducidas copiadas del formato real de la API de legislación consolidada."""

import json
from datetime import date

from boe import consolidada

ANALISIS = {"status": {"code": "200"}, "data": [{
    "notas": {"nota": "Entrada en vigor, con las excepciones indicadas, el 3 de septiembre de 2026."},
    "referencias": {
        "anteriores": [{"anterior": [
            {"id_norma": "BOE-A-2023-625", "relacion": {"codigo": "270", "texto": "MODIFICA"},
             "texto": ", con efectos desde el 1 de septiembre de 2026, el art. 31 del Real Decreto-ley 1/2023"},
            {"id_norma": "BOE-A-2003-21614", "relacion": {"codigo": "440", "texto": "DE CONFORMIDAD con"},
             "texto": "la Ley 47/2003, de 26 de noviembre"},
        ]}],
        "posteriores": [{"posterior": [
            {"id_norma": "BOE-A-2026-24120", "relacion": {"codigo": "270", "texto": "SE MODIFICA"},
             "texto": "el art. 15.2, por Real Decreto-ley 38/2026, de 17 de noviembre"},
            {"id_norma": "BOE-A-2026-19420", "relacion": {"codigo": "301", "texto": "SE PUBLICA  Acuerdo de convalidación"},
             "texto": ", por Resolución de 16 de septiembre de 2026"},
        ]}],
    },
}]}


def test_leer_analisis():
    v = consolidada.leer_analisis(ANALISIS)
    assert v["entrada_en_vigor"] == "Entrada en vigor, con las excepciones indicadas, el 3 de septiembre de 2026."
    # Solo cambios reales en otras normas (no las meras citas "de conformidad con")
    assert [m["id"] for m in v["modifica"]] == ["BOE-A-2023-625"]
    assert v["modifica"][0]["texto"].startswith("con efectos desde")  # sin la coma inicial
    # Hechos posteriores ordenados por fecha; la que no trae año queda al final
    assert [h["id"] for h in v["despues"]] == ["BOE-A-2026-19420", "BOE-A-2026-24120"]
    assert v["despues"][0] == {"relacion": "Se publica acuerdo de convalidación",
                               "texto": "por Resolución de 16 de septiembre de 2026",
                               "id": "BOE-A-2026-19420", "fecha": "2026-09-16"}


def test_notas_como_lista_y_referencias_vacias():
    v = consolidada.leer_analisis({"data": [{"notas": [{"nota": "Efectos desde el 1 de enero hasta el 31 de diciembre de 2027."}],
                                             "referencias": []}]})
    assert v["entrada_en_vigor"].startswith("Efectos desde el 1 de enero")
    assert v["modifica"] == [] and v["despues"] == []


class Respuesta:
    def __init__(self, codigo, datos=None):
        self.status_code, self._datos = codigo, datos

    def json(self):
        return self._datos

    def raise_for_status(self):
        if self.status_code >= 400:
            raise RuntimeError(self.status_code)


def test_norma_no_consolidada_y_cache(tmp_path, monkeypatch):
    llamadas = []
    def get(url, **k):
        llamadas.append(url)
        return Respuesta(404)
    monkeypatch.setattr(consolidada.requests, "get", get)
    norma = {"id": "BOE-A-2026-23896"}
    assert consolidada.vida_de(norma, tmp_path, hoy=date(2026, 11, 22))["consolidada"] is False
    consolidada.vida_de(norma, tmp_path, hoy=date(2026, 11, 22))
    assert len(llamadas) == 1  # la segunda vez usa la caché


def test_procesar_guarda_la_vida_en_la_norma(tmp_path, monkeypatch):
    monkeypatch.setattr(consolidada.requests, "get", lambda url, **k: Respuesta(200, ANALISIS))
    (tmp_path / "normas").mkdir()
    (tmp_path / "normas" / "BOE-A-2026-18429.json").write_text(json.dumps({"id": "BOE-A-2026-18429"}), encoding="utf-8")
    assert consolidada.procesar(tmp_path, hoy=date(2026, 11, 22)) == 1
    norma = json.loads((tmp_path / "normas" / "BOE-A-2026-18429.json").read_text(encoding="utf-8"))
    assert norma["vida"]["consolidada"] is True and len(norma["vida"]["despues"]) == 2
    assert consolidada.procesar(tmp_path, hoy=date(2026, 11, 22)) == 0  # sin cambios, no reescribe


def test_procesar_por_fechas_y_las_que_ya_tienen_vida(tmp_path, monkeypatch):
    pedidas = []
    monkeypatch.setattr(consolidada.requests, "get", lambda url, **k: pedidas.append(url) or Respuesta(200, ANALISIS))
    (tmp_path / "normas").mkdir()
    for id, fecha, vida in (("BOE-A-2023-1", "2023-09-05", None), ("BOE-A-2026-1", "2026-10-01", None),
                            ("BOE-A-2024-1", "2024-03-01", {"consolidada": True})):
        n = {"id": id, "fecha_publicacion": fecha}
        if vida:
            n["vida"] = vida
        (tmp_path / "normas" / f"{id}.json").write_text(json.dumps(n), encoding="utf-8")
    # La Action semanal: las recientes y las que ya tienen vida, no las antiguas sin vida.
    consolidada.procesar(tmp_path, hoy=date(2026, 11, 22), desde="2026-05-26", con_vida=True)
    assert sorted(u.split("/id/")[1].split("/")[0] for u in pedidas) == ["BOE-A-2024-1", "BOE-A-2026-1"]
    # Una tanda a mano: solo su intervalo.
    pedidas.clear()
    consolidada.procesar(tmp_path, hoy=date(2026, 11, 22), desde="2023-08-17", hasta="2023-12-31")
    assert [u.split("/id/")[1].split("/")[0] for u in pedidas] == ["BOE-A-2023-1"]
