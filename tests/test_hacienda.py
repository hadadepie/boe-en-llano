"""Pruebas de boe.hacienda con XLSX pequeños hechos aquí (sin red), con la forma de los de Hacienda."""

import zipfile

import pytest

from boe import hacienda

AÑOS = ["2023", "2025-P"]


def _xlsx(ruta, hojas):
    """Escribe un XLSX mínimo: hojas = {nombre: [[celda A, B, C…], …]} (filas desde la 4)."""
    textos = []

    def indice(texto):
        if texto not in textos:
            textos.append(texto)
        return textos.index(texto)

    hojas_xml = []
    for filas in hojas.values():
        xml_filas = []
        for n, fila in enumerate(filas, start=4):
            celdas = []
            for col, valor in zip("ABCDEFGHIJK", fila):
                if valor is None:
                    continue
                if isinstance(valor, (int, float)):
                    celdas.append(f'<c r="{col}{n}"><v>{valor}</v></c>')
                else:
                    celdas.append(f'<c r="{col}{n}" t="s"><v>{indice(valor)}</v></c>')
            xml_filas.append(f'<row r="{n}">{"".join(celdas)}</row>')
        hojas_xml.append(f'<worksheet xmlns="{hacienda.M[1:-1]}"><sheetData>{"".join(xml_filas)}</sheetData></worksheet>')
    ns_r = hacienda.R[1:-1]
    with zipfile.ZipFile(ruta, "w") as z:
        z.writestr("xl/workbook.xml", f'<workbook xmlns="{hacienda.M[1:-1]}" xmlns:r="{ns_r}"><sheets>' + "".join(
            f'<sheet name="{nombre}" sheetId="{i}" r:id="rId{i}"/>' for i, nombre in enumerate(hojas, 1)) + "</sheets></workbook>")
        z.writestr("xl/_rels/workbook.xml.rels", '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">' + "".join(
            f'<Relationship Id="rId{i}" Target="worksheets/sheet{i}.xml"/>' for i in range(1, len(hojas) + 1)) + "</Relationships>")
        for i, xml in enumerate(hojas_xml, 1):
            z.writestr(f"xl/worksheets/sheet{i}.xml", xml)
        z.writestr("xl/sharedStrings.xml", f'<sst xmlns="{hacienda.M[1:-1]}">' + "".join(
            f"<si><t>{t}</t></si>" for t in textos) + "</sst>")
    return ruta


def _hoja(titulo, primera, filas, años=AÑOS):
    return [[titulo], ["Millones de euros"], [primera, *[f" {a}" for a in años]], *filas, ["Fuente:"], ["Presupuestos Generales del Estado"]]


def _ingresos(titulo, filas):
    return _hoja(titulo, "Capítulos", filas)


@pytest.fixture
def rutas(tmp_path):
    cons = {
        "11": _hoja("1.1. Gastos. Clasificación económica ", "Capítulos", [
            ["Gastos de personal", 27, 27], ["Transferencias corrientes", 300, 310], ["Transferencias de capital", 30, 20],
            ["Activos financieros", 10, 10], ["Pasivos financieros", 90, 95], ["TOTAL PRESUPUESTO", 457, 462]]),
        "12.1": _hoja("1.2.1. Total transferencias por artículos", "Artículos", [
            ["44 y 74 Sdades, EPEs, Fundac. y resto entes SP", 10, 10], ["45 y 75 Comunidades Autónomas", 40, 40],
            ["47 y 77 Empresas privadas", 20, 20], ["48 y 78 Famlias e Instituciones sin fines lucro", 240, 240],
            ["49 y 79 Exterior", 20, 20], ["TOTAL TRANSFERENCIAS", 330, 330]]),
        "12.2": _hoja("1.2.2. Transferencias corrientes por artículos", "Artículos", [
            ["45 Comunidades Autónomas", 30, 30], ["48 Famlias e ISFL", 240, 240], ["TRANSFERENCIAS CORRIENTES", 270, 270]]),
        "12.3": _hoja("1.2.3. Transferencias de capital por artículos", "Artículos", [
            ["75 Comunidades Autónomas", 10, 10], ["77 Empresas privadas", 20, 20], ["TRANSFERENCIAS DE CAPITAL", 30, 30]])
        + [["Millones de pesetas"], ["Artículos", "1990"], ["75 Comunidades Autónomas", 999]],
        "141": _hoja("1.4. Políticas de gasto (capítulos 1 a 8)", "Políticas", [
            ["Pensiones", 190, 190], ["Deuda Pública", 31, 31], ["CAPÍTULOS 1 a 8", 367, 367]]),
        "15": _ingresos("1.5. Ingresos. Clasificación económica", [
            ["Impuestos directos", 269, 269], ["Impuestos indirectos", 58, 58], ["TOTAL CAPÍTULOS 1 a 8", 327, 327]]),
    }
    return {
        "consolidado": _xlsx(tmp_path / "01.xlsx", cons),
        "estado": _xlsx(tmp_path / "02.xlsx", {"23": _ingresos("2.3. Ingresos. Clasificación económica", [
            ["Impuestos directos", 86, 86], ["Impuestos indirectos", 58, 58]])}),
        "seguridad_social": _xlsx(tmp_path / "03.xlsx", {"32": _ingresos("3.2. Ingresos. Clasificación económica", [
            ["Cotizaciones sociales", 152, 152]])}),
        "organismos": _xlsx(tmp_path / "04.xlsx", {"42": _ingresos("4.2. Ingresos. Clasificación económica", [
            ["Impuestos directos", 31, 31]])}),
    }


