# Estado del proyecto — El BOE en llano

Última actualización: 24/11/2026, noche. Documento para retomar el trabajo (personas o
sesiones nuevas de Claude). Las reglas permanentes están en `CLAUDE.md`; lo
pendiente, en `docs/BACKLOG.md`.

## Para retomar (24/11/2026, noche)

**Dónde está todo:** una sola rama, `main`, al día en GitHub salvo lo que diga `git log origin/main..main`.
Árbol limpio. Web publicada en GitHub Pages. `?v=` actual: `estilos.css` `2026-11-24v`, `legislatura.js`
`2026-11-24w`, `app.js` `2026-11-24s`; `portada.js`, `explorar.js` y `como.js` `2026-11-24p`.

**Qué hay en la web (5 páginas, ver `web/guia.html`):** Portada (edición semanal, 172 semanas desde el
17/08/2023, selector agrupado por año, buscador), Explorar (gráfico por sección y lista con filtros),
La legislatura, Cómo se ha hecho y Guía. **La legislatura**, en este orden: «Quién decidió» (por vía, mes a
mes, tema, entrada en vigor, leyes); «Qué pasó con los decretos-ley» (tema, tamaño y apoyo, cómo votó cada
grupo, los 43 tramitados también como ley); «Gobernar sin Presupuestos»; «Qué dijeron los tribunales».
Todo sale de `informe.json` (`boe/informe.py`).

**Datos:** sección I completa de la XV (3.774 normas), recuentos diarios desde el 17/08/2023, los 72
decretos-ley con su votación (56 del Pleno con voto por grupos, 11 de la Diputación Permanente según el
BOE, 5 sin votación) y su tramitación. Campos sacados del texto oficial sin IA (`guardar --textos`):
`textos_oficiales`, `tribunal` (266) y `creditos` (30 normas estatales: 29 decretos-ley y 1 ley).
«Vida de la norma»: normas de 2023 y desde el 26/08/2026; antes y después, solo desde el 26/08/2026.

**Siguientes pasos (en este orden):**
1. **Vida de las normas de 2024–2026** (~3.150 normas, ~4 h a 4–5 s cada una): de noche, por semestres,
   `python -m boe.consolidada --desde 2024-01-01 --hasta 2024-06-30`, etc. Con todo cargado: la última
   parte del informe («normas modificadas o derogadas») y decidir el refresco por turnos de las ~800
   consolidadas antiguas en la Action.
2. **Créditos (prioridad 5, pieza 2):** importes con su unidad, revisados a mano, y los párrafos en la
   ficha de cada norma (ver «Pendientes técnicos» del backlog).
3. **El Senado (2.7, nueva):** pieza «el Senado ante el Constitucional» con los 14 conflictos ya
   guardados, y llamada de prueba a los datos abiertos del Senado para vetos y enmiendas.
4. Después, por prioridades: Sankey de los Presupuestos (5, pieza 1), sección `T` (sentencias del
   Constitucional, 4), «¿Quién decide qué?» (6).

**Cuidado:**
- Con `.env` presente, `boe.resumir` usa Ollama: lanzar con `BOE_IA_PROVEEDOR=ninguno`.
- Tras una descarga grande, pasar también `boe.congreso --desde …`, `boe.tramitacion` y
  `boe.legislatura --rehacer`, además de `guardar --textos`, `clasificar`, `resumir` y `exportar`.
- La vista previa local escucha en el puerto 8000 aunque la herramienta diga otro.
- La autora da el visto bueno a cada subida a GitHub.

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
7. `boe.consolidada` — «vida de la norma»: entrada en vigor oficial, qué modifica, qué le pasó después. En la Action, solo normas de los últimos 180 días y las que ya tienen vida; a mano, `--desde`/`--hasta` por tandas.
8. `boe.versiones` — antes/después de cada artículo modificado (desde la modificadora y desde la modificada).
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
- **Sumarios del BOE**: traen una sección `T` (Tribunal Constitucional, sentencias); desde el 24/11/2026 se muestra como «TC» en el gráfico por sección (`guardar` sigue sin guardar sus publicaciones, ver backlog 3.4).
- **Votaciones de leyes en el Congreso** (índices diarios): cada ley genera muchas votaciones (dictamen, enmiendas, «votación de conjunto» en las orgánicas, enmiendas del Senado) y el título del Congreso no lleva el número de la ley: habría que emparejar por texto (ver 2.3b del backlog).
- **Legislación consolidada**: muchas normas no se consolidan (404); las recientes tardan días (404 temporal, se reintenta a los 2 días); el endpoint de bloques solo acepta XML; notas y referencias pueden venir como dict o lista; la **lista** de consolidada no sirve para contar (le faltan muchas normas).

