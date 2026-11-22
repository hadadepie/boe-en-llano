"""Paso 4: ficha en lenguaje llano de cada norma.

Uso:
    python -m boe.resumir             # genera/actualiza las fichas de datos/normas
    python -m boe.resumir --rehacer   # vuelve a pedir a la IA también las ya hechas

Reglas obligatorias (ver CLAUDE.md):
- Basarse SOLO en el texto oficial. Nunca inventar cifras, fechas ni efectos.
- Sin resumen fiable, la ficha es "pendiente" y muestra solo el título simplificado.
- Toda ficha lleva AVISO.

Sin IA configurada, todas las fichas quedan "pendiente" (el proyecto funciona igual).
Con IA, el texto se envía en párrafos numerados y el modelo indica de qué
párrafos sale cada campo. El resumen solo se acepta si supera `verificar_ficha`:
    1. cada campo cita párrafos que existen (el programa copia el párrafo real);
    2. todo número de un campo aparece en los párrafos que cita.
"""

import argparse
import json
import re
from pathlib import Path

from boe.clasificar import normalizar


CARPETA_NORMAS = Path("datos/normas")
AVISO = "Resumen orientativo, no es asesoramiento jurídico. Consulta el texto oficial."
CAMPOS = ["titulo_llano", "que_cambia", "a_quien_afecta", "desde_cuando", "que_hacer"]
NO_CONSTA = "El texto no lo indica."
AVISO_IA = ("Resumen automático experimental, generado por un modelo de IA pequeño: puede "
            "contener errores aunque haya superado las comprobaciones automáticas. "
            "Compruébalo siempre en el texto oficial.")

MESES = "enero|febrero|marzo|abril|mayo|junio|julio|agosto|septiembre|octubre|noviembre|diciembre"
_FECHA = rf"de \d{{1,2}} de (?:{MESES})(?: de \d{{4}})?"


# ---------- Título simplificado (sin IA) ----------

def _mayuscula(texto):
    return texto[:1].upper() + texto[1:] if texto else texto


def titulo_simplificado(titulo):
    """Quita del título oficial la "cabecera" jurídica (rango, número, fecha y órgano).

    No añade información: solo recorta y reordena palabras del propio título.
        "Real Decreto 1013/2026, de 18 de noviembre, por el que se fija el salario
         mínimo interprofesional para 2027."  ->  "Se fija el salario mínimo
         interprofesional para 2027."
    """
    t = (titulo or "").strip()

    convalidacion = re.search(r"acuerdo de convalidación del (.+)", t, re.IGNORECASE)
    if convalidacion:
        return "El Congreso convalida el " + convalidacion.group(1)

    correccion = re.match(r"^corrección de (?:errores|erratas) (?:del?|de la) (.+)$", t, re.IGNORECASE)
    if correccion:
        return "Corrección de errores: " + correccion.group(1)

    # La acción principal es el PRIMER conector del título; los siguientes suelen
    # pertenecer a normas citadas ("..., que estima el recurso contra el Real
    # Decreto X, por el que se modifica...").
    candidatos = []
    por_que = re.search(r", por (?:el|la|los|las) que (.+)", t)
    if por_que:
        candidatos.append((por_que.start(), _mayuscula(por_que.group(1))))
    sentencia = re.search(r", que (estima|desestima|anula|declara|inadmite)(.+)", t)
    if sentencia:
        tribunal = re.search(r"del? (Tribunal [A-ZÁÉÍÓÚ]\w+(?: de [A-ZÁÉÍÓÚ][\w ]+?)?|Audiencia Nacional)\b",
                             t[: sentencia.start()])
        sujeto = f"El {tribunal.group(1)}" if tribunal else "La sentencia"
        candidatos.append((sentencia.start(), f"{sujeto} {sentencia.group(1)}{sentencia.group(2)}"))
    tras_fecha = re.match(rf"^[^,]+, {_FECHA}, (.+)$", t)
    if tras_fecha:
        resto = re.sub(r"^(?:de|del)\s+", "", tras_fecha.group(1))  # "Ley 5/2026, de 16 de julio, de X" -> "X"
        candidatos.append((tras_fecha.start(1), _mayuscula(resto)))

    if not candidatos:
        return t
    return min(candidatos)[1]


# ---------- Párrafos numerados ----------

