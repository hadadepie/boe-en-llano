"""El dinero de las comunidades autónomas: de cuánto disponen, qué presupuestan y qué gastan (backlog 3.10).

Fuentes (Ministerio de Hacienda, Secretaría General de Financiación Autonómica y Local, en Excel):
- «Presupuestos de las Comunidades Autónomas» (presupuestos iniciales, consolidados), portal
  `SGCIEF/PublicacionPresupuestos`: clasificación funcional (áreas y políticas de gasto) y económica
  (capítulos de ingresos y gastos).
- «Liquidación de Presupuestos de las Comunidades Autónomas», portal `SGCIEF/PublicacionLiquidaciones`:
  lo gastado (obligaciones reconocidas netas) por políticas, y por capítulos con el presupuesto inicial y
  definitivo, los derechos reconocidos (ingresos) y los pagos. Llega con unos dos años de retraso.
- Población a 1 de enero: INE, Estadística Continua de Población (tabla 56940), para «por habitante».

Uso (desde la raíz del proyecto):
    python -m boe.autonomicas            # presupuesto 2026 y 2024, liquidación 2024

Qué se comprobó con los archivos reales (26/11/2026):
- Los dos portales son formularios ASP.NET con sesión: hay que pasar por su página de entrada, enviar el
  formulario y seguir a mano la redirección al Excel. En el de liquidaciones el campo del tipo de descarga
  se llama `tipoConsulta`; en el de presupuestos, `tipoDescarga`.
- Los 17 Excel funcionales de 2026 cuadran céntimo a céntimo con el cuadro de la página 23 del informe en
  PDF de Hacienda (sanidad, educación, servicios sociales, deuda), y el total con la suma de las 17.
- Ceuta y Melilla (códigos 18 y 19) no devuelven Excel (2024–2026); además, en ellas la sanidad y la
  educación las gestiona el Estado. No se incluyen.
- «Depurado» es sin la participación de las entidades locales en los ingresos de la comunidad ni la PAC
  (dinero que solo pasa por la comunidad); es la cifra para comparar comunidades.

Nada de personas: solo agregados por comunidad, capítulo y política de gasto.
"""

import argparse
import html
import json
import re
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urljoin, urlparse

import requests

from boe.hacienda import leer_xlsx

DOMINIO = "serviciostelematicosext.hacienda.gob.es"
PORTALES = {
    # clave: (ruta, página de entrada, nombre del campo del tipo de descarga)
    "presupuestos": ("PublicacionPresupuestos", "inicio.aspx", "tipoDescarga"),
    "liquidaciones": ("PublicacionLiquidaciones", "menuInicio.aspx", "tipoConsulta"),
}
TIPOS = {"funcional": "DescargaFuncionalDC.aspx", "economica": "DescargaEconomicaDC.aspx",
         "funcional_capitulos": "DescargaFuncionalCapDC.aspx"}
# «¿Quién presta el servicio?»: estadísticas de los ministerios (no hay equivalente para servicios sociales).
SANIDAD = "https://www.sanidad.gob.es/estadEstudios/sanidadDatos/tablas/tabla31.htm"
EDUCA = "https://estadisticas.educacion.gob.es/EducaJaxiPx/files/_px/es/csv_bdsc/economicas/gasto/{año}/l0/gasto{n}.csv_bdsc"
AÑO_EDUCACION = 2024
# Políticas cuyo reparto por capítulos se guarda (sanidad, educación, servicios sociales, infraestructuras).
POLITICAS_CAPITULOS = ["31", "32", "23", "45"]
# Para reconocer cada comunidad en tablas de otros ministerios (solo letras ASCII, en minúscula).
CLAVES = {"01": "andaluc", "02": "arag", "03": "asturias", "04": "balears", "05": "canarias", "06": "cantabria",
          "07": "castillay", "08": "castillala", "09": "catalu", "10": "extremadura", "11": "galicia", "12": "madrid",
          "13": "murcia", "14": "navarra", "15": "pasvasco", "16": "rioja", "17": "comunitatvalenciana"}
INE = "https://servicios.ine.es/wstempus/js/ES/DATOS_TABLA/56940"
CABECERAS = {"User-Agent": "boe-en-llano/0.1 (proyecto educativo)"}
CARPETA_CRUDO = Path("datos/crudo/autonomicas")
SALIDA = Path("datos/hacienda/autonomicas.json")
AÑO_PRESUPUESTO = 2026
AÑO_LIQUIDACION = 2024

