"""Pruebas de boe.importes_creditos (sin red; textos tomados de normas reales, recortados)."""

from decimal import Decimal

from boe import importes_creditos as ic


def _xml(*hijos):
    return "<documento><texto>" + "".join(hijos) + "</texto></documento>"


def _p(texto, clase="parrafo"):
    return f'<p class="{clase}">{texto}</p>'


def test_importes_con_su_unidad():
    leidos = ic.importes("por importe de 1.273.495,50 miles de euros; de 400 millones de euros; de 2,7 millones de euros; "
                         "de cuatrocientos millones (400.000.000) de euros; 219.493,86 €; 1.000.000 de euros")
    assert [v for v, _ in leidos] == [Decimal("1273495500.00"), Decimal(400_000_000), Decimal("2700000.0"),
                                      Decimal(400_000_000), Decimal("219493.86"), Decimal(1_000_000)]


def test_el_bloque_no_incluye_el_parrafo_de_financiacion():
    xml = _xml(_p("1. Se aprueba un crédito extraordinario por importe de 165.000.000 euros en la aplicación 21.01.412C.471."),
               _p("2. Este crédito extraordinario se financiará con cargo al Fondo de Contingencia por 165.000.000 euros."))
    c = ic.creditos_de_norma({"id": "X", "titulo": "T", "origen_legislativo": "Estatal",
                              "creditos": [{"tipo": "Crédito extraordinario", "parrafo": 1,
                                            "texto": "1. Se aprueba un crédito extraordinario por importe de 165.000.000 euros"}]},
                             xml, {})
    assert c[0]["importe_propuesto"] == 165_000_000 and c[0]["como"] == "único importe"


def test_apartados_y_reglas_de_suma():
    els = ic.elementos(_xml(
        _p("2. Se aprueba la concesión de créditos extraordinarios en las siguientes aplicaciones y por los siguientes importes:"),
        _p("a) 37.02.942N.467 «Gastos extraordinarios»: 40.670.000 euros."),
        _p("b) 37.02.942N.767 «Gastos extraordinarios»: 4.650.000 euros."),
        _p("Los créditos extraordinarios se financiarán de conformidad con el artículo 59.")))
    partes = ic.bloque(els, 0)
    assert len(partes) == 3
    assert ic.proponer(partes)[:2] == (Decimal(45_320_000), "suma de 2 importes")


def test_total_con_desglose_y_casos_a_revisar():
    total = [("parrafo", "Se concede un suplemento por un importe máximo de 5.988.654.049,01 euros, distribuido en un importe de "
                         "3.430.669.506,06 euros y otro de 2.557.984.542,95 euros.", None)]
    assert ic.proponer(total)[:2] == (Decimal("5988654049.01"), "total con desglose")
    dos_para_uno = [("parrafo", "Se aprueba la concesión de un suplemento de crédito por importe de 2.400.000,00 euros, que "
                                "incluye 100.000,00 euros para otra cosa.", None)]
    importe, como, avisos = ic.proponer(dos_para_uno)
    assert importe is None and como is None and any("revisar" in a for a in avisos)
    # Dos apartados del mismo importe más otros: no se quita ninguno, se deja para revisar.
    repetidos = [("parrafo", "Se aprueba la concesión de créditos extraordinarios: a) 15 millones de euros; b) 15 millones de euros; "
                             "c) 20 millones de euros.", None)]
    assert ic.proponer(repetidos)[0] is None