def test_tabla_lee_años_y_para_en_fuente(rutas):
    hojas = hacienda.leer_xlsx(rutas["consolidado"])
    años, filas = hacienda.tabla(hojas, "Transferencias de capital por articulos")
    assert años == AÑOS  # sin los espacios de la cabecera
    assert filas["75 Comunidades Autónomas"] == {"2023": 10.0, "2025-P": 10.0}  # no la tabla en pesetas de debajo
    with pytest.raises(KeyError):
        hacienda.tabla(hojas, "No existe")


def test_construir_reparte_el_capitulo_1_y_calcula_la_deuda(rutas):
    datos = hacienda.construir(rutas, "2025-P")
    assert datos["prorrogado"] and datos["unidad"] == "millones de euros" and datos["avisos"] == []
    cap1 = datos["capitulo1_ingresos"]
    assert cap1["estado_impuestos"]["2025-P"] + cap1["seguridad_social_cotizaciones"]["2025-P"] + cap1["organismos_capitulo1"]["2025-P"] == 269
    # gastos 1 a 8 (total − pasivos financieros) menos ingresos 1 a 8
    assert datos["deuda_calculada"] == {"2023": 40.0, "2025-P": 40.0}
    tr = datos["transferencias"]
    assert tr["total"]["48"]["2025-P"] == 240 and "46" not in tr["total"]
    assert tr["capital"] == {"45": {"2023": 10.0, "2025-P": 10.0}, "47": {"2023": 20.0, "2025-P": 20.0}}
    assert datos["fuente"]["archivos"]["organismos"].startswith(f"https://{hacienda.DOMINIO}/")
    assert "cite expresamente su origen" in datos["fuente"]["licencia"]


def test_avisa_si_las_cifras_no_cuadran(rutas, tmp_path):
    rutas["seguridad_social"] = _xlsx(tmp_path / "03b.xlsx", {"32": _ingresos("3.2. Ingresos. Clasificación económica", [
        ["Cotizaciones sociales", 100, 152]])})
    avisos = hacienda.construir(rutas)["avisos"]
    assert len(avisos) == 1 and avisos[0].startswith("2023: el capítulo 1")


def test_solo_https_y_dominio_oficial():
    assert hacienda.url_archivo("2025-P", "01 Presupuestos Generales del Estado Consolidados.xlsx").endswith(
        "/2025-P/01%20Presupuestos%20Generales%20del%20Estado%20Consolidados.xlsx")
    for url in ("http://www.sepg.pap.hacienda.gob.es/x.xlsx", "https://ejemplo.com/x.xlsx",
                "https://www.sepg.pap.hacienda.gob.es.ejemplo.com/x.xlsx"):
        with pytest.raises(ValueError):
            hacienda._comprobar_url(url)


def test_no_descarga_dos_veces(tmp_path, monkeypatch):
    for nombre in hacienda.ARCHIVOS.values():
        (tmp_path / "2025-P").mkdir(exist_ok=True)
        (tmp_path / "2025-P" / nombre).write_bytes(b"PK")
    monkeypatch.setattr(hacienda, "pedir", lambda *a, **k: pytest.fail("no debía pedir nada"))
    rutas = hacienda.descargar("2025-P", tmp_path)
    assert set(rutas) == set(hacienda.ARCHIVOS)


def test_ediciones_de_la_pagina():
    html = ('<a href="/x/Documents/2025-P/01%20A.xlsx">e</a><a href="/x/Documents/2023/01%20A.xlsx">e</a>'
            '<a href="/x/Documents/2023-P/01%20A.pdf">p</a><a href="/x/Documents/2023-P/02%20B.xlsx">e</a>')
    assert hacienda.ediciones(html) == ["2023", "2023-P", "2025-P"]
