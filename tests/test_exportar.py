"""Pruebas del paso 5 (boe/exportar.py)."""

import json

from boe import exportar


def test_agrupar_recuento_suma_la_seccion_v_y_rellena_ceros():
    agrupado = exportar.agrupar_recuento({"1": 27, "2A": 12, "3": 72, "5A": 73, "5B": 62, "5C": 1})
    assert agrupado == {"I": 27, "II.A": 12, "II.B": 0, "III": 72, "IV": 0, "V": 136}


def test_formato_espanol():
    assert exportar.miles(1516) == "1.516"
    assert exportar.porcentaje(52, 1516) == "3,4 %"
    assert exportar.porcentaje(1, 0) == "0 %"
    assert exportar.fecha_larga("2026-11-20") == "20 de noviembre de 2026"


def _dia(fecha, i, total_resto):
    return {"fecha": fecha, "recuento": {"I": i, "II.A": 0, "II.B": 0, "III": total_resto, "IV": 0, "V": 0}}


def test_frase_resumen_rango_del_mismo_mes():
    dias = [_dia("2026-11-16", 4, 269), _dia("2026-11-21", 5, 280)]
    normas = [{"impacto": "Directo"}, {"impacto": "Técnico"}, {"impacto": "Directo"}]
    assert exportar.frase_resumen(dias, normas) == (
        "Entre el 16 y el 21 de noviembre de 2026, el BOE publicó 558 textos. "
        "Solo 9 (1,6 %) son normas generales y 2 cambian algo para mucha gente.")


def test_frase_resumen_un_dia_y_singular():
    frase = exportar.frase_resumen([_dia("2026-11-20", 27, 255)], [{"impacto": "Directo"}])
    assert frase.startswith("El 20 de noviembre de 2026, el BOE publicó 282 textos.")
    assert frase.endswith("y 1 cambia algo para mucha gente.")


def test_frase_resumen_entre_meses_y_sin_datos():
    dias = [_dia("2026-10-30", 1, 9), _dia("2026-11-02", 1, 9)]
    assert exportar.frase_resumen(dias, []).startswith("Entre el 30 de octubre y el 2 de noviembre de 2026")
    assert exportar.frase_resumen([], []) == "Todavía no hay días descargados."


def test_construir_junta_recuentos_y_normas(tmp_path):
    (tmp_path / "normas").mkdir()
    (tmp_path / "recuentos.json").write_text(json.dumps({"2026-11-20": {"1": 2, "5A": 3}}), encoding="utf-8")
    for i, impacto in enumerate(["Directo", "Técnico"]):
        norma = {"id": f"BOE-A-2026-0000{i}", "fecha_publicacion": "2026-11-20", "titulo": "T",
                 "impacto": impacto, "tema": "Trabajo y empleo", "ambito": "Estatal",
                 "ficha": {"estado": "ok" if i == 0 else "pendiente"}}
        (tmp_path / "normas" / f"{norma['id']}.json").write_text(json.dumps(norma), encoding="utf-8")

    datos = exportar.construir(tmp_path)
    assert datos["dias"] == [{"fecha": "2026-11-20", "recuento": {"I": 2, "II.A": 0, "II.B": 0, "III": 0, "IV": 0, "V": 3}}]
    assert datos["resumen"]["total_publicaciones"] == 5
    assert datos["resumen"]["porcentaje_normas"] == "40,0 %"
    assert datos["resumen"]["impacto_directo"] == 1
    assert datos["resumen"]["fichas_verificadas"] == 1
    assert [s["codigo"] for s in datos["secciones"]] == ["I", "II.A", "II.B", "III", "IV", "V"]


# ---------- Edición semanal ----------

from datetime import date as _date


def _norma(**c):
    base = {"id": "BOE-A-2026-00001", "fecha": "2026-11-20", "titulo": "T", "rango": "Real Decreto",
            "impacto": "Directo", "ambito": "Estatal", "tema": "Trabajo y empleo",
            "ficha": {"estado": "pendiente", "titulo_llano": "Se fija el salario mínimo para 2027."}}
    return base | c


def test_semana_de_y_etiqueta():
    assert exportar.semana_de("2026-11-16") == exportar.semana_de("2026-11-21") == "2026-S47"
    assert exportar.semana_de("2026-11-23") == "2026-S48"
    assert exportar.etiqueta_semana(["2026-11-16", "2026-11-21"]) == "Semana del 16 al 21 de noviembre de 2026"
    assert exportar.etiqueta_semana(["2026-11-30", "2026-12-05"]) == "Semana del 30 de noviembre al 5 de diciembre de 2026"
    assert exportar.etiqueta_semana(["2026-11-20"]) == "Edición del 20 de noviembre de 2026"


