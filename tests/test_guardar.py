"""Pruebas del paso 2 (boe/guardar.py). Sin red: se simulan las descargas."""

import json
from datetime import date
from pathlib import Path

from boe import descargar, guardar

CARPETA = Path(__file__).parent / "datos"
SUMARIO_MINI = json.loads((CARPETA / "sumario_mini.json").read_text(encoding="utf-8"))
XML_MINI = (CARPETA / "norma_mini.xml").read_text(encoding="utf-8")


def test_normas_seccion_i_conserva_departamento_y_epigrafe():
    normas = guardar.normas_seccion_i(SUMARIO_MINI)
    assert [n["id"] for n in normas] == ["BOE-A-2026-00001", "BOE-A-2026-00002", "BOE-A-2026-00003"]
    assert normas[0]["departamento_sumario"] == "CORTES GENERALES"
    assert normas[2]["epigrafe"] == "Un solo epígrafe, que llega suelto"
    assert normas[0]["fecha_publicacion"] == "2026-11-20"


def test_metadatos_de_xml():
    meta = guardar.metadatos_de_xml(XML_MINI)
    assert meta["rango"] == "Resolución"
    assert meta["origen_legislativo"] == "Estatal"
    assert meta["fecha_disposicion"] == "2026-11-18"
    assert meta["fecha_vigencia"] is None
    assert meta["numero_oficial"] is None
    assert meta["materias"] == ["Ceuta", "Subvenciones"]


def test_texto_de_xml_usa_solo_el_texto_principal():
    texto = guardar.texto_de_xml(XML_MINI)
    assert texto == "Primer párrafo con negrita.\nSegundo párrafo."
    assert "NO es el texto" not in texto


def _simular_api(monkeypatch, llamadas):
    def sumario(fecha, carpeta):
        llamadas.append(("sumario", fecha))
        return SUMARIO_MINI

    def norma(identificador, carpeta):
        llamadas.append(("norma", identificador))
        return XML_MINI

    monkeypatch.setattr(descargar, "descargar_sumario", sumario)
    monkeypatch.setattr(descargar, "descargar_norma_xml", norma)


def test_procesar_dia_guarda_recuentos_y_normas(tmp_path, monkeypatch):
    llamadas = []
    _simular_api(monkeypatch, llamadas)

    assert guardar.procesar_dia(date(2026, 11, 20), tmp_path) == "hecho"

    recuentos = json.loads((tmp_path / "recuentos.json").read_text(encoding="utf-8"))
    assert recuentos == {"2026-11-20": {"1": 3, "5A": 2, "5C": 1}}
    norma = json.loads((tmp_path / "normas" / "BOE-A-2026-00001.json").read_text(encoding="utf-8"))
    assert norma["rango"] == "Resolución" and norma["titulo"] == "Norma uno"
    assert len(list((tmp_path / "normas").iterdir())) == 3


def test_procesar_dos_veces_no_vuelve_a_descargar(tmp_path, monkeypatch):
    llamadas = []
    _simular_api(monkeypatch, llamadas)
    guardar.procesar_dia(date(2026, 11, 20), tmp_path)
    llamadas.clear()

    assert guardar.procesar_dia(date(2026, 11, 20), tmp_path) == "ya_estaba"
    assert llamadas == []


def test_dia_sin_boe_no_se_marca_como_procesado(tmp_path, monkeypatch):
    monkeypatch.setattr(descargar, "descargar_sumario", lambda fecha, carpeta: None)
    assert guardar.procesar_dia(date(2026, 11, 22), tmp_path) == "sin_boe"
    assert guardar.leer_recuentos(tmp_path) == {}


# Corrección (22/11/2026): el sumario del 9-sep-2026 usa una cuarta estructura,
# departamento > texto > epígrafe > item, y se perdía el Real Decreto-ley 23/2026.
SUMARIO_TEXTO_EPIGRAFE = {"data": {"sumario": {
    "metadatos": {"publicacion": "BOE", "fecha_publicacion": "20260909"},
    "diario": [{"numero": "223", "seccion": [{
        "codigo": "1", "nombre": "I. Disposiciones generales",
        "departamento": {"codigo": "7723", "nombre": "JEFATURA DEL ESTADO", "texto": {"epigrafe": [
            {"nombre": "Medidas urgentes", "item": {
                "identificador": "BOE-A-2026-18828",
                "titulo": "Real Decreto-ley 23/2026, de 8 de septiembre, por el que se adoptan medidas fiscales.",
                "url_html": "https://www.boe.es/diario_boe/txt.php?id=BOE-A-2026-18828"}}]}},
    }]}],
}}}


