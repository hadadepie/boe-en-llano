# Contenido, cifras y textos

La web explica lo que decide el Estado a personas que no leen el BOE. El daño más grave posible no es un
error de código: es afirmar algo falso con apariencia oficial. Estas reglas vienen de `CLAUDE.md` y son
obligatorias.

## Cifras y hechos

- Toda cifra, fecha o efecto publicado sale de una fuente oficial (BOE, Congreso, Senado, Hacienda) y se puede
  rastrear hasta el código que la calcula o el texto que la copia. Una cifra escrita a mano en un HTML que no
  sale de los datos → hallazgo: se quedará desfasada (`tests/test_web.py`, «frases desfasadas», ya ha cazado
  varias).
- Comprueba las cifras nuevas del texto contra el JSON que las genera (`web/datos/informe.json`, `datos/…`). Si
  no cuadran → `bloquea`.
- Vocabulario exacto: «concedido», no «gastado»; «convalidado», «derogado», «caducado» según el BOE; «según la
  propia norma» cuando se copia. No interpretar el porqué de una cifra si los datos no lo dicen.
- Sin resumen fiable, «pendiente». Lo generado por IA va marcado como experimental.

## Avisos

- Cada ficha lleva: «Resumen orientativo, no es asesoramiento jurídico. Consulta el texto oficial.»
- Un gráfico o bloque con datos lleva su «Cómo se calcula» enlazado al apartado del método en `como.html`, y
  lo que no cubre («Limitaciones»).

## Neutralidad y privacidad

- Sin etiquetas políticas sobre normas ni grupos (ni «progresista», «polémica», «recorte»…) y sin adjetivos
  valorativos. Los grupos, por su nombre oficial.
- Votaciones: solo agregadas por grupo o lista; nada de votos individuales, voto telemático por persona ni
  rankings de absentismo.
- Personas concretas (nombramientos, BORME, indultos): solo cifras agregadas.
- Solo se enlaza a fuentes oficiales, no a otras webs.

## Transparencia

- Una novedad visible o una corrección de algo ya publicado se explica en «Cómo se ha hecho» (`como.html`):
  método nuevo, o entrada en «Correcciones» con qué decía y qué dice ahora. Un cambio que corrige un dato
  publicado sin entrada en «Correcciones» → hallazgo.
- `guia.html` al día si cambia qué hay en cada página.

## Lenguaje llano

- Frases cortas, sin jerga jurídica sin explicar; si un término es inevitable, con su ⓘ del glosario
  (`<span data-termino="…">`). Lo que el lector debe hacer o saber, primero.
- Español de España, con comillas «» y fechas «25 de noviembre de 2026».

## Docs del proyecto

- `docs/ESTADO.md` debe seguir corto (lo vivo); lo hecho va a `docs/HISTORIAL.md`. Si el cambio cierra un
  paso, que se refleje ahí y en `docs/BACKLOG.md`.