def test_relevancia_prioriza_impacto_estatal_y_titular_claro():
    smi = _norma()
    ley_ccaa = _norma(rango="Ley", ambito="Cataluña", ficha={"titulo_llano": "Presupuestos de la Generalitat para 2026."})
    rdl_oscuro = _norma(rango="Real Decreto-ley", ficha={"titulo_llano": "Se modifica la Ley 1/2005, de 9 de marzo."})
    tramite = _norma(impacto="Técnico", rango="Ley")
    orden = sorted([tramite, ley_ccaa, rdl_oscuro, smi], key=exportar.relevancia, reverse=True)
    assert orden[0] is smi and orden[-1] is tramite


def test_titular_claro():
    assert exportar.titular_claro("Se fija el salario mínimo para 2027.")
    assert not exportar.titular_claro("Se modifica la Ley 1/2005, de 9 de marzo.")
    assert not exportar.titular_claro("Corrección de errores: Decreto-ley 4/2026.")
    assert not exportar.titular_claro("x" * 120)


def test_piezas_semana_cuentan_por_tipo_ambito_y_titulo():
    normas = [
        _norma(id="a", rango="Real Decreto-ley"),
        _norma(id="b", rango="Real Decreto-ley"),
        _norma(id="c", rango="Ley", ambito="Cataluña"),
        _norma(id="d", rango="Resolución", titulo="Resolución por la que se ordena la publicación del Acuerdo de convalidación del Real Decreto-ley 30/2026."),
        _norma(id="e", rango="Resolución", titulo="Resolución por la que se ordena la publicación del Acuerdo de derogación del Real Decreto-ley 31/2026."),
        _norma(id="f", titulo="Real Decreto por el que se regula la concesión directa de una subvención."),
    ]
    piezas = {p["texto"]: (p["cifra"], p["ids"]) for p in exportar.piezas_semana(normas)}
    assert piezas["reales decretos-ley aprobados por el Gobierno"] == (2, ["a", "b"])
    assert piezas["ley autonómica: Cataluña (1)"] == (1, ["c"])
    assert piezas["real decreto-ley convalidado por el Congreso"] == (1, ["d"])
    assert piezas["real decreto-ley rechazado (derogado) por el Congreso"] == (1, ["e"])
    assert piezas["subvención o préstamo directo a entidades concretas"] == (1, ["f"])
    assert not any("leyes aprobadas por las Cortes" in t or "ley aprobada" in t for t in piezas)


def test_ediciones_por_semana_y_en_curso():
    dias = [{"fecha": f, "recuento": {"I": 1, "II.A": 0, "II.B": 0, "III": 0, "IV": 0, "V": 0}}
            for f in ["2026-11-20", "2026-11-21", "2026-11-23"]]
    normas = [_norma(semana="2026-S47"), _norma(id="x", fecha="2026-11-23", semana="2026-S48")]
    ed = exportar.ediciones(dias, normas, hoy=_date(2026, 11, 24))  # martes de la S48
    assert [e["id"] for e in ed] == ["2026-S48", "2026-S47"]
    assert ed[0]["en_curso"] is True and ed[1]["en_curso"] is False
    assert ed[1]["resumen"]["normas_generales"] == 2
    domingo = exportar.ediciones(dias, normas, hoy=_date(2026, 11, 29))
    assert domingo[0]["en_curso"] is False  # el domingo no hay BOE: la semana está completa


# ---------- Votaciones del Congreso ----------

REGISTRO = {
    "id": "BOE-A-2026-18429", "rdl": "22/2026", "titulo": "Real Decreto-ley 22/2026, de 1 de septiembre…",
    "publicado": "2026-09-02", "estado": "convalidado",
    "convalidacion": {
        "fecha": "2026-09-16", "resultado": "convalidado", "fuente_pdf": "https://x/VOT.pdf", "fuente": "https://x/VOT.json",
        "totales": {"afavor": 304, "enContra": 33, "abstenciones": 7, "noVotan": 6}, "telematicos": 13,
        "por_grupo": {"GS": {"Sí": 120, "No vota": 1}, "GMx": {"Sí": 8, "No": 1}},
        "por_lista": {"GS": {"PSOE": {"Sí": 100, "No vota": 1}, "PSC": {"Sí": 20}},
                      "GMx": {"BNG": {"Sí": 1}, "VOX": {"No": 1}, "SUMAR": {"Sí": 7}}},
        "nombres_grupo": {"GS": "Grupo Parlamentario Socialista", "GMx": "Grupo Parlamentario Mixto"},
    },
    "tramitacion": {"fecha": "2026-09-16", "resultado": "se tramita como proyecto de ley",
                    "totales": {"afavor": 345, "enContra": 0}},
}