def parrafos(texto):
    """Lista de párrafos del texto oficial (uno por línea, sin vacíos)."""
    return [p.strip() for p in (texto or "").splitlines() if p.strip()]


_VIGOR = re.compile(r"entrar[aá] en vigor|entrada en vigor|surtir[aá] efectos|producir[aá] efectos", re.I)


def extracto_numerado(lista, maximo=12000):
    """Párrafos numerados [1], [2]... que caben en `maximo` caracteres.

    Se priorizan los primeros párrafos (2/3 del espacio) y los que hablan de
    entrada en vigor (suelen ir al final). Los números son los originales, para
    que las citas apunten siempre al párrafo correcto.
    """
    elegidos, usado = set(), 0
    for i, p in enumerate(lista):
        if usado + len(p) > maximo * 2 // 3:
            break
        elegidos.add(i)
        usado += len(p) + 6
    for i, p in enumerate(lista):
        if not _VIGOR.search(p):
            continue
        # Un encabezado corto ("Disposición final séptima. Entrada en vigor.")
        # no dice nada: el contenido está en el párrafo siguiente.
        candidatos = [i, i + 1] if len(p) < 80 and i + 1 < len(lista) else [i]
        for j in candidatos:
            if j not in elegidos and usado + len(lista[j]) <= maximo:
                elegidos.add(j)
                usado += len(lista[j]) + 6
    lineas, anterior = [], -1
    for i in sorted(elegidos):
        if i != anterior + 1:
            lineas.append("[...]")
        lineas.append(f"[{i + 1}] {lista[i]}")
        anterior = i
    return "\n".join(lineas)


# ---------- Verificación contra el texto oficial ----------

def numeros(texto):
    """Números de un texto, sin separadores: '1.184,50 €' -> {'118450'}."""
    return {re.sub(r"[.,]", "", n) for n in re.findall(r"\d[\d.,]*\d|\d", texto or "")}


# Números escritos con letras ("diez días hábiles"). Se excluyen "un/uno/una"
# porque casi siempre son artículos.
_NUMEROS_LETRA = (
    "dos tres cuatro cinco seis siete ocho nueve diez once doce trece catorce quince "
    "dieciseis diecisiete dieciocho diecinueve veinte veintiun veintiuno veintidos "
    "veintitres veinticuatro veinticinco veintiseis veintisiete veintiocho veintinueve "
    "treinta cuarenta cincuenta sesenta setenta ochenta noventa cien ciento doscientos "
    "doscientas trescientos trescientas cuatrocientos cuatrocientas quinientos quinientas "
    "seiscientos seiscientas setecientos setecientas ochocientos ochocientas novecientos "
    "novecientas mil millon millones"
).split()
_RE_NUMERO_LETRA = re.compile(r"\b(" + "|".join(_NUMEROS_LETRA) + r")\b")
_RE_VIGENCIA = re.compile(r"vigor|efectos|vigencia|aplicaci[oó]n|aplicar[aá]|a partir del?\b", re.I)
_SIGLAS_BOLETINES = "BOE BOJA BOA BOPA BOIB BOC BOCA BOCYL BOCM DOCM DOGC DOGV DOCV DOE DOG BOR BORM BON BOPV BOME BOCCE".split()
# Las palabras sin distinguir mayúsculas; las siglas solo en mayúsculas ("BOE", no "boe").
_RE_BOLETIN = re.compile(r"(?i:bolet[ií]n|diario oficial)|\b(?:" + "|".join(_SIGLAS_BOLETINES) + r")\b")
MIN_PARRAFO_VIGENCIA = 60


def numeros_con_letra(texto):
    """'diez días y treinta euros' -> {'diez', 'treinta'} (sin tildes, minúsculas)."""
    return set(_RE_NUMERO_LETRA.findall(normalizar(texto)))


