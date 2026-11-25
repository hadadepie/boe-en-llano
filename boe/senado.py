"""Qué hizo el Senado con cada ley que le llegó del Congreso, según los datos abiertos del Senado.

Uso:
    python -m boe.senado      # escribe datos/senado.json

Fuente (XML, sin claves): https://www.senado.es/web/relacionesciudadanos/datosabiertos/catalogodatos/
  - lista de iniciativas legislativas de la legislatura (`ficopendataservlet?tipoFich=9&legis=15`);
  - ficha de cada iniciativa (`tipoFich=3&tipoEx=621&numEx=000001`): situación en el Senado,
    «observaciones» (qué hizo después el Congreso con las enmiendas o el veto) y el enlace al BOE
    de la ley publicada, por el que se cruza con datos/normas;
  - enmiendas y propuestas de veto presentadas, por grupo parlamentario (totales, sin senadores).

Solo las iniciativas que llegan del Congreso: proyectos de ley (621), proposiciones de ley del
Congreso (624), reformas de la Constitución (600) y proposiciones de las comunidades autónomas (625).
Las que nacen en el Senado (620, 622), los tratados (610) y las reformas de su Reglamento (626),
no. Lo descargado va a datos/crudo/senado/; la lista se renueva cada día que se ejecuta y la ficha
de una iniciativa terminada (publicada en el BOE o caducada) no se vuelve a pedir.

Lo que hizo el Congreso se lee con reglas sobre «observaciones», por ley (todas las enmiendas
aceptadas, ninguna, una parte), no por enmienda: el Senado las enumera en texto libre.
"""

import argparse
import json
import re
import time
import xml.etree.ElementTree as ET
from datetime import date
from pathlib import Path

import requests

LEGISLATURA = 15
BASE = "https://www.senado.es"
URL_DATOS = BASE + "/web/ficopendataservlet"
CARPETA_DATOS = Path("datos")
CABECERAS = {"User-Agent": "boe-en-llano/0.1 (proyecto educativo)"}
PAUSA_SEGUNDOS = 1.0
TIPOS = {"621": "Proyecto de ley", "624": "Proposición de ley del Congreso",
         "600": "Reforma de la Constitución", "625": "Proposición de ley de una comunidad autónoma"}
_RE_BOE = re.compile(r"BOE-A-(\d{4})-(\d+)")
_RE_ANNIO = re.compile(r"(\d{4})$")


def _pedir(params_o_url, destino, renovar=False):
    """Contenido (bytes) guardado en `destino`, o pedido al Senado si no está (o si `renovar`)."""
    destino = Path(destino)
    if destino.exists() and not renovar:
        return destino.read_bytes()
    if isinstance(params_o_url, str):
        r = requests.get(params_o_url, headers=CABECERAS, timeout=60)
    else:
        r = requests.get(URL_DATOS, params=params_o_url, headers=CABECERAS, timeout=60)
    time.sleep(PAUSA_SEGUNDOS)
    if r.status_code == 404:
        return None
    r.raise_for_status()
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_bytes(r.content)
    return r.content


def _texto(nodo, ruta):
    return " ".join((nodo.findtext(ruta) or "").split())


def lista(xml):
    """[{tipo, numero, titulo, url_enmiendas}] de las iniciativas que llegan del Congreso."""
    filas = []
    for i in ET.fromstring(xml).findall("iniciativa"):
        tipo = _texto(i, "tipoExpediente")
        if tipo in TIPOS:
            filas.append({"tipo": tipo, "numero": _texto(i, "numeroExpediente"),
                          "url_enmiendas": _texto(i, "listaEnmiendas/fichGenEnmiendas/fichUrlEnmiendas") or None})
    return filas


def ids_boe(ficha):
    """Ids del BOE de la ley publicada. Corrige el año si viene mal escrito (BOE-A-0205-… por 2025),
    con el año de publicación que da la propia ficha."""
    ids = []
    for b in ficha.iter("boe"):
        m = _RE_BOE.search(b.findtext("boeURL") or "")
        if not m:
            continue
        anio = m.group(1)
        if not 2000 <= int(anio) <= 2100:
            # El error suele repetirse en boeAnnio («30-SEP-0205»): vale el primer año posible.
            anios = [m.group(1) for c in ("boeFecha", "boeAnnio") for m in [_RE_ANNIO.search(_texto(b, c))] if m]
            anio = next((a for a in anios if 2000 <= int(a) <= 2100), None)
            if not anio:
                continue
        ids.append(f"BOE-A-{anio}-{m.group(2)}")
    return ids


def resultado_en_senado(situacion, observaciones):
    """con_enmiendas | sin_cambios | veto | veto_por_rechazo | caducada | otro."""
    s, o = situacion.lower(), observaciones.lower()
    if "veto" in s:
        # El Senado rechazó el texto y lo entiende como veto (art. 106.1 de su Reglamento).
        return "veto_por_rechazo" if "ha de entenderse que el pleno del senado ha vetado" in o else "veto"
    if "caducad" in s:
        return "caducada"
    if "con modificaciones" in s:
        return "con_enmiendas"
    if "sin modificaciones" in s:
        return "sin_cambios"
    return "otro"


