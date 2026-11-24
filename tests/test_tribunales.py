"""Pruebas de boe/tribunales.py con frases reales publicadas en el BOE."""

from boe import tribunales

TC = "TRIBUNAL CONSTITUCIONAL"
TS = "TRIBUNAL SUPREMO"


def _norma(departamento, titulo, rango="Providencia", epigrafe=""):
    return {"departamento_sumario": departamento, "titulo": titulo, "rango": rango, "epigrafe": epigrafe}


def test_recurso_de_inconstitucionalidad_de_un_gobierno_autonomico():
    texto = ("El Pleno del Tribunal Constitucional, por providencia de 26 de septiembre de 2023, ha acordado admitir a "
             "trámite el recurso de inconstitucionalidad número 5491-2023, promovido por el Consejo de Gobierno de la "
             "Comunidad Autónoma de Andalucía, contra los artículos 3 f), g) y k); 8 a) y c) de la Ley 12/2023, de 24 de "
             "mayo, por el derecho a la vivienda.\nMadrid, 26 de septiembre de 2023.–El Secretario de Justicia del Pleno.")
    c = tribunales.clasificar(_norma(TC, "Recurso de inconstitucionalidad n.º 5491-2023, contra los artículos…",
                                     epigrafe="Recursos de inconstitucionalidad"), texto)
    assert c["tribunal"] == "Tribunal Constitucional" and c["documento"] == "Providencia"
    assert c["tipo"] == "Recurso de inconstitucionalidad" and c["decision"] == "Admite a trámite"
    assert c["promotor"]["categoria"] == "Gobierno autonómico"
    assert c["norma_afectada"]["rango"] == "Ley" and c["norma_afectada"]["numero"] == "12/2023"
    assert c["norma_afectada"]["texto"].startswith("Ley 12/2023, de 24 de mayo, por el derecho a la vivienda")
    assert c["fecha_decision"] == "26 de septiembre de 2023" and c["asunto"] == "5491-2023"
    assert c["suspension_161_2"] is False


def test_impugnacion_del_gobierno_con_suspension_automatica():
    texto = ("El Pleno del Tribunal Constitucional, por providencia de 8 de octubre de 2024, ha acordado admitir a trámite "
             "la impugnación de disposiciones autonómicas (título V LOTC) número 7118-2024, promovida por el Gobierno de "
             "la nación, frente al Gobierno de Canarias, respecto de los apartados segundo… Y se hace constar que por el "
             "Gobierno se ha invocado el artículo 161.2 de la Constitución, lo que produce la suspensión.")
    c = tribunales.clasificar(_norma(TC, "Impugnación de disposiciones autonómicas n.º 7118-2024",
                                     epigrafe="Impugnación de disposiciones autonómicas"), texto)
    assert c["tipo"] == "Impugnación de disposiciones autonómicas"
    assert c["promotor"]["categoria"] == "Gobierno de España"
    assert c["suspension_161_2"] is True


def test_cuestion_de_un_juzgado_y_diputados_y_organo_constitucional():
    cuestion = ("El Pleno del Tribunal Constitucional, por providencia de 21 de noviembre de 2023, ha acordado admitir a "
                "trámite la cuestión de inconstitucionalidad número 5206-2023 planteada por el Juzgado de lo "
                "Contencioso-administrativo núm. 1 de Pontevedra, en el procedimiento abreviado núm. 45/2022, en relación "
                "con el artículo 17 bis de la Ley Orgánica 8/2007, de 4 de julio, sobre financiación de los partidos políticos.")
    c = tribunales.clasificar(_norma(TC, "Cuestión de inconstitucionalidad n.º 5206-2023"), cuestion)
    assert c["tipo"] == "Cuestión de inconstitucionalidad"
    assert c["promotor"]["categoria"] == "Un órgano judicial"
    assert c["norma_afectada"]["rango"] == "Ley Orgánica"
    assert tribunales.categoria_promotor("más de cincuenta diputados del Grupo Parlamentario Popular en el Congreso") == "50 o más diputados"
    assert tribunales.categoria_promotor("el Senado frente al Congreso de los Diputados") == "Un órgano constitucional"
    assert tribunales.categoria_promotor("Comisión Nacional de los Mercados y la Competencia") == "Un organismo público"


def test_primer_parrafo_que_repite_el_titulo():
    texto = ("Recurso de inconstitucionalidad n.º 1306-2024 contra los artículos 3 y 11.2 de la Ley 12/2023, de 24 de mayo.\n"
             "El Pleno del Tribunal Constitucional, por providencia de 5 de marzo de 2024, ha acordado admitir a trámite el "
             "recurso de inconstitucionalidad número 1306-2024, promovido por el Parlamento de Cataluña, contra los artículos 3 "
             "y 11.2 de la Ley 12/2023, de 24 de mayo.")
    c = tribunales.clasificar(_norma(TC, "Recurso de inconstitucionalidad n.º 1306-2024"), texto)
    assert c["decision"] == "Admite a trámite" and c["promotor"]["categoria"] == "Parlamento autonómico"


