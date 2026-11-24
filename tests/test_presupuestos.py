"""Pruebas de boe/presupuestos.py: créditos extraordinarios y suplementos de crédito."""

from boe import presupuestos

TEXTO = """Real Decreto-ley 9/2026, de 14 de abril.
Para atender estas ayudas, este real decreto-ley explica que se concede un crédito extraordinario.
En su virtud,
DISPONGO:
Artículo 5. Concesión de créditos extraordinarios.
1. Al objeto de financiar las ayudas previstas en este capítulo se aprueba la concesión de tres créditos extraordinarios por importe total de 3.150.000 euros.
2. Se conceden suplementos de crédito en el concepto 451.
Disposición derogatoria. Queda derogado el Real Decreto-ley 3/1990, de concesión de un crédito extraordinario por importe de 280.558.000.000 de pesetas."""


def test_solo_la_parte_que_manda_y_solo_cuando_concede():
    r = presupuestos.creditos(TEXTO)
    assert [x["tipo"] for x in r] == ["Crédito extraordinario", "Suplemento de crédito"]
    assert r[0]["parrafo"] == 6 and r[0]["texto"].startswith("1. Al objeto")


def test_sin_parte_dispositiva_mira_todo_y_recorta():
    largo = "Se concede un crédito extraordinario " + "x " * 600
    r = presupuestos.creditos(largo)
    assert len(r) == 1 and r[0]["texto"].endswith("…") and len(r[0]["texto"]) <= presupuestos.MAX_CARACTERES + 1
    assert presupuestos.creditos("") == []
