# El BOE en llano

Una web que cada semana descarga lo publicado en el **Boletín Oficial del Estado**,
lo clasifica y lo explica en lenguaje sencillo para personas sin formación jurídica.

- Cuántas publicaciones hay cada día y en qué sección.
- Qué normas generales (sección I) se han aprobado, de qué tratan y a quién afectan.
- Una ficha por norma: qué cambia, a quién afecta, desde cuándo y qué hay que hacer,
  siempre con enlace al texto oficial.

> Proyecto no oficial y prueba de concepto. Los resúmenes son orientativos y **no son
> asesoramiento jurídico**: consulta siempre el texto oficial.

## La web: una edición semanal

La página funciona como un periódico semanal: portada con el titular principal y tres
secundarios (elegidos con reglas de relevancia explicadas en la propia web), «La semana
de un vistazo», «La semana en datos» (cuentas automáticas: reales decretos-ley, leyes
autonómicas, convalidaciones y derogaciones, subvenciones directas…), secciones por tema
y breves de gestión interna. Los datos de la semana (gráfico, matriz, votaciones, lista
filtrable, cifras de la legislatura) y el método están en una segunda página, «Explorar
los datos». Cada norma se abre como una ficha en cuatro preguntas (¿Qué es? · ¿Por qué? ·
¿Quién la apoyó? · ¿Qué ha pasado después?) que se despliegan para ver el detalle. Se
pueden consultar ediciones anteriores.

## Cómo funciona

```
API de datos abiertos del BOE
        │  sumario diario + XML de cada norma (con pausas y sin repetir descargas)
        ▼
boe/descargar.py ──► boe/guardar.py ──► boe/clasificar.py ──► boe/resumir.py ──► boe/exportar.py
                     recuentos y         tema, impacto y       ficha en llano       web/datos/
                     normas en datos/    ámbito (reglas o IA)  verificada              │
                                                                                       ▼
                                                                       web/ (HTML + CSS + JS, sin servidor)
```

| Carpeta / archivo | Qué hay |
|---|---|
| `boe/` | El código Python, un módulo por paso. `principal.py` los ejecuta todos. |
| `datos/recuentos.json` | Publicaciones por sección y día. **Se guarda en Git.** |
| `datos/normas/BOE-A-….json` | Una norma de la sección I: metadatos, clasificación y ficha. **Se guarda en Git.** |
| `datos/congreso/convalidaciones.json` | Votación de cada real decreto-ley en el Pleno del Congreso, **agregada por grupo** (y por lista electoral cuando votan distinto). **Se guarda en Git.** |
| `datos/congreso/votaciones_leyes.json` | Votación final de cada ley en el Pleno del Congreso (y la posterior al Senado, si la hubo), **agregada por grupo**. **Se guarda en Git.** |
| `datos/senado.json` | Qué hizo el Senado con cada texto que le llegó del Congreso (sin cambios, enmiendas, veto) y qué aceptó después el Congreso; enmiendas presentadas **por grupo**. **Se guarda en Git.** |
| `datos/sentencias_tc.json` | Sentencias y autos del Tribunal Constitucional sobre normas (sección T del BOE): admisión que resuelven y normas que juzgan, con el resultado. **Se guarda en Git.** |
| `datos/crudo/` | Respuestas de la API tal cual (temporal, fuera de Git). |
| `web/` | La web: `index.html` (portada), `datos.html` (explorar los datos de la semana), `legislatura.html` (lo que pasó en toda la legislatura), `como.html` (método, límites, glosario y correcciones) y `guia.html` (qué hay en la web y hasta dónde llegan los datos). `web/datos/` se genera (un índice, un JSON por semana y uno por ficha) y no se guarda en Git. |
| `tests/` | Pruebas automáticas (no se conectan a internet). |
| `.github/workflows/diario.yml` | La automatización semanal (domingos; también a mano). |

## Instalación

Necesitas **Python 3.11 o superior** y **Git**.

