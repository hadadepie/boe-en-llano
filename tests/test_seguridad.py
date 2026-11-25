"""Pruebas de seguridad de la web y de la Action (backlog 1b): enlaces de los datos, CSP,
acciones fijadas por SHA, permisos mínimos y dependencias con hash."""

import base64
import hashlib
import json
import re
import shutil
import subprocess
from pathlib import Path
from urllib.parse import urlsplit

import pytest

RAIZ = Path(__file__).resolve().parent.parent
WEB = RAIZ / "web"
ACTION = RAIZ / ".github" / "workflows" / "diario.yml"
DOMINIOS_FUENTE = {"www.boe.es", "boe.es", "www.congreso.es", "congreso.es"}
# Una URL con esquema (https://…) o uno de los esquemas que ejecutan código o incrustan contenido.
_URL = re.compile(r"^\s*(?:[a-z][a-z0-9+.-]*://|javascript:|data:|vbscript:)", re.I)


def _cadenas(valor):
    if isinstance(valor, str):
        yield valor
    elif isinstance(valor, dict):
        for v in valor.values():
            yield from _cadenas(v)
    elif isinstance(valor, list):
        for v in valor:
            yield from _cadenas(v)


def test_las_urls_de_los_datos_son_https_y_de_fuentes_oficiales():
    """Todo valor de web/datos/*.json que sea una URL (no texto que la mencione) va a boe.es o congreso.es."""
    malas = set()
    for archivo in WEB.joinpath("datos").rglob("*.json"):
        for s in _cadenas(json.loads(archivo.read_text(encoding="utf-8"))):
            if _URL.match(s) and " " not in s:
                partes = urlsplit(s)
                if partes.scheme != "https" or partes.hostname not in DOMINIOS_FUENTE:
                    malas.add(f"{archivo.relative_to(WEB)}: {s}")
    assert not malas, sorted(malas)[:20]


@pytest.mark.skipif(not shutil.which("node"), reason="sin Node.js (en la Action sí está)")
def test_el_navegador_descarta_enlaces_que_no_son_de_la_web_ni_oficiales():
    js = (WEB / "app.js").read_text(encoding="utf-8")
    dominios = re.search(r"^const DOMINIOS_FUENTE = .*$", js, re.M).group(0)
    funcion = re.search(r"^function enlaceSeguro\(valor\) \{.*?^\}", js, re.M | re.S).group(0)
    casos = {
        "index.html#BOE-A-2026-1": True, "#BOE-A-2026-1": True, "legislatura.html": True,
        "https://www.boe.es/buscar/act.php?id=BOE-A-2026-1": True,
        "https://www.congreso.es/es/opendata/votaciones": True,
        "javascript:alert(1)": False, " JavaScript:alert(1)": False, "data:text/html,hola": False,
        "http://www.boe.es/": False, "https://www.boe.es.ejemplo.com/": False,
        "https://ejemplo.com/?www.boe.es": False, "//ejemplo.com/": False,
    }
    prueba = (f"const location = {{ href: 'https://ejemplo.github.io/boe-en-llano/index.html', "
              f"origin: 'https://ejemplo.github.io' }};\n{dominios}\n{funcion}\n"
              f"console.log(JSON.stringify({json.dumps(list(casos))}.map(enlaceSeguro)));")
    r = subprocess.run(["node", "-e", prueba], capture_output=True, text=True, check=True)
    assert dict(zip(casos, json.loads(r.stdout))) == casos


def test_la_action_fija_cada_accion_por_sha():
    usos = re.findall(r"uses:\s*(\S+)", ACTION.read_text(encoding="utf-8"))
    assert usos and all(re.fullmatch(r"[\w.-]+/[\w.-]+@[0-9a-f]{40}", u) for u in usos), usos


def test_la_action_parte_de_solo_lectura():
    texto = ACTION.read_text(encoding="utf-8")
    global_ = re.search(r"^permissions:\n((?:  .*\n)+)", texto, re.M).group(1)
    assert global_.split() == ["contents:", "read"]
    assert "pip install --require-hashes -r requirements-ci.txt" in texto


def test_requirements_ci_tiene_las_mismas_versiones_que_requirements():
    """Si falla: se cambió requirements.txt sin pasar `python herramientas/bloquear.py`."""
    fijadas = dict(re.findall(r"^([\w-]+)==([\w.]+)", (RAIZ / "requirements.txt").read_text(encoding="utf-8"), re.M))
    ci = (RAIZ / "requirements-ci.txt").read_text(encoding="utf-8")
    bloqueadas = dict(re.findall(r"^([\w-]+)==([\w.]+)", ci, re.M))
    assert {k.lower(): v for k, v in fijadas.items()}.items() <= bloqueadas.items()
    con_hash = re.findall(r"^[\w-]+==.*\\\n    --hash=sha256:[0-9a-f]{64}", ci, re.M)
    assert len(con_hash) == len(bloqueadas)


CSP = ("default-src 'self'; script-src 'self'; style-src 'self'; "
       "img-src 'self' data:; connect-src 'self'; font-src 'self'; object-src 'none'; base-uri 'self'; form-action 'self'")


@pytest.mark.parametrize("pagina", sorted(p.name for p in WEB.glob("*.html")))
def test_cada_pagina_lleva_la_politica_de_seguridad(pagina):
    """La misma CSP en todas, antes de cargar nada, y sin scripts, estilos ni eventos en línea (la CSP los bloquearía)."""
    html = (WEB / pagina).read_text(encoding="utf-8")
    cabeza = html.split("</head>")[0]
    assert f'<meta http-equiv="Content-Security-Policy" content="{CSP}">' in cabeza
    assert '<meta name="referrer" content="strict-origin-when-cross-origin">' in cabeza
    assert cabeza.index("Content-Security-Policy") < min(cabeza.find(x) for x in ("<link", "<script") if x in cabeza)
    assert not re.search(r"<script(?![^>]*\bsrc=)|<style|\sstyle=\"|\son[a-z]+=\"", html)
    assert not re.search(r'<(?:script|link)[^>]*(?:src|href)="(?:https?:)?//', cabeza), "nada de otras webs en <head>"


def test_chart_js_es_el_publicado_y_coincide_con_su_integrity():
    """web/chart-4.4.1.umd.js es el archivo oficial sin tocar: su SHA-256 es el del atributo integrity."""
    archivo = WEB / "chart-4.4.1.umd.js"
    esperado = "sha256-" + base64.b64encode(hashlib.sha256(archivo.read_bytes()).digest()).decode()
    assert esperado == "sha256-dEAdc43T4D7l37O2hBIQ/ixOrYqWDEARykugt4qf2PM="  # el de jsDelivr para chart.js@4.4.1
    for pagina in ("datos.html", "legislatura.html"):
        assert f'src="chart-4.4.1.umd.js?v=' in (WEB / pagina).read_text(encoding="utf-8")
        assert f'integrity="{esperado}"' in (WEB / pagina).read_text(encoding="utf-8")


def test_las_descargas_usan_https_y_verifican_certificados():
    """Ningún módulo desactiva la verificación de certificados ni pide nada por http (salvo la IA local)."""
    codigo = {p.relative_to(RAIZ).as_posix(): p.read_text(encoding="utf-8")
              for p in [*RAIZ.joinpath("boe").glob("*.py"), *RAIZ.joinpath("herramientas").glob("*.py")]}
    assert not [n for n, t in codigo.items() if re.search(r"verify\s*=\s*False", t)]
    http = [f"{n}: {u}" for n, t in codigo.items() for u in re.findall(r"http://[^\s\"']+", t)
            if not u.startswith("http://localhost")]
    assert not http, http
