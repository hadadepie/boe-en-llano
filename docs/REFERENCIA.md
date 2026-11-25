# Referencia del proyecto — El BOE en llano

Detalle que no cambia cada día: qué hay en la web, datos, cadena de datos, decisiones y rarezas de las fuentes.
Se consulta cuando hace falta (buscar por encabezado), no al empezar. Lo vivo está en `docs/ESTADO.md`; lo ya hecho,
en `docs/HISTORIAL.md`; lo pendiente, en `docs/BACKLOG.md`.

## Qué hay en la web
**Qué hay en la web (7 páginas, reorganizada el 25/11/2026, noche; ver `web/guia.html`):** Portada (edición semanal,
172 semanas desde el 17/08/2023, selector agrupado por año, buscador; titulares, «¿Quién decidió?», qué ha pasado con
normas anteriores y arriba los informes enlazados), Explorar (la semana de un vistazo, mosaico por tema, «La semana en
datos», gráfico por sección y lista con filtros; la leyenda del embudo filtra la lista), La legislatura, El dinero
público (`dinero.html` + `dinero.js`), Los tribunales (`tribunales.html` + `tribunales.js`), Cómo leer el BOE en llano
(`guia.html`: preguntas frecuentes, recorrido del RDL 6/2023, qué hay en cada página, esquemas de «quién es quién»,
alcance) y Cómo se ha hecho (fuera del menú: en el pie de todas las páginas, con «Limitaciones», «Correcciones» —anclas
que abren su apartado, `como.js`— y «Avisar de un error», las *issues* de GitHub). Las tres páginas de la legislatura
comparten `informe.js` (carga de `informe.json`, ayudas de Chart.js, `irAlAncla`); `legislatura.js` redirige las anclas
antiguas (`#presupuestos`, `#sin-presupuestos`, `#tribunales`, `#sentencias-tc`). Cada bloque con datos lleva «Cómo se
calcula» a su apartado del método. Antes de la reorganización, **La legislatura** tenía, en este orden: «Quién decidió» (por vía, mes
a mes, tema, entrada en vigor por tipo de norma y **por ministerio**, leyes); «Qué pasó con los decretos-ley» (tema,
tamaño y apoyo, cómo votó cada grupo, los 43 tramitados también como ley); «Gobernar sin Presupuestos»; **«El dinero de
los Presupuestos»** (Sankey de ingresos → gasto → a quién llega o a qué se dedica, con `web/datos/presupuestos.json`);
«Qué dijeron los tribunales» (sección I y **qué decidió el Tribunal Constitucional**, sección T); **«Las leyes: votación
y Senado»** (cómo votó cada grupo la votación final de cada ley, **qué hizo el Senado con los 39 textos del Congreso** y
14 conflictos ante el Constitucional); «Cuántas veces se corrige lo publicado». Índice arriba con las subsecciones
principales (25/11/2026). La portada tiene un recuadro fijo «Más allá de la semana» con tres enlaces a «La legislatura». Todo sale de `informe.json` (`boe/informe.py`), salvo el Sankey (`presupuestos.json`).
**La ficha** (cuatro preguntas): en las leyes, «¿Quién la apoyó?» da la votación final en el Congreso con el voto por
grupo, lo que hizo el Senado y la votación posterior; «¿Qué ha pasado después?» suma las sentencias del Constitucional
(en la norma juzgada y en la admisión a trámite) y pone el año en las fechas.

## Seguridad y privacidad
**Seguridad y privacidad (backlog 1b, cerrado):** CSP por `<meta>` (`script-src 'self'`; Chart.js servido desde la propia
web, `web/chart-4.4.1.umd.js`), enlaces de datos solo a la web, boe.es, congreso.es y senado.es (`enlaceSeguro` en
`app.js`), visitas con GoatCounter sin cookies (`web/contador.js`, solo la página; panel en boe-en-llano.goatcounter.com),
Action con permisos por trabajo, acciones por SHA y `requirements-ci.txt` con hashes (`python herramientas/bloquear.py`
tras cambiar `requirements.txt`), `SECURITY.md`; ajustes de GitHub hechos por la autora. Pruebas: `tests/test_seguridad.py`.

