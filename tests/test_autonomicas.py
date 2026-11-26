"""Pruebas de boe.autonomicas (sin red; filas tomadas de los Excel reales de Hacienda, recortadas)."""

import pytest

from boe import autonomicas as au


def _fila(*celdas):
    return list(celdas) + [""] * (8 - len(celdas))


FUNCIONAL = [
    _fila("Ministerio de Hacienda y Función Pública"),
    _fila("Áreas y Políticas de gasto ", "P. Aprobado Miles de euros ", "P. Aprobado % ", "P. Depurado Miles de euros "),
    _fila("3. Producción de Bienes Públicos de Carácter Preferente", "26925617.6", "52.18", "26925617.6", "57.94"),
    _fila("31. Sanidad", "15989267.9", "30.99", "15989267.9", "34.41"),
    _fila("32. Educación", "10619344.81", "20.58", "10619344.81", "22.85"),
    _fila("12. Defensa"),
    _fila("94. Transferencias a otras Administraciones Públicas", "4103377.74", "7.95", "550426", "1.18"),
    _fila("Total Gastos", "51597944.75", "100", "46471877.4", "100"),
]

ECONOMICA_LIQUIDACION = [
    _fila("Capítulos de ingresos", "Presupuesto Inicial", "Presupuesto Definitivo", "Derechos Reconocidos Netos", "Ingresos Líquidos"),
    _fila("1. Impuestos Directos", "74807839.76", "76293745.52", "78741382.17", "78287953.86"),
    _fila("Operaciones Corrientes", "224144560.41", "232334762.44", "233730894.59", "229949261.02"),
    _fila("Capítulos de gastos ", "Presupuesto Inicial ", "Presupuesto Definitivo ", "Obligaciones Reconocidas Netas ", "Pagos Líquidos "),
    _fila("5. Fondo de contingencia", "820674.3", "270345.55"),
    _fila("6. Inversiones Reales", "15797165.69", "16860254.86", "10387565.01", "8794665.73"),
]


def test_funcional_solo_politicas_y_en_millones():
    f = au.funcional(FUNCIONAL)
    assert f["politicas"] == {"31": 15989.268, "32": 10619.345, "94": 4103.378}  # sin el área 3 ni Defensa (vacía)
    assert f["nombres"]["31"] == "Sanidad"
    assert (f["total"], f["total_depurado"]) == (51597.945, 46471.877)


def test_funcional_sin_total_avisa():
    with pytest.raises(ValueError):
        au.funcional(FUNCIONAL[:-1])


def test_economica_de_la_liquidacion_con_celdas_vacias():
    e = au.economica(ECONOMICA_LIQUIDACION)
    assert e["liquidacion"]
    assert e["ingresos"]["1"] == [74807.84, 76293.746, 78741.382, 78287.954]
    assert e["gastos"]["5"] == [820.674, 270.346, 0.0, 0.0]  # sin obligaciones ni pagos: cero, no se corre la fila
    assert "Operaciones Corrientes" not in e["ingresos"]


def test_economica_del_presupuesto_una_columna():
    e = au.economica([_fila("Capítulos de ingresos", "Miles de euros", "%"), _fila("9. Pasivos Financieros", "39834184.18", "13.04"),
                      _fila("Capítulos de gastos ", "Miles de euros ", "% "), _fila("1. Gastos de Personal", "94787486.8", "31.28")])
    assert not e["liquidacion"] and e["ingresos"] == {"9": 39834.184} and e["gastos"] == {"1": 94787.487}


def test_poblacion_a_uno_de_enero_con_la_hora_de_madrid():
    # El INE fecha el 1/1/2026 a las 0:00 de Madrid: 1767222000000 ms = 31/12/2025 23:00 UTC.
    series = [{"Nombre": f"Total. Todas las edades. {ine}. Población. Número. ",
               "Data": [{"Fecha": 1767222000000, "Valor": 1000.0 + i}, {"Fecha": 1759269600000, "Valor": 1.0}]}
              for i, (_, ine) in enumerate(au.COMUNIDADES.values())]
    series.append({"Nombre": "Total. Todas las edades. Ceuta. Población. Número. ", "Data": [{"Fecha": 1767222000000, "Valor": 9.0}]})
    p = au.poblaciones(series, [2026])
    assert p[2026]["01"] == 1000 and p[2026]["17"] == 1016
    assert p[2026]["00"] == sum(1000 + i for i in range(17))  # sin Ceuta ni el dato de octubre


def test_poblacion_incompleta_avisa():
    with pytest.raises(ValueError):
        au.poblaciones([], [2026])


def test_solo_urls_del_portal_de_hacienda():
    with pytest.raises(ValueError):
        au._comprobar_url("https://otro.example/SGCIEF/x.xlsx")
    au._comprobar_url(f"https://{au.DOMINIO}/SGCIEF/PublicacionPresupuestos/aspx/DescargaFuncionalDC.aspx?cdcdad=01&ano=2026")
