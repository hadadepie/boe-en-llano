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

from boe import clasificar, congreso, consolidada, decretos_ley, exportar, guardar, ia, legislatura, resumir, tramitacion, versiones


def ejecutar(desde, hasta):
    print(f"1/6 Descargando y guardando del {desde} al {hasta}…")
    estados = guardar.procesar_rango(desde, hasta)

    # La clasificación es siempre por reglas (transparente y probada); la IA, si
    # está configurada, solo se usa para las fichas. Para clasificar con IA:
    # python -m boe.clasificar --ia
    print("2/6 Clasificando… (reglas)")
    clasificar.clasificar_carpeta()

    cliente = ia.cliente_desde_entorno()

    print("3/6 Generando fichas…" + ("" if cliente else " (sin IA: quedan pendientes)"))
    normas = resumir.resumir_carpeta(cliente_ia=cliente, texto_de=guardar.texto_de_norma)

    print("4/6 Buscando las votaciones del Congreso…")
    try:
        congreso.procesar(desde=desde - timedelta(days=60))
        tramitacion.procesar()
        legislatura.procesar()  # índices ya guardados: solo consulta los días nuevos
        decretos_ley.procesar()  # tema y tamaño de cada decreto-ley: solo los que falten
    except Exception as error:  # el Congreso es una fuente aparte: si falla, la web se publica igual
        print(f"  No se pudieron consultar las votaciones del Congreso ({error.__class__.__name__}: {error}).")

    print("5/6 Actualizando la vida de las normas y sus cambios (legislación consolidada)…")
    try:
        # Solo las recientes y las que ya tienen vida (las antiguas, por tandas a mano: ver boe.consolidada).
        consolidada.procesar(desde=(hasta - timedelta(days=consolidada.DIAS_SEMANAL)).isoformat(), con_vida=True)
        versiones.procesar()
        versiones.procesar_recibidos()
    except Exception as error:  # fuente aparte: si falla, la web se publica igual
        print(f"  No se pudo consultar la legislación consolidada ({error.__class__.__name__}: {error}).")

    print("6/6 Exportando la web…")
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
