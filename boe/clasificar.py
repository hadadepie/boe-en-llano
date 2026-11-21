"""Paso 3: clasificar cada norma de la sección I por tema, impacto y ámbito.

Uso:
    python -m boe.clasificar            # clasifica todas las normas de datos/normas
    python -m boe.clasificar --ia       # además intenta mejorar tema/impacto con IA
                                        # (si hay un modelo configurado; ver boe/ia.py)

Método por defecto: reglas transparentes. Cada clasificación guarda los
"motivos" (qué palabras o datos la han decidido) para poder auditarla.

Señales y peso de cada una para el TEMA:
    epígrafe del sumario ×3 · título ×2 · materias oficiales del BOE ×1
    (las materias suman como máximo 3 puntos por tema, porque algunas leyes
    "ómnibus" traen 50 o más y si no decidirían ellas solas)
"""

import argparse
import json
import re
import unicodedata
from pathlib import Path

CARPETA_NORMAS = Path("datos/normas")

TEMAS = [
    "Trabajo y empleo",
    "Impuestos y dinero",
    "Vivienda y urbanismo",
    "Salud, consumo y animales",
    "Movilidad, energía y medio ambiente",
    "Derechos e igualdad",
    "Educación, cultura y ciencia",
    "Instituciones, ayudas e internacional",
]
TEMA_POR_DEFECTO = "Instituciones, ayudas e internacional"
MAX_PUNTOS_MATERIAS = 3
IMPACTOS = ["Directo", "Colectivos", "Técnico"]

# Palabras clave sin tildes y en minúsculas (el texto se normaliza igual).
# Se buscan como inicio de palabra: "tribut" encuentra "tributos", "tributación".
PALABRAS_TEMA = {
    "Trabajo y empleo": [
        "trabajador", "estatuto de los trabajadores", "salario minimo", "empleo",
        "laboral", "contrato de trabajo", "contratos de trabajo", "convenio colectivo",
        "convenios colectivos", "jornada", "seguridad social", "cotizacion", "pension",
        "jubilacion", "incapacidad", "desempleo", "empleados publicos", "funcion publica",
        "funcionarios", "retribuciones", "personal al servicio",
    ],
    "Impuestos y dinero": [
        "impuesto", "tribut", "fiscal", "irpf", "iva", "tasas", "presupuest",
        "creditos extraordinarios", "creditos presupuestarios", "deuda publica", "tesoro",
        "financiacion de las comunidades", "financiacion territorial", "recaudacion",
        "prestamo", "intereses", "hacienda", "catastro", "cesion de tributos",
    ],
    "Vivienda y urbanismo": [
        "vivienda", "urbanis", "suelo", "arrendamientos urbanos", "alquiler",
        "ordenacion del territorio", "hipoteca", "edificacion", "planeamiento",
    ],
    "Salud, consumo y animales": [
        "salud", "sanidad", "sanitari", "medicamento", "consumidores", "alimentacion",
        "alimentaria", "seguridad alimentaria", "animal", "veterinari", "ganad",
        "ganado", "plagas", "sanidad vegetal", "tabaco", "bebidas alcoholicas",
        "enfermedad", "denominaciones de origen", "vinos", "leche",
    ],
    "Movilidad, energía y medio ambiente": [
        "transporte", "ferrocarril", "ferroviari", "aereo", "aeropuerto", "buque",
        "maritim", "navegacion", "carretera", "circulacion vial", "vehiculo",
        "movilidad", "energ", "gas", "gases", "butano", "electric", "petrol", "combustible",
        "emision", "efecto invernadero", "clima", "medio ambiente", "ambiental",
        "contaminacion", "residuos", "aguas", "hidraulic", "pesca", "pesquer",
        "centros de datos", "telecomunicacion", "inundaciones", "sequias",
    ],
    "Derechos e igualdad": [
        "igualdad", "genero", "mujer", "discapacidad", "derechos humanos", "menores",
        "familia", "libertad religiosa", "asistencia social", "dependencia", "mayores",
        "ancianos", "pobreza", "migraciones", "inmigracion", "codigo civil",
        "capacidad juridica", "tutela", "divorcio", "victimas", "justicia gratuita",
        "asistencia juridica gratuita",
    ],
    "Educación, cultura y ciencia": [
        "educacion", "ensenanza", "universi", "profesorado", "formacion profesional",
        "investigacion", "ciencia", "cientific", "tecnolog", "cultura",
        "patrimonio cultural", "deporte", "curriculo", "becas", "docentes",
    ],
    "Instituciones, ayudas e internacional": [
        "acuerdo", "acuerdos internacionales", "tratado", "naciones unidas",
        "organizacion de la administracion", "agencia estatal", "agencias estatales",
        "plantilla", "administracion de justicia", "juzgados", "planta judicial",
        "ministerio fiscal", "tribunal", "cortes generales", "subvencion", "ayudas",
        "comunidades autonomas", "administracion local", "cooperacion", "defensa",
        "militar", "armamento", "entes publicos", "registros administrativos",
    ],
}

