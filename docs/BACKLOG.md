# Backlog — El BOE en llano

Última actualización: 24/11/2026. Ideas y proyectos pendientes, ordenados de lo
más cercano a lo más lejano. El estado del proyecto está en `docs/ESTADO.md`.

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

## 0. Lo primero en la siguiente sesión: diseño para el público general

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

**Paquete rápido ✅ hecho y fusionado en `main` el 24/11/2026:**
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
- **Buscador de normas** por palabras del titular en todas las semanas (índice
  pequeño, ~20 KB).
- **Cabecera compacta fija** al bajar, con el selector de semana.
- **Más jerarquía visual:** franja del color del tema en la noticia principal,
  más aire entre secciones, menos gris.
- ✅ (rama `feature/te-afecta-revisar`, 24/11/2026) **Revisar «Te afecta a ti»:** renombrado a «Afecta a mucha gente» en toda la web, con nota de que es una estimación por reglas. Texto original del punto: promete mucho para una clasificación por reglas;
  «Afecta a mucha gente» es más exacto (neutralidad y honestidad).

**Más grandes:**
- **Página «Cómo leer el BOE en llano»** para principiantes, con ejemplos (el
  «Cómo se ha hecho» actual es método técnico).
- **Boletín semanal por correo o RSS** para quien no entra cada semana.
- **Tipografía propia:** fuente libre alojada en la web, sin servicios externos.

---

## 1. Mejoras de la web actual (cortas)

| Mejora | Por qué | Notas |
|---|---|---|
| **Rellenar el hueco S42–S46** | Faltan cinco semanas (oct–nov 2026): sin edición, su seguimiento no sale en ninguna portada y los gráficos de evolución tendrían un agujero. | Lo más importante de esta lista. Ver por qué no se descargaron (¿Action sin ejecutar?) y lanzar `boe.principal` para esas fechas. |
| **Portada con la última semana completa** | Los lunes la edición en curso tiene 1–2 normas y la portada queda casi vacía. | Mostrar por defecto la semana anterior hasta que la nueva tenga, por ejemplo, 3 días; la en curso sigue a un clic. |
| **«Derogado/modificado después» en semanas antiguas** | Complemento del bloque de seguimiento: quien mira una semana pasada ve el aviso en el mosaico y las listas. | Datos ya disponibles (vida de la norma y votaciones). |
| **Pieza de «La semana en datos» y seguimiento** | «7 convalidados» y la lista de seguimiento cuentan lo mismo. | Decidir si la pieza sobra. |
| **Mosaico (portada) y matriz (Explorar)** | Muestran la misma información de dos formas. | Esperar a usar la web un tiempo; si molesta, la matriz puede ser el mosaico con filtro. |
| **Legislatura fuera de `indice.json`** | El índice pasó de 38 a 55 KB y la portada no lo necesita. | Un `legislatura.json` que solo cargue su página y la ficha de un RDL. |
| **Detalles técnicos de la revisión** | `escribir()` borra `web/datos/` antes de escribir; la semana lleva campos que solo usa la ficha; `cache: "no-cache"` en todos los JSON. | Ganancias pequeñas; hacerlas cuando se toque `exportar`. |
| **Modelo de IA mejor para las fichas** | Todas las fichas siguen pendientes (gemma3:4b no supera el validador). | Probar un modelo más capaz sin coste; el validador ya existe. |
| **Partidos dentro de coaliciones** | La lista electoral no distingue partidos dentro de una coalición. | Tabla manual con fuente para cada caso. |
| **Canal RSS** | Seguir la web sin entrar. | Barato: un `feed.xml` generado en `exportar`. |

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

### 2.3 Las decisiones que se votan 💡

- **Idea:** una sección, o un filtro en toda la web, que separe lo que se vota
  en un parlamento de lo que decide el Gobierno o la Administración sin votación.
  Hoy la ficha ya lo dice («No se vota en el Parlamento…»), pero no se puede
  filtrar ni ver en conjunto.
- **Forma razonable:**
  1. un filtro «¿Se votó?» en «Explorar»: votado en el Congreso · aprobado por
     el Gobierno sin votación · norma autonómica · decisión de un tribunal;
  2. una cifra en la portada: «De las 52 normas de esta semana, X pasaron por
     una votación».
- **Hueco a cubrir:** solo recogemos las votaciones de los reales decretos-ley.
  Las **leyes** (votación de conjunto en el Pleno del Congreso; el Senado aparte)
  serían el siguiente paso, con las mismas reglas: cifras por grupo, nunca
  votos individuales.
- **Dónde se queda corto:** las leyes autonómicas se votan en 17 parlamentos con
  datos muy desiguales. Empezar por el Congreso y decirlo.
- **Primer paso:** estado del arte (¿alguien separa «votado / no votado» al
  explicar normas?) y llamada de prueba a las votaciones de una ley concreta en
  los datos abiertos del Congreso.

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

## Orden sugerido

0. **Diseño para el público general (sección 0), empezando por el paquete rápido.**
1. Rellenar el hueco S42–S46 y la portada con la última semana completa (base
   de todo lo demás).
2. Las decisiones que se votan (2.3): sale casi de lo que ya hay y responde a
   «quién decide».
3. Qué hace el Congreso, fases A y B (2.1 y 2.2), en la página de la legislatura.
4. Promesas frente a hechos (3.3) y normas en el Constitucional (3.4): fuentes
   oficiales, unidas a lo que ya hay, y preguntas que casi nadie contesta con datos.
5. Empleo público (3.6): el más barato, los datos ya están.
6. Gasto público (3.2) empezando por las subvenciones directas, que ya contamos,
   y convenios (3.7).
7. Directivas europeas (3.5) y consultas públicas (3.8).
8. Comunidad de Madrid (3.1): el más grande; mejor cuando la cadena esté madura.
