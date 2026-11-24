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


def test_tramitados_como_ley_fase_y_dias():
    def rdl(id, presentado, fases):
        n = _n(id, "2024-01-01", "Real Decreto-ley", departamento="Jefatura del Estado",
               titulo=f"Real Decreto-ley {id}/2024, de 1 de enero, por el que se aprueban medidas.")
        n["tramitacion"] = {"presentado": presentado, "resultado": "Caducado 04/11/2026", "fecha_resultado": "2026-11-04",
                            "comision": "Comisión de Hacienda", "pasos": [{"fase": f} for f in fases]}
        return n
    normas = [rdl("2", "2024-02-01", ["Publicación", "Enmiendas", "Concluido - (Caducado)"]),
              rdl("1", "2024-01-10", ["Publicación", "Enmiendas", "Informe", "Concluido - (Caducado)"]),
              _n("X", "2024-01-01", "Ley")]
    r = informe.tramitados_como_ley(normas, {"resumen": {"convalidado": 5}})
    assert r["n"] == 2 and r["convalidados"] == 5 and r["resultados"] == {"Caducado": 2}
    assert r["fases"] == {"Informe de la ponencia": 1, "Plazo de enmiendas": 1}
    assert [x["nombre"] for x in r["lista"]] == ["Real Decreto-ley 1/2024", "Real Decreto-ley 2/2024"]  # por fecha
    assert r["lista"][0]["dias"] == 1029
    assert informe.tramitados_como_ley(NORMAS) is None


def test_tribunales_cuenta_sin_mezclar_normas_con_el_mismo_numero():
    def t(tribunal, promotor=None, numero=None, fecha=None, texto=None, **k):
        n = _n("T", "2024-05-01", "Providencia", departamento="Tribunal Constitucional")
        n["tribunal"] = {"tribunal": tribunal, "promotor": {"categoria": promotor} if promotor else None,
                         "norma_afectada": {"rango": "Ley", "numero": numero, "fecha": fecha, "texto": texto} if texto else None, **k}
        return n
    normas = ([t("Tribunal Constitucional", "Gobierno de España", "5/2024", "26 de julio", "Ley 5/2024, de 26 de julio, de A.",
                 tipo="Recurso de inconstitucionalidad", suspension_161_2=True)] * 2
              + [t("Tribunal Constitucional", "No consta", "5/2024", "26 de julio", "Ley 5/2024, de 26 de julio, de A, larga.")]
              + [t("Tribunal Constitucional", None, "5/2024", "19 de diciembre", "Ley 5/2024, de 19 de diciembre, de B.")] * 3
              + [t("Tribunal Supremo (Sala Tercera)", "Empresas, asociaciones u otras entidades", decision="Estima")])
    r = informe.tribunales(normas)
    assert (r["total"], r["constitucional"], r["supremo"], r["suspension_161_2"]) == (7, 6, 1, 2)
    assert r["decisiones_ts"] == {"Estima": 1}
    assert r["promotores"][-1] == {"categoria": "No consta en el BOE", "n": 4}  # lo que no consta, al final
    assert [(x["norma"], x["n"]) for x in r["mas_recurridas"]] == [
        ("Ley 5/2024, de 26 de julio, de A.", 3), ("Ley 5/2024, de 19 de diciembre, de B.", 3)]
    assert r["sin_norma"] == 1
    assert informe.tribunales(NORMAS) is None


