"""Paso 1: descargar el sumario de un día del BOE.

Uso desde la terminal (con el entorno virtual activado):
    python -m boe.descargar 2026-11-20

Cómo es la respuesta de la API (lo comprobamos con llamadas reales):
    data → sumario → diario[] → seccion[] → departamento[] → ...
y dentro de cada departamento las publicaciones ("items") pueden estar en
TRES sitios distintos:
    - departamento → epigrafe[] → item[]   (secciones I, II y III)
    - departamento → item[]                (secciones V.A y V.B)
    - departamento → texto → item          (sección V.C)
Además, cuando solo hay un elemento, la API no lo mete en una lista sino que
lo da "suelto" (un diccionario). Por eso usamos la función `como_lista`.
"""

import argparse
import json
import time
from datetime import date
from pathlib import Path

import requests

URL_SUMARIO = "https://www.boe.es/datosabiertos/api/boe/sumario/{fecha}"
URL_NORMA_XML = "https://www.boe.es/diario_boe/xml.php?id={identificador}"
CARPETA_SUMARIOS = Path("datos/crudo/sumarios")
CARPETA_NORMAS_XML = Path("datos/crudo/normas")
PAUSA_SEGUNDOS = 1.0  # espera tras cada petición, para no saturar la API
CABECERAS = {
    "Accept": "application/json",  # pedimos JSON (si no, la API responde en XML)
    "User-Agent": "boe-en-llano/0.1 (proyecto educativo)",
}
CLAVES_CONOCIDAS_DEPARTAMENTO = {"codigo", "nombre", "item", "epigrafe", "texto"}


def como_lista(valor):
    """Devuelve siempre una lista: [] si no hay nada, [x] si viene suelto."""
    if valor is None:
        return []
    if isinstance(valor, list):
        return valor
    return [valor]


def descargar_sumario(fecha, carpeta=CARPETA_SUMARIOS, pausa=PAUSA_SEGUNDOS):
    """Devuelve el sumario de `fecha` como diccionario, o None si ese día no hay BOE.

    Si ya está guardado en `carpeta`, lo lee del disco y NO llama a la API.
    """
    archivo = Path(carpeta) / f"{fecha:%Y%m%d}.json"

    if archivo.exists():
        print(f"  {fecha}: ya estaba guardado, no se descarga otra vez.")
        return json.loads(archivo.read_text(encoding="utf-8"))

    url = URL_SUMARIO.format(fecha=f"{fecha:%Y%m%d}")
    print(f"  {fecha}: descargando {url}")
    respuesta = requests.get(url, headers=CABECERAS, timeout=30)
    time.sleep(pausa)

    if respuesta.status_code == 404:
        # Domingos, festivos sin boletín o fechas futuras. No se guarda nada,
        # porque una fecha de hoy puede no estar publicada TODAVÍA.
        print(f"  {fecha}: no hay BOE publicado ese día.")
        return None
    respuesta.raise_for_status()  # cualquier otro error: que se vea y se pare

    datos = respuesta.json()
    archivo.parent.mkdir(parents=True, exist_ok=True)
    archivo.write_text(json.dumps(datos, ensure_ascii=False, indent=1), encoding="utf-8")
    return datos


def descargar_norma_xml(identificador, carpeta=CARPETA_NORMAS_XML, pausa=PAUSA_SEGUNDOS):
    """Devuelve el XML completo (metadatos + texto) de una norma, como texto.

    Igual que con los sumarios: si ya está en `carpeta`, no se pide otra vez.
    """
    archivo = Path(carpeta) / f"{identificador}.xml"
    if archivo.exists():
        return archivo.read_text(encoding="utf-8")

    url = URL_NORMA_XML.format(identificador=identificador)
    print(f"    {identificador}: descargando texto")
    respuesta = requests.get(url, headers={"User-Agent": CABECERAS["User-Agent"]}, timeout=30)
    time.sleep(pausa)
    respuesta.raise_for_status()

    respuesta.encoding = "utf-8"
    archivo.parent.mkdir(parents=True, exist_ok=True)
    archivo.write_text(respuesta.text, encoding="utf-8")
    return respuesta.text


def secciones(sumario):
    """Lista de todas las secciones del sumario (de todos sus diarios)."""
    resultado = []
    for diario in como_lista(sumario["data"]["sumario"]["diario"]):
        resultado.extend(como_lista(diario.get("seccion")))
    return resultado


def extraer_items(seccion):
    """Lista de todas las publicaciones de una sección, estén donde estén."""
    items = []
    for departamento in como_lista(seccion.get("departamento")):
        claves_raras = set(departamento) - CLAVES_CONOCIDAS_DEPARTAMENTO
        if claves_raras:
            print(f"  AVISO: estructura inesperada en {seccion.get('codigo')}: {claves_raras}")

        items.extend(como_lista(departamento.get("item")))
        for epigrafe in como_lista(departamento.get("epigrafe")):
            items.extend(como_lista(epigrafe.get("item")))
        texto = departamento.get("texto")
        if isinstance(texto, dict):
            items.extend(como_lista(texto.get("item")))
    return items


def contar_por_seccion(sumario):
    """Devuelve un diccionario {código de sección: número de publicaciones}.

    Ejemplo de resultado: {"1": 27, "2A": 12, "2B": 35, "3": 72, ...}
    """
    recuento = {}
    for seccion in secciones(sumario):
        # Suma (no asigna) por si un día trae varios diarios con la misma sección.
        codigo = seccion["codigo"]
        recuento[codigo] = recuento.get(codigo, 0) + len(extraer_items(seccion))
    return recuento


def main():
    parser = argparse.ArgumentParser(description="Descarga el sumario de un día del BOE.")
    parser.add_argument("fecha", help="fecha en formato AAAA-MM-DD, por ejemplo 2026-11-20")
    argumentos = parser.parse_args()
    fecha = date.fromisoformat(argumentos.fecha)

    sumario = descargar_sumario(fecha)
    if sumario is None:
        return

    nombres = {s["codigo"]: s["nombre"] for s in secciones(sumario)}
    recuento = contar_por_seccion(sumario)
    print(f"\nPublicaciones del BOE del {fecha}:")
    for codigo, cantidad in recuento.items():
        print(f"  {codigo:3} {cantidad:4}  {nombres.get(codigo, '')}")
    print(f"  Total: {sum(recuento.values())}")


if __name__ == "__main__":
    main()
