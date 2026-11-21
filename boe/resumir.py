"""Paso 4: ficha en lenguaje llano de cada norma.

Uso:
    python -m boe.resumir             # genera/actualiza las fichas de datos/normas
    python -m boe.resumir --rehacer   # vuelve a pedir a la IA también las ya hechas

Reglas obligatorias (ver CLAUDE.md):
- Basarse SOLO en el texto oficial. Nunca inventar cifras, fechas ni efectos.
- Sin resumen fiable, la ficha es "pendiente" y muestra solo el título simplificado.
- Toda ficha lleva AVISO.

Sin IA configurada, todas las fichas quedan "pendiente" (el proyecto funciona igual).
Con IA, el resumen solo se acepta si supera `verificar_ficha`:
    1. cada campo trae una cita literal que existe en el texto oficial;
    2. todo número que aparezca en la ficha aparece también en el texto oficial.
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


# ---------- Verificación contra el texto oficial ----------

def _sin_espacios_raros(texto):
    return re.sub(r"\s+", " ", normalizar(texto)).strip()


def numeros(texto):
    """Números de un texto, sin separadores: '1.184,50 €' -> {'118450'}."""
    return {re.sub(r"[.,]", "", n) for n in re.findall(r"\d[\d.,]*\d|\d", texto or "")}


def verificar_ficha(ficha, texto_oficial):
    """Devuelve la lista de problemas (vacía si la ficha es fiable)."""
    problemas = []
    texto_norm = _sin_espacios_raros(texto_oficial)
    numeros_texto = numeros(texto_oficial)

    for campo in CAMPOS:
        valor = (ficha.get(campo) or "").strip()
        if not valor:
            problemas.append(f"{campo}: vacío")
            continue
        if valor == NO_CONSTA:
            continue
        cita = (ficha.get("citas") or {}).get(campo, "")
        if campo != "titulo_llano":
            if len(cita) < 15:
                problemas.append(f"{campo}: sin cita del texto")
            elif _sin_espacios_raros(cita) not in texto_norm:
                problemas.append(f"{campo}: la cita no aparece en el texto oficial")
        inventados = numeros(valor) - numeros_texto
        if inventados:
            problemas.append(f"{campo}: números que no están en el texto: {sorted(inventados)}")
    return problemas


# ---------- Ficha ----------

def ficha_pendiente(norma, motivo):
    return {
        "estado": "pendiente",
        "titulo_llano": titulo_simplificado(norma.get("titulo")),
        "enlace": norma.get("url_html"),
        "aviso": AVISO,
        "metodo": "reglas",
        "motivo_pendiente": motivo,
    }


def extracto_para_ia(texto, maximo=12000):
    """Inicio del texto + párrafos sobre entrada en vigor (suelen ir al final)."""
    if len(texto) <= maximo:
        return texto
    inicio = texto[: maximo * 2 // 3]
    vigor = [p for p in texto.splitlines() if re.search(r"entrar[aá] en vigor|entrada en vigor|surtir[aá] efectos", p, re.I)]
    final = "\n".join(vigor)[: maximo // 3]
    return f"{inicio}\n[...]\n{final}"


INSTRUCCIONES_IA = f"""Eres un redactor que explica normas del BOE a personas sin formación jurídica.
Usa EXCLUSIVAMENTE el texto oficial que se te da. No añadas nada que no esté en él:
ni cifras, ni fechas, ni efectos, ni consejos. Frases cortas y palabras sencillas.
Si el texto no dice algo, escribe exactamente: "{NO_CONSTA}"
Escribe fechas y cifras tal como aparecen en el texto (por ejemplo "1 de enero de 2027").

Responde SOLO con un JSON con estas claves:
  "titulo_llano":   una sola frase que diga qué hace la norma
  "que_cambia":     qué cambia (2-3 frases como máximo)
  "a_quien_afecta": a quién afecta
  "desde_cuando":   desde cuándo se aplica
  "que_hacer":      qué tiene que hacer la persona afectada (o "{NO_CONSTA}")
  "citas": objeto con las claves que_cambia, a_quien_afecta, desde_cuando y que_hacer;
           cada una con un fragmento COPIADO LITERALMENTE del texto oficial
           (entre 15 y 300 caracteres) que respalde lo que has escrito.
           Si el campo es "{NO_CONSTA}", deja la cita vacía.
"""


def ficha_con_ia(cliente, norma, texto):
    """Pide la ficha al modelo y la verifica. Devuelve (ficha, problemas)."""
    usuario = f"Título oficial: {norma.get('titulo')}\n\nTexto oficial:\n{extracto_para_ia(texto)}"
    respuesta = cliente.completar_json(INSTRUCCIONES_IA, usuario)
    if not isinstance(respuesta, dict):
        return None, ["la IA no devolvió JSON"]
    problemas = verificar_ficha(respuesta, texto)
    if problemas:
        return None, problemas
    ficha = {campo: respuesta[campo].strip() for campo in CAMPOS}
    ficha.update({
        "estado": "ok",
        "citas": {k: v for k, v in (respuesta.get("citas") or {}).items() if k in CAMPOS},
        "enlace": norma.get("url_html"),
        "aviso": AVISO,
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
        return ficha_pendiente(norma, f"error de la IA ({error.__class__.__name__})")
    if ficha is None:
        return ficha_pendiente(norma, "resumen descartado: " + "; ".join(problemas)[:400])
    return ficha


def resumir_carpeta(carpeta=CARPETA_NORMAS, cliente_ia=None, texto_de=None, rehacer=False):
    """Genera fichas. Las ya verificadas ("ok") no se repiten salvo con `rehacer`."""
    normas = []
    for archivo in sorted(Path(carpeta).glob("*.json")):
        norma = json.loads(archivo.read_text(encoding="utf-8"))
        previa = norma.get("ficha") or {}
        if previa.get("estado") == "ok" and not rehacer:
            normas.append(norma)
            continue
        if previa.get("estado") == "pendiente" and cliente_ia is None:
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
