"""Pruebas del paso 0: comprueban que el entorno está bien preparado.

pytest ejecuta automáticamente cada función que empieza por `test_`.
Dentro, `assert` significa "esto tiene que ser verdad"; si no lo es, la prueba falla.
"""


def test_se_puede_importar_el_paquete():
    import boe

    assert boe.NOMBRE_PROYECTO == "El BOE en llano"


def test_esta_instalada_la_libreria_requests():
    import requests

    assert requests.__version__