# --- Impacto ---------------------------------------------------------------
# 1) Técnico: trámites, organización interna, subvenciones a entidades concretas.
PATRONES_TECNICO = [
    ("concesion directa", "subvención o préstamo a entidades concretas"),
    ("convalidacion del real decreto-ley", "trámite parlamentario de una norma ya en vigor"),
    ("se aprueba el estatuto de", "estatuto de un organismo público"),
    ("reglamento de funcionamiento", "funcionamiento interno de un órgano"),
    ("plantilla organica", "organización interna"),
    ("estructura organica", "organización interna"),
    ("se actualiza el anexo", "actualización administrativa"),
    ("se publica el fallo", "publicación de una sentencia"),
]
RANGOS_TECNICOS = {"Corrección (errores o erratas)": "corrección de errores"}

# 2) Directo: cambios que llegan a mucha gente.
PATRONES_DIRECTO = [
    "salario minimo", "pension", "impuesto sobre la renta", "irpf", "iva",
    "estatuto de los trabajadores", "jornada", "alquiler", "arrendamientos urbanos",
    "precios de venta al publico", "precios maximos de venta", "butano",
    "gases licuados", "tarifa", "permiso", "prestacion",
]

# 3) Colectivos: normas para un sector o grupo concreto.
PATRONES_COLECTIVOS = [
    "personal al servicio", "empleados publicos", "profesorado", "pesca", "pesquer",
    "productores", "empresas", "buques", "explotaciones", "centros de datos",
    "ministros de culto", "abogados", "procuradores",
]
RANGOS_DIRECTOS = {"Ley", "Ley Orgánica", "Real Decreto-ley", "Decreto-ley", "Decreto Legislativo"}

# --- Ámbito ----------------------------------------------------------------
COMUNIDADES = [
    "Andalucía", "Aragón", "Principado de Asturias", "Illes Balears", "Canarias",
    "Cantabria", "Castilla y León", "Castilla-La Mancha", "Cataluña",
    "Comunitat Valenciana", "Extremadura", "Galicia", "Comunidad de Madrid",
    "Región de Murcia", "Comunidad Foral de Navarra", "País Vasco", "La Rioja",
    "Ceuta", "Melilla",
]
ALIAS_COMUNIDADES = {
    "asturias": "Principado de Asturias",
    "baleares": "Illes Balears",
    "valenciana": "Comunitat Valenciana",
    "madrid": "Comunidad de Madrid",
    "murcia": "Región de Murcia",
    "navarra": "Comunidad Foral de Navarra",
    "euskadi": "País Vasco",
}


def normalizar(texto):
    """Minúsculas y sin tildes: 'Educación' -> 'educacion'."""
    texto = unicodedata.normalize("NFKD", texto or "")
    return "".join(c for c in texto if not unicodedata.combining(c)).lower()


def _contiene(texto_normalizado, palabra):
    """Busca `palabra` al inicio de una palabra del texto.

    Las palabras cortas (4 letras o menos) deben coincidir enteras, para que
    "gas" no encuentre "gastos" ni "iva" encuentre "ivan".
    """
    final = r"\b" if len(palabra) <= 4 else ""
    return re.search(r"\b" + re.escape(palabra) + final, texto_normalizado) is not None


def clasificar_tema(norma):
    epigrafe = normalizar(norma.get("epigrafe"))
    titulo = normalizar(norma.get("titulo"))
    materias = [normalizar(m) for m in norma.get("materias") or []]

    puntos = {tema: 0 for tema in TEMAS}
    motivos = {tema: [] for tema in TEMAS}
    for tema, palabras in PALABRAS_TEMA.items():
        for palabra in palabras:
            if _contiene(epigrafe, palabra):
                puntos[tema] += 3
                motivos[tema].append(f"epígrafe: {palabra}")
            if _contiene(titulo, palabra):
                puntos[tema] += 2
                motivos[tema].append(f"título: {palabra}")
        coincidencias = [m for m in materias if any(_contiene(m, p) for p in palabras)]
        puntos[tema] += min(len(coincidencias), MAX_PUNTOS_MATERIAS)
        motivos[tema].extend(f"materia: {m}" for m in coincidencias[:MAX_PUNTOS_MATERIAS])

    mejor = max(TEMAS, key=lambda t: puntos[t])  # en empate gana el primero de TEMAS
    if puntos[mejor] == 0:
        return TEMA_POR_DEFECTO, ["sin coincidencias: tema por defecto"]
    return mejor, [f"{puntos[mejor]} puntos"] + motivos[mejor][:6]