# Código de Hacienda → (nombre en la web, nombre de la serie del INE).
COMUNIDADES = {
    "01": ("Andalucía", "Andalucía"),
    "02": ("Aragón", "Aragón"),
    "03": ("Asturias", "Asturias, Principado de"),
    "04": ("Illes Balears", "Balears, Illes"),
    "05": ("Canarias", "Canarias"),
    "06": ("Cantabria", "Cantabria"),
    "07": ("Castilla y León", "Castilla y León"),
    "08": ("Castilla-La Mancha", "Castilla - La Mancha"),
    "09": ("Cataluña", "Cataluña"),
    "10": ("Extremadura", "Extremadura"),
    "11": ("Galicia", "Galicia"),
    "12": ("Madrid", "Madrid, Comunidad de"),
    "13": ("Región de Murcia", "Murcia, Región de"),
    "14": ("Navarra", "Navarra, Comunidad Foral de"),
    "15": ("País Vasco", "País Vasco"),
    "16": ("La Rioja", "Rioja, La"),
    "17": ("Comunitat Valenciana", "Comunitat Valenciana"),
}
TOTAL = "00"
FORALES = ["14", "15"]
# Presupuestos prorrogados según la introducción del informe de Hacienda de cada año (no viene en los Excel).
PRORROGADOS = {2024: ["09"], 2026: ["02", "04", "07", "13"]}

_POLITICA = re.compile(r"^(\d{1,2})\.\s*(.+?)\s*$")


def _comprobar_url(url):
    partes = urlparse(url)
    if partes.scheme != "https" or partes.hostname != DOMINIO:
        raise ValueError(f"URL fuera del portal de Hacienda: {url}")


def _campos_ocultos(html_formulario):
    return {m[0]: html.unescape(m[1]) for m in
            re.findall(r'<input type="hidden" name="([^"]+)" id="[^"]*" value="([^"]*)"', html_formulario)}


def descargar_excel(sesion, portal, tipo, año, codigo, pausa=1.0):
    """Bytes del XLSX de un portal, tipo, año y comunidad (formulario con sesión y redirección a mano)."""
    ruta, entrada, campo = PORTALES[portal]
    base = f"https://{DOMINIO}/SGCIEF/{ruta}/aspx/"
    formulario = base + "SelDescargaDC.aspx"
    if not sesion.cookies:
        sesion.get(base + entrada, headers=CABECERAS, timeout=60)
        time.sleep(pausa)
    pagina = sesion.get(formulario, headers={**CABECERAS, "Referer": base + entrada}, timeout=60)
    time.sleep(pausa)
    datos = _campos_ocultos(pagina.text)
    datos.update({"ctl00$MainContent$ano": str(año), "ctl00$MainContent$autonomia": codigo,
                  f"ctl00$MainContent${campo}": f"../aspx/{TIPOS[tipo]}?cdcdad=",
                  "ctl00$MainContent$botonAceptar.x": "10", "ctl00$MainContent$botonAceptar.y": "10"})
    respuesta = sesion.post(formulario, data=datos, headers={**CABECERAS, "Referer": formulario},
                            allow_redirects=False, timeout=60)
    time.sleep(pausa)
    destino = respuesta.headers.get("Location")
    if respuesta.status_code != 302 or not destino or TIPOS[tipo] not in destino:
        raise ValueError(f"{portal} {tipo} {año} {codigo}: no hay Excel (respuesta {respuesta.status_code})")
    url = urljoin(formulario, destino)
    _comprobar_url(url)
    excel = sesion.get(url, headers={**CABECERAS, "Referer": formulario}, timeout=60)
    time.sleep(pausa)
    if not excel.content.startswith(b"PK"):
        raise ValueError(f"{url}: no parece un XLSX")
    return excel.content


def archivos_necesarios(año_presupuesto=AÑO_PRESUPUESTO, año_liquidacion=AÑO_LIQUIDACION):
    """[(portal, tipo, año)] que hacen falta: presupuesto del último año y del año liquidado, y la liquidación."""
    return [("presupuestos", "funcional", año_presupuesto), ("presupuestos", "economica", año_presupuesto),
            ("presupuestos", "funcional", año_liquidacion),
            ("liquidaciones", "funcional", año_liquidacion), ("liquidaciones", "economica", año_liquidacion),
            ("liquidaciones", "funcional_capitulos", año_liquidacion)]