def verificar_ficha(ficha, lista_parrafos, titulo_oficial=""):
    """Devuelve la lista de problemas (vacía si la ficha es fiable).

    - Cada campo (salvo el título y los "no consta") cita al menos un párrafo
      que existe.
    - Todo número de un campo, en cifras o con letras, aparece en LOS PÁRRAFOS
      QUE CITA (no basta con que esté en cualquier parte del texto).
    - "Desde cuándo" debe citar un párrafo con contenido sobre vigencia o
      efectos (no basta un encabezado como "Entrada en vigor.").
    - Si un campo menciona un boletín (BOE, diario oficial...), los párrafos
      citados también deben mencionarlo.
    - Los números del título en llano deben estar en el título oficial o en el texto.
    """
    problemas = []
    fuentes = ficha.get("fuentes") or {}
    total = len(lista_parrafos)

    for campo in CAMPOS:
        valor = (ficha.get(campo) or "").strip()
        if not valor:
            problemas.append(f"{campo}: vacío")
            continue
        if campo == "titulo_llano":
            permitidos = numeros(titulo_oficial) | numeros("\n".join(lista_parrafos))
        elif valor == NO_CONSTA:
            continue
        else:
            ids = fuentes.get(campo) or []
            validos = [i for i in ids if isinstance(i, int) and 1 <= i <= total]
            if not validos:
                problemas.append(f"{campo}: no cita ningún párrafo válido")
                continue
            if len(validos) != len(ids):
                problemas.append(f"{campo}: cita párrafos que no existen")
            citados = [lista_parrafos[i - 1] for i in validos]
            permitidos = numeros(" ".join(citados))
            letras = numeros_con_letra(valor) - numeros_con_letra(" ".join(citados))
            if letras:
                problemas.append(f"{campo}: números con letra que no están en los párrafos citados: {sorted(letras)}")
            if campo == "desde_cuando" and not any(
                    _RE_VIGENCIA.search(c) and len(c) >= MIN_PARRAFO_VIGENCIA for c in citados):
                problemas.append("desde_cuando: no cita ningún párrafo sobre vigencia o efectos")
            if _RE_BOLETIN.search(valor) and not any(_RE_BOLETIN.search(c) for c in citados):
                problemas.append(f"{campo}: menciona un boletín que no aparece en los párrafos citados")
        inventados = numeros(valor) - permitidos
        if inventados:
            problemas.append(f"{campo}: números que no están en los párrafos citados: {sorted(inventados)}")
    return problemas


# ---------- Ficha ----------

def ficha_pendiente(norma, motivo, modelo_intentado=None):
    ficha = {
        "estado": "pendiente",
        "titulo_llano": titulo_simplificado(norma.get("titulo")),
        "enlace": norma.get("url_html"),
        "aviso": AVISO,
        "metodo": "reglas",
        "motivo_pendiente": motivo,
    }
    if modelo_intentado:
        ficha["modelo_intentado"] = modelo_intentado  # para no reintentar en cada ejecución
    return ficha


INSTRUCCIONES_IA = f"""Eres un redactor que explica normas del BOE a personas sin formación jurídica.
Recibirás el texto oficial dividido en párrafos numerados: [1], [2], [3]...
Usa EXCLUSIVAMENTE esos párrafos. No añadas nada que no esté en ellos:
ni cifras, ni fechas, ni cálculos propios, ni efectos, ni consejos.
Frases cortas y palabras sencillas. Escribe fechas y cifras tal como aparecen.
Si el texto no dice algo, escribe exactamente: "{NO_CONSTA}"

Claves de la respuesta:
  titulo_llano:   una sola frase que diga qué hace la norma
  que_cambia:     qué cambia (2-3 frases como máximo)
  a_quien_afecta: a quién afecta
  desde_cuando:   desde cuándo se aplica
  que_hacer:      qué tiene que hacer la persona afectada
  fuentes:        para que_cambia, a_quien_afecta, desde_cuando y que_hacer, la lista
                  de NÚMEROS de los párrafos de donde has sacado esa información
                  (por ejemplo [2, 5]). Lista vacía si el campo es "{NO_CONSTA}".
"""

_TEXTO = {"type": "string"}
_IDS = {"type": "array", "items": {"type": "integer"}}
ESQUEMA_FICHA = {
    "type": "object",
    "properties": {
        **{campo: _TEXTO for campo in CAMPOS},
        "fuentes": {
            "type": "object",
            "properties": {campo: _IDS for campo in CAMPOS[1:]},
            "required": CAMPOS[1:],
        },
    },
    "required": CAMPOS + ["fuentes"],
}
MAX_CITA = 400