## Datos
**Datos:** sección I completa de la XV (3.774 normas), recuentos diarios desde el 17/08/2023, los 72 decretos-ley con su
votación (56 del Pleno con voto por grupos, 11 de la Diputación Permanente según el BOE, 5 sin votación) y su
tramitación. Campos sacados del texto oficial sin IA (`guardar --textos`): `textos_oficiales`, `tribunal` (266) y
`creditos` (30 normas estatales). Ficheros nuevos el 25/11/2026 (en Git): `datos/senado.json` (39 textos llegados del
Congreso: situación en el Senado, respuesta del Congreso, enmiendas y vetos presentados por grupo, ley en el BOE,
boletín del Congreso), `datos/congreso/votaciones_leyes.json` (34 leyes: 27 con votación final en el Pleno, 7 aprobadas en
comisión con competencia legislativa plena) y `datos/sentencias_tc.json` (124 sentencias y 17 autos del Constitucional
sobre normas; 62 de 136 admisiones de la XV resueltas, mediana de 368 días). «Vida de la norma»: normas de 2023, de 2024
(S1 528 normas, 113 consolidadas; S2 619, 94), de 2025 (S1 566, 90; S2 692, 82), de 2026-S1 (577, 110) y el resto de 2026 (la ventana semanal de 180 días ya cubría julio y
agosto: 173, 23 consolidadas): **toda la XV completa** (25/11/2026). Antes y después de los artículos, solo desde el 26/08/2026.
`datos/hacienda/presupuestos.json` (25/11/2026, `boe/hacienda.py`, a mano y no en la Action: Hacienda publica una edición
al año): Presupuestos Generales del Estado consolidados de 2017 a 2025-P (los de 2023 prorrogados; no hay 2026-P), en
millones de euros, con comprobaciones cruzadas.

## Propósito
Entender **qué decide el Estado y por qué**, a partir del BOE. Público principal: la
propia autora (entender cómo y por qué se toman las decisiones); después, la
ciudadanía. Se prioriza la **utilidad** sobre la audiencia y la **transparencia**
(método publicado, correcciones, «qué no cubrimos») sobre el gancho.

## Repositorio (GitHub: hadadepie/boe-en-llano, público)
Una sola rama viva: **`main`** (la versión ligera). Reorganizado el 23/11/2026: las
cuatro ramas eran una misma línea apilada y la última contenía la historia de las
demás; lo único propio de cada una era su diseño de web, que queda en etiquetas.

| Etiqueta | Qué guarda |
|---|---|
| `poc-original` | POC original: vista de datos (gráfico, matriz, lista filtrable, ficha lateral). Antigua `main`. |
| `variante-periodico` | Web como periódico semanal (portada por relevancia, «La semana en datos», secciones por tema, breves, ficha como artículo). Antigua `edicion-semanal`. |
| `variante-votaciones` | Periódico + votaciones, preámbulo, vida de la norma, glosario, antes/después, tramitación y legislatura, con `web/datos.json` único (~1,9 MB). Antigua `votaciones-congreso`. |

Ver una variante: `git checkout variante-periodico` (y volver con `git checkout main`).
Forma de trabajar: ramas cortas por funcionalidad (`feature/…`, `fix/…`) que se
fusionan en `main` y se borran. Si se quiere mantener otro diseño de web a la vez,
va en otra carpeta de `main` (p. ej. `web-periodico/`) leyendo los mismos datos, no
en una rama. La Action semanal (domingo 08:00 UTC) se ejecuta desde `main`.

**Descarga de la XV (24/11/2026):** terminada y fusionada en `main`. Sección I completa desde el 17/08/2023: 3.774 normas (las mismas que en los sumarios), todas con XML y textos oficiales, y ningún día laborable sin sumario; 172 ediciones semanales. Revisión con `exploracion/revisar_descarga.py`.

