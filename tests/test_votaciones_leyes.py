"""Pruebas de boe.votaciones_leyes (sin red)."""

from datetime import date

from boe import senado, votaciones_leyes as vl

RUTA = "/webpublica/opendata/votaciones/Leg15/Sesion030/20240314/Votacion041/VOT_20240314190000.json"


def test_expediente_desde_el_boletin_que_cita_el_senado():
    b_a_exp = vl.boletines_de_proposiciones([
        {"NUMEXPEDIENTE": "122/000019/0000", "ENLACESBOCG": "https://www.congreso.es/public_oficiales/L15/CONG/BOCG/B/BOCG-15-B-32-1.PDF"},
    ])
    assert b_a_exp == {32: "122/000019"}
    assert vl.expediente_congreso({"serie": "A", "numero": 5}, b_a_exp) == "121/000005"  # proyectos: el mismo número
    assert vl.expediente_congreso({"serie": "B", "numero": 32}, b_a_exp) == "122/000019"  # proposiciones: no
    assert vl.expediente_congreso(None, b_a_exp) is None


def test_el_senado_guarda_el_boletin_del_congreso():
    import xml.etree.ElementTree as ET
    f = ET.fromstring("<f><boletin><bolCamara>S</bolCamara><bolSerie>II</bolSerie><bolNumero>1</bolNumero></boletin>"
                      "<boletin><bolCamara>C</bolCamara><bolSerie>B</bolSerie><bolNumero>32-1</bolNumero></boletin></f>")
    assert senado.boletin_congreso(f) == {"serie": "B", "numero": 32}


def test_que_votacion_es():
    e = vl.etapa
    assert e({"titulo": "Dictámenes de Comisiones sobre iniciativas legislativas.", "textoExpediente": "Votación del Dictamen del Proyecto de Ley…"}) == "dictamen"
    assert e({"titulo": "Dictámenes de Comisiones sobre iniciativas legislativas.", "textoExpediente": "Proyecto de Ley…",
              "tituloSubGrupo": "Votación del dictamen.", "textoSubGrupo": "Votación del dictamen"}) == "dictamen"
    assert e({"titulo": "Dictámenes de Comisiones sobre iniciativas legislativas.", "textoExpediente": "Proyecto de Ley…",
              "tituloSubGrupo": "Enmiendas presentadas por el Grupo Parlamentario Mixto", "textoSubGrupo": "Enmiendas 5 y 7."}) == "otra"
    assert e({"titulo": "Dictámenes de Comisiones…", "textoExpediente": "Votación de conjunto del Proyecto de Ley Orgánica…"}) == "conjunto"
    assert e({"titulo": "Enmiendas del Senado.", "textoExpediente": "Proyecto de Ley…", "tituloSubGrupo": "Votación separada de las enmiendas."}) == "senado_enmienda"
    assert e({"titulo": "Enmiendas del Senado.", "textoExpediente": "Votación de conjunto del Proyecto de Ley Orgánica…"}) == "senado_conjunto"
    assert e({"titulo": "Veto del Senado.", "textoExpediente": "Proyecto de Ley Orgánica…"}) == "senado_veto"
    assert e({"titulo": "Debates de totalidad de iniciativas legislativas.", "textoExpediente": "Votación de la enmienda a la totalidad…"}) == "totalidad"


def test_votaciones_de_un_dia_y_llamamiento():
    html = ("<p>Proposición de Ley Orgánica de amnistía. (Núm. expte. 122/000019) Votación del nuevo dictamen. Si: 178 No: 172 Abstenciones: 0 "
            f'Detalle <a href="{RUTA}">JSON</a></p>'
            "<p>Votación de conjunto (pública por llamamiento) Votación de conjunto de la Proposición de Ley Orgánica de amnistía. "
            "(Pública por llamamiento) Si: 178 No: 172 Abstenciones: 0 Detalle</p>"
            "<p>Otra cosa. (Núm. expte. 173/000015) Si: 171 No: 160 Abstenciones: 15 Detalle XML JSON</p>")
    v = vl.votaciones_de_un_dia(html, {"122/000019"})
    assert [(e, r) for e, r, _ in v] == [("122/000019", RUTA), ("122/000019", None)]
    llamamiento = vl.por_llamamiento(v[1][2], date(2024, 3, 14))
    assert llamamiento["etapa"] == "conjunto" and llamamiento["solo_totales"] and llamamiento["totales"]["afavor"] == 178
    assert vl.votaciones_de_un_dia(html, {"121/000001"}) == []


def test_resumen_ley_elige_la_de_conjunto_en_las_organicas():
    vs = [{"etapa": "dictamen", "fecha": "2024-06-27"}, {"etapa": "conjunto", "fecha": "2024-06-27"},
          {"etapa": "senado_enmienda", "fecha": "2024-07-23"}, {"etapa": "senado_enmienda", "fecha": "2024-07-23"},
          {"etapa": "senado_conjunto", "fecha": "2024-07-23"}]
    r = vl.resumen_ley(vs)
    assert r["final"]["etapa"] == "conjunto" and r["tras_senado"]["etapa"] == "senado_conjunto" and r["votaciones_enmiendas_senado"] == 2
    assert vl.resumen_ley([])["final"] is None

def test_lectura_unica_y_fechas():
    e = vl.etapa
    assert e({"titulo": "Tramitación directa y en lectura única de iniciativas legislativas.",
              "textoExpediente": "Votación de conjunto del texto del Proyecto de Ley Orgánica…"}) == "conjunto"
    assert e({"titulo": "Acuerdo de tramitación directa y en lectura única de iniciativas legislativas.",
              "textoExpediente": "Acuerdo de tramitación directa y en lectura única del Proyecto de Ley…"}) == "otra"
    assert vl._iso("14/3/2024") == "2024-03-14"


def test_reformas_de_la_constitucion_por_la_portada_del_boletin():
    # Portada real de BOCG-15-B-6-1: el primer expediente es el de la XV; los demás, de otras legislaturas.
    portada = ("PROPOSICIÓN DE REFORMA CONSTITUCIONAL\n101/000002 Proposición de Ley para la reforma del artículo 69.3 "
               "(corresponde a los números de expediente 101/000004 de la XII Legislatura)")
    assert vl.expediente_de_portada(portada) == "101/000002"
    assert vl.expediente_de_portada("sin número") is None
    assert vl.es_reforma_constitucional("100/000001") and vl.es_reforma_constitucional("101/000002")
    assert not vl.es_reforma_constitucional("122/000019") and not vl.es_reforma_constitucional(None)
