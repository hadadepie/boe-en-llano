"""Pruebas del paso 6 (boe/principal.py): la cadena llama a cada paso en orden."""

from datetime import date
from pathlib import Path

from boe import clasificar, congreso, consolidada, exportar, guardar, ia, legislatura, principal, resumir, tramitacion, versiones


def test_ejecutar_llama_a_los_pasos_en_orden(monkeypatch):
    orden = []
    monkeypatch.setattr(guardar, "procesar_rango", lambda d, h: orden.append(("guardar", d, h)) or {"2026-11-20": "hecho"})
    monkeypatch.setattr(ia, "cliente_desde_entorno", lambda: None)
    monkeypatch.setattr(clasificar, "clasificar_carpeta", lambda **k: orden.append(("clasificar", k.get("cliente_ia"))) or [])
    monkeypatch.setattr(resumir, "resumir_carpeta", lambda **k: orden.append(("resumir", k["cliente_ia"])) or [])
    monkeypatch.setattr(congreso, "procesar", lambda **k: orden.append(("congreso",)) or {})
    monkeypatch.setattr(tramitacion, "procesar", lambda: orden.append(("tramitacion",)) or 0)
    monkeypatch.setattr(legislatura, "procesar", lambda: orden.append(("legislatura",)) or {})
    monkeypatch.setattr(consolidada, "procesar", lambda: orden.append(("consolidada",)) or 0)
    monkeypatch.setattr(versiones, "procesar", lambda: orden.append(("versiones",)) or 0)
    monkeypatch.setattr(versiones, "procesar_recibidos", lambda: 0)
    monkeypatch.setattr(exportar, "main", lambda: orden.append(("exportar",)))

    principal.ejecutar(date(2026, 11, 16), date(2026, 11, 22))

    assert orden == [
        ("guardar", date(2026, 11, 16), date(2026, 11, 22)),
        ("clasificar", None),
        ("resumir", None),
        ("congreso",),
        ("tramitacion",),
        ("legislatura",),
        ("consolidada",),
        ("versiones",),
        ("exportar",),
    ]


def test_el_workflow_ejecuta_la_cadena_y_publica_la_carpeta_web():
    workflow = (Path(__file__).parent.parent / ".github" / "workflows" / "diario.yml").read_text(encoding="utf-8")
    assert "python -m boe.principal" in workflow
    assert "python -m pytest" in workflow
    assert "path: web" in workflow
    assert "workflow_dispatch" in workflow
    # Ejecución semanal (domingo), sin ejecución en cada push, y Pages opcional:
    # se publica solo con las casillas «publicar» o «solo publicar», o con la variable PUBLICAR_WEB=true.
    activas = [l for l in workflow.splitlines() if not l.lstrip().startswith("#")]
    assert any('cron: "0 8 * * 0"' in l for l in activas)
    assert not any(l.strip().startswith("push:") for l in activas)
    condicion = "if: ${{ inputs.publicar || inputs.solo_publicar || vars.PUBLICAR_WEB == 'true' }}"
    assert workflow.count(condicion) == 3  # configure-pages, upload-pages-artifact y el job publicar
    # «Solo publicar» no descarga ni guarda datos: solo exporta la web con lo guardado.
    assert workflow.count("if: ${{ !inputs.solo_publicar }}") == 2
    assert "python -m boe.exportar" in workflow
    pasos_pages = [l for l in activas if "pages" in l and "uses:" in l]
    assert len(pasos_pages) == 3


def test_si_falla_el_congreso_la_web_se_exporta_igual(monkeypatch):
    orden = []
    monkeypatch.setattr(guardar, "procesar_rango", lambda d, h: {})
    monkeypatch.setattr(ia, "cliente_desde_entorno", lambda: None)
    monkeypatch.setattr(clasificar, "clasificar_carpeta", lambda **k: [])
    monkeypatch.setattr(resumir, "resumir_carpeta", lambda **k: [])
    def falla(**k):
        raise ConnectionError("congreso.es no responde")
    monkeypatch.setattr(congreso, "procesar", falla)
    monkeypatch.setattr(consolidada, "procesar", lambda: (_ for _ in ()).throw(ConnectionError("boe.es no responde")))
    monkeypatch.setattr(exportar, "main", lambda: orden.append("exportar"))
    principal.ejecutar(date(2026, 11, 16), date(2026, 11, 22))
    assert orden == ["exportar"]