def test_listas_divididas_solo_cuando_votan_distinto():
    assert not exportar.listas_divididas({"PSOE": {"Sí": 100, "No vota": 1}, "PSC": {"Sí": 20}})
    assert exportar.listas_divididas({"BNG": {"Sí": 1}, "VOX": {"No": 1}})
    assert not exportar.listas_divididas({"SUMAR": {"Sí": 23}})


def test_votacion_para_web_es_agregada_y_con_nombres_cortos():
    web = exportar.votacion_para_web(REGISTRO)
    grupos = {g["codigo"]: g for g in web["convalidacion"]["grupos"]}
    assert grupos["GS"]["nombre"] == "PSOE" and grupos["GS"]["por_lista"] is None
    assert grupos["GMx"]["nombre"] == "Mixto" and grupos["GMx"]["por_lista"]["VOX"] == {"No": 1}
    assert web["tramitacion"]["resultado"] == "se tramita como proyecto de ley"


def test_enlazar_votaciones_al_rdl_y_a_su_resolucion_de_convalidacion():
    normas = [
        {"id": "BOE-A-2026-18429", "rango": "Real Decreto-ley", "numero_oficial": "22/2026", "titulo": "Real Decreto-ley 22/2026…"},
        {"id": "BOE-A-2026-19420", "rango": "Resolución",
         "titulo": "Resolución por la que se ordena la publicación del Acuerdo de convalidación del Real Decreto-ley 22/2026, de 1 de septiembre."},
        {"id": "otra", "rango": "Orden", "titulo": "Orden cualquiera"},
    ]
    exportar.enlazar_votaciones(normas, {"BOE-A-2026-18429": REGISTRO})
    assert normas[0]["congreso"]["rdl"] == "22/2026" and normas[1]["congreso"]["rdl"] == "22/2026"
    assert "congreso" not in normas[2]


def test_votaciones_y_pieza_de_la_semana():
    normas = [{"id": "BOE-A-2026-19420", "congreso": {"rdl": "22/2026"}}]
    votaciones = exportar.votaciones_semana({"x": REGISTRO}, normas, "2026-09-14", "2026-09-19")
    assert [v["rdl"] for v in votaciones] == ["22/2026"] and votaciones[0]["ids"] == ["BOE-A-2026-19420"]
    assert exportar.votaciones_semana({"x": REGISTRO}, normas, "2026-09-21", "2026-09-26") == []
    pieza = exportar.pieza_votaciones(votaciones, normas)
    assert pieza["cifra"] == 1 and pieza["texto"].startswith("real decreto-ley votado en el Pleno del Congreso (1 convalidado)")


# ---------- Archivos partidos para la web ----------

def _datos_partir():
    normas = [
        {"id": "A", "semana": "2026-S47", "preambulo": {"parrafos": ["uno", "dos", "tres"], "recortado": False},
         "cambios": [{"norma": "B", "bloques": [{"titulo": "Art. 1"}, {"titulo": "Art. 2"}]}, {"norma": "C", "bloques": []}],
         "cambios_recibidos": []},
        {"id": "B", "semana": "2026-S46", "preambulo": None, "cambios": None,
         "cambios_recibidos": [{"por": "A", "bloques": [{"titulo": "Art. 1"}]}]},
    ]
    ediciones = [{"id": "2026-S47", "etiqueta": "x"}, {"id": "2026-S46", "etiqueta": "y"}]
    return {"generado": "g", "temas": [], "dias": [], "ediciones": ediciones, "normas": normas}


def test_partir_separa_indice_semanas_y_detalle():
    archivos = exportar.partir(_datos_partir())
    assert set(archivos) == {"indice.json", "buscar.json", "semanas/2026-S47.json", "semanas/2026-S46.json",
                             "normas/A.json", "normas/B.json"}
    indice = archivos["indice.json"]
    assert "normas" not in indice and indice["num_normas"] == 2
    assert indice["semana_de_norma"] == {"A": "2026-S47", "B": "2026-S46"}
    assert indice["ediciones"][0] == {"id": "2026-S47", "etiqueta": "x", "archivo": "semanas/2026-S47.json", "num_normas": 1}