```powershell
git clone https://github.com/<tu-usuario>/boe-en-llano.git
cd boe-en-llano
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

En macOS o Linux, cambia `.\.venv\Scripts\python.exe` por `.venv/bin/python` en todos los comandos.

La Action instala con versiones exactas y hash (`requirements-ci.txt`). Si cambias
`requirements.txt`, regenera ese archivo con `python herramientas/bloquear.py`. Para avisar de un
fallo de seguridad, mira [SECURITY.md](SECURITY.md).

## Uso

Todo de una vez (últimos 7 días):

```powershell
.\.venv\Scripts\python.exe -m boe.principal
```

O paso a paso:

```powershell
.\.venv\Scripts\python.exe -m boe.guardar 2026-11-16 2026-11-21   # descargar y guardar un rango
.\.venv\Scripts\python.exe -m boe.clasificar                      # tema, impacto y ámbito
.\.venv\Scripts\python.exe -m boe.resumir                         # fichas
.\.venv\Scripts\python.exe -m boe.congreso                       # votaciones de convalidación en el Congreso
.\.venv\Scripts\python.exe -m boe.tramitacion                    # tramitación como proyecto de ley
.\.venv\Scripts\python.exe -m boe.legislatura                    # cifras de convalidación de la legislatura
.\.venv\Scripts\python.exe -m boe.sentencias_tc                   # sentencias del Constitucional (sección T de los sumarios guardados)
.\.venv\Scripts\python.exe -m boe.votaciones_leyes                # votación final de cada ley en el Congreso
.\.venv\Scripts\python.exe -m boe.senado                         # qué hizo el Senado con cada ley (datos abiertos del Senado)
.\.venv\Scripts\python.exe -m boe.consolidada                    # vida de cada norma (legislación consolidada del BOE)
.\.venv\Scripts\python.exe -m boe.versiones                      # antes y después de los artículos que cambia cada norma
.\.venv\Scripts\python.exe -m boe.exportar                        # datos para la web
.\.venv\Scripts\python.exe -m boe.guardar --revisar               # relee los sumarios guardados y corrige
```

Ver la web en tu ordenador (hace falta un servidor local porque el navegador no deja
leer `web/datos/` abriendo el HTML con doble clic):

```powershell
.\.venv\Scripts\python.exe -m http.server 8000 --directory web
```

y abre <http://localhost:8000>.

Pruebas:

```powershell
.\.venv\Scripts\python.exe -m pytest
```

## Inteligencia artificial (opcional)

**El proyecto funciona sin IA.** Sin modelo, la clasificación se hace con reglas y las
fichas quedan como *pendiente*, mostrando solo un título simplificado.

Con un modelo configurado, la IA escribe las fichas (y, de forma opcional, puede clasificar
con `python -m boe.clasificar --ia`). El texto oficial se le da en párrafos numerados y debe
indicar de qué párrafos sale cada apartado; el programa copia esos párrafos como citas. Una
ficha solo se publica si supera las comprobaciones automáticas:

- los párrafos citados existen;
- todos los números del apartado aparecen en los párrafos citados (se entienden las cifras
  con miles separados por punto o por espacio, «1 286», y los números con letras, «ciento veinte»);
- «desde cuándo» cita un párrafo con contenido sobre vigencia o efectos;
- si un apartado menciona un boletín (BOE, diario oficial…), los párrafos citados también.

Si no las supera, queda *pendiente* y no se vuelve a intentar con el mismo modelo
(usa `python -m boe.resumir --rehacer` para forzarlo).

> **Estado actual:** no hay ninguna ficha con resumen automático. Se probó `gemma3:4b` en local
> con cinco normas y ninguno de sus resúmenes superó las comprobaciones (en las pruebas puso mal
> fechas de entrada en vigor y citó párrafos sin relación). Las fichas muestran el título
> simplificado y frases copiadas del texto oficial (objeto, entrada en vigor, competencia).
> Si un modelo más capaz supera las comprobaciones, sus fichas se publicarán marcadas como
> **«Resumen automático (experimental)»** y con el aviso de que pueden contener errores.

Se configura con variables de entorno o con un archivo `.env` en la raíz (está en
`.gitignore`, nunca se sube):

| Variable | Valor |
|---|---|
| `BOE_IA_PROVEEDOR` | `ninguno` (por defecto), `ollama` u `openai` |
| `BOE_IA_MODELO` | p. ej. `gemma3:4b` (Ollama) o el modelo de tu API |
| `BOE_IA_URL` | opcional; por defecto `http://localhost:11434/v1` (Ollama) o `https://api.openai.com/v1` |
| `BOE_IA_CLAVE` | clave de la API externa (Ollama no la necesita) |

`openai` sirve para cualquier servicio compatible con la API de OpenAI cambiando `BOE_IA_URL`.

### Modelo local con Ollama (sin internet)

