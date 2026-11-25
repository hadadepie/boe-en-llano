"""Pruebas de boe.senado con XML como los del Senado (recortados)."""

import json

from boe import senado


def _ficha(situacion, observaciones="", boe_url="", annio="", fecha=""):
    boes = (f"<boes><boe><boeAnnio><![CDATA[{annio}]]></boeAnnio><boeFecha><![CDATA[{fecha}]]></boeFecha>"
            f"<boeURL><![CDATA[{boe_url}]]></boeURL></boe></boes>") if boe_url else ""
    return (f"<?xml version='1.0' encoding='UTF-8' ?><fichaExpediente><datosCabecera>"
            f"<titulo><![CDATA[Proyecto de Ley de prueba.  (621/000001)]]></titulo>"
            f"<situacion><![CDATA[{situacion}]]></situacion><observaciones><![CDATA[{observaciones}]]></observaciones>"
            f"</datosCabecera><publicaciones>{boes}</publicaciones></fichaExpediente>").encode("utf-8")


def test_enmiendas_y_respuesta_del_congreso():
    f = senado.ficha(_ficha("Aprobado con modificaciones en el Senado",
                            "El Pleno del Congreso de los Diputados, en su sesión del 23 de mayo de 2024, ha aprobado parcialmente "
                            "las enmiendas introducidas por el Senado. En concreto, ha rechazado: la núm. 127…",
                            "http://www.boe.es/diario_boe/txt.php?id=BOE-A-2024-11613", "08-JUN-2024", "07-JUN-2024"))
    assert f["titulo"] == "Proyecto de Ley de prueba." and f["resultado"] == "con_enmiendas" and f["congreso"] == "en_parte"
    assert f["boe"] == ["BOE-A-2024-11613"]
    assert senado.respuesta_del_congreso("con_enmiendas", "ha rechazado todas las enmiendas introducidas por el Senado.") == "ninguna"
    assert senado.respuesta_del_congreso("con_enmiendas", "ha aprobado todas las enmiendas introducidas por el Senado.") == "todas"
    assert senado.respuesta_del_congreso("con_enmiendas", "ha aprobado la enmienda introducida por el Senado.") == "todas"
    assert senado.respuesta_del_congreso("con_enmiendas", "se han rechazado todas excepto las relativas a: Artículo 9") == "en_parte"


def test_vetos_y_sin_cambios():
    levantado = senado.ficha(_ficha("Veto del Senado", "en relación con el veto aprobado por el Senado, ha acordado ratificar el texto aprobado"))
    assert (levantado["resultado"], levantado["congreso"]) == ("veto", "veto_levantado")
    rechazo = senado.ficha(_ficha("Veto del Senado", "Al haber sido rechazado por la mayoría absoluta del Senado, […] ha de entenderse "
                                                     "que el Pleno del Senado ha vetado el texto."))
    assert (rechazo["resultado"], rechazo["congreso"]) == ("veto_por_rechazo", None)
    for situacion in ("Aprobado sin modificaciones en el Senado", "Tramitado sin modificaciones en el Senado", "Sin modificaciones en el Senado"):
        assert senado.ficha(_ficha(situacion))["resultado"] == "sin_cambios"
    assert senado.ficha(_ficha("Caducado"))["resultado"] == "caducada"


def test_corrige_el_anio_mal_escrito_del_boe():
    f = senado.ficha(_ficha("Aprobado con modificaciones en el Senado", "",
                            "http://www.boe.es/diario_boe/txt.php?id=BOE-A-0205-19339", "30-SEP-0205", "29-SEP-2025"))
    assert f["boe"] == ["BOE-A-2025-19339"]


def test_enmiendas_presentadas_por_grupo():
    xml = ("<?xml version='1.0' encoding='ISO-8859-15'?><General><Grupos>"
           "<DetalleGrupo><LiteralGrupo>GRUPO A</LiteralGrupo><VetoGrupo>1</VetoGrupo><EnmiendasGrupo>19</EnmiendasGrupo></DetalleGrupo>"
           "<DetalleGrupo><LiteralGrupo>GRUPO B</LiteralGrupo><VetoGrupo>0</VetoGrupo><EnmiendasGrupo>0</EnmiendasGrupo></DetalleGrupo>"
           "</Grupos><TotalGrupo><TotalVetos>1</TotalVetos><TotalEnmiendas>19</TotalEnmiendas></TotalGrupo></General>").encode("iso-8859-15")
    assert senado.enmiendas(xml) == {"enmiendas": 19, "vetos": 1, "por_grupo": [{"grupo": "GRUPO A", "enmiendas": 19, "vetos": 1}]}
    assert senado.enmiendas(None) is None


def test_procesar_no_vuelve_a_pedir_las_terminadas(tmp_path, monkeypatch):
    lista = ("<listaIniciativasLegislativas>"
             "<iniciativa><tipoExpediente>621</tipoExpediente><numeroExpediente>000001</numeroExpediente></iniciativa>"
             "<iniciativa><tipoExpediente>622</tipoExpediente><numeroExpediente>000001</numeroExpediente></iniciativa>"
             "</listaIniciativasLegislativas>").encode("utf-8")
    pedidas = []

    class R:
        def __init__(self, contenido):
            self.status_code, self.content = 200, contenido

        def raise_for_status(self):
            pass

    def get(url, params=None, **k):
        pedidas.append((params or {}).get("tipoFich", url))
        if params and params["tipoFich"] == "9":
            return R(lista)
        return R(_ficha("Aprobado sin modificaciones en el Senado", "", "http://www.boe.es/diario_boe/txt.php?id=BOE-A-2024-1", "", "01-ENE-2024"))

    monkeypatch.setattr(senado.requests, "get", get)
    monkeypatch.setattr(senado.time, "sleep", lambda s: None)
    from datetime import date
    assert senado.procesar(tmp_path, hoy=date(2026, 11, 25)) == 1  # la 622 nace en el Senado: fuera
    guardado = json.loads((tmp_path / "senado.json").read_text(encoding="utf-8"))
    assert guardado["iniciativas"][0]["boe"] == ["BOE-A-2024-1"] and pedidas == ["9", "3"]
    pedidas.clear()
    senado.procesar(tmp_path, hoy=date(2026, 12, 2))
    assert pedidas == ["9"]  # publicada en el BOE: su ficha no se vuelve a pedir