def test_semana_sin_antes_y_despues_y_con_el_primer_parrafo():
    a = exportar.partir(_datos_partir())["semanas/2026-S47.json"]["normas"][0]
    assert "cambios" not in a and "cambios_recibidos" not in a
    assert a["preambulo"]["parrafos"] == ["uno"] and a["preambulo"]["total_parrafos"] == 3
    assert a["resumen_cambios"] == {"normas": 1, "articulos": 2, "recibidos": 0}


def test_detalle_lleva_preambulo_completo_y_cambios():
    archivos = exportar.partir(_datos_partir())
    assert archivos["normas/A.json"]["preambulo"]["parrafos"] == ["uno", "dos", "tres"]
    assert archivos["normas/B.json"] == {"id": "B", "preambulo": None, "cambios": [],
                                         "cambios_recibidos": [{"por": "A", "bloques": [{"titulo": "Art. 1"}]}]}


def test_escribir_borra_lo_que_ya_no_existe(tmp_path):
    carpeta = tmp_path / "datos"
    (carpeta / "semanas").mkdir(parents=True)
    (carpeta / "semanas" / "vieja.json").write_text("{}", encoding="utf-8")
    exportar.escribir({"indice.json": {"a": "ñ"}}, carpeta)
    assert not (carpeta / "semanas" / "vieja.json").exists()
    assert json.loads((carpeta / "indice.json").read_text(encoding="utf-8")) == {"a": "ñ"}


def test_norma_para_web_lleva_titular_corto_y_conserva_el_largo_en_la_ficha():
    largo = ("Se modifica la Orden DEF/1363/2016, de 28 de julio, por la que se regulan la jornada y el "
             "régimen de horario habitual en el lugar de destino de los miembros de las Fuerzas Armadas.")
    n = exportar.norma_para_web({"id": "BOE-A-2026-00001", "fecha_publicacion": "2026-11-20", "titulo": "T",
                                 "ficha": {"estado": "pendiente", "titulo_llano": largo}})
    assert n["titular"].startswith("Se modifica la Orden por la que se regulan la jornada")
    assert n["ficha"]["titulo_llano"] == largo


# ---------- Seguimiento: qué pasa después con normas ya publicadas ----------

def _legislatura(*decretos):
    return {"decretos_ley": list(decretos)}


def test_seguimiento_recoge_votaciones_posteriores_aunque_sean_de_la_misma_semana():
    rdl = {"rdl": "26/2026", "organo": "Pleno", "resultado": "derogado", "fecha": "2026-10-02", "afavor": 172,
           "enContra": 178, "empate": False, "fecha_publicacion": "2026-09-30", "id_boe": "BOE-A-2026-20384",
           "titular": "Medidas para la vivienda."}
    s = exportar.seguimiento_semanas([], _legislatura(rdl))
    [h] = s["2026-S40"]
    assert h["etiqueta"] == "Derogado" and h["publicada"] == "2026-09-30" and not h["en_web"]
    assert h["texto"] == "El Congreso derogó el Real Decreto-ley 26/2026: 172 sí, 178 no."


def test_seguimiento_no_cuenta_lo_votado_el_mismo_dia_ni_lo_que_no_tiene_fecha():
    mismo_dia = {"rdl": "1/2026", "organo": "Pleno", "resultado": "convalidado", "fecha": "2026-09-30", "afavor": 1,
                 "enContra": 0, "fecha_publicacion": "2026-09-30", "id_boe": "X"}
    pendiente = {"rdl": "2/2026", "resultado": "sin votación publicada"}
    assert exportar.seguimiento_semanas([], _legislatura(mismo_dia, pendiente)) == {}


def test_seguimiento_de_la_diputacion_permanente_usa_la_fecha_del_acuerdo_en_el_boe():
    rdl = {"rdl": "30/2026", "organo": "Diputación Permanente", "resultado": "convalidado", "publicado_boe": "2026-11-20",
           "fecha_publicacion": "2026-10-14", "id_boe": "BOE-A-2026-21318", "titular": "Apoyo financiero."}
    [h] = exportar.seguimiento_semanas([], _legislatura(rdl))["2026-S47"]
    assert h["texto"].startswith("La Diputación Permanente del Congreso convalidó")


