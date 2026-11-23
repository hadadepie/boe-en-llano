"""Pruebas del paso 4 (boe/resumir.py). Sin red: la IA es un cliente falso."""

import json
import re

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


# ---------- Titular corto (titulares simplificados reales de 2026) ----------

@pytest.mark.parametrize("simplificado, esperado", [
    # Corto: no se toca.
    ("Se fija el salario mínimo interprofesional para 2027.",
     "Se fija el salario mínimo interprofesional para 2027."),
    # Fuera número y fecha de la norma citada; se queda su descripción.
    ("Se modifica la Orden DEF/1363/2016, de 28 de julio, por la que se regulan la jornada.",
     "Se modifica la Orden por la que se regulan la jornada."),
    # El real decreto-ley conserva su número (sin la fecha).
    ("El Congreso convalida el Real Decreto-ley 36/2026, de 10 de noviembre, de medidas para la dependencia.",
     "El Congreso convalida el Real Decreto-ley 36/2026, de medidas para la dependencia."),
    # Fecha y órgano de una resolución citada.
    ("Se actualiza el Anexo 1 incluido en la Resolución de 4 de julio de 2017, de la Secretaría General "
     "del Tesoro y Política Financiera, por la que se define el principio de prudencia financiera.",
     "Se actualiza el Anexo 1 incluido en la Resolución por la que se define el principio de prudencia financiera."),
    # Quién interpuso el recurso.
    ("El Tribunal Supremo estima parcialmente el recurso contencioso-administrativo 19/2025, interpuesto por "
     "la Asociación Pro Derechos Humanos de España, y Extranjeristas en Red, contra el Real Decreto 1155/2024, "
     "de 19 de noviembre, por el que se aprueba el Reglamento de extranjería.",
     "El Tribunal Supremo estima parcialmente el recurso contra el Real Decreto por el que se aprueba el "
     "Reglamento…"),
    # Dónde y cuándo se firmó un acuerdo internacional.
    ("Acuerdo sobre Transporte Aéreo entre el Reino de España y la República Oriental del Uruguay, "
     "hecho en Kuala Lumpur el 22 de octubre de 2024.",
     "Acuerdo sobre Transporte Aéreo entre el Reino de España y la República Oriental del Uruguay."),
    # Largo: se corta en una cláusula, sin acabar en «de», «la»…, y con «…».
    ("Se regula la concesión directa de una subvención a la Federación Española de Municipios y Provincias "
     "para la financiación de los gastos de funcionamiento de su actividad.",
     "Se regula la concesión directa de una subvención a la Federación Española de Municipios…"),
])
def test_titular_corto(simplificado, esperado):
    assert resumir.titular_corto(simplificado) == esperado


def test_titular_corto_no_pasa_del_maximo_ni_anade_palabras():
    largo = ("Se modifican el Real Decreto 956/2017, de 3 de noviembre, por el que se establece el marco "
             "regulador de ayudas a las organizaciones profesionales del sector de la pesca y de la acuicultura, "
             "cofinanciadas por el Fondo Europeo Marítimo y de Pesca; y el Real Decreto 1044/2022, de 27 de "
             "diciembre, de ordenación de la flota pesquera.")
    corto = resumir.titular_corto(largo)
    assert len(corto) <= resumir.MAX_TITULAR_CORTO + 1  # +1 por «…»
    assert corto.endswith("…")
    palabras = lambda s: set(re.findall(r"\w+", s.lower()))
    assert palabras(corto) <= palabras(largo)


# ---------- Párrafos y verificación contra el texto oficial ----------

PARRAFOS = [
    "Artículo 1. Cuantía del salario mínimo interprofesional.",                                   # [1]
    "El salario mínimo para cualquier actividad queda fijado en 1.250,00 euros al mes.",          # [2]
    "Este real decreto será de aplicación a todas las personas trabajadoras por cuenta ajena.",   # [3]
    "Disposición final. Este real decreto entrará en vigor el día siguiente al de su "
    "publicación y surtirá efectos entre el 1 de enero y el 31 de diciembre de 2027.",          # [4]
    "Se aplicará también a las personas empleadas de hogar con un mínimo de 120 horas.",         # [5]
]
TEXTO = "\n".join(PARRAFOS * 2)  # repetido para superar el mínimo de longitud


def ficha_buena():
    return {
        "titulo_llano": "Sube el salario mínimo para 2027.",
        "que_cambia": "El salario mínimo queda en 1.250,00 euros al mes.",
        "a_quien_afecta": "A las personas trabajadoras por cuenta ajena.",
        "desde_cuando": "Del 1 de enero al 31 de diciembre de 2027.",
        "que_hacer": resumir.NO_CONSTA,
        "fuentes": {"que_cambia": [2], "a_quien_afecta": [3], "desde_cuando": [4], "que_hacer": []},
    }