- **Servidor del BOE**: en descargas largas devuelve a veces 502 (Bad Gateway); un 502 cortó la descarga de la XV el 08/02/2024 → reintentos con espera.
- **Tribunales en el BOE**: del Supremo solo se publican las sentencias que **anulan** normas (ninguna desestimatoria): no sirve para contar recursos perdidos. Del Constitucional, en la sección I van sobre todo las admisiones a trámite; las sentencias, en la sección `T`. El título de las providencias del Constitucional no dice quién recurre: está en la primera frase del texto.
- **Acuerdos internacionales**: traen tablas por país con columnas «Entrada en vigor» y «Aplicación provisional» que no son la disposición de entrada en vigor.
- **Presupuestos (Hacienda)**: los Excel de «Estadísticas de los PGE» (desde 2014) traen transferencias por artículos e ingresos por capítulos; antes de 2014, solo PDF; 2024-P y 2025-P son los de 2023 prorrogados.

## Correcciones registradas (también en la web)
Validador (miles con espacio y números con letra); sumario (cuarta estructura: 12 días y 10 normas perdidas en sep-oct); RDL 26 y 27/2026 (votados por llamamiento, aparecían «sin datos»). 24/11/2026: textos que daban a entender fichas de IA publicadas; sección T sin barra en el gráfico; RDL 8/2023 publicado como derogado por empate (el BOE publicó su convalidación); RDL 24, 25, 28 y 29/2026 «sin votación» (los decidió la Diputación Permanente); decretos-ley de 2023–2026 «pendientes» y sin voto por grupos.

## Próximos pasos
1. ~~Cerrar mejora 5~~ Hecho: `boe.legislatura` (819 días revisados). Cifras al día en el punto 16 (53 convalidados, 14 derogados, 5 sin votación; el «empate» del RDL 8/2023 era un error: el BOE publicó su convalidación).
2. ~~Versión ligera~~ Hecho (23/11/2026), hoy en `main`:
   - **Ficha en cuatro preguntas** (`web/app.js`): ¿Qué es? · ¿Por qué? · ¿Quién la apoyó? · ¿Qué ha pasado después?, una línea cada una y desplegables. «¿Quién la apoyó?» sin votación: dice quién firma (reales decretos, órdenes, resoluciones no se votan) o que no se recoge (leyes estatales y autonómicas). «A favor/en contra» = voto mayoritario de cada grupo.
   - **Leer y explorar separados**: `index.html` + `portada.js` (titulares, la semana de un vistazo como embudo en dos niveles, mosaico de las normas por tema, «La semana en datos» desplegable, y la gestión interna solo como recuento con enlace a «Explorar» filtrado (`?impacto=Técnico`); gráficos en SVG/HTML sin Chart.js) y `datos.html` + `explorar.js` (hoy: gráfico por sección y lista con filtros). La edición viaja en `?e=`; las fichas se enlazan con `#BOE-…` en ambas páginas. La legislatura tiene su página: `legislatura.html` + `legislatura.js` (no depende de la edición: `PAGINA.sinEdicion` en app.js). Desde el 24/11/2026: «Cómo se ha hecho» en `como.html` + `como.js` (glosario y estado de las fichas; `datos.html#como` redirige) y `guia.html` (estática, sin JS: qué responde cada parte, alcance de los datos, lo que falta; mantenerla al día al añadir o quitar piezas). Explorar ya no tiene la matriz tema × impacto ni las votaciones de la semana (duplicaban el mosaico y la ficha).
   - **Carga**: la portada descarga ~150 KB (antes 1,9 MB).
   - Gráficos en la portada (23/11/2026): **embudo en dos niveles** (barra con todo el BOE de la semana y la astilla de las normas generales; debajo, ampliadas, un cuadrado por norma coloreado por impacto. Sustituyó a una cuadrícula de un punto por publicación, donde las que te afectan —0,9 %— no se veían; quitar los anuncios solo lo subía al 1,6 %) y **mosaico** (un cuadrado por norma, por tema y coloreado por impacto; abre la ficha). Sustituyen a las cifras con barra y a «Por temas». Reparto acordado: la portada engancha (2 gráficos), «Explorar» analiza; como mucho un gráfico por pantalla y con su frase de lectura. Resuelto el 24/11/2026: la matriz de «Explorar» repetía el mosaico y se quitó.
   - **Qué ha pasado con normas anteriores** (portada, 23/11/2026): cada edición lista lo ocurrido esa semana a normas ya publicadas (votaciones del Pleno y acuerdos de la Diputación Permanente sobre RDL; modificaciones, derogaciones, etc. de «vida de la norma»), calculado en `exportar.seguimiento_semanas`. Motivo: quien lee cada semana no vuelve a fichas antiguas. Límite resuelto el 24/11/2026: el hueco S42–S46 se rellenó (ahora hay 14 ediciones, S35–S48).
   - Titulares cortos por reglas en portada y listas (`boe.resumir.titular_corto`, máximo 120 caracteres, sin añadir palabras).
   - Decisión (23/11/2026): `main` es la versión ligera; las variantes anteriores quedan como etiquetas (ver «Repositorio»).
