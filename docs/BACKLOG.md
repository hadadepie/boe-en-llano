# Backlog — El BOE en llano

Última actualización: 25/11/2026, noche. Hecho ese día: seguridad y privacidad de la web (1b, cerrado: CSP,
Chart.js propio, visitas con GoatCounter sin cookies, Action con permisos mínimos y dependencias con hash, ajustes de
GitHub de la autora); refresco por turnos de la vida de las normas en la Action; **vida de las normas de toda la XV**;
*vacatio legis* por ministerio (2.6); «Qué hizo el Senado con las leyes» (2.7); votación de cada ley en el Congreso con
el voto por grupo (2.3b y 2.7); sentencias del Constitucional de la sección `T` (prioridad 4, 3.4); estado del arte de
lo nuevo y, con él, índice con subsecciones en «La legislatura», la votación de las leyes junto al Senado y el recuadro
«Más allá de la semana» en la portada; **Sankey de los Presupuestos** con datos de Hacienda (prioridad 5, pieza 1, en
«La legislatura» de momento) e idea nueva 3.9 (presupuestado frente a gastado, llamada de prueba hecha). Pausada la
idea de las ampliaciones del plazo de enmiendas (2.6). Recibida y contrastada con la web una revisión externa (1c):
corregidos los textos desfasados y añadidos los avisos de lectura (prioridad C). **Reorganizada la web** (prioridad 7):
portada más ligera, «La legislatura» partida en tres páginas (`legislatura.html`, `dinero.html`, `tribunales.html`),
menú de seis páginas y «Cómo leer el BOE en llano». Siguiente (orden de `docs/ESTADO.md`): publicar y comprobar la
Action del 29/11/2026, «normas modificadas o derogadas» (prioridad 3), votaciones de las 2 reformas de la Constitución,
importes de los créditos (5) y presupuestado frente a gastado (3.9, en `dinero.html`).

## Prioridades (24/11/2026, confirmadas por la autora)

**Enfoque:** resumir el BOE día a día ya lo hacen al menos cinco webs, y las
votaciones del Congreso por grupo, otras dos (ver «Estado del arte general»). Lo
que no hace nadie: **lo que el Estado decide sin votación**, **qué pasa después con
cada norma**, **con qué competencia se dicta** y todo con método y código abiertos.
Por eso la apuesta es **informes y gráficos guiados** (pregunta → gráfico → frase de
lectura → normas de ejemplo) y **competencias**, sin repetir lo que ya hacen otras
webs. Decisión (24/11/2026): **no se enlaza a webs ajenas**, solo a fuentes oficiales.

| # | Qué | Dónde está | Tamaño | Por qué en este orden |
|---|---|---|---|---|
| ✅ S | (25/11/2026: hecho y publicado; Chart.js propio, visitas con GoatCounter y ajustes de GitHub de la autora) **Seguridad y privacidad de la web** | 1b | Corto–medio | La web es estática y ya está bien encaminada (ver 1b), pero hay huecos baratos de cerrar en la Action, en los ajustes del repositorio y en la página. Va antes que lo nuevo: la web ya es pública. |
| ✅ C | (25/11/2026: hechos los textos desfasados de 1c-A y las filas «Alta» de 1c-C) **Textos desfasados de la web y vocabulario** («Lo que aún no está», fuentes, «¿Se votó?», «finales de agosto de 2026», «43 veces») y avisos de lectura (barras, «¿Se votó?», fechas de la ficha) | 1c (A y filas «Alta» de C) | Corto | Afectan a lo que el lector entiende como cierto: van antes que lo nuevo y que la reorganización (7). |
| 1 | ✅ (24/11/2026) **Fichas sin IA**, con **«¿Con qué competencia?»** | 1 y 2.5 (pieza 1) | Corto | Las 343 fichas están «pendiente»: es lo más débil de la web. Todo lo que se añade es texto oficial. |
| 2 | ✅ (24/11/2026) **Ajustes pequeños**: bienvenida, `ESTADO.md`, RSS (enlaces a otras webs: descartado) | 1 | Corto | Baratos; el RSS resuelve parte de «quien no entra cada semana». |
| ✅ 3 | (26/11/2026: **hecho** «Qué pasó después: normas cambiadas o derogadas», `informe.cambios_despues`, con «Las leyes que más cambian» de 2.6; campo `cambia` en cada norma y `boe.citadas`) (24/11/2026: descarga hecha; publicados «Quién decidió» —por vía, mes a mes, tema, entrada en vigor, leyes—, «Cómo votó cada grupo» y los 43 decretos-ley tramitados como ley; 25/11/2026: entrada en vigor por ministerio, cómo votó cada grupo las leyes y vida de las normas de toda la XV; **siguiente**: «normas modificadas o derogadas») **Informe «La XV legislatura: quién decidió y qué pasó después»** | 2.4 | Medio (descarga de 1–2 h, avisando antes) | Oportuno: Cortes disueltas desde el 06/10/2026; las nuevas se constituyen el 23/12/2026. |
| 4 | ✅ (24/11/2026: «Qué dijeron los tribunales» con la sección I; 25/11/2026: sentencias del Constitucional de la sección `T`, ver 3.4) **Los tribunales y las normas**: qué normas se recurren o anulan, qué tribunal, quién recurre y cuánto tarda | 3.4 | Medio | Completa el informe: este cuenta quién decidió; aquello, quién lo corrigió después. Los datos llegan con la descarga de la XV (sección I) más la sección `T`. |
| 5 | 🔄 (24/11/2026: hecha la pieza 2, «Gobernar sin Presupuestos», en «La legislatura» y en la ficha de cada norma, sin importes. 25/11/2026: hecha la pieza 1, el Sankey de los Presupuestos, en «La legislatura» de momento; idea nueva 3.9, presupuestado frente a gastado) **El dinero público: de dónde viene y a dónde va** (Sankey de los Presupuestos, gobernar sin presupuestos, subvenciones directas) | 3.2 | Grande (fuente nueva: Hacienda) | Pregunta muy oída («cuesta aprobar los Presupuestos») y sin respuesta gráfica de origen → destino público o privado; «gobernar sin presupuestos» se mide con el BOE que ya tenemos. |
| 6 | **Explicador «¿Quién decide qué?»** (Estado, comunidades, ayuntamientos por tema) | 2.5 (pieza 2) | Medio (texto a mano, revisión de la autora) | Da contexto a la pieza 1 y al informe. |
| ✅ 7 | (25/11/2026, noche: **hecho**. Portada con titulares, «¿Quién decidió?», seguimiento y los informes enlazados arriba; embudo, mosaico y «La semana en datos» a «Explorar»; «La legislatura» partida en tres páginas —`legislatura.html`, `dinero.html`, `tribunales.html`, con `informe.js` común y redirección de las anclas antiguas—; menú de seis páginas; pie con método, límites, correcciones y avisos de errores; «Cómo se calcula» en cada bloque; la Guía pasa a ser «Cómo leer el BOE en llano» con preguntas frecuentes y el recorrido del RDL 6/2023) (24/11/2026: hecha la `guia.html` y quitados dos duplicados de Explorar; falta aligerar la portada. 25/11/2026: la autora pide **repensar la organización de toda la web** cuando acaben Hacienda y la vida de 2026: el recuadro «Más allá de la semana» queda al final de la columna derecha de la portada, sin verse sin bajar; «La legislatura» ya tiene 6 bloques y 18 subsecciones en una sola página; decidir qué va en portada, qué en «La legislatura» y si el dinero público y los tribunales merecen página propia. La autora, 25/11/2026: el Sankey de los Presupuestos (publicado de momento en «La legislatura», tras «Gobernar sin Presupuestos») probablemente merece un apartado propio, junto con «Gobernar sin Presupuestos», presupuestado frente a gastado (3.9) y las subvenciones; decidirlo en esta reorganización) **Portada más ligera, organización de la web** y página **«Cómo leer el BOE en llano»** | 0 | Medio | Con el informe y el explicador hechos, la portada puede enlazarlos en vez de explicarlo todo. **Siguiente tras Hacienda y la vida de 2026.** |
| 8 | **Qué competencias usa el Estado y cuáles acaban en conflicto** | 2.5 (pieza 3), 3.4 | Medio | Cruza el título competencial con el Boletín de Conflictividad y lo que ya clasifique la prioridad 4 (tribunales). |
| 9 | Qué hace el Congreso, **fase B** (de dónde vienen las leyes) | 2.2 | Medio | La fase A se recorta (ver 2.1): ya la cubren otros. |
| 10 | Promesas frente a hechos (3.3) | 3.3 | Medio | Fuente oficial y pregunta que casi nadie contesta con datos. |
| 11 | Empleo público (3.6) | 3.6 | Corto–medio | El más barato: los datos ya están. |
| 12 | Convenios entre administraciones (3.7) | 3.7 | Grande | Enlaza con el dinero público (prioridad 5). |
| 13 | Directivas europeas (3.5) y consultas públicas (3.8) | 3.5, 3.8 | Grande | |
| 14 | Comunidad de Madrid (3.1) | 3.1 | El más grande | Mejor cuando la cadena esté madura; enlaza con competencias. |
| 15 | 🔄 (24/11/2026: conflictos ante el Constitucional; 25/11/2026: qué hizo con cada ley y qué aceptó después el Congreso, y votación de cada ley en el Congreso; faltan las iniciativas que nacen en el Senado y las reformas de la Constitución) **El Senado: cómo interactúa y en qué influye** | 2.7 | Medio (fuente nueva: datos abiertos del Senado) | Ya tenemos 14 conflictos entre órganos constitucionales en el BOE, 12 promovidos por el Senado. Completa «quién decidió»: qué cambió o frenó la segunda cámara. |

Las demás mejoras cortas de la sección 1 se hacen cuando se toque el código afectado.

**Pendientes técnicos (24/11/2026), no son ideas nuevas:**
- ✅ (26/11/2026) **«Normas modificadas o derogadas»** (prioridad 3): `informe.cambios_despues` (de las 484 normas del
  Estado consolidadas, 112 cambiadas o derogadas después, 12 enteras; 10 decretos-ley derogados por el Congreso entre
  las consolidadas, de 14; primer cambio, mediana 275 días; 49 de 305 se cambiaron en su primer año; el RD 1009/2023 de
  estructura de los ministerios, 29 normas distintas) y `informe.anteriores_cambiadas` (1.864 normas anteriores cambiadas
  por 992 normas del Estado; la más tocada, la Ley 35/2006 del IRPF, 22; la más antigua, la Ley del Notariado de 1862).
  **Sorpresas:** la mitad de las leyes (17 de 36) y 33 de 76 decretos-ley no los consolida el BOE (solo modifican otras
  normas: comprobado con 404 en la API), así que su «vida» no existe; por eso lo que cambió la legislatura sale del
  análisis del diario (`<anteriores>` del XML de cada norma), guardado en el campo nuevo `cambia` (`guardar --cambia`,
  y `guardar` lo pone en las normas nuevas; 137 referencias «---» sin identificador, descartadas). Títulos de las
  anteriores: `boe.citadas` → `datos/normas_citadas.json` (XML del diario; corre en la Action, solo las que falten).
  Las resoluciones del Congreso que publican la derogación de un decreto-ley «dejan sin efecto» lo que este cambió:
  no cuentan como normas que cambian. **Posible ampliación:** «leyes escoba» (2.6) con el mismo campo `cambia`.
- ✅ **Vida de la norma de las normas antiguas** (`python -m boe.consolidada --desde … --hasta …`, por
  tandas, sin antes y después): hechas 2023 (276: 50 consolidadas), 2024 (1.147: 207), 2025 (1.258: 172), 2026-S1
  (577: 110) y las normas desde el 26/08/2026; del 01/07 al 25/08/2026 (173: 23) ya estaba por la ventana semanal: **toda la XV completa**. `boe.consolidada` reintenta
  ante cortes del BOE (25/11/2026). Es la base de «normas modificadas o derogadas»
  (prioridad 3). ✅ La Action solo consulta los últimos 180 días y las consolidadas que ya tienen vida (no
  reintenta las no consolidadas) y no calcula el antes y el después de las antiguas. ✅ (25/11/2026) Las
  consolidadas antiguas se refrescan por turnos: una de cada 4 cada domingo (cada una, cada 4 semanas).
  **Posible mejora:** la ventana de 180 días reconsulta también las ~480 no consolidadas cada domingo; si el
  BOE consolida casi siempre en pocas semanas, se podría acortar su ventana (medirlo antes).
- **Tras una descarga grande**, pasar también `boe.congreso`, `boe.tramitacion` y `boe.legislatura --rehacer`
  (anotado en `docs/ESTADO.md`).
- 🔄 **Votaciones de las 2 reformas de la Constitución** (arts. 49 y 69.3): código hecho (`c5e12e0`, ver 2.7); falta
  bajar las votaciones (congreso.es respondía 403 el 26/11/2026).
- **Comprobar la Action del domingo 29/11/2026**: primera con el refresco por turnos, `boe.senado`,
  `boe.votaciones_leyes` y `boe.sentencias_tc` (deberían hacer muy pocas peticiones: solo lo nuevo) y la primera que
  exporta `presupuestos.json` para el Sankey (`boe.hacienda` no corre en la Action: se lanza a mano cuando Hacienda
  publique una edición nueva).
- **Publicar el Sankey**: subido a `main` después de la última publicación (25/11/2026); sale con «Solo publicar»
  o el domingo.
- **Revisión de legibilidad con el plugin Design (26/11/2026, sesión aparte; informes en las notas compartidas de la
  sesión: `revision-legibilidad-creditos.md` y `revision-legibilidad-web-completa.md`).** Hecho: la ficha de los
  créditos (lista con 3 o más, coletilla una vez, 2 decimales, «Sin cifra aquí», etiquetas de destino), textos que
  decían «no se suman» (`como.html`, `dinero.js`) y el fallo de `informe.tribunales` (contaba 3 correcciones de
  errores: 271 → 268). ✅ También (26/11/2026): las dos cifras que desconciertan, explicadas (124 sentencias → 199
  decisiones, por norma juzgada; 2.380 frente a 2.987, sin internacionales ni tribunales); titular de portada a 22 px
  en móvil con «Por qué, según su preámbulo» visible; jerga de la ficha plegada (`RELACION_LEGIBLE` en `web/app.js`:
  «Se modifica» → «La cambia otra norma», «Se dicta de conformidad» → «Otra norma la desarrolla o aplica»…; «Se
  declara» se deja literal; competencia con más de 3 artículos: cuántos y qué es el 149.1). **Pendiente:** (1) la
  lista de decretos-ley va un día por detrás (faltan los RDL 42–45/2026): regenerar `boe.legislatura` cuando el
  Congreso responda; (2) menores: entradillas que repiten el índice, etiquetas mezcladas en «Correcciones»,
  «Cómo leerla» → «Guía»; (3) idea: los créditos en su propia pregunta («¿Cuánto dinero autoriza?»).
