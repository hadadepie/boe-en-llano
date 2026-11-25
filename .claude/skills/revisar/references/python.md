# Python de datos (`boe/`, `herramientas/`, `tests/`, Action)

Cada módulo de `boe/` es un paso de la cadena (`python -m boe.principal`, ver `docs/REFERENCIA.md`, «Cadena de
datos») y corre cada domingo en la Action sin nadie mirando. Un fallo silencioso publica datos malos; uno
ruidoso para la Action. Lo segundo es preferible.

## Peticiones a fuentes externas

- Toda petición nueva pasa por `descargar.pedir` (pausa de 1 s tras cada petición, `timeout`, reintentos 10/30/90 s
  ante 5xx y cortes) o por la función propia del módulo que ya la use (`congreso._get`). Un `requests.get` directo
  nuevo, sin pausa ni reintento, es hallazgo: el BOE devuelve 502 en descargas largas y el Congreso corta
  conexiones.
- `https://` y certificados verificados (nada de `verify=False`); solo dominios oficiales (BOE, Congreso, Senado,
  Hacienda/IGAE). Lo comprueba `tests/test_seguridad.py`.
- **No descargar dos veces**: lo crudo se guarda en `datos/crudo/…` y, si existe, se lee de ahí. Mira que el
  nuevo código compruebe el archivo antes de pedir y que un 404 «temporal» (consolidada reciente) no se guarde
  como definitivo.
- Coste en la Action: un bucle que consulta toda la legislatura cada domingo es hallazgo (ya pasó: >1 h). Lo
  normal es «solo lo nuevo» o una ventana (180 días, turnos de 1 de cada 4).

## Datos de las fuentes

- Las fuentes son irregulares (ver «Rarezas de las fuentes» en `docs/REFERENCIA.md`): un elemento suelto llega
  como dict y no como lista (`como_lista`), notas que vienen como dict o lista, cifras con espacio de miles y
  con letra, fechas imposibles en el Senado. Código que da por hecha una forma sin comprobarla → hallazgo si
  hay un ejemplo real que la incumple.
- Si un dato no se encuentra, se deja vacío o «pendiente», nunca un valor por defecto que parezca real (0, la
  fecha de hoy, «aprobado»). Si dos fuentes discrepan, manda el BOE y se guarda la `discrepancia`.
- Votaciones: solo agregados por grupo o lista; el voto individual no sale de `datos/crudo/`. Un campo nuevo en
  `datos/` o `web/datos/` con nombres de diputados o voto por persona → `bloquea`.

## Archivos y salida

- JSON con `ensure_ascii=False` y `indent` como el resto del archivo, para que los diffs sean legibles. Orden
  estable (claves y listas ordenadas) para que el mismo dato no cambie el archivo cada domingo.
- `datos/crudo/` nunca en Git. Lo extraído, en `datos/`; lo generado para la web (`web/datos/`), no versionado.
- Rutas con `Path` relativas a la raíz del proyecto, como el resto (`Path("datos/…")`).
- Mensajes por pantalla cortos: una línea por resumen, no por petición (la salida va al registro de la Action).

## IA

- El proyecto funciona sin IA. Código que falla o cambia resultados si no hay `.env` u Ollama → hallazgo.
- Una ficha de IA solo se publica si pasa el validador (`boe.resumir`), marcada «experimental».

## Pruebas

- Cada función nueva con lógica (análisis de un texto, cálculo de un informe) lleva prueba en `tests/` con datos
  pequeños (`tests/datos/`) o texto en línea. Las pruebas no salen a la red: `monkeypatch` sobre
  `requests.get` o la función de descarga, como en `test_consolidada.py`.
- Un caso real raro que motivó el cambio (un id concreto del BOE, un expediente) debe quedar como prueba.

## Action (`.github/workflows/diario.yml`)

- Acciones fijadas por SHA, permisos mínimos por trabajo, dependencias con hash: tras cambiar
  `requirements.txt`, `python herramientas/bloquear.py`. Lo comprueba `tests/test_seguridad.py`.
- Un paso nuevo en `boe.principal` debe tolerar no tener nada nuevo y no rehacer lo antiguo.