def clasificar_impacto(norma):
    titulo = normalizar(norma.get("titulo"))
    epigrafe = normalizar(norma.get("epigrafe"))
    rango = norma.get("rango") or ""

    if rango in RANGOS_TECNICOS:
        return "Técnico", [RANGOS_TECNICOS[rango]]
    for patron, motivo in PATRONES_TECNICO:
        if patron in titulo:
            return "Técnico", [motivo]
    for patron in PATRONES_DIRECTO:
        if _contiene(titulo, patron) or _contiene(epigrafe, patron):
            return "Directo", [f"afecta a mucha gente: {patron}"]
    for patron in PATRONES_COLECTIVOS:
        if _contiene(titulo, patron) or _contiene(epigrafe, patron):
            return "Colectivos", [f"grupo concreto: {patron}"]
    if rango in RANGOS_DIRECTOS:
        return "Directo", [f"norma con rango de ley ({rango})"]
    if rango == "Acuerdo Internacional":
        return "Técnico", ["acuerdo internacional sin efecto directo claro"]
    return "Colectivos", ["regla por defecto"]


def clasificar_ambito(norma):
    if (norma.get("origen_legislativo") or "").lower() == "estatal":
        return "Estatal"
    organo = normalizar(norma.get("departamento") or norma.get("departamento_sumario"))
    for comunidad in COMUNIDADES:
        if normalizar(comunidad) in organo:
            return comunidad
    for alias, comunidad in ALIAS_COMUNIDADES.items():
        if alias in organo:
            return comunidad
    return norma.get("departamento") or "Desconocido"


def clasificar(norma):
    """Devuelve los campos de clasificación por reglas (no modifica `norma`)."""
    tema, motivos_tema = clasificar_tema(norma)
    impacto, motivos_impacto = clasificar_impacto(norma)
    return {
        "tema": tema,
        "impacto": impacto,
        "ambito": clasificar_ambito(norma),
        "clasificacion": {
            "metodo": "reglas",
            "motivos_tema": motivos_tema,
            "motivos_impacto": motivos_impacto,
        },
    }


def clasificar_carpeta(carpeta=CARPETA_NORMAS, cliente_ia=None, texto_de=None):
    """Clasifica todos los JSON de `carpeta`, reescribiéndolos.

    Las reglas se recalculan siempre (son baratas y deterministas). Si hay
    `cliente_ia`, se intenta mejorar tema e impacto solo en las normas que aún
    no tienen clasificación por IA, para no repetir llamadas.
    """
    from boe import ia  # import tardío: el módulo de IA es opcional

    resultado = []
    for archivo in sorted(Path(carpeta).glob("*.json")):
        norma = json.loads(archivo.read_text(encoding="utf-8"))
        previa = norma.get("clasificacion") or {}
        if previa.get("metodo") == "ia":
            nueva = {k: norma[k] for k in ("tema", "impacto")} | {"clasificacion": previa}
            nueva["ambito"] = clasificar_ambito(norma)
        else:
            nueva = clasificar(norma)
            if cliente_ia is not None:
                texto = texto_de(norma["id"]) if texto_de else ""
                mejorada = ia.clasificar_con_ia(cliente_ia, norma, texto, TEMAS, IMPACTOS)
                if mejorada:
                    nueva.update(mejorada)
        norma.update(nueva)
        archivo.write_text(json.dumps(norma, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        resultado.append(norma)
    return resultado


def main():
    parser = argparse.ArgumentParser(description="Clasifica las normas guardadas.")
    parser.add_argument("--ia", action="store_true", help="mejorar con el modelo de IA configurado")
    args = parser.parse_args()

    cliente, texto_de = None, None
    if args.ia:
        from boe import guardar, ia
        cliente = ia.cliente_desde_entorno()
        texto_de = guardar.texto_de_norma
        if cliente is None:
            print("No hay modelo de IA configurado (BOE_IA_PROVEEDOR). Se usan solo reglas.")

    normas = clasificar_carpeta(cliente_ia=cliente, texto_de=texto_de)
    print(f"Clasificadas {len(normas)} normas.")
    for n in normas:
        print(f"  {n['id']}  {n['impacto']:10}  {n['tema'][:28]:28}  {n['ambito'][:18]:18}  {n['titulo'][:60]}")


if __name__ == "__main__":
    main()