def test_seguimiento_con_la_vida_de_la_norma_sin_repetir_lo_que_ya_cuenta_la_votacion():
    rdl_votado = {"rdl": "21/2026", "organo": "Pleno", "resultado": "derogado", "fecha": "2026-09-16", "afavor": 155,
                  "enContra": 179, "fecha_publicacion": "2026-08-26", "id_boe": "BOE-A-2026-18148", "titular": "Grupos de interés."}
    norma_rdl = {"id": "BOE-A-2026-18148", "fecha": "2026-08-26", "rango": "Real Decreto-ley", "numero_oficial": "21/2026",
                 "titulo": "T", "titular": "Grupos de interés.", "vida": {"despues": [
                     {"relacion": "Se deroga", "texto": "por Resolución de 16 de septiembre de 2026", "fecha": "2026-09-18"},
                     {"relacion": "Se deja sin efecto", "texto": "la relación con la disposición final", "fecha": "2026-09-18"}]}}
    otra = {"id": "BOE-A-2026-18000", "fecha": "2026-08-26", "rango": "Real Decreto", "titulo": "T2", "titular": "Ceuta.",
            "vida": {"despues": [
                {"relacion": "Se modifica", "texto": "el anexo I, por Real Decreto 761/2026", "fecha": "2026-09-30", "id": "BOE-A-2026-20500"},
                {"relacion": "Corrección de errores", "texto": "en BOE núm. 250", "fecha": "2026-09-30"}]}}
    s = exportar.seguimiento_semanas([norma_rdl, otra], _legislatura(rdl_votado))
    assert [h["etiqueta"] for h in s["2026-S38"]] == ["Derogado"]  # la resolución y lo «sin efecto» no se repiten
    [h] = s["2026-S40"]  # la corrección de errores no cuenta
    assert h["etiqueta"] == "Modificada" and h["en_web"] and h["por"] == "BOE-A-2026-20500"


def test_indice_de_busqueda_es_ligero_y_va_de_reciente_a_antiguo():
    datos = {"generado": "g", "temas": ["Vivienda", "Salud"], "normas": [
        {"id": "A", "fecha": "2026-11-17", "titular": "Alquiler de vivienda", "titulo": "largo", "tema": "Salud", "impacto": "Directo"},
        {"id": "B", "fecha": "2026-11-20", "titular": None, "titulo": "Solo título", "tema": "Otro", "impacto": "Técnico"},
    ]}
    b = exportar.indice_busqueda(datos)
    assert b["normas"] == [["B", "2026-11-20", "Solo título", -1, "Técnico"],
                           ["A", "2026-11-17", "Alquiler de vivienda", 1, "Directo"]]


def test_decision_separa_lo_que_se_vota_de_lo_que_decide_el_gobierno():
    d = exportar.decision_de
    assert d({"rango": "Real Decreto-ley", "ambito": "Estatal", "congreso": {"estado": "convalidado"}}) == "votada"
    assert d({"rango": "Real Decreto-ley", "ambito": "Estatal", "congreso": {"estado": "derogado"}}) == "votada"
    assert d({"rango": "Real Decreto-ley", "ambito": "Estatal", "congreso": {"estado": "pendiente de votación"}}) == "pendiente"
    assert d({"rango": "Real Decreto-ley", "ambito": "Estatal", "congreso": {"estado": "sin datos"}}) == "pendiente"
    assert d({"rango": "Real Decreto-ley", "ambito": "Estatal"}) == "pendiente"
    assert d({"rango": "Resolución", "ambito": "Estatal", "congreso": {"convalidacion": {"resultado": "convalidado"}}}) == "votada"
    assert d({"rango": "Ley", "ambito": "Estatal"}) == "votada"
    assert d({"rango": "Ley Orgánica", "ambito": "Estatal"}) == "votada"
    for rango in ("Real Decreto", "Orden", "Resolución", "Circular"):
        assert d({"rango": rango, "ambito": "Estatal"}) == "gobierno"
    assert d({"rango": "Ley", "ambito": "Cataluña"}) == "autonomica"
    assert d({"rango": "Decreto", "ambito": "Extremadura"}) == "autonomica"
    assert d({"rango": "Sentencia", "ambito": "Estatal"}) == "tribunal"
    assert d({"rango": "Acuerdo Internacional", "ambito": "Estatal"}) == "otra"
    assert d({"rango": "Corrección (errores o erratas)", "ambito": "Estatal"}) == "otra"
    assert d({"rango": None, "ambito": None}) == "otra"
    assert set(map(exportar.decision_de, [{"rango": "Ley", "ambito": "Estatal"}])) <= set(exportar.DECISIONES)
