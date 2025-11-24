"""
Módulo de configuración del sistema.

Este módulo define los parámetros globales utilizados en la aplicación,
incluyendo rutas de archivos y ajustes de tiempos para la lógica del juego.
"""

import os

class Config:
    """
    Clase contenedora para la configuración global de la aplicación.

    Centraliza las constantes y parámetros para facilitar su modificación
    sin alterar la lógica principal del programa.
    """
    def __init__(self):
        """
        Inicializa una nueva instancia de configuración con valores predeterminados.

        Atributos:
            model_path (str): Ruta absoluta al archivo del modelo de MediaPipe Pose Landmarker.
            padding (int): Margen de relleno utilizado en la interfaz visual.
            game_time (int): Duración total de la sesión o juego en segundos.
            circle_time (int): Tiempo en segundos que permanecen visibles los indicadores circulares.
            circle_time_radius (int): Radio de los indicadores visuales de tiempo.
        """
        self.model_path = os.path.join(os.path.dirname(__file__), 'models/pose_landmarker_full.task')
        self.padding = 100
        self.game_time = 20
        self.circle_time = 1
        self.circle_time_radius = 15

# Instancia global exportada para ser importada por otros módulos
config = Config()