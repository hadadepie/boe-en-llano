---
name: revisar
description: Revisa cambios de El BOE en llano con los criterios propios del proyecto (Python de datos en boe/, web estática HTML/CSS/JS en web/, textos y reglas de contenido). Úsala siempre que se pida revisar, repasar o dar el visto bueno a un cambio, un diff, un commit, una rama o un archivo de este repositorio, antes de un commit o subida importante, o cuando se pregunte «¿está bien esto?», «¿se me escapa algo?» o «¿lo subo?», aunque no se diga «revisión».
---

# Revisar un cambio de El BOE en llano

El objetivo es encontrar lo que de verdad importa en este proyecto: errores que publicarían algo falso,
inseguro o roto en la web, o que romperían la cadena de datos de la Action del domingo. No es una lista de
estilo: un hallazgo vale si alguien puede describir qué saldría mal y con qué entrada.

## 1. Qué se revisa

- Sin indicación: el diff sin commit (`git diff` y `git diff --cached`); si está vacío, el último commit
  (`git show HEAD`). Con una rama, un commit o un archivo, ese.
- **Si hay cambios de otra sesión en la carpeta** (archivos que no son de la tarea), revisa solo lo pedido y
  dilo. No toques ni comentes cambios ajenos salvo que se pidan.
- Lee el diff primero y solo después los trozos de archivo que hagan falta para entenderlo. No leas
  archivos enteros grandes (`app.js`, `exportar.py`, `BACKLOG.md`): busca la función o el encabezado.

## 2. Qué referencia cargar

Según lo que toque el diff, lee solo la que aplique:

| Si cambia… | Lee |
|---|---|
| `boe/*.py`, `herramientas/*.py`, `tests/*.py`, `.github/workflows/` | `references/python.md` |
| `web/*.html`, `web/*.js`, `web/estilos.css` | `references/web.md` |
| Cifras o afirmaciones publicadas, textos explicativos (fichas, `como.html`, `guia.html`, notas de gráficos), votaciones | `references/contenido.md` |

Un cambio solo de navegación, maquetación o estilos no necesita `contenido.md`.

Un cambio de datos (`datos/*.json`) se revisa con `contenido.md`: que las cifras salgan de la fuente y que
no se haya colado nada de `datos/crudo/`.

## 3. Comprobaciones automáticas (antes de opinar)

Ejecútalas y usa su resultado como evidencia; no repitas a mano lo que ya comprueban:

```
.venv/Scripts/python.exe -m pytest -q --tb=short            # todo
.venv/Scripts/python.exe -m pytest -q --tb=short tests/test_web.py tests/test_seguridad.py   # si toca web/
```

Si toca HTML: `python .claude/skills/revisar/scripts/ids_duplicados.py` (un id repetido hace que el script
actúe sobre el elemento equivocado; ninguna prueba lo cubre). Los `?v=` ya los comprueba `test_web.py`: en
una revisión no hace falta ejecutar `versionar.py`, que escribe en los HTML. Si una prueba falla, es el primer
hallazgo.

Las pruebas corren sobre el árbol actual. Si revisas un commit antiguo o hay cambios de otra sesión delante,
no hagas checkout ni stash: dilo en el informe y comprueba en el diff (y con `git show <commit>:<archivo>`)
lo que importe.

Con la vista previa (puerto 8000) disponible y un cambio visible en la web, mira la página afectada en
claro, oscuro y a 375 px, y la consola sin errores.

## 4. Informe

En español, breve, ordenado de más a menos grave. Para cada hallazgo:

- **Gravedad**: `bloquea` (publica algo falso, inseguro o roto; rompe la Action o las pruebas), `importante`
  (fallará en un caso concreto), `menor` (claridad, coherencia).
- `archivo:línea` y qué pasa, con el caso concreto que lo dispara.
- Arreglo propuesto en una línea.

Después, una línea con lo comprobado (pruebas, versionar, vista previa) y lo que no se ha podido comprobar.
Si no hay hallazgos, dilo sin rellenar. No cambies código salvo que se pida: la revisión informa.