## Cadena de datos (`python -m boe.principal`)
1. `boe.guardar` — sumario diario del BOE (API) → `datos/recuentos.json` y `datos/normas/BOE-A-….json` (sección I) con metadatos del XML, **preámbulo** literal y **textos oficiales** (objeto, entrada en vigor, título competencial; `boe.extractos`) y, si es una decisión judicial sobre normas, su ficha `tribunal` (`boe.tribunales`). Reintenta tras 10, 30 y 90 s ante errores temporales del servidor (`descargar.pedir`). `--revisar` relee sumarios en crudo y corrige; `--textos` recalcula textos oficiales y tribunales desde el crudo.
2. `boe.clasificar` — tema, impacto y ámbito por reglas (con motivos).
3. `boe.resumir` — fichas. Sin IA: «pendiente» + título simplificado. Con IA: verificación estricta (citas por párrafo, números en los párrafos citados, vigencia, boletines).
4. `boe.congreso` — votación de convalidación de cada real decreto-ley (Pleno), agregada por grupo y por lista electoral cuando votan distinto. Busca 60 días tras la publicación (el plazo de 30 es en días hábiles).
5. `boe.tramitacion` — si se tramitó como proyecto de ley: pasos, resultado (p. ej. caducado), BOCG.
6. `boe.legislatura` — todas las convalidaciones del Pleno de la XV legislatura (cifras propias, con método). El resultado lo da el acuerdo publicado en el BOE cuando existe (y el órgano, del texto de la resolución); si no coincide con el Congreso se guarda `discrepancia`. `--rehacer` recalcula con los índices guardados.
6b. `boe.decretos_ley` — de cada real decreto-ley de la legislatura, su documento oficial por ELI (`/eli/es/rdl/AAAA/MM/DD/N/dof/spa/xml`): título, materias, normas que modifica (distintas, relaciones de cambio) y tema (reglas; «Varios temas» si 3+ temas con 3+ materias cada uno) → `datos/congreso/decretos_ley_xv.json`. La fecha para el ELI sale de la búsqueda de consolidada, de los índices de votaciones del Congreso o de nuestras normas.
6c. `boe.senado` — qué hizo el Senado con cada texto llegado del Congreso (datos abiertos del Senado, XML) → `datos/senado.json`; en la Action, solo la lista y las fichas sin terminar.
6d. `boe.votaciones_leyes` — votación final de cada ley en el Pleno del Congreso y la posterior al Senado (JSON de cada votación, voto agregado por grupo) → `datos/congreso/votaciones_leyes.json`; solo busca leyes nuevas (la búsqueda recorre los índices de toda la legislatura).
7. `boe.consolidada` — «vida de la norma»: entrada en vigor oficial, qué modifica, qué le pasó después. En la Action, las normas de los últimos 180 días y, por turnos, una de cada 4 consolidadas antiguas; a mano, `--desde`/`--hasta` por tandas. Reintenta ante cortes.
8. `boe.versiones` — antes/después de cada artículo modificado (desde la modificadora y desde la modificada).
8b. `boe.sentencias_tc` — sentencias y autos del Constitucional sobre normas de la sección T de los sumarios guardados (sin amparos), con la admisión que resuelven y cada norma juzgada y su resultado, según las referencias del BOE → `datos/sentencias_tc.json`; solo lo nuevo.
8c. `boe.hacienda` — a mano, no en `principal` ni en la Action: Presupuestos Generales del Estado consolidados (Excel de «Estadísticas de los PGE») → `datos/hacienda/presupuestos.json`; `exportar` lo copia a `web/datos/presupuestos.json` para el Sankey.
9. `boe.exportar` — calcula el informe de la legislatura con `boe.informe` (quién aprueba cada norma según rango y departamento, por mes y tema, entrada en vigor) en `web/datos/informe.json`, que solo carga `legislatura.html`; añade a cada norma `decision` (¿se votó?: votada, pendiente, gobierno, autonómica, tribunal, otra) y genera `web/datos/` (no versionado): `indice.json` (~62 KB con 172 ediciones: lista ligera de ediciones, ~200 bytes cada una, y la legislatura; sin recuentos por día ni mapa norma → semana, que la web deduce de la fecha en `buscar.json`), `semanas/<semana>.json` (resumen, piezas, votaciones y seguimiento de la edición, sus recuentos por día y sus normas sin antes/después y con el primer párrafo del preámbulo) y `buscar.json` (una línea por norma para el buscador de la portada, se carga al escribir), `feed.xml` (RSS con las 50 últimas normas), `normas/<id>.json` (preámbulo completo, `cambios`, `cambios_recibidos`, `textos_oficiales`; se carga al abrir la ficha) e `informe.json` (~15 KB). Las variantes antiguas (etiquetas) usan `web/datos.json` (~1,9 MB).

