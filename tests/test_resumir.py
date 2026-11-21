"""Pruebas del paso 4 (boe/resumir.py). Sin red: la IA es un cliente falso."""

import json

import pytest

from boe import resumir

# ---------- Título simplificado (títulos reales de noviembre de 2026) ----------

@pytest.mark.parametrize("oficial, esperado", [
    ("Real Decreto 1013/2026, de 18 de noviembre, por el que se fija el salario mínimo "
     "interprofesional para 2027.",
     "Se fija el salario mínimo interprofesional para 2027."),
    ("Ley 10/2026, de 9 de julio, de presupuestos de la Generalitat de Catalunya para 2026.",
     "Presupuestos de la Generalitat de Catalunya para 2026."),
    ("Real Decreto 1006/2026, de 18 de noviembre, sobre el uso de los sistemas de limpieza de "
     "gases de escape de buques.",
     "Sobre el uso de los sistemas de limpieza de gases de escape de buques."),
    ("Resolución de 18 de noviembre de 2026, del Congreso de los Diputados, por la que se ordena "
     "la publicación del Acuerdo de convalidación del Real Decreto-ley 30/2026, de 13 de octubre.",
     "El Congreso convalida el Real Decreto-ley 30/2026, de 13 de octubre."),
    ("Corrección de errores del Decreto-ley 4/2026, de 28 de julio, de actuaciones urgentes en "
     "materia de urbanismo.",
     "Corrección de errores: Decreto-ley 4/2026, de 28 de julio, de actuaciones urgentes en "
     "materia de urbanismo."),
    # La acción principal es "estima el recurso", no el "por el que" de la norma citada.
    ("Sentencia de 15 de octubre de 2026, de la Sala Tercera del Tribunal Supremo, que estima el "
     "recurso 396/2025 contra el Real Decreto 1/2025, por el que se modifica el Real Decreto 1135/2002.",
     "El Tribunal Supremo estima el recurso 396/2025 contra el Real Decreto 1/2025, por el que se "
     "modifica el Real Decreto 1135/2002."),
    ("Acuerdo sobre Transporte Aéreo entre el Reino de España y Uruguay.",
     "Acuerdo sobre Transporte Aéreo entre el Reino de España y Uruguay."),
])
def test_titulo_simplificado(oficial, esperado):
    assert resumir.titulo_simplificado(oficial) == esperado


def test_titulo_simplificado_no_anade_palabras_nuevas_salvo_las_fijas():
    oficial = ("Orden PJC/1225/2026, de 16 de noviembre, por la que se determina el importe "
               "económico de las actuaciones de asistencia jurídica gratuita.")
    palabras_oficiales = set(oficial.lower().replace(",", " ").replace(".", " ").split())
    simplificado = resumir.titulo_simplificado(oficial).lower().replace(".", " ").split()
    assert set(simplificado) <= palabras_oficiales


# ---------- Verificación contra el texto oficial ----------

TEXTO = (
    "Artículo 1. Cuantía del salario mínimo interprofesional. "
    "El salario mínimo para cualquier actividad queda fijado en 1.250,00 euros al mes. "
    "Este real decreto será de aplicación a todas las personas trabajadoras por cuenta ajena. "
    "Disposición final. Este real decreto entrará en vigor el día siguiente al de su publicación "
    "y surtirá efectos durante el período comprendido entre el 1 de enero y el 31 de diciembre de 2027. "
) * 3  # para superar el mínimo de longitud


def ficha_buena():
    return {
        "titulo_llano": "Sube el salario mínimo para 2027.",
        "que_cambia": "El salario mínimo queda en 1.250,00 euros al mes.",
        "a_quien_afecta": "A las personas trabajadoras por cuenta ajena.",
        "desde_cuando": "Del 1 de enero al 31 de diciembre de 2027.",
        "que_hacer": resumir.NO_CONSTA,
        "citas": {
            "que_cambia": "queda fijado en 1.250,00 euros al mes",
            "a_quien_afecta": "todas las personas trabajadoras por cuenta ajena",
            "desde_cuando": "entre el 1 de enero y el 31 de diciembre de 2027",
            "que_hacer": "",
        },
    }


