"""Pruebas del paso 1 (boe/descargar.py).

Estas pruebas NO llaman a la API de verdad: usan un sumario en miniatura
(tests/datos/sumario_mini.json) con los casos raros que encontramos, y
"simulan" internet cuando hace falta. Así son rápidas y siempre dan lo mismo.
"""

import json
from datetime import date
from pathlib import Path

import pytest

from boe import descargar

SUMARIO_MINI = json.loads(
    (Path(__file__).parent / "datos" / "sumario_mini.json").read_text(encoding="utf-8")
)


def test_como_lista_cubre_los_tres_casos():
    assert descargar.como_lista(None) == []
    assert descargar.como_lista([1, 2]) == [1, 2]
    assert descargar.como_lista({"a": 1}) == [{"a": 1}]


def test_extraer_items_encuentra_las_publicaciones_esten_donde_esten():
    por_codigo = {s["codigo"]: s for s in descargar.secciones(SUMARIO_MINI)}
    assert len(descargar.extraer_items(por_codigo["1"])) == 3   # epígrafes (lista y suelto)
    assert len(descargar.extraer_items(por_codigo["5A"])) == 2  # directamente en departamento
    assert len(descargar.extraer_items(por_codigo["5C"])) == 1  # dentro de "texto"


def test_contar_por_seccion():
    assert descargar.contar_por_seccion(SUMARIO_MINI) == {"1": 3, "5A": 2, "5C": 1}


def test_si_ya_esta_guardado_no_llama_a_la_api(tmp_path, monkeypatch):
    (tmp_path / "20261120.json").write_text(json.dumps(SUMARIO_MINI), encoding="utf-8")

    def prohibido(*args, **kwargs):
        raise AssertionError("¡No debería haber llamado a la API!")

    monkeypatch.setattr(descargar.requests, "get", prohibido)
    resultado = descargar.descargar_sumario(date(2026, 11, 20), carpeta=tmp_path, pausa=0)
    assert resultado == SUMARIO_MINI


class RespuestaFalsa:
    """Imita la respuesta de `requests` sin conectarse a internet."""

    def __init__(self, codigo, datos=None):
        self.status_code = codigo
        self._datos = datos

    def json(self):
        return self._datos

    def raise_for_status(self):
        if self.status_code >= 400:
            raise RuntimeError(f"Error HTTP {self.status_code}")


def test_dia_sin_boe_devuelve_none_y_no_guarda_nada(tmp_path, monkeypatch):
    monkeypatch.setattr(descargar.requests, "get", lambda *a, **k: RespuestaFalsa(404))
    resultado = descargar.descargar_sumario(date(2026, 11, 22), carpeta=tmp_path, pausa=0)
    assert resultado is None
    assert list(tmp_path.iterdir()) == []


def test_descarga_nueva_se_guarda_en_disco(tmp_path, monkeypatch):
    monkeypatch.setattr(
        descargar.requests, "get", lambda *a, **k: RespuestaFalsa(200, SUMARIO_MINI)
    )
    descargar.descargar_sumario(date(2026, 11, 20), carpeta=tmp_path, pausa=0)
    guardado = json.loads((tmp_path / "20261120.json").read_text(encoding="utf-8"))
    assert guardado == SUMARIO_MINI


class _Respuesta:
    def __init__(self, codigo):
        self.status_code = codigo


def test_pedir_reintenta_errores_temporales_y_luego_devuelve(monkeypatch):
    respuestas = iter([_Respuesta(502), _Respuesta(503), _Respuesta(200)])
    esperas = []
    monkeypatch.setattr(descargar.requests, "get", lambda *a, **k: next(respuestas))
    monkeypatch.setattr(descargar.time, "sleep", esperas.append)
    r = descargar.pedir("http://x", {}, pausa=1, esperas=(10, 30, 90))
    assert r.status_code == 200
    assert esperas == [1, 10, 1, 30, 1]  # pausa tras cada petición y esperas crecientes


def test_pedir_no_reintenta_un_404_y_se_rinde_tras_los_reintentos(monkeypatch):
    monkeypatch.setattr(descargar.time, "sleep", lambda s: None)
    monkeypatch.setattr(descargar.requests, "get", lambda *a, **k: _Respuesta(404))
    assert descargar.pedir("http://x", {}, esperas=(1, 2)).status_code == 404

    llamadas = []
    def caido(*a, **k):
        llamadas.append(1)
        raise descargar.requests.ConnectionError("sin red")
    monkeypatch.setattr(descargar.requests, "get", caido)
    with pytest.raises(descargar.requests.ConnectionError):
        descargar.pedir("http://x", {}, esperas=(1, 2))
    assert len(llamadas) == 3