1. Instala [Ollama](https://ollama.com), descarga el modelo y crea la variante del proyecto
   (amplía la ventana de contexto a 8.192 tokens y fija la temperatura a 0):
   ```powershell
   ollama pull gemma3:4b
   ollama create boe-gemma3 -f ollama/Modelfile
   ```
2. Crea `.env`:
   ```
   BOE_IA_PROVEEDOR=ollama
   BOE_IA_MODELO=boe-gemma3
   ```
3. Con internet, descarga los datos: `python -m boe.guardar <desde> <hasta>`.
4. Ya sin internet, genera las fichas: `python -m boe.resumir` (unos 90 segundos por ficha en un portátil sin GPU).
   El modelo se ejecuta en tu ordenador y los textos se leen de `datos/crudo/`.
5. Haz commit y push de `datos/`: la web publicará las fichas verificadas, y la
   automatización semanal no las vuelve a generar.

## Automatización y despliegue

> **Estado:** la Action se ejecuta **una vez por semana** (domingo, 08:00 UTC) y guarda los
> datos nuevos. Publica la web en GitHub Pages solo si se pide (ver abajo).

La Action `.github/workflows/diario.yml` pasa las pruebas, revisa los últimos 7 días,
guarda en `datos/` lo nuevo con un commit automático y, si se pide, publica `web/` en
GitHub Pages. Se lanza sola cada domingo y también a mano: **Actions → Actualización semanal → Run workflow**.
Las ejecuciones programadas solo funcionan desde la rama principal (`main`).

Para publicar solo un cambio de la web (diseño, textos) sin consultar ninguna fuente, lánzala
a mano con la casilla **Solo publicar la web, sin descargar datos**: pasa las pruebas, exporta
`web/datos/` con los `datos/` ya guardados en el repositorio y publica. Tarda alrededor de un minuto.

Para activarla del todo más adelante:

1. **Otra frecuencia:** cambia el `cron` del bloque `schedule` (por ejemplo `"15 7 * * 1-6"` para cada mañana de lunes a sábado).
2. **Web pública en GitHub Pages:** necesita un repositorio **público** (con la cuenta
   gratuita) o un plan de pago. Activa **Settings → Pages → Build and deployment → Source:
   GitHub Actions** y lanza el workflow con la casilla **publicar** marcada. Para que se
   publique también cada domingo, crea la variable del repositorio `PUBLICAR_WEB` con el
   valor `true` (**Settings → Secrets and variables → Actions → Variables**). La web quedará
   en `https://<tu-usuario>.github.io/boe-en-llano/`.
   Otra opción, manteniendo el repositorio privado, es publicar `web/` en un servicio que lo
   permita gratis (Cloudflare Pages, Netlify) adaptando el workflow.

Para usar una IA externa también en la Action, añade los secretos `BOE_IA_PROVEEDOR`,
`BOE_IA_MODELO`, `BOE_IA_URL` y `BOE_IA_CLAVE` en **Settings → Secrets and variables → Actions**.
Un modelo local con Ollama no está disponible en la Action: genera las fichas en tu
ordenador y súbelas.

## Clasificación

- **Tema** (uno): Trabajo y empleo · Impuestos y dinero · Vivienda y urbanismo · Salud, consumo y
  animales · Movilidad, energía y medio ambiente · Derechos e igualdad · Educación, cultura y
  ciencia · Instituciones, ayudas e internacional.
- **Impacto**: *Directo* (cambia algo para mucha gente), *Colectivos* (grupos concretos) o
  *Técnico* (organización interna, subvenciones a entidades, trámites).
- **Ámbito**: estatal o la comunidad autónoma correspondiente.

Las reglas están en `boe/clasificar.py` y cada norma guarda los motivos de su clasificación.
Las limitaciones conocidas se explican en la propia web, en «Cómo se ha hecho».

## Respeto a la API del BOE

- Cada respuesta se guarda y no se vuelve a pedir (sumarios y textos).
- Pausa de 1 segundo entre peticiones.
- Un día ya procesado no se vuelve a descargar.

## Licencia

- Código: [MIT](LICENSE).
- Textos y datos propios (titulares simplificados, fichas, clasificación, cifras
  agregadas): [CC BY 4.0](LICENSE-DATOS.md).
- El contenido del BOE y del Congreso se rige por las condiciones de reutilización de cada
  fuente (detalle en [LICENSE-DATOS.md](LICENSE-DATOS.md)).
