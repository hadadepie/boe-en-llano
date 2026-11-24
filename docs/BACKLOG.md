# Backlog — El BOE en llano

Última actualización: 24/11/2026 (tras el repaso del estado del arte, la idea de
competencias y las prioridades). Ideas y proyectos pendientes; el orden de trabajo
está en «Prioridades», justo debajo. El estado del proyecto está en `docs/ESTADO.md`.

## Prioridades (propuesta del 24/11/2026, pendiente de que la confirme la autora)

**Enfoque:** resumir el BOE día a día ya lo hacen al menos cinco webs, y las
votaciones del Congreso por grupo, otras dos (ver «Estado del arte general»). Lo
que no hace nadie: **lo que el Estado decide sin votación**, **qué pasa después con
cada norma**, **con qué competencia se dicta** y todo con método y código abiertos.
Por eso la apuesta es **informes y gráficos guiados** (pregunta → gráfico → frase de
lectura → normas de ejemplo) y **competencias**, y enlazar a las demás webs en lo
que ya hacen bien en vez de repetirlo.

| # | Qué | Dónde está | Tamaño | Por qué en este orden |
|---|---|---|---|---|
| 1 | **Fichas sin IA**, con **«¿Con qué competencia?»** | 1 y 2.5 (pieza 1) | Corto | Las 343 fichas están «pendiente»: es lo más débil de la web. Todo lo que se añade es texto oficial. |
| 2 | **Ajustes pequeños**: bienvenida, `ESTADO.md`, enlaces a otras webs, RSS | 1 | Corto | Baratos; el RSS resuelve parte de «quien no entra cada semana». |
| 3 | **Informe «La XV legislatura: quién decidió y qué pasó después»** | 2.4 | Medio (descarga de 1–2 h, avisando antes) | Oportuno: Cortes disueltas desde el 06/10/2026; las nuevas se constituyen el 23/12/2026. |
| 4 | **Explicador «¿Quién decide qué?»** (Estado, comunidades, ayuntamientos por tema) | 2.5 (pieza 2) | Medio (texto a mano, revisión de la autora) | Da contexto a la pieza 1 y al informe. |
| 5 | **Portada más ligera** y página **«Cómo leer el BOE en llano»** | 0 | Medio | Con el informe y el explicador hechos, la portada puede enlazarlos en vez de explicarlo todo. |
| 6 | **Qué competencias usa el Estado y cuáles acaban en conflicto** | 2.5 (pieza 3), 3.4 | Medio | Cruza el título competencial con el Boletín de Conflictividad y el Constitucional. |
| 7 | Qué hace el Congreso, **fase B** (de dónde vienen las leyes) | 2.2 | Medio | La fase A se recorta (ver 2.1): ya la cubren otros. |
| 8 | Promesas frente a hechos (3.3) | 3.3 | Medio | Fuente oficial y pregunta que casi nadie contesta con datos. |
| 9 | Empleo público (3.6) | 3.6 | Corto–medio | El más barato: los datos ya están. |
| 10 | Gasto público (3.2) y convenios (3.7) | 3.2, 3.7 | Grande | |
| 11 | Directivas europeas (3.5) y consultas públicas (3.8) | 3.5, 3.8 | Grande | |
| 12 | Comunidad de Madrid (3.1) | 3.1 | El más grande | Mejor cuando la cadena esté madura; enlaza con competencias. |

Las demás mejoras cortas de la sección 1 se hacen cuando se toque el código afectado.

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
  contrastar»; sin código publicado. **Para el detalle de votaciones, enlazarla.**
