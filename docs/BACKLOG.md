# Backlog — El BOE en llano

Última actualización: 24/11/2026, noche (parte 2 del informe: decretos-ley tramitados como ley y
tribunales; «Gobernar sin Presupuestos»; tareas de créditos; nueva idea: el Senado, 2.7; estado del
arte de esta actualización).

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
| 1 | ✅ (24/11/2026) **Fichas sin IA**, con **«¿Con qué competencia?»** | 1 y 2.5 (pieza 1) | Corto | Las 343 fichas están «pendiente»: es lo más débil de la web. Todo lo que se añade es texto oficial. |
| 2 | ✅ (24/11/2026) **Ajustes pequeños**: bienvenida, `ESTADO.md`, RSS (enlaces a otras webs: descartado) | 1 | Corto | Baratos; el RSS resuelve parte de «quien no entra cada semana». |
| 3 | 🔄 (24/11/2026: descarga hecha; publicados «Quién decidió» —por vía, mes a mes, tema, entrada en vigor, leyes—, «Cómo votó cada grupo» y los 43 decretos-ley tramitados como ley; falta «normas modificadas o derogadas», que espera la vida de las normas de 2024–2026) **Informe «La XV legislatura: quién decidió y qué pasó después»** | 2.4 | Medio (descarga de 1–2 h, avisando antes) | Oportuno: Cortes disueltas desde el 06/10/2026; las nuevas se constituyen el 23/12/2026. |
| 4 | 🔄 (24/11/2026: publicado «Qué dijeron los tribunales» con la sección I; falta la sección `T`, sentencias del Constitucional, y cuánto tarda) **Los tribunales y las normas**: qué normas se recurren o anulan, qué tribunal, quién recurre y cuánto tarda | 3.4 | Medio | Completa el informe: este cuenta quién decidió; aquello, quién lo corrigió después. Los datos llegan con la descarga de la XV (sección I) más la sección `T`. |
| 5 | 🔄 (24/11/2026: hecha la pieza 2, «Gobernar sin Presupuestos», en «La legislatura», sin importes; prueba con Hacienda para el Sankey: viable) **El dinero público: de dónde viene y a dónde va** (Sankey de los Presupuestos, gobernar sin presupuestos, subvenciones directas) | 3.2 | Grande (fuente nueva: Hacienda) | Pregunta muy oída («cuesta aprobar los Presupuestos») y sin respuesta gráfica de origen → destino público o privado; «gobernar sin presupuestos» se mide con el BOE que ya tenemos. |
| 6 | **Explicador «¿Quién decide qué?»** (Estado, comunidades, ayuntamientos por tema) | 2.5 (pieza 2) | Medio (texto a mano, revisión de la autora) | Da contexto a la pieza 1 y al informe. |
| 7 | 🔄 (24/11/2026: hecha la `guia.html` y quitados dos duplicados de Explorar; falta aligerar la portada) **Portada más ligera** y página **«Cómo leer el BOE en llano»** | 0 | Medio | Con el informe y el explicador hechos, la portada puede enlazarlos en vez de explicarlo todo. |
| 8 | **Qué competencias usa el Estado y cuáles acaban en conflicto** | 2.5 (pieza 3), 3.4 | Medio | Cruza el título competencial con el Boletín de Conflictividad y lo que ya clasifique la prioridad 4 (tribunales). |
| 9 | Qué hace el Congreso, **fase B** (de dónde vienen las leyes) | 2.2 | Medio | La fase A se recorta (ver 2.1): ya la cubren otros. |
| 10 | Promesas frente a hechos (3.3) | 3.3 | Medio | Fuente oficial y pregunta que casi nadie contesta con datos. |
| 11 | Empleo público (3.6) | 3.6 | Corto–medio | El más barato: los datos ya están. |
| 12 | Convenios entre administraciones (3.7) | 3.7 | Grande | Enlaza con el dinero público (prioridad 5). |
| 13 | Directivas europeas (3.5) y consultas públicas (3.8) | 3.5, 3.8 | Grande | |
| 14 | Comunidad de Madrid (3.1) | 3.1 | El más grande | Mejor cuando la cadena esté madura; enlaza con competencias. |
| 15 | 🔄 (24/11/2026: publicada la pieza de conflictos ante el Constitucional; faltan enmiendas y vetos por ley) **El Senado: cómo interactúa y en qué influye** (por ordenar con la autora; propuesta: tras la prioridad 5) | 2.7 | Medio (fuente nueva: datos abiertos del Senado) | Ya tenemos 14 conflictos entre órganos constitucionales en el BOE, 12 promovidos por el Senado. Completa «quién decidió»: qué cambió o frenó la segunda cámara. |

Las demás mejoras cortas de la sección 1 se hacen cuando se toque el código afectado.

**Pendientes técnicos (24/11/2026), no son ideas nuevas:**
- **Vida de la norma de las normas antiguas** (`python -m boe.consolidada --desde … --hasta …`, por
  tandas, sin antes y después): hechas 2023 (276: 50 consolidadas) y las normas desde el 26/08/2026; faltan
  2024–2026 (~3.150 normas a ~4–5 s, ~4 h: de noche). Es la base de «normas modificadas o derogadas»
  (prioridad 3). ✅ La Action solo consulta los últimos 180 días y las consolidadas que ya tienen vida (no
  reintenta las no consolidadas) y no calcula el antes y el después de las antiguas. **Por decidir:** con
  todo cargado, ~800 consolidadas antiguas cada domingo (~1 h): refrescarlas por turnos.