def test_sin_presupuestos_leyes_ordenes_creditos_y_conflicto():
    orden = _n("O1", "2024-06-27", "Orden",
               titulo="Orden HAC/641/2024, de 25 de junio, por la que se dictan las normas para la elaboración de los Presupuestos Generales del Estado para 2025.")
    rdl = _n("R1", "2024-12-24", "Real Decreto-ley", departamento="Jefatura del Estado", titulo="Real Decreto-ley 9/2024, de 23 de diciembre, de medidas.")
    rdl["creditos"] = [{"tipo": "Suplemento de crédito", "parrafo": 9, "texto": "Se concede un suplemento de crédito…"},
                       {"tipo": "Crédito extraordinario", "parrafo": 12, "texto": "Se concede un crédito extraordinario…"}]
    conflicto = _n("C1", "2026-02-28", "Providencia", departamento="Tribunal Constitucional",
                   titulo="Conflicto entre órganos constitucionales n.º 8992-2025, en relación con el deber de presentar los Presupuestos Generales del Estado.")
    conflicto["tribunal"] = {"tipo": "Conflicto entre órganos constitucionales", "promotor": {"texto": "el Senado frente al Gobierno"}}
    autonomica = _n("A1", "2025-01-01", "Ley", origen="Autonómico", titulo="Ley 5/2024, de Presupuestos Generales de la Comunidad Autónoma de Canarias para 2025.")
    autonomica["creditos"] = rdl["creditos"]
    r = informe.sin_presupuestos(NORMAS + [orden, rdl, conflicto, autonomica])
    assert r["leyes"] == []
    assert [(o["ejercicio"], o["nombre"]) for o in r["ordenes_elaboracion"]] == [("2025", "Orden HAC/641/2024")]
    assert r["conflictos"][0]["promotor"] == "el Senado frente al Gobierno"
    assert [(c["nombre"], c["tipos"]) for c in r["creditos"]] == [("Real Decreto-ley 9/2024", ["Crédito extraordinario", "Suplemento de crédito"])]
    assert (r["rdl"], r["rdl_con_creditos"]) == (2, 1)  # A3 y R1; las autonómicas no cuentan
    assert {x["anio"]: x["con_creditos"] for x in r["por_anio"]} == {"2023": 0, "2024": 1}
    ley = _n("L1", "2023-01-01", "Ley", departamento="Jefatura del Estado", titulo="Ley 31/2022, de 23 de diciembre, de Presupuestos Generales del Estado para el año 2023.")
    assert informe.sin_presupuestos([ley])["leyes"][0]["ejercicio"] == "2023"


def test_senado_quien_frente_a_quien_y_motivo():
    def c(id, fecha, promotor, titulo):
        n = _n(id, fecha, "Providencia", departamento="Tribunal Constitucional", titulo=titulo)
        n["tribunal"] = {"tipo": "Conflicto entre órganos constitucionales", "decision": "Admite a trámite",
                         "promotor": {"texto": promotor}, "asunto": id}
        return n
    normas = NORMAS + [
        c("C2", "2025-07-15", "el Senado frente al Gobierno",
          "Conflicto entre órganos constitucionales n.º 4142-2025, en relación con el Acuerdo de disconformidad («veto presupuestario» ex art. 134.6 de la Constitución Española) con las enmiendas."),
        c("C1", "2024-04-27", "el Gobierno de la nación",
          "Conflicto entre órganos constitucionales n.º 1219-2024, en relación con el Acuerdo de la Mesa del Senado por el que se toma en consideración una proposición de ley, adoptado al amparo del artículo 134.6."),
        c("C3", "2025-12-23", "el Senado",
          "Conflicto entre órganos constitucionales n.º 8035-2025, en relación con el Acuerdo de la Mesa del Congreso de los Diputados de no proceder a la tramitación de la enmienda."),
        c("C4", "2026-06-01", "el Senado frente al Gobierno de la nación",
          "Conflicto entre órganos constitucionales n.º 2828-2026, en relación al Acuerdo del Consejo de Ministros sobre la comparecencia del Presidente del Gobierno."),
    ]
    r = informe.senado(normas)
    assert r["n"] == 4 and r["por_quien"] == {"el Senado": 3, "el Gobierno": 1}
    assert [(x["quien"], x["frente_a"]) for x in r["lista"]] == [
        ("el Gobierno", "el Senado"), ("el Senado", "el Gobierno"), ("el Senado", "el Congreso"), ("el Senado", "el Gobierno")]
    assert r["motivos"]["Enmiendas con gasto: el Gobierno se opone a tramitarlas (art. 134.6)"] == 2
    assert r["lista"][3]["motivo"] == "Comparecencia del presidente del Gobierno"
    assert r["lista"][2]["sobre"].startswith("el Acuerdo de la Mesa del Congreso")
    assert informe.senado(NORMAS) is None