def ruta_crudo(carpeta, portal, tipo, año, codigo):
    return Path(carpeta) / portal / str(año) / f"{tipo}_{codigo}.xlsx"


def descargar(carpeta=CARPETA_CRUDO, año_presupuesto=AÑO_PRESUPUESTO, año_liquidacion=AÑO_LIQUIDACION, pausa=1.0):
    """Baja lo que falte a `carpeta` (lo ya guardado no se vuelve a pedir) y la población del INE."""
    sesiones = {p: requests.Session() for p in PORTALES}
    for portal, tipo, año in archivos_necesarios(año_presupuesto, año_liquidacion):
        for codigo in [TOTAL, *COMUNIDADES]:
            destino = ruta_crudo(carpeta, portal, tipo, año, codigo)
            if destino.exists():
                continue
            contenido = descargar_excel(sesiones[portal], portal, tipo, año, codigo, pausa)
            destino.parent.mkdir(parents=True, exist_ok=True)
            destino.write_bytes(contenido)
            print(f"  descargado {portal} {tipo} {año} {codigo}")
    poblacion = Path(carpeta) / f"poblacion_{año_liquidacion}_{año_presupuesto}.json"
    if not poblacion.exists():
        r = requests.get(f"{INE}?date={año_liquidacion}0101:{año_presupuesto}0101", headers=CABECERAS, timeout=180)
        r.raise_for_status()
        poblacion.write_bytes(r.content)
        time.sleep(pausa)
    otros = [(Path(carpeta) / "sanidad_tabla31.htm", SANIDAD)]
    otros += [(Path(carpeta) / f"educacion_{AÑO_EDUCACION}_gasto{n}.csv", EDUCA.format(año=AÑO_EDUCACION, n=n)) for n in ("03", "07")]
    for destino, url in otros:
        if not destino.exists():
            r = requests.get(url, headers=CABECERAS, timeout=60)
            r.raise_for_status()
            destino.write_bytes(r.content)
            time.sleep(pausa)
    return poblacion


# --- Lectura ---

def _filas(ruta):
    """Filas del XLSX como listas por posición (A, B, C…), con "" en las celdas vacías."""
    filas = []
    for hoja in leer_xlsx(ruta).values():
        for f in hoja:
            fila = [""] * 8
            for col, v in f.items():
                if len(col) == 1 and ord(col) - 65 < 8:
                    fila[ord(col) - 65] = str(v).strip()
            filas.append(fila)
    return filas


def _num(texto):
    return round(float(texto) / 1000, 3) if texto else 0.0  # miles → millones de euros


def funcional(filas):
    """{"politicas": {"31": millones}, "nombres": {"31": "Sanidad"}, "total", "total_depurado"} de un Excel funcional.

    Columnas tras el nombre: importe (presupuestado u obligaciones), %, importe depurado (sin IFL ni PAC), %.
    Solo las políticas (dos cifras); las áreas (una cifra) son sumas de ellas. Una política sin importe no sale.
    """
    politicas, nombres, total = {}, {}, None
    for f in filas:
        if f[0] == "Total Gastos":
            total = (_num(f[1]), _num(f[3]))
            continue
        m = _POLITICA.match(f[0])
        if m and len(m[1]) == 2 and f[1]:
            politicas[m[1]] = _num(f[1])
            nombres[m[1]] = m[2]
    if total is None:
        raise ValueError("Excel funcional sin fila «Total Gastos»")
    return {"politicas": politicas, "nombres": nombres, "total": total[0], "total_depurado": total[1]}


def economica(filas):
    """{"ingresos": {"1": [...]}, "gastos": {"1": [...]}, "columnas": {...}} de un Excel por capítulos.

    En el presupuesto, una sola columna (más el %, que se descarta); en la liquidación, cuatro: presupuesto
    inicial, definitivo, derechos u obligaciones reconocidos y cobros o pagos.
    """
    lado, salida, columnas = None, {"ingresos": {}, "gastos": {}}, {}
    for f in filas:
        if f[0].startswith("Capítulos de ingresos"):
            lado = "ingresos"
        elif f[0].startswith("Capítulos de gastos"):
            lado = "gastos"
        else:
            m = re.match(r"^(\d)\. ", f[0])
            if lado and m:
                salida[lado][m[1]] = f[1:5]
            continue
        columnas[lado] = [c for c in f[1:5] if c]
    liquidacion = len(columnas.get("gastos", [])) >= 4
    for lado in ("ingresos", "gastos"):
        for cap, valores in salida[lado].items():
            # En la liquidación, una celda vacía es cero (p. ej. el fondo de contingencia no tiene obligaciones).
            salida[lado][cap] = [_num(v) for v in valores] if liquidacion else _num(valores[0])
    return {**salida, "columnas": columnas, "liquidacion": liquidacion}


