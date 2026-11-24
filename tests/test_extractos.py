"""Pruebas de boe/extractos.py: frases literales del texto oficial para la ficha."""

from boe import extractos

TEXTO = "\n".join([
    "La Ley 7/2022 encomienda al Gobierno regular los envases.",
    "Este real decreto se dicta al amparo de lo dispuesto en el artículo 149.1.13.ª de la Constitución, según anuncia el preámbulo.",
    "Las ayudas tienen por finalidad apoyar a los municipios afectados.",
    "DISPONGO:",
    "Artículo 1. Objeto.",
    "1. Este real decreto tiene por objeto regular la concesión directa de una subvención a la Federación Española de Municipios.",
    "2. La subvención se concede con carácter excepcional.",
    "Disposición final primera. Modificación del Real Decreto 1/2020.",
    "«Disposición final segunda. Entrada en vigor.",
    "Este real decreto entrará en vigor el 1 de enero de 2021.»",
    "Disposición final segunda. Título competencial.",
    "Este real decreto se dicta al amparo de lo establecido en:",
    "a) El artículo 149.1.13.ª de la Constitución Española, sobre bases de la actividad económica.",
    "b) La regla 23.ª del artículo 149.1, sobre legislación básica del medio ambiente.",
    "Disposición final tercera. Entrada en vigor.",
    "El presente real decreto entrará en vigor el día siguiente al de su publicación en el «Boletín Oficial del Estado».",
])


def test_objeto_es_la_frase_sobre_la_propia_norma():
    o = extractos.extractos_de_texto(TEXTO)["objeto"]
    # «Las ayudas tienen por finalidad» no cuenta: no habla de la norma.
    assert o["parrafo"] == 6
    assert o["texto"].startswith("1. Este real decreto tiene por objeto regular la concesión directa")


def test_entrada_en_vigor_es_la_ultima_disposicion_no_la_citada_entre_comillas():
    v = extractos.extractos_de_texto(TEXTO)["entrada_en_vigor"]
    assert v == {"parrafo": 16, "texto": "El presente real decreto entrará en vigor el día siguiente al de su publicación en el «Boletín Oficial del Estado»."}


def test_competencia_copia_el_parrafo_con_sus_apartados_y_lee_los_articulos():
    c = extractos.extractos_de_texto(TEXTO)["competencia"]
    assert c["parrafo"] == 12
    assert c["texto"].count("\n") == 2  # el encabezado acaba en «:» y le siguen a) y b)
    assert c["articulos"] == ["149.1.13.ª", "149.1.23.ª"]


def test_articulos_149_en_sus_distintas_formas():
    assert extractos.articulos_149("los artículos 149.1.6.ª y 18.ª de la Constitución") == ["149.1.6.ª", "149.1.18.ª"]
    assert extractos.articulos_149("el artículo 149.1 de la Constitución Española, cláusula 19.ª") == ["149.1.19.ª"]
    assert extractos.articulos_149("la regla 14.ª del artículo 149.1") == ["149.1.14.ª"]
    assert extractos.articulos_149("el artículo 149.2 de la Constitución") == ["149.2"]
    assert extractos.articulos_149("el artículo 9.1.16 del Estatuto de Autonomía") == []


def test_competencia_sin_encabezado_solo_si_cita_constitucion_o_estatuto():
    habilitacion = "Disposición final única.\nEste real decreto se dicta al amparo del artículo 26.1 de la Ley 3/2013, de 4 de junio."
    assert "competencia" not in extractos.extractos_de_texto(habilitacion)
    estatuto = "Disposición final única.\nEste decreto-ley se dicta al amparo del artículo 9.1.16 del Estatuto de Autonomía de Extremadura."
    c = extractos.extractos_de_texto(estatuto)["competencia"]
    assert c["parrafo"] == 2 and "articulos" not in c


def test_sin_nada_que_extraer():
    assert extractos.extractos_de_texto("") == {}
    assert extractos.extractos_de_texto("Se nombra a una persona para un cargo.") == {}


def test_parrafo_muy_largo_se_recorta():
    largo = "Esta orden tiene por objeto " + "regular muchas cosas " * 80
    o = extractos.extractos_de_texto(largo)["objeto"]
    assert len(o["texto"]) <= extractos.MAX_CARACTERES + 1 and o["texto"].endswith("…")