- ⚠️ **RDL 8/2023: el Congreso dice empate y el BOE, convalidación (visto el 26/11/2026).** Nuestros datos
  (`datos/congreso/convalidaciones.json`, votación 4 del 10/01/2024) dan 171 a 171 y lo cuentan como «derogado»;
  el índice de votaciones de ese día no trae otra votación del expediente 130/000003, pero la legislación
  consolidada del BOE registra «Se publica acuerdo de convalidación» (12/01/2024). Investigar antes de tocar nada:
  qué publicó el BOE ese día (sección I), cómo trata `boe.congreso` un empate (hoy, «derogado» por defecto) y si hay
  más empates. Si el BOE manda, corregir el dato y explicarlo en «Correcciones».
- 🔄 **Importes de los créditos** (prioridad 5, pieza 2): extraer el importe de cada párrafo de `creditos`
  con su unidad y revisarlos a mano antes de publicar una suma; decir siempre «concedido», no «gastado».
  - ✅ **Hecho (26/11/2026):** `boe/importes_creditos.py` (a mano, no en la Action: lee el XML de `datos/crudo/normas/`)
    → `datos/presupuestos/creditos.json` y la hoja `datos/presupuestos/revision_creditos.csv` («;», UTF-8 con BOM), con
    tres columnas para la autora que se conservan al regenerarla. Exploración en `exploracion/presupuestos/importes_creditos.py`.
  - **Medido:** 155 créditos en 51 normas (no 30: los datos han crecido). 130 estatales en 31 normas y 25 autonómicos
    (Cataluña, Navarra, Aragón, Castilla-La Mancha, Comunitat Valenciana: sus propios presupuestos, no dinero del
    Estado). De los estatales, 87 en leyes o decretos-ley convalidados, 12 en decretos-ley **derogados** (8/2023,
    9/2024, 7/2025, 16/2025 y 2/2026) y 31 en decretos-ley posteriores a la disolución, sin convalidación en los datos
    abiertos (Diputación Permanente). Importe propuesto con reglas en 146 de 155; 9 quedan para la autora. Solo 45
    estatales convalidados tienen propuesta y ningún aviso.
  - **Sorpresas:** (1) el párrafo de financiación («se financiará con el Fondo de Contingencia por…») repite el importe:
    sumar todo el bloque contaría el doble o el triple; el bloque acaba en el primer párrafo que no es apartado ni
    tabla. (2) Las entregas a cuenta a comunidades y entidades locales van en tablas (miles de euros), a veces sin
    cabecera; las leyes forales navarras traen una segunda tabla con la financiación, que no se suma. (3) El RDL 2/2026
    repite las entregas a cuenta del 16/2025, y los dos se derogaron: no contar dos veces ni contar como vigente lo
    derogado (aviso «el mismo importe en…»). (4) «Tu primer hogar» (RDL 29/2026): 10.000 M€ en el capítulo 8, activos
    financieros (préstamos), no gasto; aviso propio. (5) Dos apartados de 15 M€ en el RDL 5/2026: quitar repetidos
    los perdería; solo se unen importes cuando todos son iguales. (6) Algunos son para el presupuesto de 2027 o para
    obligaciones de ejercicios anteriores (avisos).
  - ✅ **Página de revisión (26/11/2026, a petición de la autora: la hoja era difícil de leer y no decía a dónde va el
    dinero):** `boe/pagina_creditos.py` → `datos/presupuestos/revision_creditos.html` (fuera de la web). Cada crédito
    del Estado, con clave C-001…, en una línea: norma, importe, **a dónde va** (clasificación económica del concepto de
    la aplicación presupuestaria: capítulos 4 y 7, a quién se transfiere; los demás, en qué se gasta; reconocido en
    125 de 130), ministerio y para qué (nombre oficial de la aplicación). Resumen por destino y situación de la norma,
    marcado «sin revisar». 25 dudosos con el motivo en castellano. El aviso de importe repetido exige ahora también
    texto casi igual (las cifras redondas coinciden mucho: 500, 10, 3 M€ en normas sin relación). Arreglado: dos
    artículos que empiezan igual (RDL 7/2026, arts. 57 y 60) se asignaban al mismo párrafo.
  - ✅ **Decidido y hecho (26/11/2026, la autora):** nada de totales (demasiados casos: derogados, repetidos,
    préstamos, entregas a cuenta; un total mal entendido haría más daño que ninguno). Solo la cifra de cada norma
    en su ficha, debajo del párrafo copiado, con «a dónde va» según la partida, y solo si es segura (`cifra_segura`:
    103 de 130 estatales; la revisión de la autora manda). `exportar.enlazar_importes_creditos`, `lineaImporteCredito`
    en `web/app.js`. La partida de otro organismo del Estado (40, 41, 43; p. ej. 2.121 M€ al FEGA en el RDL 5/2026)
    se dice «organismos del Estado, que lo gestionan o reparten». «La legislatura» sigue contando normas, no euros.
  - **Ya no pendiente (se queda como idea):** qué se suma (¿solo estatales convalidados?, ¿aparte los
    derogados y los de capítulo 8?) y dónde se muestra (ficha de cada norma y «Gobernar sin Presupuestos»).

**Piezas candidatas para los informes (2.6):** cinco preguntas más que salen de datos que ya
tenemos o casi; las recomendadas para acompañar el informe de la XV son la *vacatio legis*
(datos ya extraídos) y los mandatos pendientes (la más novedosa).

## Estado del arte general (24/11/2026)

**Resúmenes del BOE (todos diarios, con IA salvo uno que no lo dice):**