def poblaciones(datos_ine, años):
    """{año: {código: personas}} a 1 de enero de cada año, de la tabla 56940 del INE (y el total de las 17)."""
    por_nombre = {ine: codigo for codigo, (_, ine) in COMUNIDADES.items()}
    salida = {a: {} for a in años}
    for serie in datos_ine:
        partes = serie["Nombre"].split(". ")
        if len(partes) < 3 or partes[0] != "Total" or partes[1] != "Todas las edades" or partes[2] not in por_nombre:
            continue
        for d in serie["Data"]:
            fecha = datetime.fromtimestamp(d["Fecha"] / 1000, tz=timezone.utc)
            # El INE fecha el 1 de enero a las 0:00 de Madrid (el 31 de diciembre a las 23:00 en UTC).
            año, mes = (fecha.year + 1, 1) if (fecha.month, fecha.day) == (12, 31) else (fecha.year, fecha.month)
            if mes == 1 and año in salida and (fecha.month, fecha.day) in ((12, 31), (1, 1)):
                salida[año][por_nombre[partes[2]]] = int(d["Valor"])
    for año, pob in salida.items():
        if len(pob) != len(COMUNIDADES):
            raise ValueError(f"Población de {año}: faltan comunidades ({sorted(set(COMUNIDADES) - set(pob))})")
        pob[TOTAL] = sum(pob.values())
    return salida


def funcional_capitulos(filas, politicas=POLITICAS_CAPITULOS):
    """{"31": [personal, bienes y servicios, financieros, transf. corrientes, fondo, inversiones, transf. capital]}."""
    salida = {}
    for f in filas:
        m = _POLITICA.match(f[0])
        if m and m[1] in politicas:
            salida[m[1]] = [_num(v) for v in f[1:8]]
    return salida


def _clave(texto):
    """Solo letras ASCII en minúscula: «Andalucía», «Andaluc�a» y «AndalucÃ\xada» dan lo mismo («andaluca»)."""
    return re.sub(r"[^a-z]", "", texto.lower())


def comunidad_de(texto):
    k = _clave(texto)
    return next((c for c, prefijo in CLAVES.items() if k.startswith(prefijo)), None)


def _decodificar(linea):
    try:
        return linea.decode("utf-8")
    except UnicodeDecodeError:
        return linea.decode("cp1252")


def _csv(contenido):
    """Filas de un CSV de EDUCAbase (punto y coma; mezcla UTF-8 y Latin-1 según la línea)."""
    return [_decodificar(l).lstrip("﻿").rstrip("\r").split(";") for l in contenido.splitlines() if l.strip()]


def _cifra(texto):
    return float(texto.replace(".", "").replace(",", ".")) if re.fullmatch(r"-?[\d.]+(,\d+)?", texto.strip()) else 0.0


def sanidad_egsp(contenido):
    """Estadística de Gasto Sanitario Público (tabla 31 de «Sanidad en datos»): % por clasificación económica.

    {"año": 2023, "comunidades": {"01": {"personal", "compras", "conciertos", "otros"}, "00": España}}.
    """
    texto = html.unescape(re.sub(r"<[^>]+>", " ", _decodificar(contenido)))
    texto = re.sub(r"\s+", " ", texto)
    año = re.search(r"Año (\d{4})", texto)
    if not año:
        raise ValueError("Tabla de gasto sanitario sin año")
    numero = r"(\d+,\d)"
    salida = {}
    for m in re.finditer(r"([A-Za-zÁÉÍÓÚÑáéíóúñü][A-Za-zÁÉÍÓÚÑáéíóúñü ,.'-]+?) " + " ".join([numero] * 8), texto[año.end():]):
        nombre = m[1].strip()
        # La primera fila arrastra el texto de la cabecera delante de «España».
        c = TOTAL if _clave(nombre).endswith("espaa") else comunidad_de(nombre)
        if c:
            personal, compras, conciertos, otros = (float(m[i].replace(",", ".")) for i in range(2, 6))
            if abs(personal + compras + conciertos + otros - 100) > 0.5:
                raise ValueError(f"Gasto sanitario de {nombre}: los porcentajes no suman 100")
            salida[c] = {"personal": personal, "compras": compras, "conciertos": conciertos, "otros": otros}
    if len(salida) != len(COMUNIDADES) + 1:
        raise ValueError(f"Gasto sanitario: faltan comunidades ({sorted(set(COMUNIDADES) - set(salida))})")
    return {"año": año[1], "comunidades": salida}


