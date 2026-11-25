"""Lista los id repetidos en cada página de web/ (las pruebas no lo cubren).

Uso: python .claude/skills/revisar/scripts/ids_duplicados.py [archivos.html…]
Sin argumentos revisa todos los web/*.html. Con un id repetido, getElementById
devuelve el primero y el script de la página actúa sobre el elemento equivocado.
"""

import re
import sys
from collections import Counter
from pathlib import Path

paginas = [Path(a) for a in sys.argv[1:]] or sorted(Path("web").glob("*.html"))
hay = False
for pagina in paginas:
    texto = pagina.read_text(encoding="utf-8")
    ids = Counter(re.findall(r'\sid="([^"]+)"', texto))
    for id_, veces in sorted(ids.items()):
        if veces > 1:
            lineas = [texto.count("\n", 0, m.start()) + 1 for m in re.finditer(rf'\sid="{re.escape(id_)}"', texto)]
            print(f"{pagina}: id=\"{id_}\" {veces} veces (líneas {', '.join(map(str, lineas))})")
            hay = True
if not hay:
    print("Sin id repetidos.")
sys.exit(1 if hay else 0)
