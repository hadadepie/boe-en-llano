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


def test_reconoce_comunidades_con_nombres_y_codificaciones_distintas():
    assert au.comunidad_de("Andalucía - Consejería/Dpto. de Educación") == "01"
    assert au.comunidad_de("Andaluc�a") == "01" and au.comunidad_de("AndalucÃ\xada") == "01"
    assert au.comunidad_de("Castilla y León") == "07" and au.comunidad_de("Castilla-La Mancha") == "08"
    assert au.comunidad_de("País Vasco-Euskadi") == "15" and au.comunidad_de("Madrid,Comunidad de") == "12"
    assert au.comunidad_de("Ministerio de Educación") is None


def test_funcional_por_capitulos():
    filas = [_fila("31. Sanidad", "39651776.99", "37515932.2", "135315.81", "15191119.92", "", "2400941.71", "80094.15"),
             _fila("33. Cultura", "1", "1", "1", "1", "", "1", "1")]
    assert au.funcional_capitulos(filas) == {"31": [39651.777, 37515.932, 135.316, 15191.12, 0.0, 2400.942, 80.094]}


def _tabla_sanidad(filas_extra=""):
    nombres = ["España"] + [ine for _, ine in au.COMUNIDADES.values()]
    filas = "".join(f"<tr><td>{n}</td><td>45,2</td><td>26,2</td><td>8,5</td><td>20,1</td>"
                    "<td>62,1</td><td>13,9</td><td>14,7</td><td>9,3</td></tr>" for n in nombres)
    return ("<p>A&ntilde;o 2023</p><table><tr><th>Remuneraci&oacute;n de personal</th><th>Otros</th></tr>"
            + filas + filas_extra + "</table>").encode("latin-1", "xmlcharrefreplace")


def test_sanidad_egsp():
    s = au.sanidad_egsp(_tabla_sanidad())
    assert s["año"] == "2023" and s["comunidades"]["00"]["conciertos"] == 8.5 and len(s["comunidades"]) == 18


def test_sanidad_egsp_que_no_suma_100_avisa():
    with pytest.raises(ValueError):
        au.sanidad_egsp(_tabla_sanidad().replace(b"20,1", b"30,1"))


def _csv_educa(filas):
    return ("﻿" + "\n".join(";".join(f) for f in filas)).encode("utf-8")


def test_educacion_separa_lo_que_va_a_centros_privados():
    t3, t7 = [["Tipo de actividad educativa", "Administración", "Naturaleza económica", "Total"]], [["Administración", "Enseñanza", "Total"]]
    for c, (nombre, ine) in au.COMUNIDADES.items():
        admin = f"{ine} - Consejería/Dpto. de Educación"
        t3 += [["TOTAL", admin, "TOTAL", "1.000,0"], ["TOTAL", admin, "Personal (capítulo 1)", "600,0"],
               ["TOTAL", admin, "Bienes y servicios (capítulo 2)", "100,0"], ["TOTAL", admin, "Transferencias corrientes (capítulo 4)", "200,0"],
               ["TOTAL", admin, "Inversiones reales (capítulo 6)", "50,0"], ["TOTAL", admin, "Transferencias de capital (capítulo 7)", "40,0"],
               ["Educación Infantil y Primaria", admin, "TOTAL", "9.999,0"]]
        t7 += [[admin, "TOTAL", "150,0"], [admin, "ESO", "70,0"]]
    e = au.educacion(_csv_educa(t3), _csv_educa(t7))
    assert e["01"] == {"personal": 0.6, "compras": 0.1, "privada": 0.15, "otras_transferencias": 0.09, "inversiones": 0.05, "otros": 0.01}
    assert e["00"]["privada"] == round(0.15 * 17, 3)
    with pytest.raises(ValueError):  # a centros privados más de lo transferido: los datos no cuadran
        au.educacion(_csv_educa(t3), _csv_educa([[f[0], f[1], "999,0"] for f in t7]))