3. ~~Gráficos de la legislatura~~ Hecho (23/11/2026): hoy en «La legislatura», decretos-ley por tema y resultado, y tamaño (normas que modifica) frente a margen. Hallazgo: de los 11 votados en el Pleno que modifican 10+ normas se derogaron 6; de los 45 más pequeños, 8 (pocos casos; no se interpreta el porqué).
4. ~~Estado del arte de «qué hace el Congreso»~~ Hecho (23/11/2026); la fase A queda **aparcada** en el backlog.
5. ~~Publicar la web~~ Hecho: GitHub Pages, repositorio público, licencias MIT y CC BY 4.0.
6. ~~Diseño para el público general~~ Hecho el 24/11/2026 (sección 0 del backlog), todo fusionado en `main`: icono SVG y vista previa al compartir (`web/imagen-compartir.png`, generada con `herramientas/imagen_compartir.py`; URLs absolutas de `hadadepie.github.io/boe-en-llano`; la vista previa de cada ficha sigue siendo la genérica), título de pestaña con el titular, botón «Compartir», bienvenida cerrable, seguimiento agrupado (máx. 4), iconos Lucide por tema, buscador (`buscar.json`), cabecera fija, franja de color por tema, y «Te afecta a ti» renombrado «Afecta a mucha gente». Quedan solo los «más grandes»: tipografía propia (la guía y el RSS ya están).
   - Hueco S42–S46 rellenado y la portada abre la última semana completa mientras la en curso tenga menos de 3 días con datos (`edicionPorDefecto()` en `app.js`). La Action es semanal: la edición en curso se completa cada semana.
