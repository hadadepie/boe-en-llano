# El BOE en llano — instrucciones del proyecto

Web que descarga lo publicado en el BOE, lo clasifica y lo explica en lenguaje
sencillo, para entender qué decide el Estado y por qué. **Estado actual, repositorio (solo `main` + etiquetas),
decisiones y próximos pasos: `docs/ESTADO.md`** (léelo al empezar); pendientes y
proyectos futuros: `docs/BACKLOG.md`.

## Reglas de contenido (obligatorias)
- Basarse SOLO en fuentes oficiales (BOE, Congreso). Nunca inventar cifras, fechas
  ni efectos. Sin resumen fiable, la ficha queda «pendiente».
- Cada ficha lleva el aviso: «Resumen orientativo, no es asesoramiento jurídico.
  Consulta el texto oficial.» Lo generado por IA va marcado como experimental.
- El modelo de IA es intercambiable (Ollama local o API por variable de entorno) y
  el proyecto funciona sin ninguno.
- Votaciones: solo cifras agregadas (grupo, lista electoral); nada de votos
  individuales ni rankings de absentismo. Neutralidad: sin etiquetas políticas.
- Transparencia: cada novedad o corrección se explica en «Cómo se ha hecho» /
  «Correcciones» de la web.

## Requisitos técnicos
- Open source y gratuito. Python para los datos; HTML/CSS/JS estático (Chart.js).
- `datos/crudo/` fuera de Git; se versionan los datos extraídos en `datos/`.
- No descargar dos veces lo guardado; pausas de 1 s entre peticiones.
- README en español. Al cambiar un `.js` de `web/` o `web/estilos.css`, subir el
  `?v=` de sus enlaces en `web/index.html`, `web/datos.html` y `web/legislatura.html` (caché del navegador).

## Forma de trabajar
- Antes de una funcionalidad nueva: investigar si existe algo parecido y explorar
  la fuente real (llamada de prueba) antes de programar.
- Pasos pequeños: ejecutar, enseñar el resultado real, pruebas (pytest) y commit claro.
- Si los datos no son como se esperaba, avisar en lugar de suponer.
- No lanzar procesos pesados en el portátil (p. ej. IA local sobre muchas normas)
  sin avisar; con `.env` presente, usar `BOE_IA_PROVEEDOR=ninguno` si no se quiere IA.

## Comunicación
- Siempre en español. La usuaria programa: informes breves (qué se ha hecho,
  resultado real, sorpresas), sin modo aprendizaje ni huecos TODO.
- Autor de los commits: `JZR <jzr@example.com>`.