def test_ficha_fiel_al_texto_pasa_la_verificacion():
    assert resumir.verificar_ficha(ficha_buena(), PARRAFOS) == []


def test_cifra_inventada_se_detecta():
    ficha = ficha_buena() | {"que_cambia": "El salario mínimo sube a 1.300 euros al mes."}
    assert any("1300" in p for p in resumir.verificar_ficha(ficha, PARRAFOS))


def test_cifra_real_pero_de_otro_parrafo_se_detecta():
    # El 120 existe en el texto ([5]), pero no en el párrafo citado ([3]).
    ficha = ficha_buena() | {"a_quien_afecta": "A las personas trabajadoras, desde 120 horas."}
    assert any("120" in p for p in resumir.verificar_ficha(ficha, PARRAFOS))


def test_calculo_propio_del_modelo_se_detecta():
    # Caso real de gemma3:4b: calcular una cifra mensual que el texto no da.
    ficha = ficha_buena() | {"que_cambia": "Son 1.250,00 euros al mes, es decir, 15.000 euros al año."}
    assert any("15000" in p for p in resumir.verificar_ficha(ficha, PARRAFOS))


def test_campo_sin_fuentes_se_detecta():
    ficha = ficha_buena()
    ficha["fuentes"]["desde_cuando"] = []
    assert any("no cita" in p for p in resumir.verificar_ficha(ficha, PARRAFOS))


def test_parrafo_inexistente_se_detecta():
    ficha = ficha_buena()
    ficha["fuentes"]["a_quien_afecta"] = [3, 99]
    assert any("no existen" in p for p in resumir.verificar_ficha(ficha, PARRAFOS))


def test_numero_con_letra_que_no_esta_en_los_parrafos_citados_se_detecta():
    # Caso real de gemma3:4b: "diez días hábiles" citando párrafos que no lo dicen.
    ficha = ficha_buena() | {"a_quien_afecta": "A las personas trabajadoras, que tienen diez días."}
    assert any("10" in p for p in resumir.verificar_ficha(ficha, PARRAFOS))


def test_articulos_un_una_no_cuentan_como_numeros():
    ficha = ficha_buena() | {"a_quien_afecta": "A una persona trabajadora por cuenta ajena."}
    assert resumir.verificar_ficha(ficha, PARRAFOS) == []


def test_desde_cuando_debe_citar_un_parrafo_de_vigencia_con_contenido():
    lista = PARRAFOS + ["Disposición final séptima. Entrada en vigor."]  # [6]: solo encabezado
    ficha = ficha_buena() | {"desde_cuando": "Desde su publicación."}
    ficha["fuentes"]["desde_cuando"] = [6]
    assert any("vigencia" in p for p in resumir.verificar_ficha(ficha, lista))
    ficha["fuentes"]["desde_cuando"] = [2]  # párrafo largo pero sin vigencia ni efectos
    assert any("vigencia" in p for p in resumir.verificar_ficha(ficha, lista))


def test_mencionar_un_boletin_que_no_esta_en_los_parrafos_citados_se_detecta():
    # Caso real: ley autonómica "desde su publicación en el Boletín Oficial del Estado".
    ficha = ficha_buena() | {"desde_cuando": "Desde su publicación en el Boletín Oficial del Estado."}
    assert any("boletín" in p for p in resumir.verificar_ficha(ficha, PARRAFOS))


def test_extracto_incluye_el_parrafo_siguiente_a_un_encabezado_de_vigor():
    lista = ["Relleno " + "x" * 300 for _ in range(60)]
    lista[50] = "Disposición final séptima. Entrada en vigor."
    lista[51] = "Este real decreto-ley entrará en vigor el día siguiente al de su publicación."
    extracto = resumir.extracto_numerado(lista, maximo=3000)
    assert "[51] Disposición final séptima" in extracto and "[52] Este real decreto-ley" in extracto


def test_no_se_reintenta_con_el_mismo_modelo_pero_si_con_otro(tmp_path):
    (tmp_path / "n.json").write_text(json.dumps(NORMA), encoding="utf-8")
    mala = ficha_buena() | {"que_cambia": "Sube a 9.999 euros."}
    cliente = ClienteFalso(mala)
    resumir.resumir_carpeta(tmp_path, cliente, lambda _id: TEXTO)
    resumir.resumir_carpeta(tmp_path, cliente, lambda _id: TEXTO)
    assert cliente.llamadas == 1  # el mismo modelo no vuelve a intentarlo

    otro = ClienteFalso(ficha_buena())
    otro.modelo = "otro-modelo"
    resumir.resumir_carpeta(tmp_path, otro, lambda _id: TEXTO)
    assert otro.llamadas == 1
    guardada = json.loads((tmp_path / "n.json").read_text(encoding="utf-8"))
    assert guardada["ficha"]["estado"] == "ok" and guardada["ficha"]["aviso_ia"] == resumir.AVISO_IA


