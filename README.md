# El BOE en llano

Una web que cada día descarga lo publicado en el **Boletín Oficial del Estado**,
lo clasifica y lo explica en lenguaje sencillo para personas sin formación jurídica.

- Cuántas publicaciones hay cada día y en qué sección.
- Qué normas generales (sección I) se han aprobado, de qué tratan y a quién afectan.
- Una ficha por norma: qué cambia, a quién afecta, desde cuándo y qué hay que hacer,
  siempre con enlace al texto oficial.

> Proyecto no oficial y prueba de concepto. Los resúmenes son orientativos y **no son
> asesoramiento jurídico**: consulta siempre el texto oficial.

## Cómo funciona

```
API de datos abiertos del BOE
        │  sumario diario + XML de cada norma (con pausas y sin repetir descargas)
        ▼
boe/descargar.py ──► boe/guardar.py ──► boe/clasificar.py ──► boe/resumir.py ──► boe/exportar.py
                     recuentos y         tema, impacto y       ficha en llano       web/datos.json
                     normas en datos/    ámbito (reglas o IA)  verificada              │
                                                                                       ▼
                                                                       web/ (HTML + CSS + JS, sin servidor)
```

| Carpeta / archivo | Qué hay |
|---|---|
| `boe/` | El código Python, un módulo por paso. `principal.py` los ejecuta todos. |
| `datos/recuentos.json` | Publicaciones por sección y día. **Se guarda en Git.** |
| `datos/normas/BOE-A-….json` | Una norma de la sección I: metadatos, clasificación y ficha. **Se guarda en Git.** |
| `datos/crudo/` | Respuestas de la API tal cual (temporal, fuera de Git). |
| `web/` | La página. `web/datos.json` se genera y no se guarda en Git. |
| `tests/` | Pruebas automáticas (no se conectan a internet). |
| `.github/workflows/diario.yml` | La automatización diaria. |

## Instalación

Necesitas **Python 3.11 o superior** y **Git**.

```powershell
git clone https://github.com/<tu-usuario>/boe-en-llano.git
cd boe-en-llano
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

En macOS o Linux, cambia `.\.venv\Scripts\python.exe` por `.venv/bin/python` en todos los comandos.

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
.\.venv\Scripts\python.exe -m boe.exportar                        # datos para la web
```

Ver la web en tu ordenador (hace falta un servidor local porque el navegador no deja
leer `datos.json` abriendo el HTML con doble clic):

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

Con un modelo configurado, la IA puede mejorar la clasificación y escribir las fichas.
Una ficha solo se publica si supera dos comprobaciones automáticas contra el texto oficial:
cada apartado lleva una cita literal que debe existir en el texto, y todos los números de la
ficha deben aparecer en el texto. Si no, queda *pendiente*.

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

1. Instala [Ollama](https://ollama.com) y descarga un modelo pequeño: `ollama pull gemma3:4b`.
2. Crea `.env`:
   ```
   BOE_IA_PROVEEDOR=ollama
   BOE_IA_MODELO=gemma3:4b
   ```
3. Con internet, descarga los datos: `python -m boe.guardar <desde> <hasta>`.
4. Ya sin internet, genera las fichas: `python -m boe.clasificar --ia` y `python -m boe.resumir`.
   El modelo se ejecuta en tu ordenador y los textos se leen de `datos/crudo/`.
5. Haz commit y push de `datos/`: la web publicará las fichas verificadas, y la
   automatización diaria no las vuelve a generar.

## Despliegue en GitHub Pages

1. Crea un repositorio en GitHub y sube el proyecto:
   ```powershell
   git remote add origin https://github.com/<tu-usuario>/boe-en-llano.git
   git push -u origin main
   ```
   Con una cuenta gratuita, GitHub Pages solo funciona en repositorios **públicos**.
2. En el repositorio: **Settings → Pages → Build and deployment → Source: GitHub Actions**.
3. En **Actions**, abre *Actualización diaria* y pulsa **Run workflow** para la primera publicación.

Desde entonces la Action se ejecuta **cada día a las 07:15 UTC** (y en cada push a `main`):
pasa las pruebas, revisa los últimos 7 días, guarda en `datos/` lo nuevo con un commit
automático y publica la web en `https://<tu-usuario>.github.io/boe-en-llano/`.

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

Pendiente de elegir.