def educacion(contenido_03, contenido_07):
    """Gasto de la consejería de educación de cada comunidad (EDUCAbase, tablas 3 y 7), en millones de euros.

    Tabla 3: por naturaleza económica. Tabla 7: transferencias a centros de titularidad privada (conciertos y
    subvenciones), que salen de las transferencias corrientes y de capital.
    """
    naturaleza = {"Personal": "personal", "Bienes y servicios": "compras", "Transferencias corrientes": "tc",
                  "Inversiones reales": "inversiones", "Transferencias de capital": "tk", "TOTAL": "total"}
    datos = {}
    for actividad, admin, nat, valor, *_ in (f for f in _csv(contenido_03) if len(f) >= 4):
        c = comunidad_de(admin)
        clave = next((v for k, v in naturaleza.items() if nat.startswith(k)), None)
        if actividad == "TOTAL" and c and clave:
            datos.setdefault(c, {})[clave] = _cifra(valor) / 1000
    for admin, ensenanza, valor, *_ in (f for f in _csv(contenido_07) if len(f) >= 3):
        c = comunidad_de(admin)
        if ensenanza == "TOTAL" and c in datos:
            datos[c]["privada"] = _cifra(valor) / 1000
    salida = {}
    for c, d in datos.items():
        transferencias = d.get("tc", 0) + d.get("tk", 0)
        privada = d.get("privada", 0)
        if privada > transferencias + 0.1:
            raise ValueError(f"Educación {c}: lo transferido a centros privados supera las transferencias")
        fila = {"personal": d.get("personal", 0), "compras": d.get("compras", 0), "privada": privada,
                "otras_transferencias": transferencias - privada, "inversiones": d.get("inversiones", 0)}
        fila["otros"] = d.get("total", 0) - sum(fila.values())
        salida[c] = {k: round(v, 3) for k, v in fila.items()}
    if len(salida) != len(COMUNIDADES):
        raise ValueError(f"Educación: faltan comunidades ({sorted(set(COMUNIDADES) - set(salida))})")
    salida[TOTAL] = {k: round(sum(salida[c][k] for c in COMUNIDADES), 3) for k in salida["01"]}
    return salida


