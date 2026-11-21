"""Conexión opcional con un modelo de IA (intercambiable).

El proyecto funciona SIN IA. Para activarla se configuran variables de entorno:

    BOE_IA_PROVEEDOR   ninguno (por defecto) | ollama | openai
    BOE_IA_MODELO      nombre del modelo, p. ej. "llama3.1:8b" o "gpt-4o-mini"
    BOE_IA_URL         URL base de la API (opcional; ver valores por defecto)
    BOE_IA_CLAVE       clave de la API externa (no hace falta para Ollama)

Ambos proveedores usan el formato de "chat completions" compatible con OpenAI,
que Ollama también ofrece en /v1. Por eso "openai" sirve para cualquier
servicio compatible (OpenAI, Mistral, Groq, OpenRouter...) cambiando BOE_IA_URL.

Los secretos se ponen en el entorno o en un archivo .env (está en .gitignore);
nunca en el código.
"""

import json
import os
import re

import requests

URL_POR_DEFECTO = {
    "ollama": "http://localhost:11434/v1",
    "openai": "https://api.openai.com/v1",
}


class ClienteIA:
    def __init__(self, url_base, modelo, clave=None, timeout=120):
        self.url_base = url_base.rstrip("/")
        self.modelo = modelo
        self.clave = clave
        self.timeout = timeout

    def completar_json(self, sistema, usuario):
        """Envía un mensaje y devuelve la respuesta del modelo como diccionario.

        Devuelve None si la respuesta no es JSON válido.
        """
        cabeceras = {"Content-Type": "application/json"}
        if self.clave:
            cabeceras["Authorization"] = f"Bearer {self.clave}"
        cuerpo = {
            "model": self.modelo,
            "temperature": 0,
            "response_format": {"type": "json_object"},
            "messages": [
                {"role": "system", "content": sistema},
                {"role": "user", "content": usuario},
            ],
        }
        respuesta = requests.post(
            f"{self.url_base}/chat/completions", headers=cabeceras, json=cuerpo, timeout=self.timeout
        )
        respuesta.raise_for_status()
        contenido = respuesta.json()["choices"][0]["message"]["content"]
        return extraer_json(contenido)


def extraer_json(texto):
    """Saca el primer objeto JSON de un texto (los modelos a veces añaden prosa)."""
    try:
        return json.loads(texto)
    except (json.JSONDecodeError, TypeError):
        pass
    encontrado = re.search(r"\{.*\}", texto or "", re.DOTALL)
    if not encontrado:
        return None
    try:
        return json.loads(encontrado.group(0))
    except json.JSONDecodeError:
        return None


def _cargar_env(archivo=".env"):
    """Lee un .env sencillo (CLAVE=valor) sin pisar variables ya definidas."""
    if not os.path.exists(archivo):
        return
    with open(archivo, encoding="utf-8") as f:
        for linea in f:
            linea = linea.strip()
            if not linea or linea.startswith("#") or "=" not in linea:
                continue
            clave, valor = linea.split("=", 1)
            os.environ.setdefault(clave.strip(), valor.strip().strip('"').strip("'"))


def cliente_desde_entorno():
    """Crea el cliente según las variables de entorno, o None si no hay IA."""
    _cargar_env()
    proveedor = os.environ.get("BOE_IA_PROVEEDOR", "ninguno").strip().lower()
    if proveedor in ("", "ninguno", "none"):
        return None
    if proveedor not in URL_POR_DEFECTO:
        raise ValueError(f"BOE_IA_PROVEEDOR desconocido: {proveedor!r} (usa ollama u openai)")
    modelo = os.environ.get("BOE_IA_MODELO")
    if not modelo:
        raise ValueError("Falta BOE_IA_MODELO")
    url = os.environ.get("BOE_IA_URL") or URL_POR_DEFECTO[proveedor]
    return ClienteIA(url, modelo, clave=os.environ.get("BOE_IA_CLAVE"))


# ---------- Tareas ----------

MAX_CARACTERES_TEXTO = 6000


def clasificar_con_ia(cliente, norma, texto, temas, impactos):
    """Pide al modelo tema e impacto. Devuelve campos validados, o None si falla.

    Solo se aceptan valores de las listas permitidas; cualquier otra cosa se
    descarta y se mantiene la clasificación por reglas.
    """
    sistema = (
        "Clasificas normas del Boletín Oficial del Estado. Responde SOLO con JSON "
        'con las claves "tema", "impacto" y "motivo" (una frase). '
        f"tema debe ser exactamente uno de: {json.dumps(temas, ensure_ascii=False)}. "
        f"impacto debe ser exactamente uno de: {json.dumps(impactos, ensure_ascii=False)}. "
        "Directo = cambia algo para mucha gente; Colectivos = afecta a grupos concretos; "
        "Técnico = organización interna, subvenciones a entidades o trámites."
    )
    usuario = (
        f"Tipo: {norma.get('rango')}\nÓrgano: {norma.get('departamento')}\n"
        f"Título: {norma.get('titulo')}\nMaterias: {', '.join(norma.get('materias') or [])}\n\n"
        f"Texto (inicio):\n{(texto or '')[:MAX_CARACTERES_TEXTO]}"
    )
    try:
        respuesta = cliente.completar_json(sistema, usuario)
    except requests.RequestException as error:
        print(f"    {norma['id']}: IA no disponible ({error.__class__.__name__}); se usan reglas.")
        return None

    if not respuesta or respuesta.get("tema") not in temas or respuesta.get("impacto") not in impactos:
        print(f"    {norma['id']}: respuesta de IA no válida; se usan reglas.")
        return None
    return {
        "tema": respuesta["tema"],
        "impacto": respuesta["impacto"],
        "clasificacion": {
            "metodo": "ia",
            "modelo": cliente.modelo,
            "motivo": str(respuesta.get("motivo", ""))[:300],
        },
    }