Ver la web: `.venv\Scripts\python.exe -m http.server 8000 --directory web` → http://localhost:8000

## Decisiones tomadas
- **IA**: solo para fichas; `gemma3:4b` local (Ollama) **no es fiable** (0 de 5 fichas superan el validador corregido). Las que lo superen se publicarían como «experimental». Pendiente probar un modelo mejor (sin API de Claude en el plan actual).
- **Privacidad en votaciones**: solo cifras agregadas (grupo, lista); el voto individual queda en `datos/crudo/`. El voto telemático cuenta como voto y no se muestra por persona (puede revelar salud/maternidad). Sin rankings de absentismo.
- **Neutralidad**: sin etiquetas políticas por norma; glosario neutral.
- **Datos**: `datos/crudo/` fuera de Git; se versionan los datos extraídos.
- **Repositorio público** y web en GitHub Pages (`hadadepie.github.io/boe-en-llano`; comprobado el 24/11/2026), con licencias MIT (código) y CC BY 4.0 (datos y textos propios). Se publica al lanzar la Action con la casilla `publicar` o `solo publicar`, y cada domingo si la variable `PUBLICAR_WEB` vale `true`.

## Rarezas de las fuentes (aprendidas a golpes)
- El resultado de una convalidación puede no coincidir entre el Congreso y el BOE: el RDL 8/2023 figura 171-171 en los datos abiertos de votaciones, pero el BOE publicó su convalidación (y hubo votación de tramitación, que solo se hace si se convalida). Manda el BOE.
- El plazo de 30 días para convalidar cuenta en días hábiles: un decreto-ley de finales de julio se vota en septiembre.
- **Sumario BOE**: al menos 4 estructuras (dep>epígrafe>item, dep>item, dep>texto>item, dep>texto>epígrafe>item) → se recorre de forma genérica. Un elemento suelto llega como dict, no lista.
- **Cifras en el BOE**: miles con espacio («1 286») y números con letra («ciento veinte»).
- **Congreso, votaciones**: el índice por fecha (`targetDate`) da un JSON por votación; los nombres de fichero llevan marcas de hora distintas por formato (no se adivinan). Votaciones **por llamamiento**: solo PNG → totales leídos del texto del índice. **Diputación Permanente**: no está en datos abiertos. Telemático = asiento «-1».
- **Congreso, diputados**: con Cortes disueltas casi todos figuran «de baja»; la lista electoral (`FORMACIONELECTORAL`) no distingue partidos dentro de una coalición.
- **Análisis de consolidada en JSON**: la lista de materias llega recortada (1 de 54 en el RDL 9/2024); en XML está completa.
- **Decretos-ley y consolidada**: 25 de los 72 de la XV no están en la base consolidada (ni por título ni por número). El documento oficial por ELI sí existe para todos.
- **Sumarios del BOE**: traen una sección `T` (Tribunal Constitucional, sentencias): «TC» en el gráfico por sección y, desde el 25/11/2026, sus sentencias sobre normas en `datos/sentencias_tc.json`. En el XML de cada sentencia, «DICTADA en el Recurso…» apunta a la admisión y «DECLARA…» a cada norma juzgada; un «,» quiere decir «lo mismo que la anterior». Cuidado con «ha decidido» en el texto: hay frases citadas antes del fallo.
- **Votaciones de leyes en el Congreso**: el expediente de cada ley sale del boletín que cita su ficha del Senado; en la serie A (proyectos) el número es el del expediente, en la serie B (proposiciones) no (amnistía: B-32 = 122/000019; se traduce con `ENLACESBOCG` de `ProposicionesDeLey`). Qué votación es lo dice el JSON (`titulo` = parte del orden del día; «Tramitación directa y en lectura única» es otra parte, con su «Votación de conjunto del texto»). Las votaciones por llamamiento no tienen JSON, y «(Pública por llamamiento)» puede ir delante del número de expediente. Las leyes con «Competencia Legislativa Plena» no tienen votación final en el Pleno.
- **Senado (datos abiertos)**: un id del BOE con el año mal escrito también en `boeAnnio` (`BOE-A-0205-19339`; vale `boeFecha`); una fecha imposible en `observaciones` (625/000001: 2023 por 2026); un «veto» que es un rechazo por mayoría absoluta (621/000008, octubre de 2024) y que en el Congreso no tuvo votación de veto; «se han rechazado todas excepto…» es «en parte», no «ninguna».
- **Servidor del Congreso**: corta conexiones en descargas largas (ConnectionReset) → `congreso._get` reintenta (`descargar.pedir`).
- **Legislación consolidada**: muchas normas no se consolidan (404); las recientes tardan días (404 temporal, se reintenta a los 2 días); el endpoint de bloques solo acepta XML; notas y referencias pueden venir como dict o lista; la **lista** de consolidada no sirve para contar (le faltan muchas normas).