def test_tablas_con_unidad_y_fila_total():
    filas = [["Aplicación presupuestaria", "Denominación", "Importe (miles de euros)"],
             ["38.02.941M.451", "Fondo de Suficiencia Global: Cataluña.", "54.905,08"],
             ["38.03.941M.451", "Fondo de Suficiencia Global: Galicia.", "36.776,80"]]
    assert ic.suma_de_tabla(filas) == (Decimal("91681880.00"), None)
    sin_cabecera = [["46001", "Entregas a cuenta a favor de los Municipios.", "1.575.160,86"]]
    assert ic.suma_de_tabla(sin_cabecera) == (None, "tabla sin unidad (euros, miles o millones)")
    assert ic.suma_de_tabla(sin_cabecera, "miles de euros")[0] == Decimal("1575160860.00")
    con_total = [["Partida", "Importe"], ["0001 Uno", "80.000"], ["0002 Dos", "60.000"], ["Total", "", "150.000"]]
    euros, aviso = ic.suma_de_tabla(con_total, "euros")
    assert euros == Decimal(150_000) and "no coincide" in aviso


def test_avisos_de_la_norma_y_repetidos():
    xml = _xml(_p("Se concede un crédito extraordinario por importe de 1.594.526 euros."))
    norma = {"id": "BOE-A-2023-25074", "titulo": "Ley Foral", "origen_legislativo": "Autonómico",
             "creditos": [{"tipo": "Crédito extraordinario", "parrafo": 1, "texto": "Se concede un crédito extraordinario por importe"}]}
    c = ic.creditos_de_norma(norma, xml, {})
    assert "norma autonómica: no es dinero del Estado" in c[0]["avisos"]
    rdl = {**norma, "id": "BOE-A-2025-26458", "origen_legislativo": "Estatal"}
    d = ic.creditos_de_norma(rdl, xml, {"BOE-A-2025-26458": {"convalidacion": {"resultado": "derogado"}}})
    assert "decreto-ley derogado por el Congreso" in d[0]["avisos"]
    ic.marcar_repetidos(c + d)
    assert "el mismo importe y casi el mismo texto en BOE-A-2025-26458" in c[0]["avisos"]
    # La misma cifra redonda con otro texto no es una repetición: no se avisa.
    otro = {"id": "BOE-A-9", "importe_propuesto": 1594526.0, "avisos": [],
            "texto": "Para financiar el Fondo de Vivienda se aprueba un crédito en la aplicación 25.09-261N-874."}
    ic.marcar_repetidos([otro, {**otro, "id": "BOE-A-8", "avisos": [], "texto": "Ayudas a los agricultores por la sequía."}])
    assert otro["avisos"] == []


def test_a_donde_va_por_la_clasificacion_economica():
    assert ic.destino("777") == "Empresas privadas" and ic.destino("451") == "Comunidades autónomas"
    assert ic.destino("873").startswith("Préstamos") and ic.destino("150") == "Personal"
    cs = ic.conceptos("en la aplicación 21.01.411M.777.01 «Medidas urgentes para paliar la guerra» y en el concepto 453 "
                      "«Aportación del Estado al Fondo de Garantía»", [[["38.21.942M.46001", "Entregas a cuenta", "1,00"]]])
    assert [(s, c) for s, c, _ in cs] == [("21", "777"), (None, "453"), ("38", "460")]
    assert cs[0][2] == "Medidas urgentes para paliar la guerra"


def test_dos_parrafos_que_empiezan_igual_no_se_confunden():
    inicio = "1. Al objeto de financiar las ayudas previstas en esta sección se aprueba la concesión de un suplemento de crédito"
    xml = _xml(_p(f"{inicio} de 275.000.000 euros en la aplicación 15.01.000X.470 «Gasóleo profesional»."),
               _p("Artículo 27.", "articulo"),
               _p(f"{inicio} de 275.000.000 euros en la aplicación 15.01.000X.471 «Ayuda al transporte»."))
    norma = {"id": "X", "titulo": "T", "origen_legislativo": "Estatal",
             "creditos": [{"tipo": "Suplemento de crédito", "parrafo": 1, "texto": inicio},
                          {"tipo": "Suplemento de crédito", "parrafo": 3, "texto": inicio}]}
    c = ic.creditos_de_norma(norma, xml, {})
    assert "Gasóleo" in c[0]["texto"] and "transporte" in c[1]["texto"]