def test_extracto_numerado_conserva_numeros_y_prioriza_entrada_en_vigor():
    lista = [f"Párrafo de relleno número {i}. " + "x" * 200 for i in range(100)]
    lista[90] = "Disposición final única. Este real decreto entrará en vigor el día siguiente."
    extracto = resumir.extracto_numerado(lista, maximo=2000)
    assert extracto.startswith("[1] Párrafo de relleno número 0.")
    assert "[91] Disposición final única." in extracto
    assert "[...]" in extracto and len(extracto) < 2500


# ---------- Generación de fichas ----------

class ClienteFalso:
    modelo = "modelo-de-prueba"

    def __init__(self, respuesta):
        self.respuesta = respuesta
        self.llamadas = 0

    def completar_json(self, sistema, usuario, esquema=None):
        self.llamadas += 1
        self.esquema = esquema
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


def test_solo_limita_la_ia_a_las_normas_indicadas(tmp_path):
    for i in range(3):
        (tmp_path / f"n{i}.json").write_text(json.dumps(NORMA | {"id": f"BOE-A-2026-0000{i}"}), encoding="utf-8")
    cliente = ClienteFalso(ficha_buena())
    normas = resumir.resumir_carpeta(tmp_path, cliente, lambda _id: TEXTO, solo=["BOE-A-2026-00001"])
    assert cliente.llamadas == 1
    estados = {n["id"]: n["ficha"]["estado"] for n in normas}
    assert estados == {"BOE-A-2026-00000": "pendiente", "BOE-A-2026-00001": "ok", "BOE-A-2026-00002": "pendiente"}


# ---------- Corrección: cifras escritas como en el BOE (caso real, 22/11/2026) ----------
# El RD 1013/2026 dice "1 286 euros/mes" (miles con espacio) y "ciento veinte días"
# (con letras). El validador rechazaba por error "1.286" y "120".

PARRAFOS_SMI = [
    "Artículo 1. Cuantías del salario mínimo interprofesional.",
    "El salario mínimo para cualesquiera actividades en la agricultura, en la industria y en los "
    "servicios queda fijado para 2027 en 42,87 euros/día o 1 286 euros/mes, según el salario esté "
    "fijado por días o por meses.",
    "1. Las personas trabajadoras con contratos de trabajo de duración determinada cuyos servicios "
    "a una misma empresa no excedan de ciento veinte días percibirán la parte proporcional.",
]


def ficha_smi(**cambios):
    base = {
        "titulo_llano": "Sube el salario mínimo para 2027.",
        "que_cambia": "El salario mínimo será de 42,87 euros al día o 1.286 euros al mes.",
        "a_quien_afecta": "También a contratos temporales de hasta 120 días.",
        "desde_cuando": resumir.NO_CONSTA,
        "que_hacer": resumir.NO_CONSTA,
        "fuentes": {"que_cambia": [2], "a_quien_afecta": [3], "desde_cuando": [], "que_hacer": []},
    }
    return base | cambios


def test_miles_separados_con_espacio_se_leen_como_un_numero():
    assert resumir.numeros("42,87 euros/día o 1 286 euros/mes") == {"4287", "1286"}
    assert resumir.numeros("1 286 euros") == {"1286"}


def test_numeros_con_letra_se_convierten_a_su_valor():
    assert resumir.numeros_con_letra("no excedan de ciento veinte días") == {"120"}
    assert resumir.numeros_con_letra("treinta y cinco") == {"35"}
    assert resumir.numeros_con_letra("dos mil veintiséis") == {"2026"}
    assert resumir.numeros_con_letra("una persona y dos hijos") == {"2"}  # "una" sola no cuenta


def test_la_ficha_correcta_del_salario_minimo_ya_no_se_rechaza():
    assert resumir.verificar_ficha(ficha_smi(), PARRAFOS_SMI) == []


def test_pero_una_cifra_realmente_inventada_se_sigue_rechazando():
    ficha = ficha_smi(que_cambia="El salario mínimo será de 1.300 euros al mes.")
    assert any("1300" in p for p in resumir.verificar_ficha(ficha, PARRAFOS_SMI))
    ficha = ficha_smi(a_quien_afecta="A contratos temporales de hasta 90 días.")
    assert any("90" in p for p in resumir.verificar_ficha(ficha, PARRAFOS_SMI))
