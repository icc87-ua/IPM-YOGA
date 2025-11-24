"""
Base de datos de parámetros biomecánicos para posturas de yoga.

Este módulo define el diccionario `POSTURAS_YOGA`, que actúa como la fuente de verdad
para la evaluación de posturas. Cada entrada contiene los ángulos objetivo (en grados)
para articulaciones específicas y un umbral de tolerancia para la validación.

Estructura de datos:
    Clave (str): Nombre de la postura (ej. "GUERRERO_1").
    Valor (dict): Diccionario de configuración de la postura:
        - Claves de ángulo (str): Identificadores de articulaciones (ej. "angulo_codo_izq").
        - Valores de ángulo (int): Grados objetivo esperados (0-180).
        - "tolerancia" (int): Margen de error aceptable en grados (+/-) para considerar
          la postura como correcta.
"""

POSTURAS_YOGA = {
    
    "FLEXION": {
        "angulo_codo_izq": 170,
        "angulo_hombro_izq": 80,
        "angulo_cadera_izq": 175,
        "angulo_rodilla_izq": 175,
        "tolerancia": 40
    },

    "GUERRERO_4": {
        "angulo_codo_izq": 170,
        "angulo_hombro_izq": 170,
        "angulo_cadera_izq": 130,
        "angulo_rodilla_izq": 100,
        "angulo_rodilla_der": 175,
        "tolerancia": 40
    },

    "PERRO_BOCA_ABAJO": {
        "angulo_codo_izq": 175,
        "angulo_hombro_izq": 170,
        "angulo_cadera_izq": 90,
        "angulo_rodilla_izq": 175,
        "tolerancia": 40
    },

    "PERRO_BOCA_ARRIBA": {
        "angulo_codo_izq": 170,
        "angulo_hombro_izq": 90,
        "angulo_cadera_izq": 175,
        "angulo_rodilla_izq": 175,
        "tolerancia": 40
    },

    "PINZA_DE_PIE": {
        "angulo_cadera_izq": 20,
        "angulo_rodilla_izq": 175,
        "angulo_cadera_der": 20,
        "angulo_rodilla_der": 175,
        "tolerancia": 40 
    },

    "PINZA_SENTADA": {
        "angulo_cadera_izq": 45,
        "angulo_rodilla_izq": 175,
        "tolerancia": 40
    },

    "ARBOL": {
        "angulo_codo_izq": 40,
        "angulo_codo_der": 40,
        "angulo_cadera_izq": 100,
        "angulo_cadera_der": 175,
        "angulo_rodilla_izq": 45,
        "angulo_rodilla_der": 175,
        "tolerancia": 40
    },

    "POSE_FACIL": {
        "angulo_cadera_izq": 100,
        "angulo_rodilla_izq": 45,
        "angulo_codo_izq": 160,
        "angulo_cadera_der": 100,
        "angulo_rodilla_der": 45,
        "angulo_codo_der": 160,
        "tolerancia": 40
    },

    "TRIANGULO_EXTENDIDO": {
        "angulo_codo_izq": 175,
        "angulo_codo_der": 175,
        "angulo_hombro_izq": 90,
        "angulo_hombro_der": 90,
        "angulo_rodilla_izq": 175,
        "angulo_rodilla_der": 175,
        "tolerancia": 40
    },

    "BARCA": {
        "angulo_cadera_izq": 90,
        "angulo_rodilla_izq": 90,
        "angulo_codo_izq": 170,
        "tolerancia": 40
    },

    "SENTADILLA": {
        "angulo_codo_izq": 40,
        "angulo_codo_der": 40,
        "angulo_cadera_izq": 45,
        "angulo_cadera_der": 45,
        "angulo_rodilla_izq": 45,
        "angulo_rodilla_der": 45,
        "tolerancia": 40
    },

    "GUERRERO_2": {
        "angulo_codo_izq": 175,
        "angulo_codo_der": 175,
        "angulo_hombro_izq": 90,
        "angulo_hombro_der": 90,
        "angulo_rodilla_izq": 90,
        "angulo_rodilla_der": 175,
        "tolerancia": 40
    },

    "PLANCHA_LATERAL": {
        "angulo_codo_izq": 175,
        "angulo_codo_der": 175,
        "angulo_hombro_der": 90,
        "angulo_cadera_izq": 175,
        "angulo_rodilla_izq": 175,
        "tolerancia": 40
    },

    "GUERRERO_3": {
        "angulo_codo_izq": 175,
        "angulo_rodilla_izq": 175,
        "angulo_rodilla_der": 175,
        "angulo_cadera_izq": 90,
        "angulo_cadera_der": 175,
        "tolerancia": 40
    },

    "GUERRERO_1": {
        "angulo_codo_izq": 160,
        "angulo_codo_der": 160,
        "angulo_hombro_izq": 170,
        "angulo_hombro_der": 170,
        "angulo_rodilla_izq": 100,
        "angulo_rodilla_der": 175,
        "tolerancia": 40
    },

    "MESA": {
        "angulo_codo_izq": 170,
        "angulo_hombro_izq": 90,
        "angulo_cadera_izq": 90,
        "angulo_rodilla_izq": 90,
        "tolerancia": 40
    }
}