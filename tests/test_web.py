"""Pruebas de la web estática (sin navegador): versiones de caché, ids y sintaxis del JavaScript."""

import re
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parent.parent
WEB = RAIZ / "web"
sys.path.insert(0, str(RAIZ / "herramientas"))
import versionar  # noqa: E402

PAGINAS = sorted(WEB.glob("*.html"))
# Cada script de página y el HTML que lo carga (app.js es común y se prueba con cada página).
SCRIPT_DE = {"portada.js": "index.html", "explorar.js": "datos.html", "legislatura.js": "legislatura.html", "como.js": "como.html",
             "informe.js": "legislatura.html", "dinero.js": "dinero.html", "tribunales.js": "tribunales.html"}


def test_cada_html_lleva_la_version_de_su_contenido():
    """Si falla: se cambió un .js o el .css sin pasar `python herramientas/versionar.py`."""
    malos = [f"{p.name}: {recurso}?v={v} (toca {versionar.version(WEB / recurso)})"
             for p in PAGINAS for recurso, v in versionar.enlaces(p.read_text(encoding="utf-8"))
             if v != versionar.version(WEB / recurso)]
    assert not malos, "Pasa python herramientas/versionar.py:\n" + "\n".join(malos)


def test_todos_los_recursos_llevan_version():
    sin = [f"{p.name}: {m}" for p in PAGINAS
           for m in re.findall(r'(?:src|href)="([\w.-]+\.(?:js|css))"', p.read_text(encoding="utf-8"))]
    assert not sin, sin


@pytest.mark.parametrize("script,pagina", sorted(SCRIPT_DE.items()))
def test_los_ids_que_usa_cada_script_existen_en_su_pagina(script, pagina):
    """$("id") en el script de una página debe tener su id="…" en el HTML (o crearse en el propio JS)."""
    js = (WEB / script).read_text(encoding="utf-8")
    html = (WEB / pagina).read_text(encoding="utf-8")
    usados = set(re.findall(r'\$\("([\w-]+)"\)', js))
    existentes = set(re.findall(r'\bid="([\w-]+)"', html)) | set(re.findall(r'\bid: "([\w-]+)"', js))
    assert not usados - existentes, f"{script} usa ids que no están en {pagina}: {sorted(usados - existentes)}"


@pytest.mark.parametrize("pagina", [p.name for p in PAGINAS])
def test_ningun_id_se_repite_en_la_pagina(pagina):
    """Con un id repetido, $("id") devuelve el primero y el script pinta en el elemento equivocado
    (pasó con el glosario de como.html)."""
    ids = re.findall(r'\sid="([^"]+)"', (WEB / pagina).read_text(encoding="utf-8"))
    repetidos = sorted({i for i in ids if ids.count(i) > 1})
    assert not repetidos, f"{pagina}: ids repetidos {repetidos}"


def test_los_enlaces_a_otra_pagina_llevan_a_un_ancla_que_existe():
    """«Cómo se calcula», «Correcciones» y demás enlaces pagina.html#ancla: el ancla tiene que estar en esa página.
    Las fichas (#BOE-…) las abre el JavaScript y no son anclas del HTML."""
    ids = {p.name: set(re.findall(r'\sid="([^"]+)"', p.read_text(encoding="utf-8"))) for p in PAGINAS}
    rotos = [f"{p.name} → {destino}#{ancla}" for p in PAGINAS
             for destino, ancla in re.findall(r'href="([\w-]+\.html)#([\w-]+)"', p.read_text(encoding="utf-8"))
             if destino in ids and ancla not in ids[destino] and not ancla.startswith("BOE-")]
    assert not rotos, rotos


@pytest.mark.skipif(not shutil.which("node"), reason="sin Node.js (en la Action sí está)")
@pytest.mark.parametrize("script", sorted(p.name for p in WEB.glob("*.js")))
def test_el_javascript_no_tiene_errores_de_sintaxis(script):
    r = subprocess.run(["node", "--check", str(WEB / script)], capture_output=True, text=True)
    assert r.returncode == 0, r.stderr


# Frases que quedaron desfasadas (revisión del 25/11/2026): que no vuelvan.
FRASES_DESFASADAS = [
    "solo BOE y Congreso",
    "desde finales de agosto de 2026",
    "suplemento aparte del BOE que aún no recogemos",
    "todavía no sus cifras de votación",
    "se pidió 43 veces",
    "Los resúmenes son orientativos",
]


@pytest.mark.parametrize("pagina", sorted(p.name for p in WEB.glob("*.html")))
def test_sin_frases_desfasadas(pagina):
    texto = (WEB / pagina).read_text(encoding="utf-8")
    # Las correcciones citan las frases antiguas entre comillas: se miran fuera de ese apartado.
    texto = re.sub(r"<summary>Correcciones</summary>.*?</ul>", "", texto, flags=re.S)
    for frase in FRASES_DESFASADAS:
        assert frase not in texto, f"{pagina}: «{frase}»"


def test_fecha_de_la_norma_sale_del_titulo_solo_si_empieza_por_su_rango():
    """Copia en Python de fechaDeLaNorma() de app.js (sin Node en el portátil); la regex se lee del propio app.js."""
    js = (WEB / "app.js").read_text(encoding="utf-8")
    patron = re.search(r"resto\.match\(/(.+?)/\);", js).group(1)
    meses = re.search(r"^const MESES = \[(.*?)\];", js, re.M).group(1).replace('"', "").split(", ")

    def fecha(titulo, rango):
        if not titulo.startswith(rango):
            return None
        m = re.match(patron, titulo[len(rango):])
        if not m or m[3] not in meses:
            return None
        anio = m[4] or (re.search(r"/(\d{4})$", m[1] or "") or [None, None])[1]
        return f"{int(m[2])} de {m[3]} de {anio}" if anio else None

    assert fecha("Real Decreto-ley 5/2026, de 3 de marzo, por el que...", "Real Decreto-ley") == "3 de marzo de 2026"
    assert fecha("Orden INT/985/2023, de 16 de agosto, por la que...", "Orden") == "16 de agosto de 2023"
    assert fecha("Resolución de 1 de septiembre de 2023, de la Presidencia...", "Resolución") == "1 de septiembre de 2023"
    assert fecha("Corrección de errores del Real Decreto 676/2023, de 18 de julio, por...", "Corrección (errores o erratas)") is None
    assert fecha("Recurso de inconstitucionalidad n.º 5580-2023, contra la Ley 4/2023, de 6 de julio, ...", "Providencia") is None
