"""Ejecuta toda la cadena: descargar → guardar → clasificar → resumir → exportar.

Uso:
    python -m boe.principal                     # últimos 7 días (incluido hoy)
    python -m boe.principal --dias 30
    python -m boe.principal --desde 2026-11-01 --hasta 2026-11-21

Es lo que ejecuta la GitHub Action cada mañana. Los días ya procesados y las
fichas ya verificadas no se repiten, así que se puede lanzar tantas veces como
se quiera.
"""

import argparse
from datetime import date, timedelta

from boe import clasificar, exportar, guardar, ia, resumir


def ejecutar(desde, hasta):
    print(f"1/4 Descargando y guardando del {desde} al {hasta}…")
    estados = guardar.procesar_rango(desde, hasta)

    # La clasificación es siempre por reglas (transparente y probada); la IA, si
    # está configurada, solo se usa para las fichas. Para clasificar con IA:
    # python -m boe.clasificar --ia
    print("2/4 Clasificando… (reglas)")
    clasificar.clasificar_carpeta()

    cliente = ia.cliente_desde_entorno()

    print("3/4 Generando fichas…" + ("" if cliente else " (sin IA: quedan pendientes)"))
    normas = resumir.resumir_carpeta(cliente_ia=cliente, texto_de=guardar.texto_de_norma)

    print("4/4 Exportando la web…")
    exportar.main()

    nuevos = sum(1 for e in estados.values() if e == "hecho")
    verificadas = sum(1 for n in normas if n["ficha"]["estado"] == "ok")
    print(f"\nHecho: {nuevos} días nuevos · {len(normas)} normas · {verificadas} fichas verificadas.")
    return estados


def main():
    parser = argparse.ArgumentParser(description="Actualiza todos los datos y la web.")
    parser.add_argument("--dias", type=int, default=7, help="cuántos días hacia atrás revisar (por defecto 7)")
    parser.add_argument("--desde", help="AAAA-MM-DD (sustituye a --dias)")
    parser.add_argument("--hasta", help="AAAA-MM-DD (por defecto, hoy)")
    args = parser.parse_args()

    hasta = date.fromisoformat(args.hasta) if args.hasta else date.today()
    desde = date.fromisoformat(args.desde) if args.desde else hasta - timedelta(days=args.dias - 1)
    if desde > hasta:
        parser.error("--desde no puede ser posterior a --hasta")
    ejecutar(desde, hasta)


if __name__ == "__main__":
    main()
