"""Pruebas de boe/informe.py: quién decidió en la legislatura."""

from boe import exportar, informe


def _n(id, fecha, rango, departamento="Ministerio de Hacienda", origen="Estatal", tema="Impuestos y dinero",
       titulo="Norma", vigor=None):
    n = {"id": id, "fecha_publicacion": fecha, "rango": rango, "departamento": departamento,
         "origen_legislativo": origen, "tema": tema, "titulo": titulo, "textos_oficiales": {}}
    if vigor:
        n["textos_oficiales"]["entrada_en_vigor"] = {"parrafo": 9, "texto": vigor}
    return n


SIGUIENTE = "El presente real decreto entrará en vigor el día siguiente al de su publicación en el «Boletín Oficial del Estado»."
NORMAS = [
    _n("A1", "2023-09-05", "Real Decreto", titulo="Real Decreto 1/2023, por el que se regula la concesión directa de una subvención.",
       tema="Instituciones, ayudas e internacional", vigor=SIGUIENTE),
    _n("A2", "2023-11-21", "Real Decreto", titulo="Real Decreto 829/2023, de 20 de noviembre, por el que se reestructuran los departamentos ministeriales.",
       tema="Instituciones, ayudas e internacional"),
    _n("A3", "2023-12-28", "Real Decreto-ley", departamento="Jefatura del Estado", vigor="Este real decreto-ley entrará en vigor el mismo día de su publicación."),
    _n("A4", "2024-01-10", "Ley Orgánica", departamento="Jefatura del Estado", titulo="Ley Orgánica 1/2024, de amnistía.",
       vigor="La presente ley orgánica entrará en vigor a los veinte días de su publicación."),
    _n("A5", "2024-01-11", "Reforma", departamento="Jefatura del Estado", titulo="Reforma del artículo 49 de la Constitución Española."),
    _n("A6", "2024-01-12", "Orden"),
    _n("A7", "2024-01-12", "Resolución", departamento="Cortes Generales"),  # publica una convalidación
    _n("A8", "2024-01-13", "Reglamento", departamento="Cortes Generales"),
    _n("A9", "2024-01-13", "Circular", departamento="Banco de España"),
    _n("A10", "2024-01-15", "Corrección (errores o erratas)"),
    _n("A11", "2024-01-15", "Ley", origen="Autonómico", departamento="Comunidad de Madrid"),
    _n("A12", "2024-01-16", "Corrección (errores o erratas)", origen="Autonómico"),
    _n("A13", "2024-02-01", "Acuerdo Internacional", departamento="Ministerio de Asuntos Exteriores"),
    _n("A14", "2024-02-02", "Sentencia", departamento="Tribunal Constitucional"),
]


def test_categoria_por_rango_y_departamento():
    c = {n["id"]: informe.categoria(n) for n in NORMAS}
    assert c["A4"] == c["A5"] == "cortes" and c["A3"] == "rdl" and c["A1"] == "rd"
    assert c["A6"] == "ministerios" and c["A8"] == c["A9"] == "otros_organos"
    assert c["A13"] == "internacional" and c["A14"] == "tribunales"
    assert c["A11"] == "autonomica"
    assert c["A7"] is c["A10"] is c["A12"] is None  # no son decisiones nuevas


def test_construir_cuadra_los_totales():
    r = informe.construir(NORMAS, {"hasta_pleno": "2024-02-01"})
    total_categorias = sum(c["n"] for c in r["categorias"])
    assert total_categorias == r["estatales"] == 10
    assert r["estatales"] + r["autonomicas"] + r["correcciones"] + r["convalidaciones_publicadas"] == r["total"] == 14
    assert [ley["id"] for ley in r["leyes"]] == ["A4", "A5"]
    assert r["subvenciones_directas"] == {"n": 1, "de": 2}


def test_nuevo_gobierno_y_ritmo():
    r = informe.construir(NORMAS, {"hasta_pleno": "2024-02-01"})
    assert r["nuevo_gobierno"]["id"] == "A2"
    f, g = r["ritmo"]["en_funciones"], r["ritmo"]["con_gobierno"]
    assert (f["desde"], f["hasta"], f["rd"]) == ("2023-09-05", "2023-11-21", 1)
    assert (g["hasta"], g["rd"], g["rdl"], g["cortes"]) == ("2024-02-01", 1, 1, 2)


def test_por_mes_rellena_los_meses_sin_normas():
    m = informe.construir(NORMAS)["por_mes"]
    assert m["meses"] == ["2023-09", "2023-10", "2023-11", "2023-12", "2024-01", "2024-02"]
    assert m["rd"] == [1, 0, 1, 0, 0, 0] and m["cortes"] == [0, 0, 0, 0, 2, 0]


def test_vigencia_por_tipo_de_norma():
    g = {x["grupo"]: x for x in informe.construir(NORMAS)["vigencia"]}
    assert g["Reales decretos"]["tipos"]["dia_siguiente"] == 1 and g["Reales decretos"]["sin_parrafo"] == 1
    assert g["Reales decretos-ley"]["tipos"]["mismo_dia"] == 1
    assert g["Leyes"]["tipos"]["plazo"] == 1 and g["Leyes"]["total"] == 1  # la reforma de la Constitución no es «Ley»


def test_sin_normas_no_hay_informe():
    assert informe.construir([]) is None


def test_exportar_lo_saca_del_indice_a_su_archivo():
    datos = {"generado": "x", "ediciones": [], "dias": [], "normas": [], "informe": {"total": 1}}
    archivos = exportar.partir(datos)
    assert archivos["informe.json"] == {"total": 1} and "informe" not in archivos["indice.json"]


def test_posicion_del_grupo_es_la_mayoria_o_dividido():
    assert informe.posicion({"Sí": 121}) == "Sí"
    assert informe.posicion({"Sí": 5, "No": 2, "Abstención": 1}) == "Sí"
    assert informe.posicion({"No vota": 7}) == "No vota"
    assert informe.posicion({"Sí": 4, "No": 4}) == "Dividido"
    assert informe.posicion({}) is None


def test_votos_por_grupo_cuenta_posiciones_y_ordena_por_diputados():
    def votacion(grupos):
        return {"convalidacion": {"por_grupo": grupos, "nombres_grupo": {"GS": "Grupo Parlamentario Socialista", "GMx": "Grupo Parlamentario Mixto"}}}
    convalidaciones = {
        "a": votacion({"GMx": {"Sí": 4, "No": 4}, "GS": {"Sí": 121}}),
        "b": votacion({"GMx": {"Sí": 6, "No": 2}, "GS": {"Sí": 120, "No vota": 1}}),
        "c": {"convalidacion": {"solo_totales": True, "por_grupo": {}}},
    }
    r = informe.votos_por_grupo(convalidaciones)
    assert r["votaciones"] == 2 and r["solo_totales"] == 1
    assert [g["nombre"] for g in r["grupos"]] == ["PSOE", "Mixto"]  # por diputados, no por cómo votaron
    assert r["grupos"][0]["posiciones"]["Sí"] == 2
    assert r["grupos"][1]["posiciones"]["Dividido"] == 1 and r["grupos"][1]["posiciones"]["Sí"] == 1
    assert informe.votos_por_grupo({}) is None
