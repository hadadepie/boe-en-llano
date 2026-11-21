"""Pruebas del paso 3 (boe/clasificar.py y boe/ia.py). Sin red."""

import json

import pytest

from boe import clasificar, ia


def norma(**campos):
    base = {"id": "BOE-A-2026-00001", "titulo": "", "epigrafe": "", "rango": "Real Decreto",
            "materias": [], "origen_legislativo": "Estatal", "departamento": "Jefatura del Estado"}
    return base | campos


# ---------- Reglas (casos tomados de normas reales de noviembre de 2026) ----------

def test_salario_minimo_es_trabajo_y_directo():
    n = norma(titulo="Real Decreto 1013/2026, por el que se fija el salario mínimo interprofesional para 2027.",
              epigrafe="Salario mínimo interprofesional", materias=["Salario Mínimo Interprofesional"])
    c = clasificar.clasificar(n)
    assert (c["tema"], c["impacto"]) == ("Trabajo y empleo", "Directo")


def test_subvencion_directa_a_entidad_es_tecnica():
    n = norma(titulo="Real Decreto por el que se regula la concesión directa de una subvención a una fundación.",
              epigrafe="Subvenciones", materias=["Subvenciones", "Fundaciones"])
    c = clasificar.clasificar(n)
    assert (c["tema"], c["impacto"]) == ("Instituciones, ayudas e internacional", "Técnico")


def test_convalidacion_de_real_decreto_ley_es_tecnica():
    n = norma(rango="Resolución", titulo="Resolución por la que se ordena la publicación del Acuerdo de "
              "convalidación del Real Decreto-ley 31/2026, de mejora de la Seguridad Social.")
    assert clasificar.clasificar_impacto(n)[0] == "Técnico"


def test_correccion_de_errores_es_tecnica():
    assert clasificar.clasificar_impacto(norma(rango="Corrección (errores o erratas)"))[0] == "Técnico"


def test_precio_del_butano_es_directo_y_energia():
    n = norma(rango="Resolución", epigrafe="Productos petrolíferos. Precios",
              titulo="Resolución por la que se publican los nuevos precios máximos de venta del butano.")
    c = clasificar.clasificar(n)
    assert (c["tema"], c["impacto"]) == ("Movilidad, energía y medio ambiente", "Directo")


def test_ley_omnibus_no_la_deciden_solo_las_materias():
    n = norma(rango="Ley", epigrafe="Medidas fiscales, financieras y administrativas",
              titulo="Ley 11/2026, de medidas fiscales, financieras, administrativas y del sector público.",
              materias=["Transporte de viajeros", "Aguas", "Puertos", "Carreteras", "Gestión de residuos",
                        "Medio ambiente", "Cambio climático", "Ferrocarriles"])
    assert clasificar.clasificar_tema(n)[0] == "Impuestos y dinero"


def test_palabras_cortas_deben_coincidir_enteras():
    assert clasificar._contiene("gas natural", "gas")
    assert not clasificar._contiene("gastos de personal", "gas")


def test_sin_coincidencias_usa_tema_por_defecto():
    assert clasificar.clasificar_tema(norma(titulo="Xyz"))[0] == clasificar.TEMA_POR_DEFECTO


def test_todas_las_salidas_son_valores_permitidos():
    c = clasificar.clasificar(norma(titulo="Cualquier cosa"))
    assert c["tema"] in clasificar.TEMAS and c["impacto"] in clasificar.IMPACTOS


@pytest.mark.parametrize("origen, organo, esperado", [
    ("Estatal", "Ministerio de Hacienda", "Estatal"),
    ("Autonómico", "Comunidad Autónoma de Cataluña", "Cataluña"),
    ("Autonómico", "Comunidad Autónoma de Castilla-La Mancha", "Castilla-La Mancha"),
    ("Autonómico", "Comunidad Foral de Navarra", "Comunidad Foral de Navarra"),
    ("Autonómico", "Comunidad Autónoma de las Illes Balears", "Illes Balears"),
])
def test_ambito(origen, organo, esperado):
    assert clasificar.clasificar_ambito(norma(origen_legislativo=origen, departamento=organo)) == esperado


# ---------- IA (con un cliente falso) ----------

class ClienteFalso:
    modelo = "modelo-de-prueba"

    def __init__(self, respuesta):
        self.respuesta = respuesta
        self.llamadas = 0

    def completar_json(self, sistema, usuario):
        self.llamadas += 1
        return self.respuesta


def test_ia_valida_acepta_respuesta_correcta():
    cliente = ClienteFalso({"tema": "Vivienda y urbanismo", "impacto": "Directo", "motivo": "alquiler"})
    r = ia.clasificar_con_ia(cliente, norma(), "texto", clasificar.TEMAS, clasificar.IMPACTOS)
    assert r["tema"] == "Vivienda y urbanismo" and r["clasificacion"]["metodo"] == "ia"


def test_ia_rechaza_valores_inventados():
    cliente = ClienteFalso({"tema": "Deportes extremos", "impacto": "Directo"})
    assert ia.clasificar_con_ia(cliente, norma(), "", clasificar.TEMAS, clasificar.IMPACTOS) is None


def test_extraer_json_tolera_texto_alrededor():
    assert ia.extraer_json('Claro: {"tema": "x"} ¡listo!') == {"tema": "x"}
    assert ia.extraer_json("sin json") is None


def test_sin_variables_de_entorno_no_hay_ia(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)  # sin .env
    monkeypatch.delenv("BOE_IA_PROVEEDOR", raising=False)
    assert ia.cliente_desde_entorno() is None


def test_ollama_se_configura_con_url_local(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("BOE_IA_PROVEEDOR", "ollama")
    monkeypatch.setenv("BOE_IA_MODELO", "llama3.1:8b")
    monkeypatch.delenv("BOE_IA_URL", raising=False)
    cliente = ia.cliente_desde_entorno()
    assert cliente.url_base == "http://localhost:11434/v1" and cliente.clave is None


def test_clasificar_carpeta_no_repite_llamadas_a_la_ia(tmp_path):
    (tmp_path / "BOE-A-2026-00001.json").write_text(json.dumps(norma(titulo="Algo")), encoding="utf-8")
    cliente = ClienteFalso({"tema": "Derechos e igualdad", "impacto": "Colectivos"})

    clasificar.clasificar_carpeta(tmp_path, cliente_ia=cliente, texto_de=lambda _id: "texto")
    clasificar.clasificar_carpeta(tmp_path, cliente_ia=cliente, texto_de=lambda _id: "texto")

    assert cliente.llamadas == 1
    guardada = json.loads((tmp_path / "BOE-A-2026-00001.json").read_text(encoding="utf-8"))
    assert guardada["tema"] == "Derechos e igualdad" and guardada["clasificacion"]["metodo"] == "ia"