def test_la_hoja_de_revision_conserva_lo_anotado(tmp_path):
    hoja = tmp_path / "revision_creditos.csv"
    credito = {"id": "BOE-A-1", "parrafo": 7, "tipo": "Crédito extraordinario", "fecha": "2026-01-01", "ejercicio": 2026,
               "importe_propuesto": 1000.0, "como": "único importe", "avisos": [], "importes_en_el_texto": ["1.000 euros"],
               "titulo": "T", "texto": "Se concede…"}
    ic.escribir_revision(hoja, [credito])
    texto = hoja.read_text(encoding="utf-8-sig").replace(";1000,00;único importe;;1.000 euros;;;;", ";1000,00;único importe;;1.000 euros;sí;;ok;")
    hoja.write_text(texto, encoding="utf-8-sig")
    ic.escribir_revision(hoja, [{**credito, "importe_propuesto": 2000.0}])
    assert ic.leer_revision(hoja)[("BOE-A-1", "7")] == {"contar": "sí", "importe_revisado": "", "nota": "ok"}


def test_cifra_segura_y_revision_de_la_autora():
    base = {"id": "BOE-A-1", "situacion": "convalidado", "importe_propuesto": 1000.0, "destinos": ["Empresas privadas"],
            "avisos": [], "texto": "t", "titulo": "Real Decreto-ley 1/2026"}
    seguro, dudoso, quitado = {**base, "parrafo": 1}, {**base, "parrafo": 2, "importe_propuesto": None}, {**base, "parrafo": 3}
    auto = {**base, "parrafo": 4, "situacion": "autonómica"}
    revision = {("BOE-A-1", "2"): {"contar": "sí", "importe_revisado": "2.500.000,00", "nota": ""},
                ("BOE-A-1", "3"): {"contar": "no", "importe_revisado": "", "nota": ""}}
    ic.marcar_cifras_seguras([seguro, dudoso, quitado, auto], revision)
    assert seguro["cifra_segura"] and not quitado["cifra_segura"] and not auto["cifra_segura"]
    assert dudoso["cifra_segura"] and dudoso["importe"] == 2_500_000.0


def test_la_ficha_solo_recibe_cifras_seguras():
    from boe import exportar
    normas = [{"id": "BOE-A-1", "creditos": [{"parrafo": 1, "texto": "a"}, {"parrafo": 2, "texto": "b"}]}]
    exportar.enlazar_importes_creditos(normas, {("BOE-A-1", 1): {"importe": 1000.0, "destinos": ["Personal"], "como": "único importe"}})
    assert normas[0]["creditos"][0]["importe"] == 1000.0 and "importe" not in normas[0]["creditos"][1]


def test_apartados_separados_por_explicaciones_y_red_de_seguridad():
    # RDL 5/2026, art. 2: entre «a)» y «b)» va un párrafo de «repercusión» que antes cortaba el bloque.
    els = ic.elementos(_xml(
        _p("2. Se aprueba la concesión de los siguientes créditos extraordinarios en el Presupuesto del Ministerio:"),
        _p("a) Crédito extraordinario en la aplicación 23.05.000X.710.10 por importe de 61.190.000 euros."),
        _p("El crédito extraordinario anterior tendrá la siguiente repercusión: 61.190.000 euros."),
        _p("b) Crédito extraordinario en la aplicación 23.05.000X.710.11 por importe de 14.000.000 euros."),
        _p("Este crédito se financiará con el Fondo de Contingencia.")))
    partes = ic.bloque(els, 0)
    assert len(partes) == 4 and partes[-1][1].startswith("b)")
    assert ic.proponer(partes)[0] is None  # importes repetidos y distintos: sin cifra, mejor que una incompleta
    # Varios créditos y un solo importe legible: sin cifra.
    solo_uno = [("parrafo", "Se conceden los siguientes suplementos de crédito por importe de 74.033.475 euros.", None)]
    importe, _, avisos = ic.proponer(solo_uno)
    assert importe is None and any("varios créditos" in a for a in avisos)