def test_estructura_departamento_texto_epigrafe_item():
    normas = guardar.normas_seccion_i(SUMARIO_TEXTO_EPIGRAFE)
    assert [n["id"] for n in normas] == ["BOE-A-2026-18828"]
    assert normas[0]["departamento_sumario"] == "JEFATURA DEL ESTADO"
    assert normas[0]["epigrafe"] == "Medidas urgentes"
    assert descargar.contar_por_seccion(SUMARIO_TEXTO_EPIGRAFE) == {"1": 1}


def test_revisar_corrige_dias_ya_guardados_sin_volver_a_pedir_el_sumario(tmp_path, monkeypatch):
    # Un día guardado con el recuento antiguo (0 en la sección I) y su sumario en crudo.
    (tmp_path / "crudo" / "sumarios").mkdir(parents=True)
    (tmp_path / "crudo" / "sumarios" / "20260909.json").write_text(json.dumps(SUMARIO_TEXTO_EPIGRAFE), encoding="utf-8")
    guardar.escribir_json(tmp_path / "recuentos.json", {"2026-09-09": {"1": 0}})
    monkeypatch.setattr(descargar, "descargar_sumario", lambda *a, **k: (_ for _ in ()).throw(AssertionError("no debe pedir el sumario")))
    monkeypatch.setattr(descargar, "descargar_norma_xml", lambda identificador, carpeta: XML_MINI)

    cambios = guardar.revisar(tmp_path)

    assert cambios == {"2026-09-09": ({"1": 0}, {"1": 1}, 1)}
    assert (tmp_path / "normas" / "BOE-A-2026-18828.json").exists()
    assert guardar.revisar(tmp_path) == {}  # una segunda revisión no cambia nada


# ---------- Preámbulo (por qué se aprueba) ----------

def test_preambulo_salta_formula_encabezados_y_tramite_y_para_en_la_parte_dispositiva():
    texto = "\n".join([
        "Las Cortes de Castilla-La Mancha han aprobado y yo, en nombre del Rey, promulgo la siguiente ley.",
        "EXPOSICIÓN DE MOTIVOS",
        "I",
        "Transcurrido un tiempo desde la aplicación de la Ley 2/2020, se hace necesario regular aspectos que no quedaban definidos en la norma.",
        "Este real decreto cumple con los principios de buena regulación exigibles conforme al artículo 129 de la Ley 39/2015, de 1 de octubre.",
        "Con esta modificación, se da más participación a los Ayuntamientos para que puedan decidir qué proyectos se desarrollan en sus municipios.",
        "II",
        "La presente ley se estructura en un artículo único con ocho apartados, una disposición transitoria y una final, que regulan el procedimiento.",
        "Artículo único. Modificación de la Ley 2/2020.",
        "La Ley 2/2020 se modifica en los siguientes términos, que no forman parte del preámbulo ni deben aparecer en él.",
    ])
    r = guardar.preambulo_de_texto(texto)
    assert [p[:20] for p in r["parrafos"]] == ["Transcurrido un tiem", "Con esta modificació"]
    assert r["recortado"] is True  # había una segunda parte (II) que no se muestra


def test_preambulo_con_indice_previo():
    texto = "\n".join([
        "EL PRESIDENTE DE LA GENERALITAT DE CATALUNYA",
        "Índice",
        "Preámbulo.",
        "Título I. Ámbito de aplicación y aprobación de los presupuestos y régimen de las modificaciones presupuestarias.",
        "Artículo 1. Ámbito de aplicación de los presupuestos de la Generalitat.",
        "Preámbulo",
        "Cataluña afronta el año 2026 con el objetivo de impulsar la prosperidad compartida y reforzar la cohesión social del país.",
        "Título I",
    ])
    r = guardar.preambulo_de_texto(texto)
    assert r["parrafos"] == ["Cataluña afronta el año 2026 con el objetivo de impulsar la prosperidad compartida y reforzar la cohesión social del país."]


def test_sin_preambulo_devuelve_none():
    assert guardar.preambulo_de_texto("DISPONGO:\nArtículo 1. Objeto.") is None
    assert guardar.preambulo_de_texto("") is None
