# Web estática (`web/*.html`, `web/*.js`, `web/estilos.css`)

Web pública en GitHub Pages, sin servidor ni compilación: lo que hay en `web/` es lo que se publica. Mucha
gente la abre en el móvil y en modo oscuro.

## Seguridad (lo primero)

- Texto que viene de los datos se inserta con `textContent` o con `el(…, { texto })` de `app.js`, nunca con
  `innerHTML`. `innerHTML` solo con constantes del código y con un comentario que lo diga. Un `innerHTML` con
  datos → `bloquea`.
- Enlaces construidos con datos: con `el("a", { href })`, que pasa por `enlaceSeguro` (solo la propia web o,
  por https, boe.es, congreso.es, senado.es). Un `a.href = …` directo con datos → hallazgo.
- CSP por `<meta>` en cada página (`script-src 'self'`, `style-src 'self'`): nada de `<script>` en línea,
  `onclick=` en el HTML, `style=` en línea ni recursos de otros dominios (CDN, fuentes de Google). Una página
  nueva copia la cabecera completa de otra (CSP, referrer, metas `og:`, icono, `contador.js`). Lo comprueba
  `tests/test_seguridad.py`.
- Chart.js es el local (`chart-4.4.1.umd.js` con `integrity`).

## Caché y estructura

- Tras cambiar un `.js` o `estilos.css`: `python herramientas/versionar.py` (pone el `?v=` por contenido). Lo
  comprueba `tests/test_web.py`, que también mira que cada `$("id")` de un script exista en su página.
- Las páginas cargan `app.js` (utilidades comunes: `el`, `$`, fechas, `miles`, `activarTerminos`) y su propio
  script; las de la legislatura comparten `informe.js`. Una utilidad que ya existe en `app.js` no se duplica.
- Peso: la portada descarga ~150 KB. Datos grandes van a archivos que se cargan al abrir (`normas/<id>.json`,
  `buscar.json` al escribir), no a la semana ni al índice. Un campo nuevo en `semanas/*.json` o `indice.json`
  que haga crecer la carga inicial → hallazgo con la cifra.
- Si se quita o mueve un apartado con ancla, las anclas antiguas siguen funcionando (redirección como en
  `legislatura.js`) y los enlaces internos (`guia.html`, «Cómo se calcula») apuntan a la nueva.
- Al añadir o quitar una pieza visible, `guia.html` («qué hay en cada página») se actualiza.

## CSS y modo oscuro

- Colores solo con variables de `:root`. Un color nuevo se define en **tres sitios**: `:root`, el bloque
  `@media (prefers-color-scheme: dark) { :root:not([data-theme="light"]) … }` y `:root[data-theme="dark"]`.
  Si falta en alguno, en oscuro sale el color claro → hallazgo.
- Hex sueltos en reglas (fuera de las variables) → hallazgo menor, salvo en las series de gráficos ya definidas.
- Móvil: comprobar a 375 px que nada desborda en horizontal (tablas anchas dentro de un contenedor con
  scroll propio, gráficos que no queden aplastados ni con etiquetas montadas).

## Accesibilidad

- Botones de verdad (`<button>`) para acciones; enlaces para navegar. Foco visible (`:focus-visible` con el
  contorno del acento, como el resto).
- Cada gráfico lleva su frase de lectura y una alternativa en texto o tabla; el color no es la única pista
  (leyenda, etiquetas, patrón).
- Imágenes con `alt`; SVG decorativos con `aria-hidden="true"`; regiones que cambian con `aria-live` si
  avisan de algo (como «Enlace copiado»).
- Animaciones respetan `prefers-reduced-motion`.
- Contraste: texto tenue (`--tinta-tenue`) solo para lo secundario, no para cifras clave.

## JavaScript

- Si falla la carga de un JSON, la página dice qué pasa en lugar de quedarse en blanco (como `app.js` con
  «No se han podido cargar los datos…»).
- Fechas con `aFecha` y los formatos de `app.js`: `new Date("2026-11-25")` se interpreta en UTC y, según la zona
  horaria de quien lee, puede mostrar el día anterior. Números con `miles`. En español: «1.234», «25 de noviembre de 2026».
- Sin dependencias nuevas: es una web sin compilación y sin npm.