def test_ficha_fiel_al_texto_pasa_la_verificacion():
    assert resumir.verificar_ficha(ficha_buena(), TEXTO) == []


def test_cifra_inventada_se_detecta():
    ficha = ficha_buena() | {"que_cambia": "El salario mínimo sube a 1.300 euros al mes."}
    problemas = resumir.verificar_ficha(ficha, TEXTO)
    assert any("1300" in p for p in problemas)


def test_cita_que_no_esta_en_el_texto_se_detecta():
    ficha = ficha_buena()
    ficha["citas"]["a_quien_afecta"] = "también a los autónomos y a los pensionistas"
    assert any("cita no aparece" in p for p in resumir.verificar_ficha(ficha, TEXTO))


def test_campo_sin_cita_se_detecta():
    ficha = ficha_buena()
    ficha["citas"]["desde_cuando"] = ""
    assert any("sin cita" in p for p in resumir.verificar_ficha(ficha, TEXTO))


def test_la_cita_tolera_mayusculas_tildes_y_espacios():
    ficha = ficha_buena()
    ficha["citas"]["a_quien_afecta"] = "TODAS las personas   trabajadoras por cuenta ajena"
    assert resumir.verificar_ficha(ficha, TEXTO) == []


# ---------- Generación de fichas ----------

class ClienteFalso:
    modelo = "modelo-de-prueba"

    def __init__(self, respuesta):
        self.respuesta = respuesta
        self.llamadas = 0

    def completar_json(self, sistema, usuario):
        self.llamadas += 1
        return self.respuesta


NORMA = {"id": "BOE-A-2026-24189", "titulo": "Real Decreto 1013/2026, de 18 de noviembre, por el "
         "que se fija el salario mínimo interprofesional para 2027.",
         "url_html": "https://www.boe.es/diario_boe/txt.php?id=BOE-A-2026-24189"}


def test_sin_ia_la_ficha_es_pendiente_con_aviso_y_enlace():
    ficha = resumir.generar_ficha(NORMA)
    assert ficha["estado"] == "pendiente"
    assert ficha["titulo_llano"] == "Se fija el salario mínimo interprofesional para 2027."
    assert ficha["aviso"] == resumir.AVISO and ficha["enlace"] == NORMA["url_html"]
    assert "que_cambia" not in ficha  # una ficha pendiente no muestra contenido


def test_con_ia_fiable_la_ficha_es_ok():
    ficha = resumir.generar_ficha(NORMA, ClienteFalso(ficha_buena()), lambda _id: TEXTO)
    assert ficha["estado"] == "ok" and ficha["aviso"] == resumir.AVISO
    assert ficha["que_cambia"].startswith("El salario mínimo")


def test_con_ia_que_inventa_la_ficha_queda_pendiente():
    inventada = ficha_buena() | {"desde_cuando": "Desde el 1 de marzo de 2026."}
    ficha = resumir.generar_ficha(NORMA, ClienteFalso(inventada), lambda _id: TEXTO)
    assert ficha["estado"] == "pendiente" and "descartado" in ficha["motivo_pendiente"]


def test_si_falla_la_descarga_del_texto_queda_pendiente():
    def falla(_id):
        raise ConnectionError("sin red")
    ficha = resumir.generar_ficha(NORMA, ClienteFalso(ficha_buena()), falla)
    assert ficha["estado"] == "pendiente"


def test_resumir_carpeta_no_repite_fichas_verificadas(tmp_path):
    (tmp_path / "n.json").write_text(json.dumps(NORMA), encoding="utf-8")
    cliente = ClienteFalso(ficha_buena())
    resumir.resumir_carpeta(tmp_path, cliente, lambda _id: TEXTO)
    resumir.resumir_carpeta(tmp_path, cliente, lambda _id: TEXTO)
    assert cliente.llamadas == 1