- **Servidor del BOE**: en descargas largas devuelve a veces 502 (Bad Gateway); un 502 cortó la descarga de la XV el 08/02/2024 → reintentos con espera.
- **Tribunales en el BOE**: del Supremo solo se publican las sentencias que **anulan** normas (ninguna desestimatoria): no sirve para contar recursos perdidos. Del Constitucional, en la sección I van sobre todo las admisiones a trámite; las sentencias, en la sección `T`. El título de las providencias del Constitucional no dice quién recurre: está en la primera frase del texto.
- **Correcciones de errores**: el órgano de la corrección es el mismo que el de la norma corregida (las de reales
  decretos van con el ministerio que los propuso; las de leyes y decretos-ley, con la Jefatura del Estado). El
  título repite el de la norma tras «Corrección de errores del/de la…», pero un mismo número («Ley 3/2025») lo
  tienen muchas leyes autonómicas: enlazar por título completo y órgano, no por número.
- **Acuerdos internacionales**: traen tablas por país con columnas «Entrada en vigor» y «Aplicación provisional» que no son la disposición de entrada en vigor.
- **Presupuestos (Hacienda)**: los Excel de «Estadísticas de los PGE» (desde 2014) traen transferencias por artículos e ingresos por capítulos; antes de 2014, solo PDF; 2024-P y 2025-P son los de 2023 prorrogados y no hay 2026-P. El capítulo 1 de ingresos («Impuestos directos») incluye las cotizaciones sociales; los indirectos son solo la parte del Estado; la deuda nueva no aparece (se calcula por diferencia); no hay cruce política × destinatario. Ejecución: la IGAE, en Excel mensual (los diciembres de años anteriores con otro nombre, en páginas por año); la Seguridad Social, solo en PDF.
- **Ventana semanal de la vida de las normas**: la Action consulta las normas de los últimos 180 días, así que una tanda a mano sobre ese periodo no trae nada nuevo (julio y agosto de 2026, 25/11/2026).