def respuesta_del_congreso(resultado, observaciones):
    """Qué hizo el Congreso: todas | ninguna | en_parte (enmiendas), veto_levantado, o None."""
    o = observaciones.lower()
    if resultado == "veto":
        return "veto_levantado" if "ratificar el texto" in o else None
    if resultado != "con_enmiendas":
        return None
    if "parcialmente" in o or "todas excepto" in o:  # antes que «rechazado todas»: «rechazado todas excepto…»
        return "en_parte"
    if "rechazado todas" in o:
        return "ninguna"
    if "aprobado todas" in o or "aprobado la enmienda" in o:
        return "todas"
    return None


def ficha(xml):
    f = ET.fromstring(xml)
    c = f.find("datosCabecera")
    situacion, observaciones = _texto(c, "situacion"), _texto(c, "observaciones")
    resultado = resultado_en_senado(situacion, observaciones)
    titulo = re.sub(r"\s*\(\d{3}/\d{6}\)\s*$", "", _texto(c, "titulo")).rstrip(". ") + "."
    return {"titulo": titulo, "situacion": situacion, "resultado": resultado,
            "congreso": respuesta_del_congreso(resultado, observaciones),
            "observaciones": observaciones or None, "boe": ids_boe(f), "boletin_congreso": boletin_congreso(f)}


def boletin_congreso(ficha_xml):
    """Primer boletín del Congreso que cita la ficha («BOCG-15-A-5-1»): serie y número. Sirve para
    encontrar el expediente en el Congreso (boe.votaciones_leyes): en la serie A (proyectos de ley)
    el número es el del expediente; en la serie B (proposiciones), no."""
    for b in ficha_xml.iter("boletin"):
        serie, numero = _texto(b, "bolSerie"), _texto(b, "bolNumero").split("-")[0]
        if _texto(b, "bolCamara") == "C" and serie in ("A", "B") and numero.isdigit():
            return {"serie": serie, "numero": int(numero)}
    return None


def enmiendas(xml):
    """Enmiendas y propuestas de veto presentadas en el Senado, en total y por grupo parlamentario."""
    if not xml:
        return None
    e = ET.fromstring(xml)
    grupos = [{"grupo": _texto(g, "LiteralGrupo"), "enmiendas": int(_texto(g, "EnmiendasGrupo") or 0),
               "vetos": int(_texto(g, "VetoGrupo") or 0)} for g in e.iter("DetalleGrupo")]
    return {"enmiendas": int(_texto(e, "TotalGrupo/TotalEnmiendas") or 0),
            "vetos": int(_texto(e, "TotalGrupo/TotalVetos") or 0),
            "por_grupo": [g for g in grupos if g["enmiendas"] or g["vetos"]]}


def _terminada(fila):
    return bool(fila.get("boe")) or fila.get("resultado") == "caducada"


def procesar(carpeta_datos=CARPETA_DATOS, hoy=None):
    carpeta_datos = Path(carpeta_datos)
    hoy = hoy or date.today()
    crudo = carpeta_datos / "crudo" / "senado"
    salida = carpeta_datos / "senado.json"
    previas = {f"{x['expediente']}": x for x in (json.loads(salida.read_text(encoding="utf-8"))["iniciativas"]
                                               if salida.exists() else [])}
    xml_lista = _pedir({"tipoFich": "9", "legis": str(LEGISLATURA)}, crudo / f"iniciativas_{hoy:%Y%m%d}.xml")
    filas = []
    for i in lista(xml_lista):
        expediente = f"{i['tipo']}/{i['numero']}"
        previa = previas.get(expediente)
        renovar = not (previa and _terminada(previa))
        archivo = crudo / "expedientes" / f"{i['tipo']}_{i['numero']}.xml"
        datos = ficha(_pedir({"legis": str(LEGISLATURA), "tipoFich": "3", "tipoEx": i["tipo"], "numEx": i["numero"]},
                             archivo, renovar=renovar))
        enm = (enmiendas(_pedir(i["url_enmiendas"], crudo / "enmiendas" / f"{i['tipo']}_{i['numero']}.xml", renovar=renovar))
               if i["url_enmiendas"] else None)
        filas.append({"expediente": expediente, "tipo": TIPOS[i["tipo"]], **datos, "presentadas": enm,
                      "url": f"{BASE}/web/actividadparlamentaria/iniciativas/detalleiniciativa/index.html"
                             f"?legis={LEGISLATURA}&id1={i['tipo']}&id2={i['numero']}"})
    resultado = {"legislatura": LEGISLATURA, "fuente": "https://www.senado.es/web/relacionesciudadanos/datosabiertos/catalogodatos/",
                 "iniciativas": filas}
    anterior = json.loads(salida.read_text(encoding="utf-8")) if salida.exists() else None
    if anterior != resultado:
        salida.write_text(json.dumps(resultado, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return len(filas)


def main():
    argparse.ArgumentParser(description="Qué hizo el Senado con cada ley (datos abiertos del Senado).").parse_args()
    print(f"Iniciativas del Senado guardadas en datos/senado.json: {procesar()}")


if __name__ == "__main__":
    main()
