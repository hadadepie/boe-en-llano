# Estado del proyecto — El BOE en llano

Última actualización: 23/11/2026. Documento para retomar el trabajo (personas o
sesiones nuevas de Claude). Las reglas permanentes están en `CLAUDE.md`.

## Propósito
Entender **qué decide el Estado y por qué**, a partir del BOE. Público principal: la
propia autora (entender cómo y por qué se toman las decisiones); después, la
ciudadanía. Se prioriza la **utilidad** sobre la audiencia y la **transparencia**
(método publicado, correcciones, «qué no cubrimos») sobre el gancho.

## Ramas (GitHub: hadadepie/boe-en-llano, privado)
| Rama | Contenido |
|---|---|
| `main` | POC original: vista de datos (gráfico, matriz, lista filtrable, ficha lateral). Con las correcciones del validador y del sumario. |
| `edicion-semanal` | Web como periódico semanal (portada por relevancia, «La semana en datos», secciones por tema, breves, ficha como artículo). Action semanal (domingo 08:00 UTC). |
| `votaciones-congreso` | `edicion-semanal` + todo lo demás (la más completa): votaciones, preámbulo, diseño aligerado, vida de la norma, glosario, antes/después, tramitación, cifras de la legislatura. |
| `version-ligera` | `votaciones-congreso` aligerada: ficha en cuatro preguntas, portada ligera + página `datos.html`, datos partidos por semana y por ficha. |

Nada está fusionado en `main` salvo correcciones.

## Cadena de datos (`python -m boe.principal`)
1. `boe.guardar` — sumario diario del BOE (API) → `datos/recuentos.json` y `datos/normas/BOE-A-….json` (sección I) con metadatos del XML y **preámbulo** literal. `--revisar` relee sumarios en crudo y corrige.
2. `boe.clasificar` — tema, impacto y ámbito por reglas (con motivos).
3. `boe.resumir` — fichas. Sin IA: «pendiente» + título simplificado. Con IA: verificación estricta (citas por párrafo, números en los párrafos citados, vigencia, boletines).
4. `boe.congreso` — votación de convalidación de cada real decreto-ley (Pleno), agregada por grupo y por lista electoral cuando votan distinto.
5. `boe.tramitacion` — si se tramitó como proyecto de ley: pasos, resultado (p. ej. caducado), BOCG.
6. `boe.legislatura` — todas las convalidaciones del Pleno de la XV legislatura (cifras propias, con método).
7. `boe.consolidada` — «vida de la norma»: entrada en vigor oficial, qué modifica, qué le pasó después.
8. `boe.versiones` — antes/después de cada artículo modificado (desde la modificadora y desde la modificada).
9. `boe.exportar` — `web/datos/` (no versionado): `indice.json` (~38 KB), `semanas/<semana>.json` (25–113 KB, sin antes/después y con el primer párrafo del preámbulo) y `normas/<id>.json` (preámbulo completo, `cambios`, `cambios_recibidos`; se carga al abrir la ficha). En la rama `version-ligera`; las demás siguen con `web/datos.json` (~1,9 MB).

Ver la web: `.venv\Scripts\python.exe -m http.server 8000 --directory web` → http://localhost:8000

## Decisiones tomadas
- **IA**: solo para fichas; `gemma3:4b` local (Ollama) **no es fiable** (0 de 5 fichas superan el validador corregido). Las que lo superen se publicarían como «experimental». Pendiente probar un modelo mejor (sin API de Claude en el plan actual).
- **Privacidad en votaciones**: solo cifras agregadas (grupo, lista); el voto individual queda en `datos/crudo/`. El voto telemático cuenta como voto y no se muestra por persona (puede revelar salud/maternidad). Sin rankings de absentismo.
- **Neutralidad**: sin etiquetas políticas por norma; glosario neutral.
- **Datos**: `datos/crudo/` fuera de Git; se versionan los datos extraídos.
- **Repositorio privado**, web en local; Pages desactivado (casilla `publicar`).

## Rarezas de las fuentes (aprendidas a golpes)
- **Sumario BOE**: al menos 4 estructuras (dep>epígrafe>item, dep>item, dep>texto>item, dep>texto>epígrafe>item) → se recorre de forma genérica. Un elemento suelto llega como dict, no lista.
- **Cifras en el BOE**: miles con espacio («1 286») y números con letra («ciento veinte»).
- **Congreso, votaciones**: el índice por fecha (`targetDate`) da un JSON por votación; los nombres de fichero llevan marcas de hora distintas por formato (no se adivinan). Votaciones **por llamamiento**: solo PNG → totales leídos del texto del índice. **Diputación Permanente**: no está en datos abiertos. Telemático = asiento «-1».
- **Congreso, diputados**: con Cortes disueltas casi todos figuran «de baja»; la lista electoral (`FORMACIONELECTORAL`) no distingue partidos dentro de una coalición.
- **Legislación consolidada**: muchas normas no se consolidan (404); las recientes tardan días (404 temporal, se reintenta a los 2 días); el endpoint de bloques solo acepta XML; notas y referencias pueden venir como dict o lista; la **lista** de consolidada no sirve para contar (le faltan muchas normas).

## Correcciones registradas (también en la web)
Validador (miles con espacio y números con letra); sumario (cuarta estructura: 12 días y 10 normas perdidas en sep-oct); RDL 26 y 27/2026 (votados por llamamiento, aparecían «sin datos»).

## Próximos pasos
1. ~~Cerrar mejora 5~~ Hecho: `boe.legislatura` (819 días revisados). XV: 49 convalidados (42 Pleno + 7 Diputación Permanente según BOE), 14 derogados (1 por empate, RDL 8/2023), 9 sin votación publicada. Cuadra con Es la hora de la verdad (42/13 + 1 empate en el Pleno).
2. ~~Versión ligera~~ Hecho en `version-ligera` (23/11/2026):
   - **Ficha en cuatro preguntas** (`web/app.js`): ¿Qué es? · ¿Por qué? · ¿Quién la apoyó? · ¿Qué ha pasado después?, una línea cada una y desplegables. «¿Quién la apoyó?» sin votación: dice quién firma (reales decretos, órdenes, resoluciones no se votan) o que no se recoge (leyes estatales y autonómicas). «A favor/en contra» = voto mayoritario de cada grupo.
   - **Leer y explorar separados**: `index.html` + `portada.js` (titulares, la semana de un vistazo como barra HTML sin Chart.js, «La semana en datos» desplegable, temas, breves) y `datos.html` + `explorar.js` (gráfico, matriz, votaciones, lista, legislatura, «Cómo se ha hecho»). La edición viaja en `?e=`; las fichas se enlazan con `#BOE-…` en ambas páginas.
   - **Carga**: la portada descarga ~150 KB (antes 1,9 MB).
   - Pendiente de decidir: fusionar `version-ligera` en `votaciones-congreso` o en `main`.
3. Pendientes de más largo plazo: modelo de IA mejor para fichas; partidos dentro de coaliciones (tabla manual con fuentes); feed RSS; parlamentos autonómicos; publicar la web.