def construir(carpeta=CARPETA_CRUDO, año_presupuesto=AÑO_PRESUPUESTO, año_liquidacion=AÑO_LIQUIDACION):
    ap, al = str(año_presupuesto), str(año_liquidacion)
    leer = lambda portal, tipo, año, c: _filas(ruta_crudo(carpeta, portal, tipo, año, c))
    datos_ine = json.loads((Path(carpeta) / f"poblacion_{al}_{ap}.json").read_text(encoding="utf-8"))
    pob = poblaciones(datos_ine, [año_presupuesto, año_liquidacion])
    nombres, comunidades, avisos = {}, {}, []
    for c in [TOTAL, *COMUNIDADES]:
        pre = funcional(leer("presupuestos", "funcional", año_presupuesto, c))
        pre_l = funcional(leer("presupuestos", "funcional", año_liquidacion, c))
        liq = funcional(leer("liquidaciones", "funcional", año_liquidacion, c))
        eco = economica(leer("presupuestos", "economica", año_presupuesto, c))
        eco_l = economica(leer("liquidaciones", "economica", año_liquidacion, c))
        caps_l = funcional_capitulos(leer("liquidaciones", "funcional_capitulos", año_liquidacion, c))
        for f in (pre, pre_l, liq):
            nombres.update(f.pop("nombres"))
        # El presupuesto inicial de la liquidación y el de la publicación de presupuestos deben coincidir.
        inicial = round(sum(v[0] for v in eco_l["gastos"].values()), 1)
        if abs(inicial - pre_l["total"]) > 1:
            avisos.append(f"{c}: el presupuesto inicial de {al} no coincide entre las dos publicaciones "
                          f"({inicial} y {pre_l['total']} millones)")
        comunidades[c] = {
            "nombre": "Total de las 17 comunidades" if c == TOTAL else COMUNIDADES[c][0],
            "poblacion": {ap: pob[año_presupuesto][c], al: pob[año_liquidacion][c]},
            "presupuestado": {ap: {**pre, "ingresos": eco["ingresos"], "gastos": eco["gastos"]}, al: pre_l},
            "gastado": {al: {**liq, "ingresos": eco_l["ingresos"], "gastos": eco_l["gastos"], "capitulos_politica": caps_l}},
        }
    # El total debe ser la suma de las 17 (el consolidado de cada comunidad ya quita lo interno).
    for año, clase in ((ap, "presupuestado"), (al, "presupuestado"), (al, "gastado")):
        for p, v in comunidades[TOTAL][clase][año]["politicas"].items():
            suma = sum(comunidades[c][clase][año]["politicas"].get(p, 0) for c in COMUNIDADES)
            if abs(suma - v) > 1:
                avisos.append(f"{clase} {año}, política {p}: el total ({v}) no es la suma de las 17 ({round(suma, 3)})")
    return {
        "fuente": {
            "organismo": "Ministerio de Hacienda (Secretaría General de Financiación Autonómica y Local); INE",
            "publicacion": "Presupuestos de las Comunidades Autónomas; Liquidación de Presupuestos de las Comunidades "
                           "Autónomas (datos consolidados); Estadística Continua de Población (tabla 56940)",
            "presupuestos": f"https://{DOMINIO}/SGCIEF/PublicacionPresupuestos/aspx/inicio.aspx",
            "liquidaciones": f"https://{DOMINIO}/SGCIEF/PublicacionLiquidaciones/aspx/menuInicio.aspx",
        },
        "unidad": "millones de euros",
        "año_presupuesto": ap,
        "año_liquidacion": al,
        "prorrogados": {str(a): v for a, v in PRORROGADOS.items() if a in (año_presupuesto, año_liquidacion)},
        "forales": FORALES,
        "politicas": dict(sorted(nombres.items())),
        "quien_presta": {
            "sanidad": {**sanidad_egsp((Path(carpeta) / "sanidad_tabla31.htm").read_bytes()),
                        "fuente": "Ministerio de Sanidad, Estadística de Gasto Sanitario Público (tabla 31 de «Sanidad en datos»)",
                        "unidad": "% del gasto sanitario público gestionado por la comunidad"},
            "educacion": {"año": str(AÑO_EDUCACION), "unidad": "millones de euros",
                          "fuente": "Ministerio de Educación, Estadística del gasto público en educación (EDUCAbase, tablas 3 y 7)",
                          "comunidades": educacion(*((Path(carpeta) / f"educacion_{AÑO_EDUCACION}_gasto{n}.csv").read_bytes() for n in ("03", "07")))},
        },
        "comunidades": comunidades,
        "avisos": avisos,
    }


def procesar(carpeta=CARPETA_CRUDO, salida=SALIDA):
    descargar(carpeta)
    datos = construir(carpeta)
    salida = Path(salida)
    salida.parent.mkdir(parents=True, exist_ok=True)
    salida.write_text(json.dumps(datos, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    return datos


def main():
    argparse.ArgumentParser(description=__doc__.splitlines()[0]).parse_args()
    datos = procesar()
    t = datos["comunidades"][TOTAL]
    ap, al = datos["año_presupuesto"], datos["año_liquidacion"]
    print(f"Total de las 17 (millones de euros): presupuestado {ap} {t['presupuestado'][ap]['total']:,.0f}; "
          f"presupuestado {al} {t['presupuestado'][al]['total']:,.0f}; gastado {al} {t['gastado'][al]['total']:,.0f}")
    print(f"  sanidad: {t['presupuestado'][ap]['politicas']['31']:,.0f} ({ap}); gastado {al}: "
          f"{t['gastado'][al]['politicas']['31']:,.0f} de {t['presupuestado'][al]['politicas']['31']:,.0f} presupuestados")
    print(f"  avisos: {datos['avisos'] or 'ninguno'} → {SALIDA}")


if __name__ == "__main__":
    main()
