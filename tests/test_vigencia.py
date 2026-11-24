"""Pruebas de boe/vigencia.py con frases reales de entrada en vigor."""

from boe import vigencia


def test_dia_siguiente_y_mismo_dia():
    r = vigencia.clasificar("El presente real decreto entrará en vigor el día siguiente al de su publicación en el «Boletín Oficial del Estado».")
    assert r == {"tipo": "dia_siguiente", "etiqueta": "Al día siguiente de su publicación",
                 "boletin": "Boletín Oficial del Estado", "excepciones": False}
    assert vigencia.clasificar("Este Decreto-ley entra en vigor al día siguiente de su publicación en el «Diari Oficial de la "
                               "Generalitat de Catalunya».")["tipo"] == "dia_siguiente"
    r = vigencia.clasificar("La presente resolución entrará en vigor el mismo día de su publicación en el «Boletín Oficial del Estado».")
    assert r["tipo"] == "mismo_dia"


def test_plazos_en_cifras_letras_y_meses():
    r = vigencia.clasificar("Este real decreto entrará en vigor a los veinte días de su publicación en el «Boletín Oficial del Estado».")
    assert r["tipo"] == "plazo" and r["plazo"] == {"cantidad": 20, "unidad": "días"}
    assert r["etiqueta"] == "A los 20 días de su publicación"
    assert vigencia.clasificar("1. La presente Circular entrará en vigor a los 20 días de su publicación en el «Boletín Oficial del "
                               "Estado».")["plazo"]["cantidad"] == 20
    assert vigencia.clasificar("Esta ley entrará en vigor a los veinte días naturales de su publicación en el «Diari Oficial de la "
                               "Generalitat Valenciana».")["plazo"]["cantidad"] == 20
    mes = vigencia.clasificar("Esta ley entrará en vigor al mes de su publicación en el «Diario Oficial de Castilla-La Mancha».")
    assert mes["plazo"] == {"cantidad": 1, "unidad": "meses"} and mes["etiqueta"] == "Al mes de su publicación"
    assert vigencia.clasificar("El presente real decreto entrará en vigor un mes después de su publicación en el «Boletín Oficial "
                               "del Estado».")["plazo"]["unidad"] == "meses"
    seis = vigencia.clasificar("La presente ley entrará en vigor a los seis meses de su publicación en el «Boletín Oficial de la Comunidad de Madrid».")
    assert seis["plazo"] == {"cantidad": 6, "unidad": "meses"} and seis["boletin"] == "Boletín Oficial de la Comunidad de Madrid"


def test_fecha_concreta_y_condicion():
    r = vigencia.clasificar("Esta ley foral entrará en vigor el 1 de enero de 2025.")
    assert r["tipo"] == "fecha" and r["fecha"] == "1 de enero de 2025"
    assert vigencia.clasificar("El presente real decreto entrará en vigor el día 1 de enero de 2027.")["fecha"] == "1 de enero de 2027"
    acuerdo = vigencia.clasificar("1. El presente Acuerdo entrará en vigor 120 días después de la fecha en que se haya depositado el "
                                  "sexagésimo instrumento de ratificación, aprobación, aceptación o adhesión.\n2. Respecto de cada Estado…")
    assert acuerdo["tipo"] == "condicion"
    canje = vigencia.clasificar("1. El presente Acuerdo entrará en vigor un mes después de la fecha de la última nota del Canje de "
                                "Notas Diplomáticas intercambiadas entre las Partes.")
    assert canje["tipo"] == "condicion"
    # Si el Acuerdo ya da la fecha resultante, cuenta como fecha.
    assert vigencia.clasificar("El presente Acuerdo entrará en vigor el 1 de octubre de 2024, el primer día del segundo mes siguiente "
                               "a la fecha de recepción de la última notificación.")["tipo"] == "fecha"


def test_excepciones():
    r = vigencia.clasificar("Este real decreto-ley entrará en vigor el día siguiente al de su publicación en el «Boletín Oficial del "
                            "Estado». No obstante, las medidas previstas en el capítulo I entrarán en vigor el 1 de enero de 2027.")
    assert r["tipo"] == "dia_siguiente" and r["excepciones"] is True
    r = vigencia.clasificar("1. La presente ley entrará en vigor el día siguiente al de su publicación en el «Boletín Oficial de la "
                            "Comunidad de Madrid».\n2. Se exceptúa del apartado anterior el reconocimiento de la condición de familia.")
    assert r["excepciones"] is True
    r = vigencia.clasificar("El presente decreto-ley entrará en vigor el mismo día de su publicación en el «Boletín Oficial de "
                            "Canarias», con efectos desde el día 1 de octubre de 2024.")
    assert r["tipo"] == "mismo_dia" and r["excepciones"] is True


def test_variantes_reales_menos_frecuentes():
    assert vigencia.clasificar("El presente real decreto entrará en vigor el día de su publicación en el «Boletín Oficial del "
                               "Estado».")["tipo"] == "mismo_dia"
    tres = vigencia.clasificar("El presente real decreto entrará en vigor a los tres meses desde el día de su publicación en el "
                               "«Boletín Oficial del Estado».")
    assert tres["tipo"] == "plazo" and tres["plazo"] == {"cantidad": 3, "unidad": "meses"}
    assert vigencia.clasificar("La presente resolución entrará en vigor a partir del día siguiente al de su publicación en el "
                               "«Boletín Oficial del Estado».")["tipo"] == "dia_siguiente"
    assert vigencia.clasificar("Uno. La presente norma entrará en vigor el día siguiente al de su publicación.")["tipo"] == "dia_siguiente"
    assert vigencia.clasificar("Esta orden entrará en vigor el día 1 de enero del año 2024.")["fecha"] == "1 de enero del año 2024"
    assert vigencia.clasificar("Esta orden entrará en vigor el día uno del mes siguiente al de su publicación en el «Boletín "
                               "Oficial del Estado».")["tipo"] == "mes_siguiente"
    assert vigencia.clasificar("El presente acuerdo entrará en vigor en la fecha de su firma por las Partes.")["tipo"] == "condicion"


def test_sin_texto_o_sin_clasificar():
    assert vigencia.clasificar("") is None
    assert vigencia.clasificar("Esta norma se aplicará conforme a lo que disponga el reglamento.")["tipo"] == "otro"