- **Tras una descarga grande**, pasar también `boe.congreso`, `boe.tramitacion` y `boe.legislatura --rehacer`
  (anotado en `docs/ESTADO.md`).
- **Importes de los créditos** (prioridad 5, pieza 2): extraer el importe de cada párrafo de `creditos`
  con su unidad (euros, miles de euros, millones de euros; a veces en letra: «cuatrocientos millones
  (400.000.000) de euros») y revisarlos a mano en las 30 normas antes de publicar una suma. Cuidados: un
  párrafo puede conceder varios créditos; en algunos el importe va en una tabla aparte; no contar dos veces
  lo que un decreto-ley posterior modifica; decir siempre «concedido», no «gastado».

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
- **Portada más ligera** (prioridad 7): hoy tiene siete bloques (titulares, embudo,
  «¿Quién decidió?», mosaico, seguimiento, «La semana en datos», gestión interna) y
  pide entender mucho de golpe. Dejar tres (titulares, «¿Quién decidió?» y qué ha
  pasado con normas anteriores) y enlazar los informes y el explicador de
  competencias. Lo demás, a «Explorar».
- **Página «Cómo leer el BOE en llano»** para principiantes, con ejemplos (el
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

### 2.7 El Senado: cómo interactúa y en qué influye 🔄 (24/11/2026, idea de la autora)

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
- **Siguiente paso:** llamada de prueba a los datos abiertos del Senado y a las fases de `boe.tramitacion`
  de una ley de 2024 con enmiendas del Senado, para contar por ley enmiendas aprobadas, vetos y qué aceptó
  después el Congreso.
- **Cuidados:** neutralidad (contar vetos, enmiendas y conflictos; no valorar si son obstrucción o
  control); nada de votos individuales de senadores (solo agregados por grupo, como en el Congreso); la
  composición del Senado cambia por elección y por designación autonómica: decir de qué fecha es cada dato.

### 2.6 Más preguntas para los informes 💡 (24/11/2026)

Ideas para piezas de informe (pregunta → gráfico → frase de lectura → normas de
ejemplo). Ninguna tiene aún estado del arte propio; antes de programar, el método de
siempre.

| Idea | Pregunta | Datos | Coste | Notas |
|---|---|---|---|---|
| 🧪 (24/11/2026: clasificador hecho, `boe/vigencia.py`, 7 pruebas) **Entrada en vigor inmediata (*vacatio legis*)** ⭐ | ¿Cuántas normas se aplican al día siguiente de publicarse, sin tiempo para adaptarse? ¿Cambia por tipo de norma o ministerio? | Ya extraído: párrafo de entrada en vigor en `textos_oficiales` (240 de 343 normas recientes). Clasificar con reglas: «día siguiente», «mismo día», «a los N días», fecha concreta. | Bajo | Hecho, no valoración: hay motivos legítimos para la urgencia. **Medido (1.959 normas con párrafo de entrada en vigor, a mitad de la descarga de la XV):** día siguiente 65,7 %, mismo día 13,1 % (las resoluciones, 72 %), plazo 8,9 % (casi siempre 20 días), fecha concreta 6,9 %, mes siguiente 0,9 %, depende de otro hecho 1,6 % (acuerdos internacionales), sin clasificar 2,8 %; 180 con excepciones. Ningún real decreto-ley con plazo de espera. ✅ «días hábiles» y el encabezado de tabla «Aplicación provisional» (24/11/2026). Pendiente: llevarlo a la web y al informe. |
| **Mandatos pendientes** ⭐ | Cuando una norma dice «en el plazo de seis meses el Gobierno aprobará…», ¿se cumplió? | Texto de las normas (disposiciones finales y adicionales) + BOE posterior para encontrar la norma que lo cumple. | Medio-alto | La más novedosa: explica «por qué las cosas no salen». Enlaza con promesas frente a hechos (3.3). Emparejar mandato y cumplimiento será dudoso a veces: marcarlo. |
| **Las leyes que más cambian** | ¿Qué normas se modificaron más veces en la legislatura? ¿Cuánto dura una norma sin tocarse? | Vida de la norma (legislación consolidada): relaciones «se modifica» con fecha. | Medio | Depende de cargar la vida de la norma de toda la XV (por tandas). |
| **Leyes «escoba»** | ¿Qué leyes y reales decretos cambian a la vez muchas normas de temas distintos? | Lo que ya se hace para los decretos-ley (`boe.decretos_ley`: normas que modifica y sus temas), extendido a todo rango. | Medio | Ya hay un hallazgo con decretos-ley (los que modifican 10+ normas se derogaron más). Sin juicio: contar, no calificar. |
| **Correcciones de errores por ministerio** | ¿Cuántas veces hay que corregir lo publicado y quién? | Ya en los datos: rango «Corrección (errores o erratas)» y su departamento. | Bajo | Pista de calidad normativa; normalizar por cuántas normas publica cada ministerio. |

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
  - **Por comprobar:** si «Impuestos directos» (269.000) incluye las cotizaciones
    sociales en el consolidado (lo sugiere la cifra); que los impuestos indirectos
    (57.809) son solo la parte del Estado (el IVA se reparte con las comunidades); la
    licencia (no aparece en las páginas; mirar el aviso legal); y si hay archivo 2026-P.
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
se votan (2.3, sin cifras de leyes: 2.3b). Hecho el 24/11/2026: prioridades 1 y 2, la descarga y
la primera parte del informe (3), la guía (parte de la 7) y las votaciones por grupo (2.1, acotado).