def ficha_con_ia(cliente, norma, texto):
    """Pide la ficha al modelo y la verifica. Devuelve (ficha, problemas)."""
    lista = parrafos(texto)
    usuario = f"Título oficial: {norma.get('titulo')}\n\nTexto oficial:\n{extracto_numerado(lista)}"
    respuesta = cliente.completar_json(INSTRUCCIONES_IA, usuario, esquema=ESQUEMA_FICHA)
    if not isinstance(respuesta, dict):
        return None, ["la IA no devolvió JSON"]
    problemas = verificar_ficha(respuesta, lista, norma.get("titulo", ""))
    if problemas:
        return None, problemas

    ficha = {campo: respuesta[campo].strip() for campo in CAMPOS}
    # Las citas las pone el programa copiando los párrafos reales: nunca pueden ser falsas.
    citas = {}
    for campo, ids in (respuesta.get("fuentes") or {}).items():
        if campo in CAMPOS and ficha.get(campo) != NO_CONSTA and ids:
            citas[campo] = [{"parrafo": i, "texto": lista[i - 1][:MAX_CITA]} for i in sorted(set(ids))]
    ficha.update({
        "estado": "ok",
        "citas": citas,
        "enlace": norma.get("url_html"),
        "aviso": AVISO,
        "aviso_ia": AVISO_IA,
        "metodo": "ia",
        "modelo": cliente.modelo,
    })
    return ficha, []


def generar_ficha(norma, cliente_ia=None, texto_de=None):
    if cliente_ia is None:
        return ficha_pendiente(norma, "no hay modelo de IA configurado")
    try:
        texto = texto_de(norma["id"]) if texto_de else ""
    except Exception as error:  # red caída, XML roto...
        return ficha_pendiente(norma, f"no se pudo leer el texto oficial ({error.__class__.__name__})")
    if len(texto) < 200:
        return ficha_pendiente(norma, "texto oficial demasiado corto o vacío")
    try:
        ficha, problemas = ficha_con_ia(cliente_ia, norma, texto)
    except Exception as error:
        # Error de conexión u otro fallo: no se marca como intentado, se reintentará.
        return ficha_pendiente(norma, f"error de la IA ({error.__class__.__name__})")
    if ficha is None:
        return ficha_pendiente(norma, "resumen descartado: " + "; ".join(problemas)[:400],
                               modelo_intentado=cliente_ia.modelo)
    return ficha


def resumir_carpeta(carpeta=CARPETA_NORMAS, cliente_ia=None, texto_de=None, rehacer=False):
    """Genera fichas.

    No se repiten (salvo con `rehacer`): las fichas ya generadas con IA ("ok") ni
    las que el MISMO modelo ya intentó y no superaron la verificación. Con otro
    modelo sí se vuelven a intentar.
    """
    normas = []
    for archivo in sorted(Path(carpeta).glob("*.json")):
        norma = json.loads(archivo.read_text(encoding="utf-8"))
        previa = norma.get("ficha") or {}
        if previa.get("estado") == "ok" and not rehacer:
            normas.append(norma)
            continue
        ya_intentada = cliente_ia is not None and previa.get("modelo_intentado") == cliente_ia.modelo
        if previa.get("estado") == "pendiente" and (cliente_ia is None or (ya_intentada and not rehacer)):
            # Sin IA solo se refresca el título simplificado (las reglas pueden mejorar).
            norma["ficha"] = previa | {"titulo_llano": titulo_simplificado(norma.get("titulo"))}
        else:
            norma["ficha"] = generar_ficha(norma, cliente_ia, texto_de)
        archivo.write_text(json.dumps(norma, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        normas.append(norma)
    return normas


def main():
    parser = argparse.ArgumentParser(description="Genera las fichas en lenguaje llano.")
    parser.add_argument("--rehacer", action="store_true", help="repetir también las fichas ya verificadas")
    args = parser.parse_args()

    from boe import guardar, ia
    cliente = ia.cliente_desde_entorno()
    if cliente is None:
        print("No hay modelo de IA configurado: las fichas quedan como 'pendiente'.")

    normas = resumir_carpeta(cliente_ia=cliente, texto_de=guardar.texto_de_norma, rehacer=args.rehacer)
    estados = [n["ficha"]["estado"] for n in normas]
    print(f"Fichas: {estados.count('ok')} verificadas, {estados.count('pendiente')} pendientes.")
    for n in normas:
        print(f"  {n['id']}  [{n['ficha']['estado']:9}]  {n['ficha']['titulo_llano'][:95]}")


if __name__ == "__main__":
    main()