| Web | Qué hace | Votos | Qué pasó después | Código / método |
|---|---|---|---|---|
| [Agente BOE](https://agenteboe.com/) | Sección I, impacto 1–5, avisos por Telegram | No | No | No |
| [BOE explicado](https://boeexplicado.es/) | Normas, convenios y ayudas; marca la IA | No | Solo fecha de actualización | General |
| [BOE en Lenguaje Claro](https://boeenlenguajeclaro.es/) | «Qué cambia, a quién, desde cuándo», boletín por correo | No | No | No |
| [Hoy IA BOE](https://hoyaiboe.com/) | Resumen diario y boletín | No | No | No |
| BOEtracker | IA más reglas; pide cuenta de Google | No | No | No |

**Congreso y decretos-ley:**
- [El Congreso en tu mano](https://elcongresoentumano.es/): votaciones del Pleno de la XV
  (y X–XIV con menos detalle), voto por grupo, unas 87 fichas de leyes y decretos-ley
  con enlace al BOE, alertas. Resúmenes marcados como «interpretación automática, sin
  contrastar»; sin código publicado. (No se enlaza: decisión del 24/11/2026.)
- [El Congreso en datos (Bocal)](https://espanaendatos.bocal.online/congreso/): gráficos
  de coincidencia entre partidos, quién gana las votaciones, decretos-ley derogados;
  análisis puntual con datos descargables.
- [Electomanía](https://electomania.es/radiografia-del-decreto-ley-en-espana-747-aprobados-16-rechazados-13-en-el-ultimo-gobierno/):
  radiografía de los decretos-ley 1977–2026 por legislatura (artículo único).
- CEOE, «Producción normativa» (anual): cuántas normas y páginas se publican.

**Otros:** *El BOE nuestro de cada día* (Civio, desde 2012, periodismo) y
[BOE-XSUM](https://arxiv.org/html/2509.24908v1) (UNED): 3.648 normas del BOE con su
resumen en lenguaje claro de máximo 280 caracteres, útil para medir un modelo de IA.

**Actualización (24/11/2026, noche), para lo publicado hoy en «La legislatura»:**
- *Decretos-ley tramitados como ley:* la prensa los llama «congelados» (ampliaciones semanales del plazo
  de enmiendas, sin límite en el Reglamento) con cifras sueltas y de fechas distintas; el Tribunal
  Constitucional resolvió en 2026 un recurso de diputados contra una 71.ª ampliación consecutiva (acuerdos
  de 2022). No se ha encontrado un recuento de toda la XV con fase y días como el nuestro.
- *Gobernar sin Presupuestos:* la AIReF y la prensa económica analizan el uso del Fondo de Contingencia y
  de las modificaciones presupuestarias durante la prórroga, en cifras globales. Nadie lista norma a norma
  qué decretos-ley conceden créditos extraordinarios o suplementos, ni los cruza con las órdenes de
  elaboración y el conflicto del Senado.
- *Tribunales:* sigue sin haber un seguimiento norma a norma (ver 3.4).
- *Senado:* ver 2.7.

**Actualización (25/11/2026, noche), para lo publicado ese día:**
- **Webs nuevas con balance de la XV:** *Es la hora de la verdad* (sin autoría; datos abiertos del Congreso y BOE;
  resúmenes con IA; CC BY 4.0; sin código): 29 leyes con votación final, 42 decretos-ley convalidados y 13 derogados,
  posición de cada grupo en las votaciones decisivas, y las de enmiendas y veto del Senado como votaciones del
  Congreso. **No tiene datos del Senado**: 12 de sus leyes van «sin datos del Senado ni del BOE». *Demócrata*
  (herramienta del especial 29N): 132 iniciativas votadas en la XV con la posición de cada grupo, matriz de
  coincidencias y CSV; sin código.
- **Votación de cada ley por grupo:** ya la dan al menos tres webs (*El Congreso en tu mano*, *Es la hora de la
  verdad*, *Demócrata*). Lo nuestro no es nuevo; aporta solo al ir en la ficha junto a lo que hizo el Senado y la
  norma del BOE. **No ampliarlo** (nada de matrices de coincidencia).
- **Qué hizo el Senado con cada ley y qué aceptó después el Congreso:** no se ha encontrado en ninguna web. Novedad.
- **Sentencias del Constitucional norma a norma:** hay datos globales (memoria anual del Tribunal) y los informes
  mensuales y el Boletín de Conflictividad del Ministerio de Política Territorial (solo Estado–comunidades, no los
  recursos de diputados). Nadie publica, norma a norma, qué se recurrió, qué se resolvió, con qué resultado y en
  cuánto tiempo. Novedad.
- ***Vacatio legis* por ministerio:** solo doctrina (la entrada en vigor al día siguiente resta seguridad jurídica);
  ningún recuento. Novedad.
- **Accesibilidad de lo nuevo en la web (revisado en la web publicada):** «Cómo votó cada grupo las leyes» queda
  dentro de «Quién decidió», entre la entrada en vigor por ministerio y los decretos-ley, sin entrada en el índice
  de la página: cuesta encontrarlo. «Qué decidió el Tribunal Constitucional» está bien situado (en «Los
  tribunales») pero tampoco tiene entrada propia. La portada no anuncia ninguna novedad (solo enlaza «La
  legislatura»). ✅ (25/11/2026, noche) Índice con las subsecciones, la votación de las leyes junto al Senado
  («Las leyes: votación y Senado») y, en la portada, un recuadro fijo «Más allá de la semana» con tres enlaces a
  «La legislatura» (sin fecha, para que no envejezca).

**Hueco:** ninguna sigue lo que pasa con las normas aprobadas (solo las derogaciones
de decretos-ley), ninguna mira lo que se decide sin votar, ninguna dice con qué
competencia se dicta cada norma y ninguna publica su código.

## Cómo se trabaja cada propuesta

Nada pasa a programarse sin estos pasos, en este orden:

1. **Estado del arte.** ¿Existe ya? ¿Quién lo hace y cómo? ¿Qué aportaríamos?
   Si alguien lo hace bien, mejor no repetirlo (sin enlazar a webs ajenas: solo
   fuentes oficiales, decisión del 24/11/2026).
2. **Llamada de prueba a la fuente.** Ver los datos reales, no los que se
   suponen: formato, cobertura, huecos y cuánto cuesta descargarlos.
3. **Prototipo mínimo** en una rama, con datos reales y una sola pregunta.
4. **Decidir:** seguir, recortar o descartar, y anotarlo aquí con el motivo.

Cada propuesta tiene que poder responder con datos oficiales y sin rankings de
personas (reglas de `CLAUDE.md`). **Criterio para parar:** si la pregunta solo
se puede contestar con datos que no son públicos, o con interpretaciones que
la web no puede justificar, se dice en la web («qué no cubrimos») y no se
fuerza.

Estados: 💡 idea · 🔎 estado del arte hecho · 🧪 prototipo · ⏸ aparcado.

---

## 0. Diseño para el público general (casi todo hecho; quedan los «más grandes»)

Revisión de la web de `main` del 24/11/2026 (escritorio y móvil). La base
funciona; faltan cosas básicas para que la gente llegue, entienda la página y la
comparta, y algunos bloques son densos. Hacerlo en una rama y revisar antes de subir.

**Lo que se vio:**
- Al compartir no se ve nada: no hay icono ni vista previa (título, descripción,
  imagen); el enlace a una ficha sale con el título genérico de la web.
- Quien entra por primera vez no sabe qué está viendo: el lema es pequeño y
  «Te afecta a ti», el embudo o el mosaico no se explican hasta el método.
- «Qué ha pasado con normas anteriores» es largo y repetitivo (semana 47: 9
  tarjetas, 7 con la misma frase de la Diputación Permanente).
- Todo tiene el mismo peso visual: títulos de sección iguales, mucho gris, poco
  color; la noticia principal solo se distingue por el tamaño.
- No hay buscador; en móvil, al bajar se pierde la navegación.

**Paquete rápido ✅ hecho y fusionado en `main` el 24/11/2026** (y, con él, el resto de la sección salvo los «más grandes»):
1. **Icono y vista previa al compartir:** icono propio, metadatos para redes y
   mensajería (título, descripción, imagen) y el título de la pestaña cambia al
   de la norma al abrir su ficha.
2. **Botón «Compartir» en la ficha:** menú de compartir del móvil o copiar enlace.
3. **Bienvenida de una línea** para quien entra por primera vez («Cada semana, lo
   que publica el BOE explicado: qué te afecta, por qué se aprueba y quién lo
   apoyó. Cómo leer esta página →»); se cierra y no vuelve (preferencia en el
   navegador).
4. **Seguimiento compacto:** agrupar lo repetido («La Diputación Permanente
   convalidó 7 decretos-ley» y la lista de títulos) y como mucho 4 elementos
   más «Ver todos».
5. **Iconos por tema** junto a cada antetítulo y en el mosaico (colección libre,
   p. ej. Lucide, licencia ISC).

   *Límite conocido:* la vista previa de una ficha concreta sigue siendo la genérica
   de la web (Pages es estático y los rastreadores de redes no ejecutan JS); el
   título de la pestaña y el texto del botón «Compartir» sí llevan el titular. Para
   una vista previa por norma haría falta generar una página HTML por norma en
   `boe.exportar`.

**Mejoras medias:**
- ✅ (24/11/2026, fusionado) **Buscador de normas** por palabras del titular en todas las semanas (`web/datos/buscar.json`: 31 KB sin comprimir y 7 KB comprimido para 200 normas, unos 16 KB más por cada 100; se descarga solo al escribir). Solo en la portada; busca en el titular corto, no en el título oficial ni en el preámbulo. Si el índice crece demasiado (más de ~1 MB), partirlo por año.
- ✅ (24/11/2026, fusionado) **Cabecera compacta fija** al bajar, con el selector de semana.
- ✅ (misma rama) **Más jerarquía visual:** franja del color del tema en la noticia principal,
  más aire entre secciones, menos gris.
- ✅ (24/11/2026, fusionado) **Revisar «Te afecta a ti»:** renombrado a «Afecta a mucha gente» en toda la web, con nota de que es una estimación por reglas. Texto original del punto: promete mucho para una clasificación por reglas;
  «Afecta a mucha gente» es más exacto (neutralidad y honestidad).

**Más grandes:**
- ✅ (25/11/2026) **Portada más ligera** (prioridad 7): hoy tiene siete bloques (titulares, embudo,
  «¿Quién decidió?», mosaico, seguimiento, «La semana en datos», gestión interna) y
  pide entender mucho de golpe. Dejar tres (titulares, «¿Quién decidió?» y qué ha
  pasado con normas anteriores) y enlazar los informes y el explicador de
  competencias. Lo demás, a «Explorar».
- ✅ (25/11/2026, en `guia.html`) **Página «Cómo leer el BOE en llano»** para principiantes, con ejemplos (el
  «Cómo se ha hecho» actual es método técnico). Hoy «Cómo leer esta página» de la
  bienvenida lleva al método técnico.
- **Boletín semanal por correo o RSS** para quien no entra cada semana.
- **Tipografía propia:** fuente libre alojada en la web, sin servicios externos.

---

## 1. Mejoras de la web actual (cortas)

| Mejora | Por qué | Notas |
|---|---|---|
| ✅ (24/11/2026) **Fichas sin IA** (prioridad 1) | Hecho: `boe/extractos.py` copia del texto oficial el objeto (132 de 343), la entrada en vigor (240) y el título competencial (148), guardados en `textos_oficiales` al descargar (`python -m boe.guardar --textos` los recalcula) y exportados en `normas/<id>.json`. Las fichas siguen «pendiente» de resumen. Texto original: las 343 fichas están «pendiente»: la web promete «explicado» y solo da el titular corto y el preámbulo. | Rellenar con lo que ya es oficial: «¿Qué es?» con el objeto del preámbulo, «¿Desde cuándo?» con la entrada en vigor de consolidada (o `fecha_vigencia`), materias, y **«¿Con qué competencia?»** (ver 2.5). Sin inventar nada: lo que no esté, «pendiente». |
| ✅ (24/11/2026) **Bienvenida: «qué te afecta»** (prioridad 2) | La bienvenida de la portada aún dice «qué te afecta»; el resto de la web ya usa «Afecta a mucha gente». | Cambiar el texto en `web/index.html`. |
| ✅ (24/11/2026) **Contradicción en `docs/ESTADO.md`** (prioridad 2): era cierto lo público (repositorio y Pages responden). | «Decisiones tomadas» dice repositorio privado y Pages desactivado; «Próximos pasos» (5) dice web publicada y repositorio público. | Comprobar cuál es cierto y dejar una sola versión. |
| ❌ (24/11/2026, decisión de la autora: **no enlazar**) **Enlazar a quien ya lo hace** (prioridad 2) | Para las votaciones de leyes y el resumen diario hay webs que lo hacen (ver «Estado del arte general»). | Dudas (24/11/2026): sus resúmenes son automáticos sin contrastar (choca con «solo fuentes oficiales»), muestran votos que aquí no se enseñan y son proyectos ajenos. Propuesta: en fichas y «La legislatura», enlace a la fuente oficial (votaciones del Congreso); en «Cómo se ha hecho», un apartado neutro «Otras webs sobre el BOE y el Congreso» que diga qué hace cada una, sin recomendarlas. |
| ✅ **Rellenar el hueco S42–S46** (24/11/2026) | Faltan cinco semanas (oct–nov 2026): sin edición, su seguimiento no sale en ninguna portada y los gráficos de evolución tendrían un agujero. | Lo más importante de esta lista. Hecho: no era un fallo de la Action (solo existe desde el 22–23/11): se habían bajado dos tandas locales y quedó sin bajar del 12/10 al 14/11. Se lanzó `boe.principal --desde 2026-10-12 --hasta 2026-11-14` sin IA: +30 días y +143 normas, 14 ediciones en total. Pendiente: sus fichas siguen «pendiente» como todas. |
| ✅ **Portada con la última semana completa** (24/11/2026) | Los lunes la edición en curso tiene 1–2 normas y la portada queda casi vacía. | Hecho: se abre la semana anterior mientras la en curso tenga menos de 3 días con datos (`DIAS_MINIMOS_EDICION` en `app.js`); un aviso con botón lleva a la en curso. |
| **«Derogado/modificado después» en semanas antiguas** | Complemento del bloque de seguimiento: quien mira una semana pasada ve el aviso en el mosaico y las listas. | Datos ya disponibles (vida de la norma y votaciones). |
| **Pieza de «La semana en datos» y seguimiento** | «7 convalidados» y la lista de seguimiento cuentan lo mismo. | Decidir si la pieza sobra. |
| **Mosaico (portada) y matriz (Explorar)** | Muestran la misma información de dos formas. | Esperar a usar la web un tiempo; si molesta, la matriz puede ser el mosaico con filtro. |
| **Legislatura fuera de `indice.json`** | Tras el índice ligero (24/11/2026) es lo que más ocupa: 27 de 31 KB, y la portada no lo necesita. | Un `legislatura.json` que solo cargue su página y la ficha de un RDL. |
| **Detalles técnicos de la revisión** | `escribir()` borra `web/datos/` antes de escribir; la semana lleva campos que solo usa la ficha; `cache: "no-cache"` en todos los JSON. | Ganancias pequeñas; hacerlas cuando se toque `exportar`. |
| **Modelo de IA mejor para las fichas** | Todas las fichas siguen pendientes (gemma3:4b no supera el validador). | Probar un modelo más capaz sin coste; el validador ya existe. |
| **Partidos dentro de coaliciones** | La lista electoral no distingue partidos dentro de una coalición. | Tabla manual con fuente para cada caso. |
| **Decretos-ley votados por la Diputación Permanente** | El filtro «¿Se votó?» los deja en «pendiente o sin datos» aunque el BOE publique su acuerdo. | `boe.legislatura.acuerdos_boe` ya los conoce: marcarlos como votados (sin cifras). |
| ✅ (24/11/2026: «TC. Sentencias del Tribunal Constitucional», al final de `SECCIONES_WEB` para no cambiar los colores; color `--s7`) **Sección `T` del gráfico por sección** | El BOE trae una sección `T` (Tribunal Constitucional) que `exportar` no conoce: avisa y no la dibuja. | Añadirla a `SECCIONES_WEB` o agruparla; enlaza con 3.4. |
| **Comprobar `buscar.json` en la Action** | El buscador depende de que el despliegue genere `web/datos/buscar.json`. | Lanzar «solo publicar» y probar «vivienda» en la web publicada. |
| **Seguimiento vacío en S42–S45** | Tras rellenar el hueco, esas semanas salen sin «qué ha pasado con normas anteriores». | Comprobar si es real o si falta consolidada/votaciones. |
| **Fichas de las 143 normas nuevas (S42–S46)** | Siguen «pendiente» como todas. | Depende de «Modelo de IA mejor». |
| ✅ (24/11/2026) **Canal RSS** (prioridad 2): `web/datos/feed.xml`, 50 últimas normas con objeto literal o título oficial; enlace al pie y `<link rel=alternate>`. | Seguir la web sin entrar. | Barato: un `feed.xml` generado en `exportar`. |

---

## 1b. Seguridad y privacidad de la web ✅ (25/11/2026)

**Hecho el 25/11/2026** (pruebas en `tests/test_seguridad.py`):
- **Action:** `permissions: contents: read` global; `contents: write` solo en `actualizar`, `pages: write` e
  `id-token: write` solo en `publicar`; las 5 acciones fijadas por SHA con la versión en comentario;
  `.github/dependabot.yml` (acciones, mensual); `pip install --require-hashes -r requirements-ci.txt`
  (11 paquetes con todos sus hashes de PyPI, generado por `herramientas/bloquear.py`; la prueba falla si
  `requirements.txt` cambia sin regenerarlo). Los *secrets* de IA ya solo llegaban a su paso.
- **Enlaces:** `enlaceSeguro()` en `el()` (`app.js`): un `href` solo va a la propia web o, por https, a
  boe.es/congreso.es; si no, se queda sin href y avisa en consola. Prueba con Node y otra que recorre
  `web/datos/*.json` (todas las URL de los datos ya cumplían).
- **CSP por `<meta>`** en los 5 HTML (`script-src 'self' https://cdn.jsdelivr.net/npm/chart.js@4.4.1/`,
  `style-src 'self'`, `object-src 'none'`, `base-uri 'self'`…) y `referrer`. Vista previa: consola limpia,
  gráficos y fichas bien; bloquea scripts en línea, ajenos y `eval`.
- **Descargas:** ya eran todas https a fuentes oficiales y sin `verify=False`; ahora lo comprueba una prueba.
- **`SECURITY.md`** (avisos privados de GitHub) y «Seguridad y privacidad» en «Cómo se ha hecho».

- **Chart.js propio** (25/11/2026, decisión de la autora): `web/chart-4.4.1.umd.js`, el archivo de jsDelivr
  sin tocar (mismo SRI, comprobado en una prueba; `.gitattributes` evita que Git cambie sus finales de
  línea). CSP: `script-src 'self'`. Ninguna otra web recibe la IP de quien visita.

- **Visitas** (25/11/2026, decisión de la autora): GoatCounter alojado (cuenta de la autora,
  `boe-en-llano.goatcounter.com`), sin su script: `web/contador.js` pide el píxel `/count?p=<página>`
  (sin título, referrer ni pantalla; `referrerPolicy = no-referrer`), solo en `hadadepie.github.io` y
  respetando GPC/DNT. CSP: `img-src` añade solo `https://boe-en-llano.goatcounter.com/count`.

- **Ajustes de GitHub** (fila 1): hechos por la autora el 25/11/2026.


**Punto de partida (revisión rápida del 25/11/2026, sin cambiar nada):** web estática en GitHub Pages, sin
servidor, cuentas, formularios ni cookies. Ya bien: todo texto de los datos se inserta con `textContent`
(el único `innerHTML` es un trazo SVG constante de `app.js`); Chart.js va con versión fija e `integrity`
(SRI); el RSS escapa títulos y textos (`xml.sax.saxutils.escape`); `.env` está en `.gitignore` y no hay
secretos versionados; las claves de IA van como *secrets* de Actions; `requests` con versión fija.

**Qué revisar y cerrar (en este orden, cada uno con su prueba o comprobación):**

| Qué | Riesgo | Cómo |
|---|---|---|
| **Ajustes de la cuenta y del repositorio** | Que alguien con la contraseña o un token publique en nombre de la autora | 2FA en la cuenta; protección de `main` (sin *force push* ni borrado); *secret scanning* y *push protection*; Dependabot (alertas); comprobar «Enforce HTTPS» en Pages. Lo hace la autora en GitHub (ajustes de su cuenta): se le da la lista. |
| **La Action** (`diario.yml`) | Una acción de terceros comprometida escribe en el repositorio o publica otra web | Permisos mínimos por trabajo (hoy `contents: write`, `pages: write` e `id-token: write` para todo el flujo); fijar las acciones por SHA y no por etiqueta (`actions/checkout@v7`…), con Dependabot para actualizarlas; `pip install --require-hashes` o al menos versiones fijas también para lo que instale la Action; que los *secrets* de IA solo lleguen al paso que los usa. |
| **Enlaces que vienen de los datos** | Un dato manipulado con `javascript:` en un `href` (p. ej. `v.enlace` de la consolidada) | Comprobar en `el()` o al exportar que toda URL externa empieza por `https://` y es de `boe.es` o `congreso.es`; prueba en `tests/test_web.py`. Los enlaces internos (`index.html#BOE-…`) ya se construyen con el id. |
| **Política de seguridad del contenido (CSP)** | Si algún día se colara HTML, que no pueda cargar scripts de otros sitios | GitHub Pages no deja poner cabeceras: `<meta http-equiv="Content-Security-Policy">` en cada HTML (`default-src 'self'; script-src 'self' https://cdn.jsdelivr.net; img-src 'self' data:`…), probada en la vista previa con la consola limpia. Límite: por `meta` no vale `frame-ancestors` (no se puede impedir que otra web la incruste). Añadir también `<meta name="referrer" content="strict-origin-when-cross-origin">`. |
| **Lo que se descarga de las fuentes** | Datos alterados o descargas fuera de las fuentes oficiales | Solo `https` y solo dominios oficiales (BOE, Congreso, Hacienda); `requests` verifica certificados por defecto: comprobar que nadie lo desactiva (`verify=False`). Los PDF y archivos externos, en `datos/crudo/`, leídos como datos. |
| **Cómo avisar de un fallo** | Que quien encuentre un problema no sepa a quién decírselo | `SECURITY.md` en el repositorio (avisos privados de GitHub) y una línea en «Cómo se ha hecho». |
| **Medir visitas sin rastrear** | Añadir analítica es meter un script de terceros y, con cookies, un aviso de consentimiento | Decidir si hace falta. GitHub Pages no da estadísticas de visitas (Insights → Traffic solo cuenta las visitas al repositorio, 14 días). Si se quiere: herramienta sin cookies y de código abierto (p. ej. GoatCounter), declarada en la CSP y explicada en «Cómo se ha hecho». Coherente con la regla de no enlazar ni depender de webs ajenas: valorarlo antes de añadir nada. |

**Cuidados:** no tocar la seguridad del propio equipo ni los permisos de Claude Code; cada cambio de ajustes de
GitHub lo hace la autora. Al terminar: novedad en «Cómo se ha hecho» (qué se protege y qué no puede proteger
una web en GitHub Pages).

## 1c. Revisión externa de la web (25/11/2026) 🔎

Documento de mejoras recibido el 25/11/2026, ordenado por página. **Contrastado punto por punto con `main`** (guia, como,
datos, legislatura, index y sus `.js`): varios puntos ya estaban hechos y otros repiten pendientes de las secciones 0 y 1;
aquí solo queda lo nuevo, con su estado real. Lo que afecta a lo que el lector entiende como cierto va primero.

**A. Textos desfasados o incorrectos** ✅ (25/11/2026: corregidos los de esta tabla, más «Solo normas desde finales de agosto de 2026» de la portada y la frase de «¿Quién la apoyó?» de «Cómo se ha hecho», que decía que no se recogían las votaciones de las leyes; entrada en «Correcciones» y `test_sin_frases_desfasadas` en `tests/test_web.py`. El vocabulario solo se ha corregido en el aviso general, «fichas y titulares»; el aviso de cada ficha sigue literal, como pide `CLAUDE.md`):

| Dónde | Qué dice hoy | Qué hay que poner |
|---|---|---|
| `guia.html`, «Lo que aún no está» | Qué pasó después «solo está para las normas desde finales de agosto de 2026» | Quitar el punto: la vida de las normas cubre toda la XV desde el 25/11/2026 (la tabla de cobertura ya lo dice). Lo que sí es solo desde el 26/08/2026 es el antes y el después de los artículos. |
| `guia.html`, «Lo que aún no está» | Las sentencias del Constitucional «van en un suplemento aparte que aún no recogemos» | Quitar o reescribir: la sección `T` se recoge desde el 25/11/2026. Decir qué no está: los recursos de amparo (lo explica `legislatura.html`, no la guía) y las admisiones anteriores al 17/08/2023. |
| `guia.html`, «Lo que aún no está» | El dinero público, pendiente | El Sankey ya está (pieza 1); quedan presupuestado frente a gastado (3.9) y las subvenciones. |
| `guia.html`, «¿Me puedo fiar?» | «fuentes (solo BOE y Congreso)» | BOE, Congreso, Senado y Hacienda (estadísticas de los Presupuestos). *Nota:* el documento dice «Excel del Tesoro»: no es el Tesoro, es la Secretaría de Estado de Presupuestos y Gastos (Hacienda). El Constitucional no es una fuente aparte: llega por la sección `T` del BOE. |
| Pie de `index`, `datos`, `guia` y `legislatura` | «BOE, Congreso y Senado» | Añadir Hacienda, como ya hace el pie de `como.html` (`legislatura.html` usa sus datos en el Sankey). |
| `como.html`, «¿Se votó?» | «de las leyes estatales solo sabemos que las aprobaron las Cortes, todavía no sus cifras de votación» | Desfasado desde 2.3b (25/11/2026): ya están la votación final y el voto por grupo. |
| `como.html`, «Qué ha pasado con normas anteriores» | «Solo cubre las normas que guardamos, desde finales de agosto de 2026» | Toda la legislatura, desde el 17/08/2023. |
| `guia.html`, esquema de los decretos-ley | «En la XV se pidió 43 veces y ninguna terminó» | Ambiguo: puede leerse como que esos decretos-ley no se aprobaron. Propuesta: «Se pidió para 43; ninguna de esas tramitaciones como ley terminó, y los decretos-ley siguieron en vigor tal como se convalidaron» (comprobar antes en los datos la cifra y si alguno se modificó o derogó después). |
| Toda la web | «resúmenes», «fichas» y «titulares» se usan como si fueran lo mismo (p. ej. «Los resúmenes son orientativos» cuando no hay ninguno publicado) | Fijar el vocabulario: *ficha* (la página de una norma), *titular* (título simplificado), *resumen* (el texto automático, hoy ninguno). El aviso obligatorio de `CLAUDE.md` se mantiene literal. Revisar las 5 páginas. |

Al corregirlos: una línea en «Correcciones» (regla de `CLAUDE.md`) y una prueba que busque en `web/*.html` las frases
desfasadas para que no vuelvan.

**B. Lo que ya estaba hecho** (no se añade nada): fecha de actualización (al pie de todas las páginas, «Actualizado el…»,
desde `indice.generado`; falta hacerla visible, ver C); menú de páginas fijo al bajar (sección 0); índice con anclas en
«La legislatura»; filtro por tema en «Explorar» (hay Día, Tema, A quién afecta, Ámbito y ¿Se votó?); explicación de
«¿Se votó?» en «Cómo se ha hecho»; cifras absolutas junto a los porcentajes (frases de lectura y tooltips de
`legislatura.js`); aviso de los plazos del Constitucional (`legislatura.html`: solo admisiones desde el 17/08/2023, el
tiempo real suele ser mayor); `aria-label` en los gráficos de «La legislatura»; términos con ⓘ en «La legislatura»; los
esquemas de la guía ya son listas numeradas (`<ol>`), no texto plano.

**C. Mejoras nuevas que quedan pendientes** (✅ 25/11/2026: hechas las cinco de prioridad alta: fecha arriba en todas las páginas con `pintarActualizado()` y `guia.js`; aviso de las barras; nota de «¿Se votó?» en «Explorar» y en la ficha; «Fechas» en la ficha con `fechaDeLaNorma()`, que lee la fecha del título solo si empieza por su rango —3.089 normas con fecha, ninguna corrección ni recurso—; y dos subtítulos de «La legislatura» que no decían que hablaban de decretos-ley) (las de prioridad media y baja, mejor dentro de la reorganización de la
prioridad 7):

| Página | Mejora | Prioridad del documento | Notas |
|---|---|---|---|
| Todas | **Fecha de los datos visible arriba**, no solo al pie, y junto a la tabla «Hasta dónde llegan los datos» de la guía | Alta | El dato ya existe (`indice.generado`). La «versión del análisis» puede ser la fecha de la última entrada de «Correcciones». |
| `datos.html` | **Aviso de que el tamaño de las barras no mide importancia**: cuenta textos; solo la sección I son normas que cambian reglas | Alta | Una nota bajo el gráfico por sección. |
| Fichas y `datos.html` | **«¿Se votó?» explicado donde se usa**: no dice nada de la validez (un real decreto es válido sin votación) | Alta | Hoy solo se explica en «Cómo se ha hecho». Va con la fila de la Diputación Permanente (sección 1). |
| Fichas | **Separar publicación, aprobación y entrada en vigor** | Alta | La ficha tiene «Publicada» y la entrada en vigor; falta la fecha de aprobación, que está en el título oficial («…, de 3 de marzo, …»). Sacarla con reglas, sin inventar. |
| `legislatura.html` | **Títulos que distingan leyes y decretos-ley** donde se habla de votaciones | Alta | Revisar los títulos de 2.3 y 2.7. |
| `guia.html` | ✅ (25/11/2026) Que todas las remisiones sean enlaces | Media | Casi todas ya lo son («Quién decidió», «Las correcciones», «Los tribunales»): revisar las que falten. |
| `guia.html` | ✅ (25/11/2026: caption visible y `role="group"` con `aria-label` en los esquemas) `<caption>` en las tablas (la segunda no tiene título) y una frase o `aria-label` que resuma cada esquema | Media | |
| Portada | ✅ (25/11/2026, en «Cómo leer el BOE en llano») Preguntas frecuentes | Media | Mejor en la página «Cómo leer el BOE en llano» (sección 0, «más grandes») que en la portada, que se quiere aligerar. |
| `datos.html` | Resumen breve de la semana al principio | Media | Solo cifras y titulares que salgan de los datos, sin IA ni valoraciones. |
| `datos.html` | Línea con la media semanal en los gráficos | Media | Barato con Chart.js. |
| Fichas y `datos.html` | Glosario emergente (ⓘ) como el de «La legislatura» | Media | Reutilizar `data-termino` de `app.js`. |
| `legislatura.html` | Enlaces descriptivos en vez de «Ver todos» | Media | |
| `legislatura.html` | Tabla equivalente al Sankey | Media | Los datos ya están en `presupuestos.json`. Va con «tabla para cada gráfico». |
| `legislatura.html` | Títulos neutros en «Las correcciones» | Media | Revisar con la regla de neutralidad. |
| `como.html` | ✅ (25/11/2026) Dos niveles: explicación general y técnica | Media | Es la página «Cómo leer el BOE en llano» (sección 0) frente a «Cómo se ha hecho». |
| `como.html` | ✅ (25/11/2026, RDL 6/2023 en «Cómo leer el BOE en llano») Ejemplo paso a paso del recorrido de una norma | Media | Un decreto-ley real: BOE → convalidación → tramitación → modificaciones → tribunal. |
| `como.html` | Porcentaje de aciertos de las clasificaciones | Media | Exige revisar a mano una muestra (p. ej. 100 normas) de tema e impacto; anotar el método antes de publicar cifras. |
| `como.html` | Registro de cambios de criterio | Media | Hoy van mezclados en «Correcciones»: etiquetar cada entrada (novedad, corrección, cambio de criterio). |
| `como.html` | ✅ (25/11/2026: en el pie de todas las páginas y en «Seguridad y privacidad») Canal visible para avisar de errores en los datos | Media | Hoy dice «basta con un aviso normal», sin enlace: enlazar a las *issues* de GitHub. |
| Todas | Tabla y texto alternativo para cada gráfico | Media | `aria-label` ya en «La legislatura»; faltan la portada, «Explorar» y las tablas. |
| Todas | Móvil: controles cómodos con el pulgar | Media | Revisar el tamaño de selectores y botones (mín. 44 px). |
| Descargas | **CSV de las tablas agregadas** | Media | Viable: las cifras de «La legislatura» ya salen de `legislatura.json`. Un CSV único de todo, no (fuentes en XML y texto, una norma modifica varias, votos por grupo en otra tabla, justificaciones en texto libre). Si se hace: varios CSV con diccionario de columnas. |
| Fichas | Cargar el preámbulo y el antes y el después al abrirlos | Baja | Medir antes el peso de `normas/<id>.json`. |

**D. Lo que no se hace tal cual** (✅ 25/11/2026: menú de seis páginas —Portada, Explorar, La legislatura, El dinero público, Los tribunales, Cómo leerla—; «Cómo se ha hecho», «Limitaciones», «Correcciones» y «Avisar de un error» en el pie; «Descargas» espera a los CSV; «Cómo se calcula» bajo cada bloque, no bajo cada gráfico): el menú de siete entradas (Datos, Legislatura, Guía, Metodología, Limitaciones,
Descargas, Errores) se decide en la reorganización (prioridad 7): «Limitaciones» y «Correcciones» ya son apartados de
«Cómo se ha hecho» y puede bastar con enlazarlos. «Enlazar los gráficos con la metodología y la guía», igual: un enlace
«Cómo se calcula» bajo cada gráfico al reorganizar.

---

## 2. Ampliaciones del proyecto

### 2.1 Qué hace el Congreso — fase A ⏸ (🔎 estado del arte hecho, 23/11/2026)

- **Pregunta:** ¿a qué dedica el Congreso su trabajo? Legislar, controlar al
  Gobierno y orientar (proposiciones no de ley, mociones).
- **Dónde iría:** página «La legislatura».
- **Fuente:** el «Índice de iniciativas» del Congreso da los recuentos oficiales
  por tipo y función de la XV legislatura y de todas las anteriores (por
  ejemplo, 44.849 preguntas escritas o 3.824 proposiciones no de ley en
  Comisión). Es una página web, no datos abiertos: hay que leerla con cuidado y
  vigilar que no cambie. Su recuento de reales decretos-ley (63) cuadra con el
  nuestro.
- **Qué existe:** *Qué Hacen Los Diputados* (Political Watch) es un buscador con
  alertas y fichas de diputados; los proyectos de fuera (TheyWorkForYou,
  NosDéputés…) miran a cada representante. Nadie cuenta la institución en
  conjunto de forma visual.
- **Revisión del 24/11/2026:** las votaciones ya las cubren *El Congreso en tu mano*
  (voto por grupo, fichas, alertas) y *El Congreso en datos* de Bocal (gráficos de
  coincidencia y de quién gana). **Decisión propuesta: recortar.** Las votaciones se
  enlazan; si se retoma, solo el recuento oficial por tipo y función del índice de
  iniciativas, que sigue sin hacer nadie.
- ✅ **Hecho (24/11/2026), acotado a los decretos-ley:** «Cómo votó cada grupo» en «La legislatura»
  (posición mayoritaria de cada grupo en las 54 convalidaciones del Pleno con voto por grupos;
  Mixto sin desglose por lista para no publicar historiales individuales). Idea siguiente, si se
  quiere: **votos decisivos** (en las votaciones ajustadas, qué grupos habrían cambiado el resultado
  con otro voto), contado sin juicio.
- **Riesgos:** contar no es valorar (44.849 preguntas no dicen si el control fue
  bueno); repartir por grupos se acerca a un ranking (empezar sin desglose);
  comparar legislaturas exige normalizar por duración (la XIII duró meses).
- **Primer paso al retomarlo:** leer el índice de la XV y de dos legislaturas
  anteriores y comprobar que la estructura de la página es estable.

### 2.2 Qué hace el Congreso — fase B: de dónde vienen las leyes 💡

- **Pregunta:** ¿cuántas leyes vienen del Gobierno y cuántas de los grupos, del
  Senado, de las comunidades o de la iniciativa popular? ¿Cuántas se aprueban,
  cuántas llegan al BOE y cuántas caducan al disolverse las Cortes?
- **Fuente:** datos abiertos del Congreso (proyectos y proposiciones de ley,
  iniciativas aprobadas), que ya usa `boe.tramitacion`.
- **Valor añadido:** une la tramitación con las normas del BOE que ya tenemos
  (cada ley publicada enlazada a su origen).
- **Primer dato (24/11/2026, `boe.tramitacion`):** de los reales decretos-ley de la XV, 43 se
  tramitaron como proyecto de ley y los 43 figuran como «Caducado 04/11/2026»: ninguno terminó.
- **Dónde se queda corto:** el Senado va aparte (comprobar sus datos abiertos).

### 2.3 Las decisiones que se votan ✅ (24/11/2026, fusionado)

- **Hecho:** cada norma lleva `decision` (calculada en `boe.exportar.decision_de`, con
  prueba): *se votó en el Congreso o las Cortes* · *real decreto-ley con votación
  pendiente o sin datos* · *Gobierno o Administración, sin votación* · *norma
  autonómica* · *decisión de un tribunal* · *otro tipo*. En la web: filtro «¿Se
  votó?» en «Explorar» (también por URL, `?decision=gobierno`), línea «¿Quién
  decidió?» en la portada con cada fila enlazada a ese filtro (la fila «0 se votaron»
  se muestra siempre), fila en «Datos y clasificación» de la ficha y explicación en
  «Cómo se clasifican». Semana 47: 0 votadas, 5 decretos-ley pendientes, 38 del
  Gobierno o la Administración, 6 autonómicas, 1 tribunal, 2 de otro tipo.
- **Estado del arte (24/11/2026):** nadie parece separar «votado / no votado» al
  explicar normas del BOE; solo hay explicaciones del procedimiento (Maldita,
  Democrata) y el portal de datos abiertos del Congreso, que da las votaciones sin
  relacionarlas con el BOE.
- **Llamada de prueba (votaciones de leyes):** los 853 índices diarios de la XV ya
  guardados contienen las votaciones de leyes, pero cada ley genera muchas (dictamen,
  enmiendas, «votación de conjunto» en las orgánicas, enmiendas del Senado: la
  Ley 4/2026 acaba con una larga lista de votaciones del Senado, sin conjunto
  propio) y el título del Congreso («Proyecto de Ley por la que…») no lleva el número
  de la ley, así que habría que emparejar por el texto. Ejemplo comprobado: Ley
  Orgánica 4/2026 (agentes de la autoridad, 11/06/2026): dictamen 324–19–2 y votación
  de conjunto.
- **Decisión: recortar.** No se recogen todavía las cifras de las leyes: solo 2 de
  343 normas generales son leyes estatales, así que el coste de emparejar no compensa
  hoy. Las leyes cuentan como «votadas» (las aprobaron las Cortes) y la web dice que
  faltan sus cifras. Se retomará si crece el número de leyes (**2.3b**: votación de
  conjunto por grupo para leyes orgánicas y última votación del Congreso para las
  demás, emparejando por texto del título).
- ✅ **2.3b hecho (25/11/2026)** con la XV completa: `boe/votaciones_leyes.py`, sin emparejar por texto (el expediente
  sale del boletín que cita el Senado). Ver 2.7.
- **Hueco conocido:** «pendiente o sin datos» mezcla los decretos-ley aún dentro de
  plazo con los que votó la Diputación Permanente. La cadena ya conoce 7 acuerdos
  de la Diputación Permanente por el BOE (`boe.legislatura`): se podrían marcar como
  «votada (Diputación Permanente, sin cifras)». Ver la tabla de mejoras cortas.

### 2.4 Informes con gráficos: balance de la XV legislatura 🔎 (prioridad 3)

- **Idea:** pasar de solo «periódico semanal» a **informes guiados**: cada uno es una
  pregunta, un gráfico, una frase de lectura y las normas de ejemplo enlazadas a su
  ficha. Se leen una vez, explican los conceptos donde aparecen (qué es un
  decreto-ley, la Diputación Permanente…) y se comparten mejor que una portada.
- **Primer informe: «La XV legislatura: quién decidió y qué pasó después».**
  Preguntas:
  - ¿Cuántas normas aprobó el Estado y cuántas pasaron por las Cortes?
  - ¿Leyes o decretos-ley? Cuántos decretos-ley se convalidaron y cuántos se derogaron.
  - ¿De qué temas decide el Gobierno solo y de cuáles las Cortes?
  - ¿Cuántas normas se cambiaron después y en cuánto tiempo?
- **Estado del arte:** hay recuentos de decretos-ley (Electomanía), de votaciones
  (Bocal, El Congreso en tu mano) y de producción normativa (CEOE), pero nadie mira
  el BOE entero con lo que se decide sin votar ni la vida posterior de las normas.
  No se enlaza a otras webs (decisión del 24/11/2026): si hace falta, a la fuente oficial.
- **Momento:** Cortes disueltas desde el 06/10/2026; las nuevas se constituyen el
  23/12/2026.
- **Dónde se quedan cortos los datos:** las normas guardadas empiezan a finales de
  agosto de 2026 (343); solo los decretos-ley cubren toda la XV. Hace falta
  **descargar la sección I desde agosto de 2023**: unos 800 sumarios más el texto de
  cada norma, con 1 s de pausa, entre una y dos horas, sin IA. **Avisar antes de
  lanzarlo.** Las cifras de otras webs no coinciden entre sí para la XV (por cómo
  cuentan lo aprobado con las Cortes disueltas): explicar nuestro criterio.
- **Dónde iría:** una página nueva de informes (o dentro de «La legislatura»).
- **Primera parte hecha (24/11/2026, `boe/informe.py` → `web/datos/informe.json`, en «La legislatura»):**
  de 3.774 textos de la sección I, 2.973 normas del Estado: 36 leyes y reformas de la Constitución, 72
  reales decretos-ley, 1.022 reales decretos (384 son concesiones directas de subvenciones), 1.189
  órdenes y resoluciones de ministerios, 52 de otros órganos, 339 acuerdos internacionales y 263
  decisiones de tribunales; además 565 autonómicas. Gobierno en funciones (hasta el RD 829/2023, 21/11/2023):
  ~8 reales decretos cada 30 días, ningún decreto-ley ni ley; después ~26. El mes con más reales decretos,
  octubre de 2026 (54), ya con las Cortes disueltas. Ninguna ley de Presupuestos en toda la legislatura.
  Entrada en vigor: 83 % el mismo día o al siguiente; ningún decreto-ley con plazo; las leyes, 7 de 33.
  **Falta:** «qué pasó después» (vida de la norma de toda la XV por tandas y tribunales, prioridad 4) y,
  si se quiere, una pieza de «Gobierno con las Cortes disueltas» (desde el 06/10/2026).
- **Llamada de prueba (24/11/2026, `exploracion/prueba_2023.py`, fuera de `datos/`):**
  | Mes | Días con BOE | Normas (sección I) | Tiempo | Datos versionables | Crudo |
  |---|---|---|---|---|---|
  | Septiembre 2023 | 26 | 39 (35 estatales) | 87 s | 138 KB | 5,4 MB |
  | Marzo 2024 | 26 | 81 (61 estatales) | 143 s | 283 KB | 10,3 MB |
  - **Estructura:** los sumarios se leen igual; solo reaparece la sección `T` ya conocida.
  - **Septiembre de 2023 no es representativo:** Gobierno en funciones tras las
    elecciones (3 reales decretos en el mes). Es un dato para el informe: la
    producción normativa cae con el Gobierno en funciones.
  - **Textos oficiales más escasos que en 2026:** en marzo de 2024 solo 6 de 12 reales
    decretos dicen su título competencial. No es un fallo: los otros 6 son reales
    decretos de estructura de ministerios (nuevo Gobierno), que no citan
    competencia constitucional. «¿Con qué competencia?» no aplica a la autoorganización.
  - **Estimación para toda la XV (17/08/2023 – agosto 2026, ~36 meses):** entre 40 y
    115 normas al mes (2026 va por ~113) → **unas 3.000–3.600 normas**; descarga de
    sumarios y textos en **70–90 minutos**; **10–13 MB** más en `datos/normas/`
    (sin «vida de la norma» ni antes y después) y **~300 MB** en `datos/crudo/` (fuera de Git).
  - **Lo caro no es la descarga sino «qué pasó después»:** `consolidada` haría
    3.000+ peticiones más y `versiones` (antes y después) muchas más, y hoy cada
    norma con antes y después ocupa ~12 KB de media (los 343 actuales suman 4,2 MB).
    Para el informe basta la «vida de la norma» (fechas de modificación y
    derogación); el antes y después de artículos puede quedar solo para las normas
    recientes.
  - **Efecto en la web si las normas antiguas entran en `datos/`:** unas 150
    ediciones semanales más; `buscar.json` ~0,6 MB (por debajo del límite de 1 MB
    anotado) e `indice.json` habría crecido sobre todo por las ediciones (~2 KB cada
    una, ~320 KB con 160).
  - **Decisión (24/11/2026):** las normas antiguas van a `datos/`, con la web (una
    sola fuente; el informe se puede comprobar norma a norma). Antes de la descarga,
    ✅ **índice ligero** (hecho el 24/11/2026): el índice solo lleva la lista de
    ediciones (~200 bytes cada una) y cada semana trae su resumen, piezas,
    votaciones, seguimiento y recuentos; 73 → 31 KB. Pendiente: vida de la norma por
    tandas sin antes y después para las antiguas (la Action ya está protegida; ver
    «Pendientes técnicos») y agrupar por año el selector de semanas.

### 2.5 Competencias: quién decide qué 🔎 + prueba hecha (prioridades 1, 6 y 8)

- **Pregunta:** en política se reparten culpas sin que se vea de quién es cada
  competencia. ¿Qué puede decidir el Estado, qué las comunidades y qué los
  ayuntamientos, y con qué competencia se dicta cada norma?
- **Estado del arte (24/11/2026):** explicaciones periodísticas sueltas por tema
  ([Newtral](https://www.newtral.es/competencias-vivienda-comunidades-estado-ayuntamientos/20260214/)
  y [Maldita](https://maldita.es/malditateexplica/20230426/competencia-vivienda-autonomias-gobierno/)
  sobre vivienda; [que.es](https://www.que.es/2026/10/07/competencias-estado-comunidades-autonomas/)
  sobre vivienda, sanidad y educación), que no se actualizan; el texto legal
  (Constitución arts. 148 y 149, estatutos, Ley de Bases de Régimen Local arts. 25 y
  26); y el [Boletín de Conflictividad](https://mptmd.gob.es/content/dam/mpt/politica-territorial/autonomica/regimen_juridico/Boletin_de_Conflictividad_1_Trimestre_2026.pdf)
  trimestral del Ministerio de Política Territorial (recursos ante el Constitucional y
  comisiones bilaterales; en PDF). **Nadie une las competencias con cada norma.**
- **Llamada de prueba (24/11/2026, `datos/crudo/normas/`):** las normas estatales
  suelen traer una disposición final «Título competencial» («se dicta al amparo del
  artículo 149.1.Xª»). Búsqueda de «título competencial» o «149.1.Nª» en las 313
  estatales con texto: reales decretos 113 de 127, reales decretos-ley 17 de 21,
  órdenes 16 de 50; resoluciones, sentencias y circulares 0 (normal: no crean normas
  nuevas). Más citadas: **149.1.13.ª** (bases y coordinación de la planificación
  general de la economía) 45, 149.1.1.ª (igualdad básica de derechos) 26, 149.1.15.ª
  (investigación) 19, 149.1.16.ª (bases de la sanidad) 11. El 149.1.13.ª es la vía
  por la que el Estado entra en materias de las comunidades, como vivienda.
  Ojo: la búsqueda también encuentra las frases del preámbulo que *anuncian* la
  disposición («la sexta regula el título competencial»): al extraer, leer la
  disposición final, no el preámbulo.
- **Tres piezas:**
  1. ✅ (24/11/2026) **En cada ficha, «¿Con qué competencia?»** (prioridad 1, con las fichas sin IA). Hecho sin frase fija por artículo: se muestra el párrafo literal, que ya dice la materia. Plan original:
     el artículo citado, extraído de la disposición final, y una frase fija por
     artículo («permite al Estado fijar las bases de la economía»). Normas
     autonómicas: citan su estatuto; empezar por las estatales.
  2. **Explicador fijo «¿Quién decide qué?»** (prioridad 6): tabla con nuestros ocho
     temas y, para cada uno, qué hace el Estado (exclusiva / bases), las comunidades
     (desarrollo / gestión) y los ayuntamientos, con el artículo de donde sale cada
     casilla. Escrito a mano desde las fuentes oficiales y revisado por la autora.
  3. **Qué competencias usa el Estado y cuáles acaban en conflicto** (prioridad 8):
     gráfico de los títulos competenciales y cruce con el Boletín de Conflictividad
     y las sentencias del Constitucional (enlaza con 3.4).
- **Cuidados:**
  - Casi nada es de uno solo (bases, desarrollo, gestión): la tabla muestra los
    niveles, no reparte cada tema entero a uno.
  - El título competencial es lo que **afirma el Estado**; una comunidad puede
    discutirlo y lo decide el Constitucional: decir «según la propia norma».
  - Neutralidad: quién tiene la competencia, nunca quién lo hace bien o mal.
  - Qué no cubrimos: tener la competencia no es tener el dinero (financiación
    autonómica).

### 2.7 El Senado: cómo interactúa y en qué influye 🔄 (24/11/2026, idea de la autora; 25/11/2026: «Qué hizo el Senado con las leyes» publicado)

- **Pregunta:** ¿qué hace el Senado con lo que aprueba el Congreso y qué cambia de verdad? ¿Cuántas
  leyes enmendó o vetó, qué pasó después en el Congreso, y en qué otros asuntos decide o frena?
- **Quién puede qué** (para el explicador; reglas de la Constitución):
  - **Leyes (art. 90):** el Senado tiene dos meses (veinte días naturales si son urgentes) para
    **enmendar** (mayoría simple) o **vetar** (mayoría absoluta) un texto del Congreso. El Congreso acepta
    o rechaza las enmiendas por mayoría simple; levanta el veto por mayoría absoluta enseguida o por
    mayoría simple pasados dos meses. Es decir: el Senado retrasa y propone, pero la última palabra la
    tiene el Congreso.
  - **Decretos-ley (art. 86):** la convalidación es solo del Congreso; el Senado solo interviene si se
    tramitan además como proyecto de ley.
  - **Enmiendas con gasto (art. 134.6):** si una enmienda aumenta el gasto o reduce los ingresos, el
    Gobierno puede oponerse («veto presupuestario»); varios de los conflictos de abajo vienen de ahí.
  - **Conflictos ante el Tribunal Constitucional:** el Senado puede plantear conflictos entre órganos
    constitucionales frente al Gobierno o al Congreso, y al revés.
  - **Otros:** nombra a parte del Tribunal Constitucional y del Consejo General del Poder Judicial, aprueba
    las medidas del artículo 155, autoriza tratados junto al Congreso y controla al Gobierno (preguntas,
    comisiones de investigación).
- **Lo que ya tenemos (BOE, sección I, guardado con `boe.tribunales`):** 14 conflictos entre órganos
  constitucionales en la XV, **12 promovidos por el Senado** (frente al Gobierno: «veto presupuestario» de
  enmiendas, presentar los Presupuestos de 2024–2026, requerimientos rechazados; frente al Congreso:
  acuerdos de su Mesa de no tramitar textos del Senado o de no cerrar plazos de enmiendas) y 2 del Gobierno
  frente al Senado. ✅ Publicada (24/11/2026) en «La legislatura»: «El Senado frente al Gobierno y al
  Congreso» (`informe.senado`: quién, frente a quién, motivo por reglas sobre el título y asunto literal;
  7 de 14 sobre enmiendas con gasto y el artículo 134.6).
- **Fuentes por probar:** datos abiertos del Senado (catálogo en datos.gob.es: «Lista de votaciones de
  sesiones plenarias, XV legislatura», XML, actualización semanal); por comprobar si hay datos abiertos de
  la tramitación de cada proyecto (enmiendas aprobadas, vetos) o si hay que leerlo del Boletín Oficial de
  las Cortes Generales (sección Senado). Del Congreso ya tenemos la tramitación (`boe.tramitacion`):
  comprobar si sus fases dicen «Senado» y «enmiendas del Senado» para cada ley.
- **Estado del arte (24/11/2026):** noticias caso a caso (p. ej. el rechazo de octubre de 2024 que la
  presidencia del Senado trató como veto y la Mesa del Congreso no reconoció; la mayoría del Senado
  enmendando el paquete fiscal de diciembre de 2024 en vez de vetarlo). No se ha encontrado un recuento
  sistemático de vetos, enmiendas incorporadas o rechazadas por el Congreso y conflictos del Senado en la
  XV, ni un gráfico de «qué cambió el Senado».
- **🔎 Llamada de prueba (25/11/2026, `exploracion/senado/prueba_datos_abiertos.py`, crudo en
  `datos/crudo/senado/`):** el Senado publica en XML, sin claves, todo lo necesario:
  - **Ficha de cada iniciativa** (`/web/ficopendataservlet?legis=15&tipoFich=3&tipoEx=621&numEx=000001`):
    `situacion` en el Senado, `observaciones` (qué hizo después el Congreso con las enmiendas o el veto, en
    texto), boletines («Enmiendas del Senado mediante mensaje motivado», «Veto aprobado por el Senado»),
    votaciones, sesiones y **el enlace al BOE de la ley** (`BOE-A-…`): se cruza directamente con `datos/normas`.
    Lista de iniciativas: `tipoFich=9&legis=15` (274).
  - **Enmiendas y vetos presentados por grupo** (`/legis15/expedientes/621/enmiendas/global_enmiendas_vetos_15_621000001.xml`):
    totales por grupo parlamentario (sirve tal cual: agregado, sin senadores).
  - **Medido:** 39 iniciativas llegaron del Congreso (22 proyectos de ley, 14 proposiciones del Congreso,
    2 reformas constitucionales, 1 de una comunidad); 36 acabaron en el BOE (35 en nuestros datos). Situación
    en el Senado: 19 con enmiendas, 13 sin cambios, 4 vetos, 3 caducadas por la disolución. Respuesta del
    Congreso a las 19 enmendadas (reglas sobre `observaciones`): todas aceptadas 4, ninguna 3, en parte 12
    (la prueba contaba 4 y 11: «rechazado todas excepto…» se leía como «ninguna»; corregido con una prueba);
    los 4 vetos, levantados (el Congreso ratificó su texto).
  - **Rarezas de la fuente:** un id del BOE mal escrito (`BOE-A-0205-19339` por 2025, expediente 621/000015);
    una fecha imposible en `observaciones` (625/000001: «23 de julio de 2023», ley de julio de 2026); y el veto
    de 621/000008 (octubre de 2024), que el Senado registra como veto por entender así un rechazo y que la Mesa
    del Congreso no reconoció: contarlo como «el Senado lo registra como veto» y explicarlo.
  - **Ya teníamos** (Congreso, `ProyectosDeLey`): la fase «Enmiendas o veto del Senado» en 14 de los 22
    proyectos aprobados, sin distinguir veto de enmiendas ni la respuesta. El Congreso publica además
    `ProposicionesDeLey` e `IniciativasLegislativasAprobadas`, que aún no usamos.
  - **No sirve sin más:** cuántas enmiendas concretas aceptó el Congreso (`observaciones` las enumera en
    texto libre, con transaccionales): contar por ley (todas, ninguna, en parte), no por enmienda.
- ✅ **Hecho (25/11/2026):** `boe/senado.py` (en la Action: solo la lista y las fichas sin terminar) → `datos/senado.json`;
  `informe.senado_leyes`; parte «Qué hizo el Senado con las leyes» en «La legislatura» y línea en «¿Quién la apoyó?» de
  cada ley. **Pendiente:** las votaciones de las leyes (Congreso y Senado) y las iniciativas que nacen en el Senado.
- **🔎 Votaciones de las leyes en el Congreso: llamada de prueba (25/11/2026; scripts en el scratchpad, sin nada nuevo en
  `datos/` salvo JSON de prueba en `datos/crudo/congreso/votaciones/` y los ficheros de iniciativas de hoy):**
  - **Enlace ley → expediente del Congreso, sin comparar títulos:** la ficha del Senado cita los boletines del Congreso.
    Serie A (proyectos): el número del boletín es el del expediente (A-5 = 121/000005). Serie B (proposiciones): no
    coincide (amnistía: B-32 = 122/000019); se traduce con `ENLACESBOCG` del fichero `ProposicionesDeLey` del Congreso
    (comprobado en las 15, también una cuyo título cambió). Las 2 reformas de la Constitución, aparte (ver
    «Reformas de la Constitución» más abajo).
  - **Votaciones:** los índices diarios ya guardados cubren los 819 días laborables de la legislatura. Cada votación tiene
    su JSON (`informacion.titulo` = parte del orden del día: «Dictámenes de Comisiones…», «Enmiendas del Senado», «Veto
    del Senado»; `textoExpediente`/`tituloSubGrupo`: «Votación del dictamen», «Votación de conjunto» en las orgánicas,
    o una enmienda concreta). Con eso se distingue sin reglas sobre texto libre la votación final en el Congreso, la de
    las enmiendas del Senado (una por bloque) y la del veto. Voto por grupo con `congreso.resumir_votacion` (agregado).
  - **Sorpresas:** las votaciones públicas por llamamiento (amnistía) no tienen JSON, solo totales en el índice (ya lo
    resuelve `congreso.totales_del_indice`); la ley del veto discutido (621/000008) se aprobó en el Congreso 346 a 0.
    Buscar con ventanas de texto en el HTML del índice es frágil (salieron 18 de 36 con votación final): hay que bajar el
    JSON de cada votación cuyo enlace sigue a una mención del expediente (unas 10 por ley, ~360 en total, una vez).
    Leer los 88 MB de índices le cuesta ~80 s a Python en este portátil; la limpieza de HTML de `congreso._texto_visible`
    es demasiado lenta para recorrerlos todos (más de 2 min con 5 índices): buscar en el HTML crudo.
    Las leyes aprobadas por una comisión con competencia legislativa plena no tienen votación final en el Pleno: decirlo.
  - ✅ **Hecho (25/11/2026):** `boe/votaciones_leyes.py` → `datos/congreso/votaciones_leyes.json` (34 leyes: 27 con votación
    final, 15 de conjunto y 12 del dictamen; las 7 sin ella son exactamente las de «Competencia Legislativa Plena», dato que
    se guarda; 5 votaciones tras el Senado, 3 de veto; 2 por llamamiento, solo totales). Parte del orden del día que no
    estaba en la prueba: «Tramitación directa y en lectura única» (su «Votación de conjunto del texto» es la final). Ficha
    «¿Quién la apoyó?» con voto por grupo; «Cómo votó cada grupo las leyes» en «La legislatura»; `boe/congreso.py` reintenta
    ante cortes. **Pendiente:** las 2 reformas de la Constitución (abajo).
  - **🔎 Reformas de la Constitución (26/11/2026):** lo que suponía el backlog estaba mal. `PropuestasDeReforma` es de
    **Estatutos de Autonomía** (expedientes 127: La Rioja, Castilla-La Mancha), y ningún fichero de iniciativas del
    Congreso trae las reformas de la Constitución. Sus expedientes son **100/000001** (art. 49, de grupos parlamentarios)
    y **101/000002** (art. 69.3, Formentera, del Parlamento balear); el 102/000001 es otra propuesta, rechazada en el
    debate de totalidad (30/04/2026, 171 a 177), que no llegó al BOE. Enlace sin títulos: la portada del boletín que cita
    el Senado (BOCG-15-B-56-1 y B-6-1, PDF) empieza por el expediente; los que siguen son de otras legislaturas
    («corresponde a…»). En los índices de votaciones salen en «Toma en consideración», «Acuerdo de tramitación directa y
    en lectura única» y «Tramitación directa y en lectura única de Proposición de reforma constitucional» (la final:
    18/01/2024, 312 a 32; 26/03/2026, 312 a 33 y 5 abstenciones, según el índice). Exigen tres quintos (210, art. 167).
    ✅ Código (`c5e12e0`): `votaciones_leyes.expediente_del_boletin_b` y la marca `reforma_constitucional`.
    **Pendiente:** bajar sus votaciones (congreso.es respondía 403 a todo el 26/11/2026, también a la portada) y
    comprobar que la final sale como «conjunto». Cuidado: cada pasada recorre los 819 índices (~10 min) y un JSON que
    falle tira la pasada entera.
  - **Propuesta original:** `boe/votaciones_leyes.py` → `datos/congreso/votaciones_leyes.json` (por ley: votación final en el
    Congreso, votación sobre el Senado si la hubo, totales y voto por grupo); en «¿Quién la apoyó?» de cada ley, la
    votación final con el voto por grupo, como en los decretos-ley; en «La legislatura», «Cómo votó cada grupo las leyes».
- **Propuesta original:** `boe/senado.py` que guarde por ley (por su id del BOE) la situación en el
  Senado, la respuesta del Congreso y las enmiendas y vetos presentados por grupo; en «La legislatura», ampliar
  «El Senado frente al Gobierno y al Congreso» con «Qué hizo el Senado con las leyes» (barras: sin cambios /
  enmendadas, con lo que aceptó el Congreso / vetadas) y, en la ficha de cada ley, una línea «En el Senado».
  Las iniciativas que nacen en el Senado (136 proposiciones de ley, 622 y 620) quedan para otra pieza.
- **Cuidados:** neutralidad (contar vetos, enmiendas y conflictos; no valorar si son obstrucción o
  control); nada de votos individuales de senadores (solo agregados por grupo, como en el Congreso); la
  composición del Senado cambia por elección y por designación autonómica: decir de qué fecha es cada dato.

### 2.6 Más preguntas para los informes 💡 (24/11/2026)

Ideas para piezas de informe (pregunta → gráfico → frase de lectura → normas de
ejemplo). Ninguna tiene aún estado del arte propio; antes de programar, el método de
siempre.

| Idea | Pregunta | Datos | Coste | Notas |
|---|---|---|---|---|
| ✅ (25/11/2026: por tipo de norma y, ahora, por ministerio en «La legislatura», `informe.vigencia_ministerios`) **Entrada en vigor inmediata (*vacatio legis*)** ⭐ | ¿Cuántas normas se aplican al día siguiente de publicarse, sin tiempo para adaptarse? ¿Cambia por tipo de norma o ministerio? | Ya extraído: párrafo de entrada en vigor en `textos_oficiales` (240 de 343 normas recientes). Clasificar con reglas: «día siguiente», «mismo día», «a los N días», fecha concreta. | Bajo | Hecho, no valoración: hay motivos legítimos para la urgencia. **Medido (1.959 normas con párrafo de entrada en vigor, a mitad de la descarga de la XV):** día siguiente 65,7 %, mismo día 13,1 % (las resoluciones, 72 %), plazo 8,9 % (casi siempre 20 días), fecha concreta 6,9 %, mes siguiente 0,9 %, depende de otro hecho 1,6 % (acuerdos internacionales), sin clasificar 2,8 %; 180 con excepciones. Ningún real decreto-ley con plazo de espera. ✅ «días hábiles» y el encabezado de tabla «Aplicación provisional» (24/11/2026). **Por ministerio (25/11/2026):** solo reales decretos y órdenes (las resoluciones, casi siempre «mismo día», deformarían: Hacienda publica muchas), mínimo 25 con párrafo, nombres del BOE sin normalizar, orden por volumen. 18 ministerios; 80 % mismo día o siguiente; Educación, plazo en 59 de 130; Defensa, 18 de 54; sin ningún plazo: Exteriores, Cultura, Política Territorial. |
| **Mandatos pendientes** ⭐ | Cuando una norma dice «en el plazo de seis meses el Gobierno aprobará…», ¿se cumplió? | Texto de las normas (disposiciones finales y adicionales) + BOE posterior para encontrar la norma que lo cumple. | Medio-alto | La más novedosa: explica «por qué las cosas no salen». Enlaza con promesas frente a hechos (3.3). Emparejar mandato y cumplimiento será dudoso a veces: marcarlo. |
| ✅ (26/11/2026: en «Qué pasó después» de «La legislatura», `informe.cambios_despues` y `anteriores_cambiadas`) **Las leyes que más cambian** | ¿Qué normas se modificaron más veces en la legislatura? ¿Cuánto dura una norma sin tocarse? | Vida de la norma (legislación consolidada): relaciones «se modifica» con fecha. | Medio | Depende de cargar la vida de la norma de toda la XV (por tandas). |
| **Leyes «escoba»** | ¿Qué leyes y reales decretos cambian a la vez muchas normas de temas distintos? | Lo que ya se hace para los decretos-ley (`boe.decretos_ley`: normas que modifica y sus temas), extendido a todo rango. | Medio | Ya hay un hallazgo con decretos-ley (los que modifican 10+ normas se derogaron más). Sin juicio: contar, no calificar. |
| ⏸️ (24/11/2026: pausada por la autora, parece un callejón sin salida: las actas dicen quién pide cada ampliación, nunca por qué) **Por qué no acabó ningún decreto-ley tramitado como ley** | Los 43 caducaron: ¿dónde se pararon y quién pidió alargar el plazo de enmiendas? | (1) Ya descargado: campo `PLAZOS` del fichero «ProyectosDeLey» del Congreso, con cada ampliación y su fecha. (2) Actas de acuerdos de la Mesa (PDF, una por reunión: `app.congreso.es/svt/descargarOrdenDia?fecha=DD/MM/AAAA&sesion=1&tipoDocumento=2`): cada solicitud de ampliación lleva expediente, grupo que la pide y nueva fecha; ningún motivo. Texto extraíble con `pypdf`. | Bajo (1) / Medio (2) | **Medido con (1):** se presentaron como proyecto de ley entre 5 y 41 días después del BOE (mediana, 21); 41 de 43 siguieron en enmiendas hasta la disolución (06/10/2026), con una mediana de 26 ampliaciones semanales (máximo, 80: RDL 1/2024). Los proyectos ordinarios del Gobierno que caducaron tuvieron casi las mismas (mediana 24,5) y los aprobados, 10,5: el atasco no es propio de los decretos-ley. **Muestra de (2), acta del 22/09/2026 (194 págs.):** 39 de los 43 proyectos se ampliaron ese día; en los 39 lo pidió el Grupo Socialista y en 4 también el Popular. Para generalizar hacen falta todas las actas de la XV (~150 PDF, en `datos/crudo/`). Cuidados: contar por grupo, nunca por diputado; pedir una ampliación no dice por qué (puede ser negociación); quien la concede es la Mesa. |
| ✅ (24/11/2026: `informe.correcciones`, parte «Cuántas veces se corrige lo publicado» de «La legislatura») **Correcciones de errores por ministerio** | ¿Cuántas veces hay que corregir lo publicado y quién? | Rango «Corrección (errores o erratas)» y su departamento; la norma corregida, por título exacto + órgano (138 de 169). | Bajo | **Medido:** 169 correcciones (138 estatales, 31 autonómicas), 4,5 por cada 100 normas del Estado. Tasa más alta (≥50 normas): Jefatura del Estado, 11,9 (16 de 135). Exteriores: 27 de 28 son de textos internacionales. Mediana: 20 días tras la norma. Solo 2 normas del Estado corregidas dos veces. Órganos ordenados por volumen, no por tasa; sin normalizar nombres de ministerios. **Posible ampliación:** de qué tipo es cada corrección (errata, cifra, anexo) leyendo su texto; hoy no se valora. |

---

## 3. Proyectos paralelos

Proyectos con entidad propia: podrían vivir en otra carpeta de `main` o en
otro repositorio, reutilizando la cadena de datos.

### 3.1 La Comunidad de Madrid en llano 💡

- **Idea:** la misma lógica aplicada a una comunidad: qué decide el Gobierno
  regional, qué se vota en la Asamblea y qué pasa después.
- **Fuentes a comprobar:** el BOCM (Boletín Oficial de la Comunidad de Madrid:
  ¿sumario en XML o API como el BOE?), los datos abiertos de la Comunidad y de
  la Asamblea de Madrid (¿votaciones por grupo?).
- **La pregunta de los tiempos («lo que tarda en ejecutarse»)** hay que
  separarla en preguntas que los datos sí pueden contestar:
  - **De la norma estatal a la regional:** cuando una ley o un real decreto
    estatal pide desarrollo autonómico, ¿cuánto tarda la comunidad en aprobar
    su norma? Medible si la norma regional cita a la estatal (BOE y BOCM son
    públicos), aunque no siempre la cita de forma expresa.
  - **De la norma a su primer acto de aplicación:** por ejemplo, de una ley de
    ayudas a la primera convocatoria y a su resolución, ambas en el BOCM.
  - **Plazos que fija la propia norma frente a lo que pasó:** «en seis meses se
    aprobará el reglamento…», y ver si se cumplió.
- **Dónde se opacan los datos:** la **ejecución real** (si el dinero se pagó, si
  el servicio funciona) casi nunca está en los boletines. Puede asomar en la
  ejecución presupuestaria o en el portal de transparencia regional, con otro
  nivel de detalle y retraso. Medir el cumplimiento a partir de los boletines es
  medir el papel, no la realidad, y hay que decirlo.
- **Comparar con otras comunidades** daría sentido a los tiempos (¿Madrid tarda
  más o menos?), pero multiplica las fuentes. Empezar por una.
- **Primer paso:** estado del arte (observatorios de transparencia autonómica,
  estudios sobre el desarrollo autonómico de leyes estatales) y llamada de
  prueba al BOCM.

### 3.2 El dinero público: de dónde viene y a dónde va 🔎 (prioridad 5; idea de la autora del 24/11/2026)

- **Pregunta:** ¿de dónde sale el dinero del Estado (impuestos, cotizaciones, deuda),
  a qué se dedica y a quién llega: otras administraciones o entidades privadas? Y,
  como es tan difícil aprobar los Presupuestos, ¿cómo se gobierna sin ellos?
- **Contexto (24/11/2026):** los Presupuestos son una ley que necesita mayoría en el
  Congreso; si no se aprueban, se prorrogan solos los anteriores (art. 134.4 de la
  Constitución). España arrancó 2026 con los de 2023 prorrogados por tercer año. No
  se ha confirmado si llegó a presentarse un proyecto para 2026; con las Cortes
  disueltas desde el 06/10/2026, no puede aprobarse ahora.
- **Estado del arte:** *¿Dónde van mis impuestos?* (Civio) visualiza los Presupuestos
  del Estado por política de gasto y presupuestado frente a ejecutado (materiales de
  2014–2021: comprobar si sigue al día). Hacienda (Secretaría de Estado de
  Presupuestos y Gastos) publica los Presupuestos en datos abiertos (Excel, CSV,
  JSON) y estadísticas en PDF por clasificación económica. Quién recibe en concreto:
  Base de Datos Nacional de Subvenciones y Plataforma de Contratación del Sector
  Público. **No se ha visto** un gráfico de origen → destino que distinga público y
  privado, ni «gobernar sin presupuestos» medido con el BOE.
- **Tres piezas, en este orden:**
  1. **Sankey de los Presupuestos** (los de 2023, prorrogados hasta hoy): a la
     izquierda los ingresos (IRPF, IVA, Sociedades, cotizaciones, deuda), en el
     centro las políticas (pensiones, intereses, desempleo…), a la derecha los
     destinatarios según la clasificación económica de las transferencias: otras
     administraciones (Seguridad Social, comunidades, entidades locales, organismos),
     empresas públicas, **empresas privadas**, **familias e instituciones sin fines de
     lucro** y exterior (p. ej. la UE). Distinguir «transferido a empresas» de «pagado
     a empresas por un contrato» (compras e inversiones, capítulos 2 y 6).
  2. ✅ **Gobernar sin presupuestos** (24/11/2026): `boe.presupuestos` detecta en la parte
     dispositiva los créditos extraordinarios y suplementos de crédito (campo `creditos`: 29 de
     72 decretos-ley y 1 ley); `informe.sin_presupuestos`. **Siguiente:** los importes (vienen en
     euros, miles o millones y a veces en tablas: extraer con su unidad y revisar a mano los 30)
     y mostrar los párrafos en la ficha de cada norma.
  3. **Las subvenciones directas de cada semana** (ya las contamos en sección I),
     cruzadas con la Base de Datos Nacional de Subvenciones: a quién, cuánto y para qué.
- **Llamada de prueba (24/11/2026, `exploracion/hacienda/`): ✅ viable.** La Secretaría
  de Estado de Presupuestos y Gastos publica en Excel (XLSX, desde 2014; antes solo PDF)
  las «Estadísticas de los PGE»: `01 Presupuestos Generales del Estado Consolidados.xlsx`
  (200 KB) trae, por años (2017 … 2023, 2023-P, 2024-P, 2025-P), gastos por capítulos,
  **transferencias por artículos** (justo la división público/privado), ingresos por
  capítulos, políticas de gasto y programas. Se lee sin dependencias
  (`exploracion/hacienda/leer_xlsx.py`). Cifras consolidadas 2025-P (= los de 2023
  prorrogados), en millones de euros:
  - Transferencias (358.652): familias e instituciones sin fines de lucro 242.120
    (sobre todo pensiones), comunidades autónomas 42.520, entidades locales 24.800,
    exterior 20.140, **empresas privadas 17.135**, empresas y entes del sector público 11.937.
  - Otros gastos: personal 27.476, bienes y servicios 10.605 e inversiones 13.511 (la
    mayor parte acaba en empresas por contratos), intereses de la deuda 31.373.
  - Ingresos no financieros 383.171 frente a gastos no financieros 445.581: la
    diferencia se cubre con deuda.
  - **Comprobado (25/11/2026)** con los Excel 01 a 04 de la edición 2025-P:
    - «Impuestos directos» (269.000) es el capítulo 1 «Impuestos directos y cotizaciones
      sociales» y **sí incluye las cotizaciones**: suma exacta de los impuestos directos del
      Estado (86.429), las cotizaciones de la Seguridad Social (152.075) y el capítulo 1 de
      los organismos autónomos (30.497; por su tamaño, cotizaciones como las de desempleo y
      formación del SEPE: no desglosado en estas tablas).
    - Los impuestos indirectos consolidados (57.809) son exactamente los del Estado: la parte
      que se queda el Estado; lo cedido a comunidades y entidades locales no está aquí.
    - Licencia (aviso legal de la web): «Se autoriza la reproducción total o parcial de los
      contenidos del Portal, siempre que se cite expresamente su origen».
    - **No hay 2026-P**: la última edición es 2025-P (Enero 2026); la web anuncia la
      «Prórroga del Presupuesto para 2026». Los ingresos llegan al capítulo 8: la deuda
      nueva no aparece y se calcula como diferencia (90.698 en 2025-P).
    - **No hay cruce política × destinatario** en estas estadísticas: el Sankey solo puede
      ir ingresos → presupuesto → políticas, o ingresos → presupuesto → tipo de gasto y
      destinatario. Para cruzarlos haría falta el presupuesto completo (ZIP de 190 MB).
  - Hecho `boe/hacienda.py` → `datos/hacienda/presupuestos.json` (todas las columnas
    2017 … 2025-P, con comprobaciones cruzadas que avisan si algo no cuadra).
  - ✅ **Publicado (25/11/2026)** en «La legislatura», sección «El dinero de los Presupuestos»
    (`legislatura.js`: `pintarPresupuestos`, SVG propio con bandas rellenas; `exportar` copia
    el JSON a `web/datos/presupuestos.json` sin las URL de los Excel; método en «Cómo se ha
    hecho»). En el móvil, más alto y con los nombres partidos; las etiquetas se reparten para
    no pisarse. Dónde va al final: en la reorganización de la web (prioridad 7).
    **Pendiente:** cifras por habitante y comparación con 2023 aprobado; que la Action pase
    `boe.hacienda` cuando haya edición nueva (hoy se lanza a mano: `python -m boe.hacienda
    --ediciones` dice si hay una).
  - **Prototipo** (25/11/2026, ya integrado):
    `exploracion/hacienda/prototipo_sankey.py` → `prototipo_sankey.html` (SVG propio, sin
    librerías). Ingresos → gasto de los capítulos 1 a 8 (480.626) → a elegir «¿A quién
    llega?» (transferencias por destinatario y pagos: personal, contratos, intereses,
    préstamos) o «¿A qué se dedica?» (políticas; las de menos del 2 %, juntas: 17 políticas,
    61.530). Propuesta: sección «El dinero de los Presupuestos» en «La legislatura», junto a
    «Gobernar sin Presupuestos», con su JSON aparte (`web/datos/presupuestos.json`, copiado
    por `exportar`); página propia cuando lleguen las subvenciones (pieza 3). Falta para
    integrarlo: versión móvil (lista o vertical), tabla accesible, etiquetas pequeñas que se
    pisan, decir que Sanidad y Educación salen pequeñas porque las gestionan las comunidades
    (van dentro de «Transferencias a otras Administraciones Públicas») y el texto de método
    en `web/como.html`.
  - El presupuesto prorrogado completo está además en HTML y en ZIP de 190 MB (no hace
    falta para el Sankey). Ejecución (Intervención General) y Base de Datos Nacional de
    Subvenciones también ofrecen Excel/CSV/JSON en el catálogo de datos abiertos.
- **Dónde se opacan los datos / cuidados:**
  - parte del IRPF y del IVA va directamente a las comunidades: el presupuesto del
    Estado no muestra todo lo que se paga en impuestos (decirlo);
  - presupuestado no es gastado: la ejecución (IGAE) llega después y con menos detalle;
  - prorrogado no es aprobado: decir siempre qué año se ve;
  - no contar dos veces (Estado → Seguridad Social → pensiones): cifras consolidadas;
  - cifras con contexto (por habitante, parte del total, frente al año anterior);
  - beneficiarios finales de contratos y subcontratas no siempre públicos;
  - nada de subvenciones a personas físicas;
  - neutralidad: mostrar el flujo, no si está bien o mal repartido.

### 3.3 Lo que el Gobierno promete legislar frente a lo que aprueba 💡

- **Pregunta:** ¿qué normas anunció el Gobierno en su Plan Anual Normativo,
  cuáles aprobó, con cuánto retraso y cuáles se quedaron sin hacer?
- **Fuentes a comprobar:** Plan Anual Normativo e Informe Anual de Evaluación
  Normativa (PDF en el Portal de Transparencia); el BOE para cruzar lo aprobado.
- **Por qué encaja:** «qué decide el Estado» visto desde la intención; pocos
  datos (cientos de normas al año) y bastante objetivos.
- **Dónde se opaca:** los títulos del plan son genéricos y no siempre coinciden
  con el de la norma final: habrá emparejamientos dudosos, que se marcan como tales.
- **Primer paso:** estado del arte y emparejar a mano el plan de un año con el BOE.

### 3.4 Los tribunales y las normas 🔎 (prioridad 4; idea ampliada por la autora el 24/11/2026)

- **Pregunta:** ¿en qué medida los tribunales cambian lo que decide el Estado? ¿Qué
  normas se recurren o se anulan, qué tribunal lo hace, quién recurre, cuánto tarda
  y qué decide? Antes era solo «normas en el Tribunal Constitucional».
- **Quién puede hacer qué** (para el explicador de la web):
  - **Tribunal Constitucional** (fuera del poder judicial): el único que puede
    anular **leyes** (de las Cortes, reales decretos-ley, leyes autonómicas). Vías:
    recurso de inconstitucionalidad (presidente del Gobierno, Defensor del Pueblo,
    50 diputados, 50 senadores, gobiernos y parlamentos autonómicos), cuestión de
    inconstitucionalidad (un juez que duda de una ley que debe aplicar) y conflictos
    de competencia Estado–comunidades (enlaza con 2.5). Si el Gobierno recurre una
    ley autonómica puede pedir su suspensión automática mientras se decide.
  - **Tribunal Supremo, Sala Tercera:** no toca leyes, pero puede **anular
    reglamentos del Gobierno** (reales decretos) y suspenderlos cautelarmente. Si
    cree inconstitucional una ley, pregunta al Constitucional.
  - **Audiencia Nacional y tribunales superiores de justicia:** órdenes ministeriales
    y reglamentos autonómicos; lo autonómico sale en los boletines de cada comunidad,
    no en el BOE → «qué no cubrimos».
  - **Tribunal de Justicia de la UE:** puede obligar a inaplicar o cambiar normas
    españolas, pero no publica en el BOE → «qué no cubrimos».
  - **Tribunal de Cuentas:** fiscaliza cuentas; no anula normas (en el BOE solo
    salen sus propios acuerdos).
- **Llamada de prueba (24/11/2026, sección I ya guardada, ~1.800 normas a mitad de
  la descarga de la XV):** 88 providencias del Constitucional (admisiones a trámite
  de recursos y cuestiones de inconstitucionalidad, con los artículos recurridos),
  1 auto del Constitucional, 38 sentencias del Supremo (Sala Tercera; p. ej. «estima
  en parte el recurso… contra el Real Decreto 958/20…») y 16 autos del Supremo
  (p. ej. suspensión cautelar de una oferta de empleo público). Las sentencias del
  Constitucional van en la sección `T`, que hoy solo se cuenta (10 en 3 días de
  oct-nov de 2026).
- **Estado del arte:** la memoria anual del Constitucional (estadísticas) y el
  Boletín de Conflictividad del Ministerio de Política Territorial (trimestral, PDF,
  solo Estado–comunidades). Nadie sigue norma a norma qué recurso afecta a qué ley ni
  qué reglamentos anula el Supremo.
- **Qué haría falta:**
  1. Clasificar por reglas, a partir del título, cada publicación: tribunal, tipo de
     decisión (admite, suspende, estima, desestima, anula) y quién recurre.
  2. Enlazar con la norma afectada (el título la cita: «contra el Real Decreto
     958/2023», «en relación con la Ley 1/2023 de la Comunidad de Madrid»).
  3. Guardar también la sección `T` en `guardar` (barato).
  4. En la ficha, dentro de «¿Qué ha pasado después?»: «Recurrida ante el
     Constitucional por…», «Anulada en parte por el Supremo el…»; y un informe con
     las cifras de la legislatura.
- **Cuidados:** hechos, no argumentos (admitido, estimado, anulado, fecha); el
  Constitucional tarda años y muchos casos estarán pendientes: decirlo; «quién
  recurre» es un dato institucional (Gobierno, comunidad, grupo de diputados), sin
  etiquetas políticas.
- **Fuentes complementarias:** el índice de iniciativas del Congreso (138 recursos
  de inconstitucionalidad en la XV).
- ✅ **Clasificador hecho (24/11/2026, `boe/tribunales.py`, 8 pruebas):** tipo de
  asunto, decisión, quién lo promueve (categoría institucional; de una persona
  particular no se guarda el nombre), norma afectada, fecha y suspensión por el art.
  161.2. Medido con `exploracion/tribunales/medir.py` sobre 195 publicaciones de
  tribunales (191 decisiones sobre normas, a mitad de la descarga de la XV): tipo y
  decisión en todas; norma afectada en 175 (89 están en nuestros datos; el resto son
  normas anteriores a la XV o autonómicas); quién promueve: órganos judiciales 37,
  gobiernos autonómicos 35, entidades 32, Gobierno de España 19, diputados 11,
  senadores 5…; 14 suspensiones por el art. 161.2.
  - **Sesgo de la fuente (decirlo en la web):** el BOE solo publica las sentencias del
    Supremo que **anulan** una norma (28 estiman, 25 estiman en parte, 0 desestiman):
    no sirve para contar cuántos recursos pierde el Gobierno. Del Constitucional se
    publican sobre todo las admisiones a trámite; las sentencias van en la sección `T`.
  - ✅ (24/11/2026) La clasificación se guarda al descargar (campo `tribunal`, en
    `guardar.derivados_de_texto`; `python -m boe.guardar --textos` la recalcula).
  - **Pendiente:** guardar la sección `T`, enlazar con la ficha de la norma afectada («¿Qué ha pasado
    después?») y el informe con las cifras de la legislatura.
- **🔎 Llamada de prueba a la sección `T` (25/11/2026; crudo en `datos/crudo/sentencias_tc/` y
  `datos/crudo/sumarios_T.json`):**
  - Los 1.025 sumarios guardados traen **556 publicaciones de la sección `T`** (17/08/2023–nov. 2026): 406 recursos
    de amparo (casos de personas, con nombres: **fuera**), 102 recursos y 32 cuestiones de inconstitucionalidad,
    3 conflictos de competencia, 2 impugnaciones autonómicas, 2 cuestiones forales, 1 conflicto entre órganos,
    3 correcciones y 2 declaraciones sobre tratados. Sobre normas: **142** (124 sentencias y 17 autos).
  - **El XML de cada sentencia lo trae todo sin leer el texto:** en `analisis/referencias/anteriores`,
    «DICTADA en el Recurso 3726/2023» apunta a la **admisión a trámite** (id del BOE, sección I) y «DECLARA …»
    apunta a **cada norma juzgada** con su resultado en texto corto: «la inconstitucionalidad y nulidad de…»,
    «la desestimación en relación con…», «la pérdida sobrevenida del objeto…», «la inadmisión…», «su extinción…»
    (un «,» significa «lo mismo que la anterior»). El apartado «FALLO» lo confirma («ha decidido estimar…»),
    pero cuidado: hay frases con «ha decidido» citadas antes del fallo.
  - **Medido (124 sentencias):** 120 enlazan con la admisión y 120 con la norma juzgada. Resultado por norma
    juzgada: desestimación 81, nulidad ~56, pérdida de objeto 13, inconstitucional sin nulidad 10, extinción 4,
    inadmisión 4. **Solo 14 normas de nuestros datos (publicadas desde el 17/08/2023) tienen ya sentencia**
    (34 pares sentencia–norma; la Ley de amnistía, 20); el resto juzga normas anteriores a la legislatura.
  - **Cuánto tarda:** de las 136 admisiones de recursos y cuestiones de inconstitucionalidad publicadas en la
    sección I desde agosto de 2023, **62 tienen ya sentencia** en la sección `T` y 74 siguen pendientes. Entre la
    publicación de la admisión y la de la sentencia (65 casos con las dos en nuestros datos): mediana **368 días**,
    mínimo 77, máximo 995. Ojo: los recursos admitidos antes de agosto de 2023 no tienen su admisión en nuestros
    datos, así que la mediana infravalora los más lentos (decirlo).
  - ✅ **Hecho (25/11/2026):** `boe/sentencias_tc.py` → `datos/sentencias_tc.json` (141: 124 sentencias, 17 autos; en la
    Action, solo lo nuevo de los sumarios de la semana); `informe.sentencias_tc`; «Qué decidió el Tribunal Constitucional»
    en «Qué dijeron los tribunales»; en la ficha, «¿Qué ha pasado después?» de la norma juzgada (más de dos: resumen por
    resultado) y de la admisión («Resuelto por la sentencia…»); las sentencias dan su fecha a los «Se declara» de la
    legislación consolidada. **Pendiente:** cuánto tarda contando también los admitidos antes de la legislatura (habría que
    descargar sus admisiones); qué pasó con los 14 conflictos del Senado (solo 1 tiene sentencia).
  - **Propuesta original:** `boe/sentencias_tc.py` que guarde por sentencia (sin amparos): tipo, fecha, admisión (id) y
    normas juzgadas con su resultado; en la ficha de la norma juzgada, «¿Qué ha pasado después?» («El Tribunal
    Constitucional desestimó el recurso…, sentencia del…»); en la ficha de la admisión, si ya hay sentencia;
    y en «Qué dijeron los tribunales», cuántas admisiones están resueltas, cuánto tardaron y con qué resultado.
    Los autos (levantar o mantener la suspensión) pueden ir aparte.

### 3.5 Directivas europeas: transposición y retrasos 💡

- **Pregunta:** ¿cuánto tarda España en transponer las directivas, en qué temas y
  cuántas veces la advierte o lleva al Tribunal de Justicia la Comisión?
- **Fuentes a comprobar:** EUR-Lex (medidas nacionales de transposición de cada
  directiva) y la base de datos de procedimientos de infracción de la Comisión;
  las normas del BOE cuyo título dice «se transpone la Directiva…».
- **Por qué encaja:** explica parte del «por qué» de muchas normas: la obligación
  viene de la UE, a menudo con el plazo vencido.
- **Dónde se opaca:** el enlace directiva–norma nacional no siempre es completo.

### 3.6 Empleo público: qué plazas se convocan 💡

- **Pregunta:** ¿cuántas plazas públicas se convocan, de qué cuerpos y
  administraciones, y cómo cambia con el tiempo?
- **Fuente:** la sección II.B del BOE (oposiciones y concursos), ya en nuestros
  sumarios: es el 17 % de lo publicado y hoy solo se cuenta.
- **Por qué encaja:** datos que ya tenemos y útiles para mucha gente. Es el más barato.
- **Cuidado:** solo convocatorias y número de plazas; nunca listas de admitidos o
  aprobados (llevan nombres).
- **Dónde se opaca:** el número de plazas está en el texto de la convocatoria, no
  en el sumario: hay que extraerlo, con riesgo de error.

### 3.7 Convenios entre administraciones 💡

- **Pregunta:** ¿quién colabora con quién (ministerios, comunidades,
  universidades, entidades), para qué y con cuánto dinero cuando el convenio lo dice?
- **Fuente:** la sección III del BOE, ya en nuestros sumarios.
- **Por qué encaja:** enlaza con el gasto público (3.2) y es otra parte del BOE
  que hoy solo contamos.
- **Dónde se opaca:** el importe está en el texto, no en los metadatos.

### 3.8 ¿Se consultó a la ciudadanía antes de aprobar la norma? 💡

- **Pregunta:** ¿qué normas pasaron por consulta pública previa y audiencia,
  cuánto tiempo estuvo abierta y cuáles se aprobaron sin ella (los decretos-ley,
  por ejemplo, no la tienen)?
- **Fuentes:** las webs de participación de cada ministerio (no hay registro
  central).
- **Por qué encaja:** transparencia sobre cómo se decide, no solo sobre qué.
- **Dónde se opaca:** muy dispersa; quizá solo sea viable una muestra.

---

### 3.9 Presupuestado frente a gastado 🔎 (idea de la autora del 25/11/2026)

- **Pregunta:** de lo que se presupuestó en la legislatura (los de 2023 y sus prórrogas),
  ¿cuánto se gastó de verdad, en qué se gastó de más o de menos y cuánto cambió el
  presupuesto por el camino (créditos extraordinarios, suplementos, ampliaciones)? Enlaza
  con 3.2: el Sankey enseña lo previsto; esto, lo que pasó.
- **Ojo con el calendario:** la ejecución va por años naturales, no por legislaturas. La
  XV (17/08/2023 – 06/10/2026) toca 2023, 2024, 2025 y parte de 2026; los años completos
  cerrados son 2024 y 2025.
- **Llamada de prueba (25/11/2026, `exploracion/hacienda/ejecucion/`): ✅ hay datos.**
  - La **Intervención General (IGAE)** publica cada mes la ejecución del presupuesto **del
    Estado** en Excel (`MENSUAL SEPTIEMBRE 2026.xlsx`, 690 KB, miles de euros, acumulado
    hasta fin de mes y comparado con el año anterior): por capítulo, sección (ministerio),
    programa y capítulo, con **créditos iniciales, créditos definitivos (con las
    modificaciones), obligaciones reconocidas y pagos**. La página solo enlaza 2026 (enero a
    septiembre); `MENSUAL DICIEMBRE 2025.xlsx` existe aunque no está enlazado, y los de
    diciembre de 2024 y 2023 **no están con ese nombre** (buscar dónde están los años
    anteriores). Licencia: aviso legal de Hacienda (datos.gob.es lo cita como licencia).
  - Solo el **Estado**: la Seguridad Social y los organismos van aparte (ejecución de
    organismos en datos.gob.es; la Seguridad Social, por comprobar). No es directamente
    comparable con el consolidado del Sankey: comparar Estado con Estado (archivo 02).
  - Cierre oficial: la **Cuenta General del Estado** (IGAE) y la declaración del Tribunal de
    Cuentas. **Ya sale en el BOE que guardamos:** el dictamen de la Comisión Mixta Congreso–
    Tribunal de Cuentas sobre cada Cuenta General (p. ej. BOE-A-2026-23477, BOE-A-2025-21699),
    con unos dos o tres años de retraso.
- **Qué saldría:** por año, «aprobado → definitivo → gastado (obligaciones) → pagado», por
  capítulo y por ministerio o política; cuánto creció el crédito con las modificaciones
  (cruzar con los créditos extraordinarios que ya detecta `boe.presupuestos`, prioridad 5
  pieza 2) y qué quedó sin gastar (p. ej. inversiones, fondos europeos).
- **Cuidados:** obligación reconocida no es pago; los créditos definitivos incluyen dinero
  de años anteriores (remanentes, fondos europeos), así que «gastar más de lo aprobado» no
  es siempre gastar más; comparar mismos ámbitos (Estado con Estado); dato mensual =
  acumulado provisional hasta el cierre.
- **Encontrados los cierres (25/11/2026):** cada año tiene su página
  (`…/EjecucionPresupuestaria/Paginas/imejecucionpresupuesto2023.aspx`, …2024, …2025) y el
  diciembre se llama `MENSUAL DICIEMBRE 2023 (EXCEL).xlsx`, `… 2024 (EXCEL).xlsx` y
  `MENSUAL DICIEMBRE 2025.xlsx` (descargados en `exploracion/hacienda/ejecucion/descargas/`).
  La hoja clave es **`GTOS 008`** (por políticas; `GTOS 007` por ministerios, `GTOS 009` por
  artículos): créditos iniciales, modificaciones, definitivos, gastos comprometidos,
  obligaciones reconocidas, **pagos realizados**, obligaciones pendientes de pago y
  remanentes (lo no usado). Totales del Estado, millones de euros:

  | Año | Inicial | Modificaciones | Definitivo | Comprometido | Obligaciones | Pagado | Pendiente de pago | Sin usar |
  |---|---|---|---|---|---|---|---|---|
  | 2023 | 386.088 | 20.995 | 407.083 | 375.965 | 371.289 | 351.638 | 19.650 | 35.794 |
  | 2024 | 380.822 | 52.341 | 433.163 | 414.467 | 408.564 | 387.996 | 20.568 | 24.600 |
  | 2025 | 380.822 | 76.944 | 457.766 | 427.012 | 423.336 | 398.547 | 24.789 | 34.430 |

  Ejemplo: «Infraestructuras y ecosistemas resilientes» 2025: inicial 10.906, definitivo
  16.978, comprometido 8.411, obligaciones 7.024, pagado 5.619 y sin usar 9.954.
- **Cómo se sabe qué está pagado:** cuatro escalones. *Comprometido*: hay un contrato o
  una resolución con importe. *Obligación reconocida*: el servicio se ha prestado y el
  Estado reconoce que debe pagar. *Pago realizado*: el dinero ha salido. *Pendiente de
  pago* = obligaciones − pagos a 31 de diciembre; se paga al año siguiente y aparece como
  pago de **«presupuestos cerrados»** (`GTOS 013`): en 2024 se pagaron 16.104 de años
  anteriores (a fin de 2023 quedaban 19.650 pendientes) y en 2025, 14.370. Los cerrados
  mezclan años: para seguir una obligación concreta haría falta más detalle. `GTOS 012`
  añade los «pagos pendientes de aplicación» (pagos hechos que aún no se han imputado al
  presupuesto: cifras pequeñas, pueden ser negativas).
- **Sorpresa:** aquí «Pensiones» son ~20.500 millones, no 190.000: es solo el Estado (clases
  pasivas); las de la Seguridad Social van en su propio presupuesto y su ejecución.
- **Seguridad Social (25/11/2026, `exploracion/hacienda/ejecucion/seguridad_social/`):** la
  publica su Intervención General cada mes, **solo en PDF** (no se ha encontrado Excel):
  `https://www.seg-social.es/descarga/es/L_Sistema_<Mes>_<Año>.pdf` (sistema agregado;
  `L_Entidades_…` por entidad). Hay que seguir una redirección (`curl -L`). De 2024 y 2025
  solo existe el **«Diciembre Provisional»** (`L_Sistema_Diciembre Provisional_2024.pdf`);
  el definitivo no está con ese nombre (buscar en la Cuenta General de la Seguridad Social).
  El texto se extrae bien con `pypdf` (ya instalado): una fila por línea en 2024 y 2025,
  una cifra por línea en 2023. Trae, por capítulo y con el capítulo 4 desglosado (pensiones
  por clase, incapacidad temporal, nacimiento y cuidado…), presupuesto inicial,
  modificaciones, total, obligaciones reconocidas y pagos. Millones de euros, acumulado a
  diciembre:

  | Año | Inicial | Modificaciones | Total | Obligaciones | Pagado | De ello, pensiones (obligaciones) |
  |---|---|---|---|---|---|---|
  | 2023 | 209.177 | 7.704 | 216.881 | 213.341 | 213.227 | 161.067 |
  | 2024 (provisional) | 208.980 | 26.447 | 235.426 | 231.973 | 231.796 | 172.666 |
  | 2025 (provisional) | 208.980 | 39.195 | 248.175 | 244.916 | 244.780 | 182.526 |

  Sorpresas: casi todo lo reconocido se paga en el año (pendiente de pago < 0,1 %,
  frente al ~5 % del Estado), y con el presupuesto prorrogado las pensiones se presupuestan
  igual cada año (159.526) y se completan con modificaciones (13.288 en 2024, 23.082 en 2025).
- **Por comprobar:** el inicial de 2023 del PDF (209.177) no coincide con el presupuesto de
  la Seguridad Social del archivo 03 de Hacienda (204.220). El PDF da «estados agregados»
  y la diferencia (~4.960) se parece a las transferencias entre entidades de la propia
  Seguridad Social («A la Seguridad Social», 4.726 en 2023): confirmarlo antes de usar cifras.
- **Para sumar Estado y Seguridad Social** hay que quitar lo que el Estado transfiere a la
  Seguridad Social (si no, se cuenta dos veces); la IGAE no publica un consolidado mensual.
- **Primer paso:** `boe/ejecucion.py` que lea `GTOS 008` y `GTOS 013` de los diciembres
  2023–2025 (y el último mes de 2026) y las tablas de gasto acumulado de los PDF de la
  Seguridad Social, comprobando que los iniciales coinciden con los archivos 02 y 03 de
  Hacienda.

## Relaciones entre lo público y lo privado

**BORME** (cargos en empresas), **nombramientos y ceses** (sección II.A),
**indultos** y **registros de intereses** son datos de personas concretas: se
tratan solo en cifras agregadas. Lo que encaja es mirar la estructura:

- **Relaciones entre instituciones:** ministerio ↔ empresa o entidad a través de
  contratos, subvenciones o convenios (ver 3.2 y 3.7).
- **Cifras agregadas y oficiales sobre «puertas giratorias»**, si existen: por
  ejemplo, los informes de la Oficina de Conflictos de Intereses sobre
  incompatibilidades de antiguos altos cargos (comprobar qué publican).
- **Relaciones de un solo salto**, documentadas en una fuente oficial y con fecha,
  sobre cargos públicos en el ejercicio del cargo (como ya hace la ficha cuando
  dice qué órgano firma una norma).

---

## Orden de trabajo

Está en **«Prioridades»**, al principio de este documento (24/11/2026). Ya hecho del
orden anterior: diseño para el público general salvo los «más grandes» (sección 0),
el hueco S42–S46 y la portada con la última semana completa, y las decisiones que
se votan (2.3, con las cifras de las leyes desde el 25/11/2026: 2.3b). Hecho el 24/11/2026: prioridades 1 y 2, la
descarga y la primera parte del informe (3), la guía (parte de la 7) y las votaciones por grupo (2.1, acotado). Hecho el
25/11/2026: seguridad (1b), prioridad 4 (tribunales con la sección `T`), buena parte de la 15 (el Senado) y la vida de
las normas de 2024–2025.
