# El BOE en llano — instrucciones del proyecto

Web que cada día descarga lo publicado en el Boletín Oficial del Estado (BOE),
lo clasifica y lo explica en lenguaje sencillo para personas sin formación jurídica.

## Objetivo
Que cualquier persona vea de un vistazo qué ha publicado el BOE, qué le afecta
y qué significa, y pueda entrar en el detalle de cada norma.

## Fuente de datos
- API de datos abiertos del BOE (boe.es, "datos abiertos"), endpoint de sumario diario.
- Del sumario se guarda el recuento de publicaciones por sección (I, II.A, II.B,
  III, IV, V) para todos los días.
- Para la sección I (Disposiciones generales) se guarda cada norma: identificador
  BOE-A, fecha, tipo (ley, real decreto-ley, orden...), órgano, título oficial y
  enlace al texto. Se descarga también su texto completo para poder resumirlo.

## Clasificación de cada norma de la sección I
- Tema (una sola categoría): Trabajo y empleo · Impuestos y dinero · Vivienda y
  urbanismo · Salud, consumo y animales · Movilidad, energía y medio ambiente ·
  Derechos e igualdad · Educación, cultura y ciencia · Instituciones, ayudas e
  internacional.
- Impacto: "Directo" (cambia algo para mucha gente), "Colectivos" (afecta a grupos
  concretos) o "Técnico" (organización interna, subvenciones a entidades, trámites).
- Ámbito: estatal o la comunidad autónoma correspondiente.
- Primero reglas sencillas (palabras clave, tipo de norma, órgano); dejar preparada
  la opción de mejorarla con un modelo de IA.

## Ficha en lenguaje llano de cada norma
Campos: título en llano (una frase), qué cambia, a quién afecta, desde cuándo,
qué tiene que hacer la persona y enlace al texto oficial.

Reglas obligatorias:
- Basarse SOLO en el texto oficial. Nunca inventar cifras, fechas ni efectos.
- Si no hay resumen fiable, la ficha se marca como "pendiente" y muestra solo el
  título traducido.
- Cada ficha lleva el aviso: "Resumen orientativo, no es asesoramiento jurídico.
  Consulta el texto oficial."
- El modelo de IA debe ser intercambiable: modelo abierto en local (p. ej. Ollama)
  o API externa configurada con variable de entorno. El proyecto debe funcionar
  aunque no haya ninguno configurado.

## La web
Página estática (sin servidor), en español, que funcione bien en móvil:
1. Cabecera con una frase resumen calculada de los datos y 4 cifras: total de
   publicaciones, normas generales, % del BOE que son normas y normas de impacto directo.
2. Gráfico de barras apiladas: publicaciones por sección en cada día.
3. Matriz tema × impacto con el número de normas en cada casilla (color más intenso
   cuanto más alto). Al pulsar una casilla se filtra la lista.
4. Lista de normas filtrable (tema, impacto, fecha, ámbito); al pulsar una, su ficha
   completa al lado (debajo en móvil).
5. Apartado "Cómo se ha hecho": fuentes, clasificación y limitaciones.

## Requisitos técnicos
- Todo open source y gratuito. Python para los datos; HTML, CSS y JavaScript con
  una librería de gráficos ligera para la web.
- Datos guardados en archivos (JSON o DuckDB) dentro del repositorio.
- GitHub Action que lo ejecute cada mañana y publique la web en GitHub Pages.
- No descargar varias veces lo ya guardado; respetar la API con pausas entre peticiones.
- README en español: instalación, ejecución y despliegue.

## Forma de trabajar
- Antes de escribir código, proponer un plan (estructura de carpetas y pasos) y
  esperar aprobación.
- Avanzar por pasos pequeños que funcionen por sí solos, en este orden:
  descargar un día → guardar → clasificar → resumir → web → automatización.
- Después de cada paso: ejecutarlo, enseñar el resultado real, añadir pruebas
  básicas y hacer un commit con un mensaje claro.
- Si algo de la API o de los datos no es como se esperaba, avisar en lugar de suponer.

## Comunicación
- Hablar siempre en español.
- La usuaria tiene experiencia programando: sin modo aprendizaje, sin huecos `TODO`
  para que los rellene ella y sin explicar conceptos básicos. Informes breves:
  qué se ha hecho, resultado real y cualquier sorpresa de la API o los datos.
- Autor de los commits en este repositorio: `JZR <jzr@example.com>`.
