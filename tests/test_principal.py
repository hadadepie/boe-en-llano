"""Pruebas del paso 6 (boe/principal.py): la cadena llama a cada paso en orden."""

from datetime import date
from pathlib import Path

from boe import clasificar, exportar, guardar, ia, principal, resumir


def test_ejecutar_llama_a_los_pasos_en_orden(monkeypatch):
    orden = []
    monkeypatch.setattr(guardar, "procesar_rango", lambda d, h: orden.append(("guardar", d, h)) or {"2026-11-20": "hecho"})
    monkeypatch.setattr(ia, "cliente_desde_entorno", lambda: None)
    monkeypatch.setattr(clasificar, "clasificar_carpeta", lambda **k: orden.append(("clasificar", k.get("cliente_ia"))) or [])
    monkeypatch.setattr(resumir, "resumir_carpeta", lambda **k: orden.append(("resumir", k["cliente_ia"])) or [])
    monkeypatch.setattr(exportar, "main", lambda: orden.append(("exportar",)))

    principal.ejecutar(date(2026, 11, 16), date(2026, 11, 22))

    assert orden == [
        ("guardar", date(2026, 11, 16), date(2026, 11, 22)),
        ("clasificar", None),
        ("resumir", None),
        ("exportar",),
    ]


def test_el_workflow_ejecuta_la_cadena_y_publica_la_carpeta_web():
    workflow = (Path(__file__).parent.parent / ".github" / "workflows" / "diario.yml").read_text(encoding="utf-8")
    assert "python -m boe.principal" in workflow
    assert "python -m pytest" in workflow
    assert "path: web" in workflow
    assert "cron:" in workflow and "workflow_dispatch" in workflow
