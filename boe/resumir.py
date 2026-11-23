"""Paso 4: ficha en lenguaje llano de cada norma.

Uso:
    python -m boe.resumir             # genera/actualiza las fichas de datos/normas
    python -m boe.resumir --rehacer   # vuelve a pedir a la IA también las ya hechas
    python -m boe.resumir --solo BOE-A-2026-24189 BOE-A-2026-24317   # prueba con pocas normas

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


# ---------- Titular corto (sin IA) ----------
# Para portada y listas. Solo quita palabras del titular simplificado (fechas,
# números de normas citadas, quién interpuso un recurso, dónde se firmó un
# acuerdo) y, si aún es largo, lo corta con «…». El título completo sigue en la ficha.

MAX_TITULAR_CORTO = 120
_REFERENCIA = r"\b(?:[A-Z]{2,5}/)?\d+/\d{4}"  # "1013/2026", "DEF/1363/2016"
# Los reales decretos-ley conservan su número: es como se los conoce (y como se votan).
_RANGO_CITADO = r"(?:Real Decreto Legislativo|Real Decreto(?!-ley)|Decreto(?!-ley)|Ley Orgánica|Ley Foral|Ley|Orden|Resolución)"
# Palabras con las que no debe acabar un titular cortado ("…de la…").
_PALABRAS_VACIAS = {"a", "al", "con", "de", "del", "e", "el", "en", "entre", "la", "las", "lo", "los", "o",
                    "para", "por", "que", "se", "sobre", "su", "sus", "un", "una", "y"}


def _quitar_final_vacio(t):
    palabras = t.rstrip(" ,;:").split(" ")
    while len(palabras) > 1 and palabras[-1].lower() in _PALABRAS_VACIAS:
        palabras.pop()
    return " ".join(palabras).rstrip(" ,;:")


def _cortar(t, maximo):
    """Corta en el último límite de cláusula antes de `maximo` (o, si no hay, de palabra) y añade «…»."""
    if len(t) <= maximo:
        return t
    trozo = t[:maximo]
    for separador in ("; ", ", ", " y "):
        k = trozo.rfind(separador)
        if k >= maximo * 2 // 3:
            return _quitar_final_vacio(trozo[:k]) + "…"
    return _quitar_final_vacio(re.sub(r"\s+\S*$", "", trozo)) + "…"


def titular_corto(titular, maximo=MAX_TITULAR_CORTO):
    """'Se modifica la Orden DEF/1363/2016, de 28 de julio, por la que se regulan...'
    -> 'Se modifica la Orden por la que se regulan...'. No añade palabras."""
    t = re.sub(r"\s+", " ", (titular or "")).strip()
    # Fecha detrás de una norma citada: "Real Decreto 956/2017, de 3 de noviembre," -> "Real Decreto 956/2017,"
    t = re.sub(rf"({_REFERENCIA}), {_FECHA}(?=[,;.:)]| y )", r"\1", t)
    # Fecha y órgano de una resolución o acuerdo citado: "Resolución de 4 de julio de 2017, de la Secretaría…, por la que"
    t = re.sub(rf"\b(Resolución|Acuerdo del? Consejo de Ministros) {_FECHA}(?:, (?:del?|de la) [^,]+)?, (?=por)", r"\1 ", t)
    # Número de la norma citada cuando sigue su descripción: "el Real Decreto 267/2017, por el que" -> "el Real Decreto por el que"
    t = re.sub(rf"\b({_RANGO_CITADO}) {_REFERENCIA},? (?=por (?:el|la) que |sobre |reguladora |de )", r"\1 ", t)
    # Recursos: "el recurso contencioso-administrativo 19/2025, interpuesto por X, contra" -> "el recurso contra"
    t = re.sub(rf"\b(recursos?)(?: contencioso-administrativos?)?(?: (?:n\.º )?{_REFERENCIA})?,? interpuestos? por .+? contra ", r"\1 contra ", t)
    # Acuerdos internacionales: ", hecho en Madrid el 3 y 4 de agosto de 2026" fuera.
    t = re.sub(r", hech[oa] en [^.;]+? el [^.;]+?\d{4}(?=[.;]|$)", "", t)
    t = re.sub(r"\s+,", ",", t).strip()
    if not t.endswith((".", "…")):
        t += "."
    return _cortar(t, maximo)


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

# El BOE separa a veces los miles con un espacio ("1 286 euros/mes") o un
# espacio duro; se unen antes de leer los números.
_SEPARADOR_MILES = re.compile(r"(?<=\d)[    ](?=\d{3}(?!\d))")

# Números escritos con letras ("ciento veinte días") -> su valor (120).
_VALOR_PALABRA = {
    "cero": 0, "un": 1, "uno": 1, "una": 1, "dos": 2, "tres": 3, "cuatro": 4, "cinco": 5,
    "seis": 6, "siete": 7, "ocho": 8, "nueve": 9, "diez": 10, "once": 11, "doce": 12,
    "trece": 13, "catorce": 14, "quince": 15, "dieciseis": 16, "diecisiete": 17,
    "dieciocho": 18, "diecinueve": 19, "veinte": 20, "veintiun": 21, "veintiuno": 21,
    "veintiuna": 21, "veintidos": 22, "veintitres": 23, "veinticuatro": 24, "veinticinco": 25,
    "veintiseis": 26, "veintisiete": 27, "veintiocho": 28, "veintinueve": 29, "treinta": 30,
    "cuarenta": 40, "cincuenta": 50, "sesenta": 60, "setenta": 70, "ochenta": 80,
    "noventa": 90, "cien": 100, "ciento": 100,
    **{f"{p}ient{g}": v for p, v in [("dosc", 200), ("tresc", 300), ("cuatroc", 400),
                                      ("seisc", 600), ("setec", 700), ("ochoc", 800)]
       for g in ("os", "as")},
    "quinientos": 500, "quinientas": 500, "novecientos": 900, "novecientas": 900,
}
_MULTIPLICADOR = {"mil": 1000, "millon": 1_000_000, "millones": 1_000_000}
_ARTICULOS = {"un", "uno", "una"}  # solos casi siempre son artículos, no números


def numeros_con_letra(texto):
    """Valores de los números escritos con letras: 'ciento veinte días' -> {'120'}.

    Se agrupan las palabras numéricas seguidas (admitiendo "y": "treinta y cinco").
    "un", "uno" o "una" solos no cuentan.
    """
    palabras = re.findall(r"[a-zñ]+", normalizar(texto))
    valores, grupo = set(), []

    def cerrar():
        if grupo and not (len(grupo) == 1 and grupo[0] in _ARTICULOS):
            total = actual = 0
            for p in grupo:
                if p in _VALOR_PALABRA:
                    actual += _VALOR_PALABRA[p]
                elif p == "mil":
                    total += (actual or 1) * 1000
                    actual = 0
                else:  # millón / millones
                    total = (total + (actual or 1)) * 1_000_000
                    actual = 0
            valores.add(str(total + actual))
        grupo.clear()

    for i, p in enumerate(palabras):
        es_numero = p in _VALOR_PALABRA or p in _MULTIPLICADOR
        enlace = (p == "y" and grupo and i + 1 < len(palabras)
                  and palabras[i + 1] in _VALOR_PALABRA)
        if es_numero:
            grupo.append(p)
        elif not enlace:
            cerrar()
    cerrar()
    return valores


def numeros(texto):
    """Números de un texto, en cifras o con letras, sin separadores.

    '1.184,50 €' -> {'118450'}; '1 286 euros' -> {'1286'}; 'ciento veinte' -> {'120'}.
    """
    texto = _SEPARADOR_MILES.sub("", texto or "")
    cifras = {re.sub(r"[.,]", "", n) for n in re.findall(r"\d[\d.,]*\d|\d", texto)}
    return cifras | numeros_con_letra(texto)
_RE_VIGENCIA = re.compile(r"vigor|efectos|vigencia|aplicaci[oó]n|aplicar[aá]|a partir del?\b", re.I)
_SIGLAS_BOLETINES = "BOE BOJA BOA BOPA BOIB BOC BOCA BOCYL BOCM DOCM DOGC DOGV DOCV DOE DOG BOR BORM BON BOPV BOME BOCCE".split()
# Las palabras sin distinguir mayúsculas; las siglas solo en mayúsculas ("BOE", no "boe").
_RE_BOLETIN = re.compile(r"(?i:bolet[ií]n|diario oficial)|\b(?:" + "|".join(_SIGLAS_BOLETINES) + r")\b")
MIN_PARRAFO_VIGENCIA = 60


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


def resumir_carpeta(carpeta=CARPETA_NORMAS, cliente_ia=None, texto_de=None, rehacer=False, solo=None):
    """Genera fichas.

    No se repiten (salvo con `rehacer`): las fichas ya generadas con IA ("ok") ni
    las que el MISMO modelo ya intentó y no superaron la verificación. Con otro
    modelo sí se vuelven a intentar.

    `solo` (lista de identificadores) limita la IA a esas normas; el resto solo
    refresca su título simplificado. Útil para pruebas rápidas.
    """
    normas = []
    for archivo in sorted(Path(carpeta).glob("*.json")):
        norma = json.loads(archivo.read_text(encoding="utf-8"))
        previa = norma.get("ficha") or {}
        if previa.get("estado") == "ok" and not rehacer:
            normas.append(norma)
            continue
        ya_intentada = cliente_ia is not None and previa.get("modelo_intentado") == cliente_ia.modelo
        fuera_de_prueba = solo is not None and norma["id"] not in solo
        if fuera_de_prueba and previa.get("estado") == "ok":
            normas.append(norma)
            continue
        if fuera_de_prueba or (previa.get("estado") == "pendiente" and (cliente_ia is None or (ya_intentada and not rehacer))):
            # Sin IA solo se refresca el título simplificado (las reglas pueden mejorar).
            norma["ficha"] = (previa or ficha_pendiente(norma, "no hay modelo de IA configurado")) | {
                "titulo_llano": titulo_simplificado(norma.get("titulo"))}
        else:
            norma["ficha"] = generar_ficha(norma, cliente_ia, texto_de)
        archivo.write_text(json.dumps(norma, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        normas.append(norma)
    return normas


def main():
    parser = argparse.ArgumentParser(description="Genera las fichas en lenguaje llano.")
    parser.add_argument("--rehacer", action="store_true", help="repetir también las fichas ya hechas o intentadas")
    parser.add_argument("--solo", nargs="+", metavar="BOE-A-…", help="usar la IA solo con estas normas (prueba rápida)")
    args = parser.parse_args()

    from boe import guardar, ia
    cliente = ia.cliente_desde_entorno()
    if cliente is None:
        print("No hay modelo de IA configurado: las fichas quedan como 'pendiente'.")

    normas = resumir_carpeta(cliente_ia=cliente, texto_de=guardar.texto_de_norma, rehacer=args.rehacer, solo=args.solo)
    estados = [n["ficha"]["estado"] for n in normas]
    print(f"Fichas: {estados.count('ok')} automáticas (experimentales), {estados.count('pendiente')} pendientes.")
    for n in normas:
        print(f"  {n['id']}  [{n['ficha']['estado']:9}]  {n['ficha']['titulo_llano'][:95]}")


if __name__ == "__main__":
    main()
