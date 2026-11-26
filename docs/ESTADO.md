# Estado del proyecto — El BOE en llano

Última actualización: 26/11/2026. Resumen corto para retomar el trabajo (personas o sesiones nuevas de Claude): se lee
entero al empezar. El resto se consulta solo cuando hace falta, buscando por encabezado (`grep -n '^#' docs/…`):

| Archivo | Qué tiene |
|---|---|
| `docs/REFERENCIA.md` | Qué hay en cada página de la web, seguridad, datos y ficheros, repositorio y etiquetas, cadena de datos paso a paso, decisiones tomadas y rarezas de las fuentes |
| `docs/HISTORIAL.md` | Lo ya hecho, día a día, y las correcciones registradas |
| `docs/BACKLOG.md` | Cada propuesta con su método, estado del arte y prioridades (largo: buscar la sección, no leerlo entero) |

## Dónde está todo

Una sola rama, `main`, al día en GitHub (último commit subido: `21b2936`, 26/11/2026) salvo lo que diga
`git log origin/main..main`. Web publicada en GitHub Pages con todo lo del 25/11/2026 **salvo el Sankey de los
Presupuestos, la reorganización de la web, «Qué pasó después», el importe de cada crédito en la ficha y el arreglo de
«Los tribunales» (26/11/2026)**, que están en `main` pero aún no publicados. 296 pruebas (26/11/2026: 284 pasan; 12
se saltan sin Node y en la Action sí corren).

La web tiene 7 páginas: Portada, Explorar, La legislatura, El dinero público, Los tribunales, Cómo leer el BOE en llano
y Cómo se ha hecho (en el pie). Detalle en `docs/REFERENCIA.md`, «Qué hay en la web».

## Siguientes pasos (en este orden)

1. **Publicar la web** con el Sankey, la reorganización, «Qué pasó después», los importes de los créditos y el arreglo
   de «Los tribunales» (la autora: Action con «Solo publicar») y,
   el domingo 29/11, mirar en el registro que la Action no falla y cuánto tarda el paso 5/6 (refresco por turnos,
   Senado, votaciones de las leyes, sentencias, `boe.citadas`; primera que exporta `presupuestos.json`).
2. **Votaciones de las 2 reformas de la Constitución** (arts. 49 y 69.3): código en `c5e12e0` (expedientes
   100/000001 y 101/000002, leídos de la portada del boletín). Falta el dato: congreso.es respondía 403 a todo el
   26/11/2026; cuando responda, `boe.votaciones_leyes` (~10 min), `exportar`, revisar la ficha y hacer commit de los
   textos de la web que ya están preparados sin commit (`como.html`, `guia.html`, `legislatura.js`) (backlog 2.7).
3. **Importes de los créditos**: hecho (en la ficha de cada norma, solo cifras seguras, sin totales; ver HISTORIAL).
   Si la autora revisa algún dudoso en `datos/presupuestos/revision_creditos.html`, se anota en la hoja y su cifra
   pasa a la ficha al regenerar (`boe.importes_creditos` y `exportar`).
4. **Presupuestado frente a gastado** (backlog 3.9, llamada de prueba hecha, va en `dinero.html`): `boe/ejecucion.py`
   con los cierres de la IGAE (hoja `GTOS 008`) y los PDF de la Seguridad Social; antes, aclarar por qué el inicial de
   2023 de la Seguridad Social no cuadra con Hacienda (~4.960 M€, parecen transferencias internas).
5. Después, por prioridades: «leyes escoba» (backlog 2.6, con el campo `cambia` de cada norma), «¿Quién decide qué?» (6, backlog 2.5, texto revisado por la autora), las iniciativas que
   nacen en el Senado (2.7) y medir si se acorta la ventana de las no consolidadas en la Action.

## Pendientes del backlog (índice)

| Prioridad | Qué | Sección |
|---|---|---|
| 5 🔄 | Dinero público: importes de los créditos, subvenciones, presupuestado frente a gastado | 3.2, 3.9 |
| 6 | Explicador «¿Quién decide qué?» | 2.5 |
| 8 | Competencias que usa el Estado y conflictos | 2.5, 3.4 |
| 9 | Qué hace el Congreso, fase B (de dónde vienen las leyes) | 2.2 |
| 10–14 | Promesas frente a hechos, empleo público, convenios, directivas y consultas, Comunidad de Madrid | 3.3, 3.6, 3.7, 3.5, 3.8, 3.1 |
| 15 🔄 | El Senado: iniciativas que nacen allí y reformas de la Constitución | 2.7 |
| — | Mejoras cortas de la web (se hacen al tocar el código afectado) y revisión externa | 1, 1c |

## Cuidado

- Con `.env` presente, `boe.resumir` usa Ollama: lanzar con `BOE_IA_PROVEEDOR=ninguno`.
- Tras una descarga grande, pasar también `boe.congreso --desde …`, `boe.tramitacion` y
  `boe.legislatura --rehacer`, además de `guardar --textos`, `clasificar`, `resumir` y `exportar`.
- La vista previa local escucha en el puerto 8000 aunque la herramienta diga otro
  (`.venv\Scripts\python.exe -m http.server 8000 --directory web`).
- **Dos sesiones en la misma carpeta**: añadir al commit solo los archivos propios por ruta, nunca `git add -A` ni
  `git add` de carpetas que toque la otra, y no hacer commit con una prueba fallando. Un archivo que editan las dos
  (p. ej. `web/como.html`) no se puede repartir con `git add`.
- La autora da el visto bueno a cada subida a GitHub. La Action guarda datos en `main` cada domingo (y si se lanza a
  mano sin «Solo publicar»): antes de subir, `git fetch` y, si hay commits suyos, `git pull --rebase` (sus datos y los
  nuestros no suelen tocar los mismos archivos).
- En este portátil la consola Bash de Claude Code se colgó con un `ls` (25/11/2026): para procesos largos, PowerShell.
  Python tarda ~80 s en leer los 88 MB de índices de votaciones del Congreso (`datos/crudo/congreso/indices/`);
  `congreso._texto_visible` es demasiado lenta para recorrerlos todos: buscar en el HTML crudo.
- Al acabar una tarea, actualizar aquí solo lo vivo (dónde está todo, siguientes pasos, cuidado) y llevar lo hecho a
  `docs/HISTORIAL.md`: este archivo debe seguir siendo corto.