def test_sentencia_del_supremo_que_anula_en_parte_un_real_decreto():
    titulo = ("Sentencia de 22 de abril de 2024, de la Sala Tercera del Tribunal Supremo, que declara estimar parcialmente el "
              "recurso contencioso-administrativo 752/2023, contra el Real Decreto 608/2023, de 11 de julio, por el que se "
              "desarrolla el Mecanismo RED de Flexibilidad y Estabilización del Empleo.")
    texto = ("En el recurso contencioso-administrativo núm. 752/2023, contra el Real Decreto 608/2023, de 11 de julio, la Sala "
             "Tercera (Sección Cuarta) del Tribunal Supremo ha dictado sentencia con fecha 22 de abril de 2024 cuya parte "
             "dispositiva es del tenor literal siguiente:")
    c = tribunales.clasificar(_norma(TS, titulo, rango="Sentencia"), texto)
    assert c["tribunal"] == "Tribunal Supremo (Sala Tercera)"
    assert c["documento"] == "Sentencia" and c["tipo"] == "Recurso contencioso-administrativo"
    assert c["decision"] == "Estima en parte"
    assert c["norma_afectada"]["numero"] == "608/2023" and c["norma_afectada"]["fecha"] == "11 de julio"
    assert c["fecha_decision"] == "22 de abril de 2024"
    assert c["promotor"] is None  # el texto no dice quién recurrió


def test_auto_que_suspende_y_promotor_sin_nombres_de_personas():
    texto = ("En la pieza de medidas cautelares del recurso contencioso-administrativo núm. 766/2023, interpuesto por la "
             "representación procesal de la Asociación Sindical de Secretarios de la Administración de Justicia contra el "
             "Real Decreto 625/2023, de 11 de julio, por el que se aprueba la oferta de empleo público, la Sala Tercera del "
             "Tribunal Supremo ha dictado auto con fecha 3 de octubre de 2023 cuya parte dispositiva es: La Sala acuerda: "
             "1.º Suspender cautelarmente la ejecución.")
    titulo = ("Auto de 3 de octubre de 2023, de la Sala Tercera del Tribunal Supremo, que declara suspender cautelarmente la "
              "ejecución de la Oferta de Empleo Público para el ejercicio 2023.")
    c = tribunales.clasificar(_norma(TS, titulo, rango="Auto"), texto)
    assert c["decision"] == "Suspende cautelarmente"
    assert c["promotor"] == {"categoria": "Empresas, asociaciones u otras entidades",
                             "texto": "Asociación Sindical de Secretarios de la Administración de Justicia"}
    # Una persona: se guarda la categoría, nunca el nombre.
    persona = tribunales.promotor("recurso interpuesto por don Juan Pérez García contra el Real Decreto 1/2024, de 9 de enero")
    assert persona == {"categoria": "Una persona particular"}
    # Solo se nombra al procurador: no consta quién recurre.
    procurador = tribunales.promotor("recurso interpuesto por el procurador don José Martín, contra el Real Decreto 1/2024")
    assert procurador == {"categoria": "No consta"}
    representadas = tribunales.promotor("interpuesto por el procurador don José Martín, en representación de las entidades "
                                        "Iberdrola Clientes, SA, la Sala Tercera")
    assert representadas["texto"].startswith("Iberdrola Clientes")


def test_normas_citadas_sin_fecha_o_con_siglas():
    assert tribunales.norma_afectada("contra la Orden TED/1315/2022, de 23 de diciembre, por la que se regulan las subastas.")["numero"] == "TED/1315/2022"
    sin_fecha = tribunales.norma_afectada("contra el Real Decreto 1012/2022, por el que se establece la estructura orgánica.")
    assert sin_fecha["numero"] == "1012/2022" and sin_fecha["fecha"] is None
    assert tribunales.norma_afectada("contra la reforma del Reglamento del Senado") is None


def test_lo_que_no_es_una_decision_judicial():
    cuentas = _norma("TRIBUNAL DE CUENTAS", "Resolución de 18 de diciembre de 2024, de la Presidencia del Tribunal de Cuentas…",
                     rango="Resolución")
    assert tribunales.clasificar(cuentas, "El Pleno del Tribunal de Cuentas ha aprobado la siguiente Instrucción.") is None
    assert tribunales.clasificar(_norma("MINISTERIO DE HACIENDA", "Orden…", rango="Orden"), "") is None
