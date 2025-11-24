"""
Definición de relaciones geométricas para el cálculo de ángulos corporales.

Este módulo contiene el diccionario `ANGULO_LANDMARKS_MAP`, que establece la topología
necesaria para calcular ángulos utilizando los índices de MediaPipe Pose.

Cada ángulo se define mediante una tupla de tres puntos (landmarks):
    1. Punto inicial (Extremo A).
    2. Vértice del ángulo (Punto central).
    3. Punto final (Extremo C).
"""

import mediapipe as mp
mp_pose = mp.solutions.pose

# Mapeo de identificadores de ángulo a tuplas de landmarks de MediaPipe (A, Vértice, C)
ANGULO_LANDMARKS_MAP = {
    "angulo_codo_izq": (
        mp_pose.PoseLandmark.LEFT_SHOULDER.value,
        mp_pose.PoseLandmark.LEFT_ELBOW.value,
        mp_pose.PoseLandmark.LEFT_WRIST.value
    ),
    "angulo_codo_der": (
        mp_pose.PoseLandmark.RIGHT_SHOULDER.value,
        mp_pose.PoseLandmark.RIGHT_ELBOW.value,
        mp_pose.PoseLandmark.RIGHT_WRIST.value
    ),
    "angulo_hombro_izq": (
        mp_pose.PoseLandmark.LEFT_ELBOW.value,
        mp_pose.PoseLandmark.LEFT_SHOULDER.value,
        mp_pose.PoseLandmark.LEFT_HIP.value
    ),
    "angulo_hombro_der": (
        mp_pose.PoseLandmark.RIGHT_ELBOW.value,
        mp_pose.PoseLandmark.RIGHT_SHOULDER.value,
        mp_pose.PoseLandmark.RIGHT_HIP.value
    ),
    "angulo_cadera_izq": (
        mp_pose.PoseLandmark.LEFT_SHOULDER.value,
        mp_pose.PoseLandmark.LEFT_HIP.value,
        mp_pose.PoseLandmark.LEFT_KNEE.value
    ),
    "angulo_cadera_der": (
        mp_pose.PoseLandmark.RIGHT_SHOULDER.value,
        mp_pose.PoseLandmark.RIGHT_HIP.value,
        mp_pose.PoseLandmark.RIGHT_KNEE.value
    ),
    "angulo_rodilla_izq": (
        mp_pose.PoseLandmark.LEFT_HIP.value,
        mp_pose.PoseLandmark.LEFT_KNEE.value,
        mp_pose.PoseLandmark.LEFT_ANKLE.value
    ),
    "angulo_rodilla_der": (
        mp_pose.PoseLandmark.RIGHT_HIP.value,
        mp_pose.PoseLandmark.RIGHT_KNEE.value,
        mp_pose.PoseLandmark.RIGHT_ANKLE.value
    ),
}