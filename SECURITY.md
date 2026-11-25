# Seguridad

## Cómo avisar de un fallo

Si encuentras un fallo de seguridad en la web o en el código (por ejemplo, una forma de que la web
muestre o ejecute algo que no viene de las fuentes oficiales), avisa **en privado** desde la pestaña
**Security → Report a vulnerability** de este repositorio (aviso privado de GitHub). No abras un
*issue* público hasta que esté corregido.

Para errores en los datos o en las explicaciones (una cifra mal leída, una norma mal clasificada),
basta con un *issue* normal: se corrigen y se explican en «Cómo se ha hecho → Correcciones».

## Qué se protege

La web es estática (GitHub Pages): no tiene servidor propio, cuentas, formularios que envíen datos
ni cookies. Las visitas se cuentan con GoatCounter sin cookies: `web/contador.js` solo envía qué página
se abre, sin la cabecera Referer, y no cuenta si el navegador pide no ser rastreado.

- **Lo que muestra la web:** todo texto de los datos se inserta como texto, nunca como HTML. Los
  enlaces construidos con datos solo pueden ir a la propia web o, por `https`, a `boe.es`,
  `congreso.es` y `senado.es` (si no, el enlace se queda sin dirección).
- **Lo que puede cargar la página:** una política de seguridad del contenido (CSP) en cada HTML deja
  cargar solo los archivos de la propia web (y la imagen del contador de visitas). Chart.js 4.4.1 se sirve desde aquí, tal cual se publica
  y con comprobación de hash (SRI). Bloquea scripts en línea y de otros sitios.
- **La actualización automática (GitHub Actions):** permisos mínimos por trabajo (solo lectura por
  defecto), acciones fijadas por SHA y dependencias de Python instaladas con versión exacta y hash
  (`requirements-ci.txt`, generado con `python herramientas/bloquear.py`). Las claves de IA, si las
  hay, son *secrets* que solo recibe el paso que las usa.
- **Las descargas:** solo de fuentes oficiales y por `https`, con verificación de certificados.

## Qué no se puede proteger desde aquí

- GitHub Pages no deja poner cabeceras HTTP: la CSP va en una etiqueta `<meta>`, que no admite
  `frame-ancestors`, así que no se puede impedir que otra web incruste esta.
- Si una fuente oficial publica un dato erróneo, la web lo reproduce (y lo corrige cuando la fuente lo
  corrige).
- GitHub, que aloja la web, ve las visitas como cualquier servidor.