7. ~~Decisiones que se votan (2.3 del backlog)~~ Hecho y fusionado el 24/11/2026: filtro «¿Se votó?», línea «¿Quién decidió?» en la portada y explicación en el método. Las cifras de votación de las leyes quedan fuera por ahora (2 de 343 normas son leyes estatales): ver 2.3b.
8. **Todo lo pendiente está en `docs/BACKLOG.md`** (24/11/2026), con el método para cada propuesta (estado del arte → llamada de prueba → prototipo → decidir) y dónde se quedan cortos los datos: mejoras cortas (decretos-ley votados por la Diputación Permanente, sección T, comprobar `buscar.json` en la Action, IA, coaliciones, RSS…), ampliaciones («qué hace el Congreso» A y B, las decisiones que se votan) y proyectos paralelos (Comunidad de Madrid y tiempos de desarrollo autonómico; gasto público; promesas del Plan Anual Normativo frente a lo aprobado; normas en el Tribunal Constitucional; transposición de directivas; empleo público; convenios; consultas públicas). Relaciones público-privadas: solo entre instituciones o en cifras agregadas oficiales (ver backlog).
9. **Prioridades y enfoque** (24/11/2026, confirmadas): tras revisar el estado del arte (cinco webs resumen el BOE a diario con IA; El Congreso en tu mano y Bocal ya cubren las votaciones por grupo), la apuesta es informes y gráficos guiados y competencias, sin enlazar a webs ajenas. Orden: fichas sin IA con «¿Con qué competencia?», ajustes pequeños, informe de la XV legislatura, explicador «¿Quién decide qué?»… Ver «Prioridades» y 2.4–2.5 en `docs/BACKLOG.md`.
10. ~~Fichas sin IA (prioridad 1)~~ Hecho el 24/11/2026: `boe.extractos` copia del texto oficial el objeto, la entrada en vigor y el título competencial (paso `guardar`, campo `textos_oficiales`; recalcular con `python -m boe.guardar --textos`). La ficha muestra «Según la propia norma: …» en «¿Qué es?», «Desde cuándo (copiado de la norma)» si no hay dato de consolidada, y una pregunta nueva «¿Con qué competencia?». Van en `web/datos/normas/<id>.json`, no en la semana (habría pasado de 125 a 159 KB).
11. ~~Ajustes pequeños (prioridad 2)~~ Hecho el 24/11/2026: bienvenida («a quién afecta»), «Repositorio» y «Decisiones» corregidos (repositorio público y web en Pages), canal RSS `web/datos/feed.xml` (`exportar.canal_rss`). Decidido no enlazar a webs ajenas (sus resúmenes no están contrastados, muestran votos que aquí no se enseñan y son proyectos ajenos): solo fuentes oficiales.
12. ~~Índice ligero (preparación del informe de la XV, 2.4)~~ Hecho el 24/11/2026: `indice.json` de 73 a 31 KB y ya no crece con las ediciones (cada una, ~200 bytes; 160 ediciones serían ~32 KB). Lo que más ocupa ahora es la legislatura (27 KB, fija). Siguiente: descarga completa de la XV en `datos/` (decidido junto con la web, no aparte).
13. ~~Descarga de la XV~~ Hecha y fusionada (24/11/2026; la rama `datos/xv-completa` ya no existe): `python -m boe.guardar 2023-08-17 2026-08-24`, registro en `exploracion/descarga_xv.log`, revisión con `exploracion/revisar_descarga.py`. Pruebas previas: septiembre de 2023 (39 normas, Gobierno en funciones) y marzo de 2024 (81). A mitad: 3.094 normas, todas con texto.
14. Hecho mientras descargaba (24/11/2026, con pruebas; la entrada en vigor ya está en el informe, los tribunales aún no en la web): `boe.tribunales` (clasificador de decisiones judiciales: tribunal, tipo, decisión, quién promueve por categoría, norma afectada, suspensión del 161.2; 191 decisiones medidas) guardado al descargar; `boe.vigencia` (*vacatio legis*: 65,7 % al día siguiente, 13,1 % el mismo día, 8,9 % tras un plazo); sección `T` como «TC» en el gráfico por sección (`?v=2026-11-24n`); prueba con Hacienda: el Sankey de los Presupuestos es viable con su Excel consolidado. Prioridades nuevas: tribunales (4) y dinero público (5); ver `docs/BACKLOG.md`.
15. **Informe de la XV, primera parte** (24/11/2026): «La legislatura» empieza con «Quién decidió» (cuatro gráficos y la lista de leyes; `legislatura.js?v=2026-11-24o`, `estilos.css?v=2026-11-24o`). Falta «qué pasó después» (vida de la norma por tandas, tribunales).
16. **Guía y menos duplicados** (24/11/2026): menú con «Guía»; `?v=2026-11-24p`. Visto al revisar: la pieza de votaciones de la portada solo existe en semanas desde septiembre de 2026 (las convalidaciones semanales vienen de `boe.congreso`, que solo cubre las normas recientes; las de toda la XV están en `legislatura_xv.json`). ✅ Hecho el mismo día: `boe.congreso --desde 2023-08-17` (56 votaciones del Pleno con voto por grupos; `DIAS_PLAZO` 60 porque el plazo es en días hábiles) y `boe.tramitacion` (43 decretos-ley tramitados como proyecto de ley, todos «Caducado 04/11/2026»). `boe.legislatura` toma el resultado del acuerdo publicado en el BOE cuando existe (y el órgano, del texto de la resolución) y guarda la `discrepancia` si no coincide con el Congreso (RDL 8/2023: 171-171 en los datos abiertos, convalidado según el BOE). Cifras: 53 convalidados, 14 derogados, 5 sin votación (37–41/2026). **Tras una descarga grande, pasar también `congreso`, `tramitacion` y `legislatura --rehacer`.**
17. **Cómo votó cada grupo** (24/11/2026): `informe.votos_por_grupo` → `informe.json` (`votos_grupos`) → gráfico al 100 % y tabla en «La legislatura». Posición = mayoría del grupo («Dividido» si empatan); Mixto sin desglose por lista (listas de un diputado = historial individual). `?v=2026-11-24r`.
19. **Parte 2 del informe y gobernar sin Presupuestos** (24/11/2026, noche): `informe.tramitados_como_ley`,
    `informe.tribunales` (agrupa las normas recurridas por rango, número y fecha: el número solo mezclaba
    leyes autonómicas distintas) e `informe.sin_presupuestos` con `boe.presupuestos` (párrafos de la parte
    dispositiva que conceden créditos; sin sumar importes). La Action no reintenta las no consolidadas ni
    calcula el antes y el después de las antiguas (`versiones --desde`). Selector de semanas por año.
18. **Action protegida** (24/11/2026): `boe.principal` solo consulta la vida de las normas de los últimos 180 días y las que ya tienen vida (antes consultaba todas: con la XV completa habría sido más de 1 h cada domingo y habría cargado de golpe el antes y el después de las antiguas). `boe.consolidada --desde/--hasta` para las tandas.