- [El Congreso en datos (Bocal)](https://espanaendatos.bocal.online/congreso/): gráficos
  de coincidencia entre partidos, quién gana las votaciones, decretos-ley derogados;
  análisis puntual con datos descargables.
- [Electomanía](https://electomania.es/radiografia-del-decreto-ley-en-espana-747-aprobados-16-rechazados-13-en-el-ultimo-gobierno/):
  radiografía de los decretos-ley 1977–2026 por legislatura (artículo único).
- CEOE, «Producción normativa» (anual): cuántas normas y páginas se publican.

**Otros:** *El BOE nuestro de cada día* (Civio, desde 2012, periodismo) y
[BOE-XSUM](https://arxiv.org/html/2509.24908v1) (UNED): 3.648 normas del BOE con su
resumen en lenguaje claro de máximo 280 caracteres, útil para medir un modelo de IA.

**Hueco:** ninguna sigue lo que pasa con las normas aprobadas (solo las derogaciones
de decretos-ley), ninguna mira lo que se decide sin votar, ninguna dice con qué
competencia se dicta cada norma y ninguna publica su código.

## Cómo se trabaja cada propuesta

Nada pasa a programarse sin estos pasos, en este orden:

1. **Estado del arte.** ¿Existe ya? ¿Quién lo hace y cómo? ¿Qué aportaríamos?
   Si alguien lo hace bien, enlazarlo puede ser mejor que repetirlo.
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
- **Portada más ligera** (prioridad 5): hoy tiene siete bloques (titulares, embudo,
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
| **Fichas sin IA** (prioridad 1) | Las 343 fichas están «pendiente»: la web promete «explicado» y solo da el titular corto y el preámbulo. | Rellenar con lo que ya es oficial: «¿Qué es?» con el objeto del preámbulo, «¿Desde cuándo?» con la entrada en vigor de consolidada (o `fecha_vigencia`), materias, y **«¿Con qué competencia?»** (ver 2.5). Sin inventar nada: lo que no esté, «pendiente». |
| **Bienvenida: «qué te afecta»** (prioridad 2) | La bienvenida de la portada aún dice «qué te afecta»; el resto de la web ya usa «Afecta a mucha gente». | Cambiar el texto en `web/index.html`. |
| **Contradicción en `docs/ESTADO.md`** (prioridad 2) | «Decisiones tomadas» dice repositorio privado y Pages desactivado; «Próximos pasos» (5) dice web publicada y repositorio público. | Comprobar cuál es cierto y dejar una sola versión. |
| **Enlazar a quien ya lo hace** (prioridad 2) | Para el voto de cada diputado y el resumen diario hay webs que lo hacen (ver «Estado del arte general»). | En la ficha de un decreto-ley y en «La legislatura», enlace a El Congreso en tu mano; en «Cómo se ha hecho», una línea con las demás. |
| ✅ **Rellenar el hueco S42–S46** (24/11/2026) | Faltan cinco semanas (oct–nov 2026): sin edición, su seguimiento no sale en ninguna portada y los gráficos de evolución tendrían un agujero. | Lo más importante de esta lista. Hecho: no era un fallo de la Action (solo existe desde el 22–23/11): se habían bajado dos tandas locales y quedó sin bajar del 12/10 al 14/11. Se lanzó `boe.principal --desde 2026-10-12 --hasta 2026-11-14` sin IA: +30 días y +143 normas, 14 ediciones en total. Pendiente: sus fichas siguen «pendiente» como todas. |
| ✅ **Portada con la última semana completa** (24/11/2026) | Los lunes la edición en curso tiene 1–2 normas y la portada queda casi vacía. | Hecho: se abre la semana anterior mientras la en curso tenga menos de 3 días con datos (`DIAS_MINIMOS_EDICION` en `app.js`); un aviso con botón lleva a la en curso. |
| **«Derogado/modificado después» en semanas antiguas** | Complemento del bloque de seguimiento: quien mira una semana pasada ve el aviso en el mosaico y las listas. | Datos ya disponibles (vida de la norma y votaciones). |
| **Pieza de «La semana en datos» y seguimiento** | «7 convalidados» y la lista de seguimiento cuentan lo mismo. | Decidir si la pieza sobra. |
| **Mosaico (portada) y matriz (Explorar)** | Muestran la misma información de dos formas. | Esperar a usar la web un tiempo; si molesta, la matriz puede ser el mosaico con filtro. |
| **Legislatura fuera de `indice.json`** | El índice pasó de 38 a 55 KB y la portada no lo necesita. | Un `legislatura.json` que solo cargue su página y la ficha de un RDL. |
| **Detalles técnicos de la revisión** | `escribir()` borra `web/datos/` antes de escribir; la semana lleva campos que solo usa la ficha; `cache: "no-cache"` en todos los JSON. | Ganancias pequeñas; hacerlas cuando se toque `exportar`. |
| **Modelo de IA mejor para las fichas** | Todas las fichas siguen pendientes (gemma3:4b no supera el validador). | Probar un modelo más capaz sin coste; el validador ya existe. |
| **Partidos dentro de coaliciones** | La lista electoral no distingue partidos dentro de una coalición. | Tabla manual con fuente para cada caso. |
| **Decretos-ley votados por la Diputación Permanente** | El filtro «¿Se votó?» los deja en «pendiente o sin datos» aunque el BOE publique su acuerdo. | `boe.legislatura.acuerdos_boe` ya los conoce: marcarlos como votados (sin cifras). |
| **Sección `T` del gráfico por sección** | El BOE trae una sección `T` (Tribunal Constitucional) que `exportar` no conoce: avisa y no la dibuja. | Añadirla a `SECCIONES_WEB` o agruparla; enlaza con 3.4. |
| **Comprobar `buscar.json` en la Action** | El buscador depende de que el despliegue genere `web/datos/buscar.json`. | Lanzar «solo publicar» y probar «vivienda» en la web publicada. |
| **Seguimiento vacío en S42–S45** | Tras rellenar el hueco, esas semanas salen sin «qué ha pasado con normas anteriores». | Comprobar si es real o si falta consolidada/votaciones. |
| **Fichas de las 143 normas nuevas (S42–S46)** | Siguen «pendiente» como todas. | Depende de «Modelo de IA mejor». |
| **Canal RSS** (prioridad 2) | Seguir la web sin entrar. | Barato: un `feed.xml` generado en `exportar`. |

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
  Para el voto de cada diputado, enlazar a El Congreso en tu mano.
- **Momento:** Cortes disueltas desde el 06/10/2026; las nuevas se constituyen el
  23/12/2026.
- **Dónde se quedan cortos los datos:** las normas guardadas empiezan a finales de
  agosto de 2026 (343); solo los decretos-ley cubren toda la XV. Hace falta
  **descargar la sección I desde agosto de 2023**: unos 800 sumarios más el texto de
  cada norma, con 1 s de pausa, entre una y dos horas, sin IA. **Avisar antes de
  lanzarlo.** Las cifras de otras webs no coinciden entre sí para la XV (por cómo
  cuentan lo aprobado con las Cortes disueltas): explicar nuestro criterio.
- **Dónde iría:** una página nueva de informes (o dentro de «La legislatura»).
- **Primer paso:** llamada de prueba con un mes de 2023 (cuánto ocupa y si las
  estructuras del sumario son las mismas) antes de la descarga completa.

### 2.5 Competencias: quién decide qué 🔎 + prueba hecha (prioridades 1, 4 y 6)

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
  1. **En cada ficha, «¿Con qué competencia?»** (prioridad 1, con las fichas sin IA):
     el artículo citado, extraído de la disposición final, y una frase fija por
     artículo («permite al Estado fijar las bases de la economía»). Normas
     autonómicas: citan su estatuto; empezar por las estatales.
  2. **Explicador fijo «¿Quién decide qué?»** (prioridad 4): tabla con nuestros ocho
     temas y, para cada uno, qué hace el Estado (exclusiva / bases), las comunidades
     (desarrollo / gestión) y los ayuntamientos, con el artículo de donde sale cada
     casilla. Escrito a mano desde las fuentes oficiales y revisado por la autora.
  3. **Qué competencias usa el Estado y cuáles acaban en conflicto** (prioridad 6):
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

### 3.2 Gasto público: a dónde va el dinero 💡

- **Idea:** seguir el dinero desde la decisión (presupuesto, real decreto,
  convocatoria) hasta quién lo recibe.
- **Ya existe mucho:** *¿Dónde van mis impuestos?* (Civio) explica los
  Presupuestos; hay trabajos periodísticos sobre contratos y fondos europeos.
  El estado del arte decidirá si aportamos algo o si basta con enlazar.
- **Puente natural con lo que ya tenemos:** cada semana contamos «subvenciones o
  préstamos de concesión directa a entidades concretas» (sección I) y el BOE
  publica anuncios de contratos (sección V). Unir eso con:
  - la **Base de Datos Nacional de Subvenciones** (importes y beneficiarios de
    subvenciones; comprobar su API);
  - la **Plataforma de Contratación del Sector Público** (licitaciones y
    adjudicaciones en datos abiertos);
  - los **Presupuestos** y su **ejecución** (Hacienda / IGAE);
  - los fondos del **Plan de Recuperación**.
- **Pregunta abarcable para empezar:** «Las subvenciones directas aprobadas por
  real decreto esta semana: a quién, cuánto y para qué», cruzando cada norma con
  su registro en la Base de Datos Nacional de Subvenciones.
- **Dónde se opacan los datos:**
  - beneficiarios finales de contratos y subcontratas (no siempre públicos);
  - inversiones territorializadas: lo presupuestado por provincia es público,
    lo ejecutado lo es con menos detalle y más tarde;
  - presupuestos prorrogados: sin presupuesto nuevo, comparar «previsto frente
    a ejecutado» se complica;
  - datos personales: subvenciones a personas físicas (no publicarlas).
- **Riesgo:** cifras grandes sin contexto alimentan titulares fáciles. Cada
  cifra con su comparación (por habitante, frente al año anterior o al total).
- **Primer paso:** estado del arte (Civio y otros) y llamada de prueba a la Base
  de Datos Nacional de Subvenciones con una subvención de concesión directa que
  ya tengamos en `datos/normas/`.

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

### 3.4 Las normas que acaban en el Tribunal Constitucional 💡

- **Pregunta:** ¿qué leyes se recurren, quién las recurre (Gobierno, comunidades,
  grupos de diputados), cuánto tarda el Tribunal y qué decide?
- **Fuentes:** el propio BOE (admisiones a trámite de recursos y cuestiones de
  inconstitucionalidad y sentencias); el índice de iniciativas del Congreso
  (138 recursos de inconstitucionalidad en la XV legislatura).
- **Por qué encaja:** continuación natural de «¿Qué ha pasado después?», con la
  misma fuente.
- **Dónde se opaca:** el Tribunal tarda años (muchos casos pendientes) y el fondo
  de una sentencia es difícil de resumir sin interpretar: quedarse en hechos
  (admitido, estimado, desestimado, fecha).
- **Primer paso:** estado del arte y localizar en los sumarios cómo aparecen esos
  anuncios y sentencias.
- **Pista (24/11/2026):** los sumarios traen una sección `T` («T.C. Sección del Tribunal Constitucional», sentencias) que `exportar.agrupar_recuento` no conoce: avisa «sección desconocida 'T'» y esas publicaciones (10 en 3 días de oct-nov) no salen en el gráfico por sección. Hoy `guardar` solo conserva la sección I.

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
se votan (2.3, sin cifras de leyes: 2.3b).
