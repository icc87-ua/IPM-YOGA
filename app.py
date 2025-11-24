"""
Sistema de Instructor de Yoga Inteligente (AI Yoga Instructor).

Este script utiliza MediaPipe Pose y OpenCV para crear una aplicación interactiva
que guía al usuario a través de una secuencia de posturas de yoga. Compara los
ángulos corporales del usuario en tiempo real con los ángulos objetivo definidos
para cada asana.

Dependencias:
    - cv2 (OpenCV)
    - mediapipe
    - numpy
    - config (módulo local)
    - posturas (módulo local)
    - angulos (módulo local)
"""

import sys
import cv2
import mediapipe as mp
import numpy as np
import time
import os
import glob

from config import config
from posturas import POSTURAS_YOGA
from angulos import ANGULO_LANDMARKS_MAP

# Configuración de MediaPipe Pose
BaseOptions = mp.tasks.BaseOptions
PoseLandmarker = mp.tasks.vision.PoseLandmarker
PoseLandmarkerOptions = mp.tasks.vision.PoseLandmarkerOptions
VisionRunningMode = mp.tasks.vision.RunningMode

options = PoseLandmarkerOptions(
    base_options=BaseOptions(model_asset_path=config.model_path),
    running_mode=VisionRunningMode.VIDEO,
    num_poses=1
)

def calcular_angulo(a, b, c):
    """
    Calcula el ángulo geométrico en grados en el vértice 'b' formado por los puntos a, b y c.

    Utiliza el producto escalar de vectores para determinar el ángulo. Verifica la
    visibilidad de los landmarks antes de calcular.

    Args:
        a (Landmark): Primer punto (ej. cadera).
        b (Landmark): Vértice del ángulo (ej. rodilla).
        c (Landmark): Tercer punto (ej. tobillo).

    Returns:
        float: El ángulo en grados (0-180).
        None: Si la visibilidad de algún punto es baja o hay error matemático.
    """
    if a.visibility < 0.5 or b.visibility < 0.5 or c.visibility < 0.5:
        return None

    A = np.array([a.x, a.y])
    B = np.array([b.x, b.y])
    C = np.array([c.x, c.y])
    
    # Vectores BA y BC
    ba = A - B
    bc = C - B
    
    prod_escalar = np.dot(ba, bc)
    magnitud_ba = np.linalg.norm(ba)
    magnitud_bc = np.linalg.norm(bc)
    
    if magnitud_ba == 0 or magnitud_bc == 0:
        return None
        
    cos_theta = prod_escalar / (magnitud_ba * magnitud_bc)
    cos_theta = np.clip(cos_theta, -1.0, 1.0)
    angulo_rad = np.arccos(cos_theta)
    angulo_grados = np.degrees(angulo_rad)
    
    return angulo_grados

def crear_fondo_gradiente(width, height, color1, color2, vertical=True):
    """
    Genera una imagen de fondo con un gradiente lineal suave entre dos colores.

    Args:
        width (int): Ancho de la imagen.
        height (int): Alto de la imagen.
        color1 (tuple): Color inicial (B, G, R).
        color2 (tuple): Color final (B, G, R).
        vertical (bool): True para gradiente vertical, False para horizontal.

    Returns:
        numpy.ndarray: Imagen generada con el gradiente.
    """
    imagen = np.zeros((height, width, 3), dtype=np.uint8)
    
    if vertical:
        for i in range(height):
            ratio = i / height
            color = tuple([int(color1[j] * (1 - ratio) + color2[j] * ratio) for j in range(3)])
            imagen[i, :] = color
    else:
        for i in range(width):
            ratio = i / width
            color = tuple([int(color1[j] * (1 - ratio) + color2[j] * ratio) for j in range(3)])
            imagen[:, i] = color
    
    return imagen

def dibujar_texto_con_sombra(img, text, pos, font=cv2.FONT_HERSHEY_SIMPLEX, 
                             font_scale=1, text_color=(255, 255, 255), 
                             shadow_color=(0, 0, 0), thickness=2, shadow_offset=3):
    """
    Dibuja texto sobre una imagen proyectando una sombra para mejorar la legibilidad.

    Args:
        img (numpy.ndarray): Imagen destino.
        text (str): Texto a escribir.
        pos (tuple): Coordenadas (x, y) de la esquina inferior izquierda.
        font (int): Tipo de fuente OpenCV.
        font_scale (float): Escala de la fuente.
        text_color (tuple): Color del texto principal (B, G, R).
        shadow_color (tuple): Color de la sombra.
        thickness (int): Grosor de la línea.
        shadow_offset (int): Desplazamiento de la sombra en píxeles.
    """
    x, y = pos
    # Dibujar sombra
    cv2.putText(img, text, (x + shadow_offset, y + shadow_offset), 
                font, font_scale, shadow_color, thickness + 1)
    # Dibujar texto principal
    cv2.putText(img, text, (x, y), font, font_scale, text_color, thickness)

def draw_text_with_background(img, text, pos, font=cv2.FONT_HERSHEY_SIMPLEX, 
                               font_scale=1, text_color=(255, 255, 255), 
                               bg_color=(0, 0, 0), thickness=2, padding=15, border_radius=20):
    """
    Renderiza texto sobre un cuadro de fondo semitransparente con esquinas redondeadas.

    Args:
        img (numpy.ndarray): Imagen destino.
        text (str): Texto a mostrar.
        pos (tuple): Posición (x, y).
        font (int): Fuente OpenCV.
        font_scale (float): Tamaño de fuente.
        text_color (tuple): Color del texto.
        bg_color (tuple): Color del fondo del recuadro.
        thickness (int): Grosor del texto.
        padding (int): Espaciado interno alrededor del texto.
        border_radius (int): Radio para el efecto de esquinas redondeadas.
    """
    x, y = pos
    text_size = cv2.getTextSize(text, font, font_scale, thickness)[0]
    
    # Crear overlay para transparencia
    overlay = img.copy()
    
    # Coordenadas del rectángulo contenedor
    x1 = x - padding
    y1 = y - text_size[1] - padding
    x2 = x + text_size[0] + padding
    y2 = y + padding
    
    # Dibujar esquinas redondeadas (elipses)
    cv2.ellipse(overlay, (x1 + border_radius, y1 + border_radius), 
                (border_radius, border_radius), 180, 0, 90, bg_color, -1)
    cv2.ellipse(overlay, (x2 - border_radius, y1 + border_radius), 
                (border_radius, border_radius), 270, 0, 90, bg_color, -1)
    cv2.ellipse(overlay, (x1 + border_radius, y2 - border_radius), 
                (border_radius, border_radius), 90, 0, 90, bg_color, -1)
    cv2.ellipse(overlay, (x2 - border_radius, y2 - border_radius), 
                (border_radius, border_radius), 0, 0, 90, bg_color, -1)
    
    # Rellenar centro con rectángulos
    cv2.rectangle(overlay, (x1 + border_radius, y1), (x2 - border_radius, y2), bg_color, -1)
    cv2.rectangle(overlay, (x1, y1 + border_radius), (x2, y2 - border_radius), bg_color, -1)
    
    # Aplicar transparencia (Alpha Blending)
    alpha = 0.8
    cv2.addWeighted(overlay, alpha, img, 1 - alpha, 0, img)
    
    # Renderizar texto final
    cv2.putText(img, text, (x, y), font, font_scale, text_color, thickness)

def dibujar_circulo_om(img, centro, radio, color):
    """
    Dibuja un elemento gráfico decorativo (círculo estilizado tipo 'Om').

    Args:
        img (numpy.ndarray): Imagen destino.
        centro (tuple): Coordenadas (x, y) del centro.
        radio (int): Radio del círculo exterior.
        color (tuple): Color de las líneas (B, G, R).
    """
    x, y = centro
    cv2.circle(img, (x, y), radio, color, 3)
    cv2.circle(img, (x, y), int(radio * 0.6), color, 2)
    cv2.line(img, (x, y - radio), (x, y + radio), color, 2)

# --- Configuración Global ---
LIENZO_SHAPE = (1280, 720)
W_LIENZO, H_LIENZO = LIENZO_SHAPE

# Carga y generación de recursos gráficos (Fondos)
try:
    fondo_inicio = cv2.imread('fotos/inicio.jpg')
    if fondo_inicio is None:
        raise FileNotFoundError
    fondo_inicio = cv2.resize(fondo_inicio, (W_LIENZO, H_LIENZO))
    print("Imagen de inicio cargada correctamente")
except:
    print("No se encontró inicio.jpg, generando fondo dinámico")
    fondo_inicio = crear_fondo_gradiente(W_LIENZO, H_LIENZO, 
                                          (140, 90, 60),    # Morado oscuro 
                                          (180, 130, 50),   # Morado claro
                                          vertical=True)
    # Decoración fondo inicio
    for i in range(5):
        x = int(W_LIENZO * (0.2 + i * 0.15))
        y = int(H_LIENZO * 0.15)
        dibujar_circulo_om(fondo_inicio, (x, y), 30, (180, 150, 100))
        
    for i in range(5):
        x = int(W_LIENZO * (0.2 + i * 0.15))
        y = int(H_LIENZO * 0.85)
        dibujar_circulo_om(fondo_inicio, (x, y), 30, (180, 150, 100))

try:
    fondo_final = cv2.imread('fotos/final.jpg')
    if fondo_final is None:
        raise FileNotFoundError
    fondo_final = cv2.resize(fondo_final, (W_LIENZO, H_LIENZO))
    print("Imagen final cargada correctamente")
except:
    print("No se encontró final.jpg, generando fondo dinámico")
    fondo_final = crear_fondo_gradiente(W_LIENZO, H_LIENZO, 
                                         (100, 180, 50),   # Verde azulado
                                         (150, 200, 100),  # Verde claro
                                         vertical=True)
    # Decoración fondo final
    for i in range(8):
        x = int(W_LIENZO * (0.1 + i * 0.11))
        y = int(H_LIENZO * 0.2)
        cv2.circle(fondo_final, (x, y), 8, (255, 255, 150), -1)

    for i in range(8):
        x = int(W_LIENZO * (0.1 + i * 0.11))
        y = int(H_LIENZO * 0.8)
        cv2.circle(fondo_final, (x, y), 8, (255, 255, 150), -1)

# Configuración de visualización de cámara
W_CAMARA_DISPLAY = 900
H_CAMARA_DISPLAY = 700
MARGEN = 10

MAPEO_IMAGENES = {
    "GUERRERO_4": "guerrero 4.jpg",
    "PERRO_BOCA_ABAJO": "perro boca abajo.jpg",
    "PINZA_SENTADA": "pinza sentada.jpg",
    "ARBOL": "arbol.jpg",
    "POSE_FACIL": "pose facil.jpg",
    "TRIANGULO_EXTENDIDO": "triangulo extendido.jpg",
    "BARCA": "barca.jpg",
    "SENTADILLA": "sentadilla.jpg",
    "GUERRERO_2": "guerrero 2.jpg",
    "PLANCHA_LATERAL": "plancha lateral.jpg",
    "GUERRERO_3": "guerrero 3.jpg",
    "GUERRERO_1": "guerrero 1.jpg",
    "MESA": "gato.jpg"
}

# Carga de imágenes de referencia para las posturas
POSTURAS_IMAGENES = {}
for nombre_postura, nombre_archivo in MAPEO_IMAGENES.items():
    try:
        img = cv2.imread(f'fotos/{nombre_archivo}')
        POSTURAS_IMAGENES[nombre_postura] = img
    except Exception as e:
        print(f"Error cargando {nombre_archivo}: {e}")
        # Fallback: color sólido si falla la imagen
        POSTURAS_IMAGENES[nombre_postura] = np.full((720, 1280, 3), (200, 150, 100), dtype=np.uint8)

LISTA_POSTURAS = [
    "POSE_FACIL",
    "MESA",
    "PERRO_BOCA_ABAJO",
    "PINZA_SENTADA",
    "SENTADILLA",
    "PLANCHA_LATERAL",
    "ARBOL",
    "GUERRERO_1",
    "GUERRERO_2",
    "GUERRERO_3",
    "GUERRERO_4",
    "TRIANGULO_EXTENDIDO",
    "BARCA"
]

# Bucle Principal del Juego
with PoseLandmarker.create_from_options(options) as landmarker:
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: No se puede abrir la cámara.")
        sys.exit()

    H_CAM = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    W_CAM = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))

    # Variables de estado
    estado_juego = "INICIO"
    postura_actual_idx = 0
    postura_tiempo_inicio = None
    SEGUNDOS_PARA_SUPERAR = 3 

    timestamp = 0
    start_time = time.time()

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            print("Error al leer frame.")
            break

        # Efecto espejo
        frame = cv2.flip(frame, 1)

        if estado_juego == "INICIO":
            lienzo = fondo_inicio.copy()
            
            # Elementos gráficos UI (Cajas decorativas y sombras)
            shadow_offset = 10
            radius = 40
            overlay_shadow = lienzo.copy()
            x1, y1 = int(W_LIENZO * 0.1), int(H_LIENZO * 0.08)
            x2, y2 = int(W_LIENZO * 0.9), int(H_LIENZO * 0.4)
            
            # Renderizado de formas decorativas de inicio
            cv2.ellipse(overlay_shadow, (x1 + radius + shadow_offset, y1 + shadow_offset + radius), 
                       (40, 40), 180, 0, 90, (0, 0, 0), -1)
            cv2.ellipse(overlay_shadow, (x2 - radius + shadow_offset, y1 + shadow_offset + radius), 
                       (40, 40), 270, 0, 90, (0, 0, 0), -1)
            cv2.ellipse(overlay_shadow, (x1 + radius + shadow_offset, y2 + shadow_offset - radius), 
                       (40, 40), 90, 0, 90, (0, 0, 0), -1)
            cv2.ellipse(overlay_shadow, (x2 - radius + shadow_offset, y2 + shadow_offset - radius), 
                       (40, 40), 0, 0, 90, (0, 0, 0), -1)
            cv2.rectangle(overlay_shadow, (x1 + shadow_offset + radius, y1 + shadow_offset), 
                         (x2 + shadow_offset - radius, y2 + shadow_offset), (0, 0, 0), -1)
            cv2.rectangle(overlay_shadow, (x1 + shadow_offset, y1 + shadow_offset + radius), 
                         (x2 + shadow_offset, y2 + shadow_offset - radius), (0, 0, 0), -1)
            cv2.addWeighted(overlay_shadow, 0.3, lienzo, 0.7, 0, lienzo)
            
            overlay = lienzo.copy()
            cv2.ellipse(overlay, (x1 + radius, y1 + radius), (radius, radius), 180, 0, 90, (255, 255, 255), -1)
            cv2.ellipse(overlay, (x2 - radius, y1 + radius), (radius, radius), 270, 0, 90, (255, 255, 255), -1)
            cv2.ellipse(overlay, (x1 + radius, y2 - radius), (radius, radius), 90, 0, 90, (255, 255, 255), -1)
            cv2.ellipse(overlay, (x2 - radius, y2 - radius), (radius, radius), 0, 0, 90, (255, 255, 255), -1)
            cv2.rectangle(overlay, (x1 + radius, y1), (x2 - radius, y2), (255, 255, 255), -1)
            cv2.rectangle(overlay, (x1, y1 + radius), (x2, y2 - radius), (255, 255, 255), -1)
            
            cv2.addWeighted(overlay, 0.15, lienzo, 0.85, 0, lienzo)
            
            # Marco decorativo con bucle
            for i in range(6):
                opacity = 1.0 - (i * 0.15)
                color_intensity = int(255 * opacity)
                cv2.ellipse(lienzo, (x1 + radius, y1 + radius), (radius + i, radius + i), 180, 0, 90, 
                           (color_intensity, color_intensity, color_intensity), 1)
                cv2.ellipse(lienzo, (x2 - radius, y1 + radius), (radius + i, radius + i), 270, 0, 90, 
                           (color_intensity, color_intensity, color_intensity), 1)
                cv2.ellipse(lienzo, (x1 + radius, y2 - radius), (radius + i, radius + i), 90, 0, 90, 
                           (color_intensity, color_intensity, color_intensity), 1)
                cv2.ellipse(lienzo, (x2 - radius, y2 - radius), (radius + i, radius + i), 0, 0, 90, 
                           (color_intensity, color_intensity, color_intensity), 1)
                cv2.line(lienzo, (x1 + radius, y1 - i), (x2 - radius, y1 - i), 
                        (color_intensity, color_intensity, color_intensity), 1)
                cv2.line(lienzo, (x1 + radius, y2 + i), (x2 - radius, y2 + i), 
                        (color_intensity, color_intensity, color_intensity), 1)
                cv2.line(lienzo, (x1 - i, y1 + radius), (x1 - i, y2 - radius), 
                        (color_intensity, color_intensity, color_intensity), 1)
                cv2.line(lienzo, (x2 + i, y1 + radius), (x2 + i, y2 - radius), 
                        (color_intensity, color_intensity, color_intensity), 1)
            
            # Textos de pantalla de inicio
            titulo = "BIENVENIDO A TU CLASE DE YOGA"
            dibujar_texto_con_sombra(lienzo, titulo, 
                                    (int(W_LIENZO * 0.18), int(H_LIENZO * 0.2)), 
                                    font=cv2.FONT_HERSHEY_DUPLEX,
                                    font_scale=1.6, 
                                    text_color=(255, 255, 255), 
                                    shadow_color=(80, 50, 30),
                                    thickness=3, 
                                    shadow_offset=4)
            
            tiempo_actual = time.time()
            parpadeo = int(tiempo_actual * 2) % 2 
            if parpadeo:
                draw_text_with_background(lienzo, ">>> Pulsa ESPACIO para iniciar <<<", 
                                        (int(W_LIENZO * 0.23), int(H_LIENZO * 0.3)), 
                                        font=cv2.FONT_HERSHEY_DUPLEX,
                                        font_scale=1.1, 
                                        text_color=(255, 255, 255), 
                                        bg_color=(0, 0, 0), 
                                        thickness=2, 
                                        padding=15,
                                        border_radius=25)

        elif estado_juego == "TERMINADO":
            lienzo = fondo_final.copy()
            
            # Configuración UI Fin del juego
            shadow_offset = 8
            overlay_shadow = lienzo.copy()
            radius = 30
            x1, y1 = int(W_LIENZO * 0.18), int(H_LIENZO * 0.08)
            x2, y2 = int(W_LIENZO * 0.82), int(H_LIENZO * 0.40)
            
            # Sombra y fondo semitransparente
            cv2.ellipse(overlay_shadow, (x1 + shadow_offset + radius, y1 + shadow_offset + radius), 
                       (radius, radius), 180, 0, 90, (0, 0, 0), -1)
            cv2.ellipse(overlay_shadow, (x2 + shadow_offset - radius, y1 + shadow_offset + radius), 
                       (radius, radius), 270, 0, 90, (0, 0, 0), -1)
            cv2.ellipse(overlay_shadow, (x1 + shadow_offset + radius, y2 + shadow_offset - radius), 
                       (radius, radius), 90, 0, 90, (0, 0, 0), -1)
            cv2.ellipse(overlay_shadow, (x2 + shadow_offset - radius, y2 + shadow_offset - radius), 
                       (radius, radius), 0, 0, 90, (0, 0, 0), -1)
            cv2.rectangle(overlay_shadow, (x1 + shadow_offset + radius, y1 + shadow_offset), 
                         (x2 + shadow_offset - radius, y2 + shadow_offset), (0, 0, 0), -1)
            cv2.rectangle(overlay_shadow, (x1 + shadow_offset, y1 + shadow_offset + radius), 
                         (x2 + shadow_offset, y2 + shadow_offset - radius), (0, 0, 0), -1)
            cv2.addWeighted(overlay_shadow, 0.25, lienzo, 0.75, 0, lienzo)
            
            overlay = lienzo.copy()
            cv2.ellipse(overlay, (x1 + radius, y1 + radius), (radius, radius), 180, 0, 90, (255, 255, 255), -1)
            cv2.ellipse(overlay, (x2 - radius, y1 + radius), (radius, radius), 270, 0, 90, (255, 255, 255), -1)
            cv2.ellipse(overlay, (x1 + radius, y2 - radius), (radius, radius), 90, 0, 90, (255, 255, 255), -1)
            cv2.ellipse(overlay, (x2 - radius, y2 - radius), (radius, radius), 0, 0, 90, (255, 255, 255), -1)
            cv2.rectangle(overlay, (x1 + radius, y1), (x2 - radius, y2), (255, 255, 255), -1)
            cv2.rectangle(overlay, (x1, y1 + radius), (x2, y2 - radius), (255, 255, 255), -1)
            cv2.addWeighted(overlay, 0.12, lienzo, 0.88, 0, lienzo)
            
            # Marco dorado decorativo
            for i in range(6):
                opacity = 1.0 - (i * 0.15)
                color = (int(0 * opacity), int(215 * opacity), int(255 * opacity))
                cv2.ellipse(lienzo, (x1 + radius, y1 + radius), (radius + i, radius + i), 180, 0, 90, color, 1)
                cv2.ellipse(lienzo, (x2 - radius, y1 + radius), (radius + i, radius + i), 270, 0, 90, color, 1)
                cv2.ellipse(lienzo, (x1 + radius, y2 - radius), (radius + i, radius + i), 90, 0, 90, color, 1)
                cv2.ellipse(lienzo, (x2 - radius, y2 - radius), (radius + i, radius + i), 0, 0, 90, color, 1)
                cv2.line(lienzo, (x1 + radius, y1 - i), (x2 - radius, y1 - i), color, 1)
                cv2.line(lienzo, (x1 + radius, y2 + i), (x2 - radius, y2 + i), color, 1)
                cv2.line(lienzo, (x1 - i, y1 + radius), (x1 - i, y2 - radius), color, 1)
                cv2.line(lienzo, (x2 + i, y1 + radius), (x2 + i, y2 - radius), color, 1)
            
            # Textos de felicitación
            mensaje = "FELICIDADES!"
            mensaje_size = cv2.getTextSize(mensaje, cv2.FONT_HERSHEY_DUPLEX, 2.2, 4)[0]
            x_mensaje = int((W_LIENZO - mensaje_size[0]) / 2)
            dibujar_texto_con_sombra(lienzo, mensaje, 
                                    (x_mensaje, int((y1 + y2) / 2) - 40), 
                                    font=cv2.FONT_HERSHEY_DUPLEX,
                                    font_scale=2.2, 
                                    text_color=(255, 255, 255), 
                                    shadow_color=(50, 100, 50),
                                    thickness=4, 
                                    shadow_offset=5)
            
            mensaje2 = "Has completado tu sesion de yoga"
            mensaje2_size = cv2.getTextSize(mensaje2, cv2.FONT_HERSHEY_DUPLEX, 1.1, 2)[0]
            x_mensaje2 = int((W_LIENZO - mensaje2_size[0]) / 2)
            dibujar_texto_con_sombra(lienzo, mensaje2, 
                                    (x_mensaje2, int((y1 + y2) / 2) + 10), 
                                    font=cv2.FONT_HERSHEY_DUPLEX,
                                    font_scale=1.1, 
                                    text_color=(240, 240, 240), 
                                    shadow_color=(40, 80, 40),
                                    thickness=2, 
                                    shadow_offset=3)
            
            salir_text = "Pulsa ESC para salir"
            salir_size = cv2.getTextSize(salir_text, cv2.FONT_HERSHEY_DUPLEX, 0.85, 2)[0]
            x_salir = int((W_LIENZO - salir_size[0]) / 2) - 7
            draw_text_with_background(lienzo, salir_text, 
                                    (x_salir, int((y1 + y2) / 2) + 70), 
                                    font=cv2.FONT_HERSHEY_DUPLEX,
                                    font_scale=0.85, 
                                    text_color=(255, 255, 255), 
                                    bg_color=(80, 100, 80), 
                                    thickness=2, 
                                    padding=12,
                                    border_radius=20)
        
        elif estado_juego == "JUGANDO":
            nombre_postura = LISTA_POSTURAS[postura_actual_idx]
            definicion_postura = POSTURAS_YOGA[nombre_postura]
            img_profesor = POSTURAS_IMAGENES[nombre_postura]
            
            # Preparación del lienzo de juego (Imagen de referencia)
            img_completa = cv2.resize(img_profesor, (W_LIENZO, H_LIENZO))
            lienzo = np.zeros_like(img_completa)
            shift = 0
            lienzo[:, :W_LIENZO - shift] = img_completa[:, shift:]

            # Procesamiento de MediaPipe
            end_time = time.time()
            t = end_time - start_time
            start_time = end_time
            timestamp += int(t * 1000)

            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame)
            result = landmarker.detect_for_video(mp_image, timestamp)
            all_angles_correct = False

            # Verificación de ángulos de la postura
            if result.pose_landmarks:
                person_landmarks = result.pose_landmarks[0]
                feedback_colores = {}
                all_angles_correct = True

                try:
                    for angulo_nombre, angulo_objetivo in definicion_postura.items():
                        if angulo_nombre == "tolerancia": continue
                        
                        p1_idx, p2_idx, p3_idx = ANGULO_LANDMARKS_MAP[angulo_nombre]
                        p1, p2, p3 = person_landmarks[p1_idx], person_landmarks[p2_idx], person_landmarks[p3_idx]
                        
                        angulo_usuario = calcular_angulo(p1, p2, p3)
                        
                        color_articulacion = (0, 0, 255) # Rojo por defecto
                        
                        if angulo_usuario is None:
                            all_angles_correct = False
                        else:
                            error = abs(angulo_usuario - angulo_objetivo)
                            if error <= definicion_postura["tolerancia"]:
                                color_articulacion = (0, 255, 0) # Verde si es correcto
                            else:
                                all_angles_correct = False
                        feedback_colores[p2_idx] = color_articulacion

                    # Dibujar puntos de articulación sobre el frame original
                    for articulacion_idx, color in feedback_colores.items():
                        articulacion = person_landmarks[articulacion_idx]
                        x, y = int(articulacion.x * W_CAM), int(articulacion.y * H_CAM)
                        cv2.circle(frame, (x, y), 15, color, -1)
                        cv2.circle(frame, (x, y), 15, (255, 255, 255), 2)
                
                except Exception as e:
                    all_angles_correct = False

            # Composición final: Overlay de cámara sobre lienzo
            frame_resized = cv2.resize(frame, (W_CAMARA_DISPLAY, H_CAMARA_DISPLAY))
            
            x_cam = W_LIENZO - W_CAMARA_DISPLAY 
            y_cam = MARGEN
            
            # Marcos decorativos de la cámara
            cv2.rectangle(lienzo, 
                         (x_cam - 8, y_cam - 8), 
                         (x_cam + W_CAMARA_DISPLAY + 8, y_cam + H_CAMARA_DISPLAY + 8), 
                         (255, 255, 255), 8)
            cv2.rectangle(lienzo, 
                         (x_cam - 3, y_cam - 3), 
                         (x_cam + W_CAMARA_DISPLAY + 3, y_cam + H_CAMARA_DISPLAY + 3), 
                         (200, 200, 255), 3)
            
            lienzo[y_cam:y_cam+H_CAMARA_DISPLAY, x_cam:x_cam+W_CAMARA_DISPLAY] = frame_resized
            
            # UI: Información de postura
            draw_text_with_background(lienzo, nombre_postura.replace("_", " "), 
                                    (30, 60), 
                                    font=cv2.FONT_HERSHEY_DUPLEX,
                                    font_scale=1.3, 
                                    text_color=(255, 255, 100), 
                                    bg_color=(0, 0, 0), 
                                    thickness=3, 
                                    padding=15,
                                    border_radius=20)
            
            postura_info = f"Postura {postura_actual_idx + 1}/{len(LISTA_POSTURAS)}"
            draw_text_with_background(lienzo, postura_info, 
                                    (30, 110), 
                                    font=cv2.FONT_HERSHEY_DUPLEX,
                                    font_scale=0.8, 
                                    text_color=(200, 255, 200), 
                                    bg_color=(0, 0, 0), 
                                    thickness=2, 
                                    padding=10,
                                    border_radius=15)
            
            draw_text_with_background(lienzo, "Presiona ENTER para saltar", 
                                    (30, H_LIENZO - 500), 
                                    font=cv2.FONT_HERSHEY_DUPLEX,
                                    font_scale=0.6,
                                    text_color=(255, 255, 255), 
                                    bg_color=(50, 50, 50), 
                                    thickness=2, 
                                    padding=10,
                                    border_radius=15)

            # Lógica de progreso y feedback de alineación
            if all_angles_correct:
                if postura_tiempo_inicio is None:
                    postura_tiempo_inicio = time.time()
                tiempo_mantenido = time.time() - postura_tiempo_inicio
                
                # Renderizar barra de progreso
                barra_width = W_CAMARA_DISPLAY - 40
                progreso = int((tiempo_mantenido / SEGUNDOS_PARA_SUPERAR) * barra_width)
                progreso = min(progreso, barra_width)
                
                x_barra = x_cam + 20
                y_barra = y_cam + H_CAMARA_DISPLAY + 30
                
                cv2.rectangle(lienzo, (x_barra - 3, y_barra - 3), 
                            (x_barra + barra_width + 3, y_barra + 33), 
                            (255, 255, 255), 2)
                cv2.rectangle(lienzo, (x_barra, y_barra), 
                            (x_barra + barra_width, y_barra + 30), 
                            (30, 30, 30), -1)
                
                # Relleno de barra con gradiente
                for i in range(progreso):
                    ratio = i / barra_width
                    color = (0, int(200 + 55 * ratio), int(100 + 155 * ratio))
                    cv2.line(lienzo, (x_barra + i, y_barra), 
                            (x_barra + i, y_barra + 30), color, 1)
                
                tiempo_texto = f"¡Bien! Manten: {int(tiempo_mantenido)+1}s / {SEGUNDOS_PARA_SUPERAR}s"
                cv2.putText(lienzo, tiempo_texto, 
                           (x_barra + 10, y_barra + 20), 
                           cv2.FONT_HERSHEY_DUPLEX, 0.6, (255, 255, 255), 2)

                # Cambio de postura si se cumple el tiempo
                if tiempo_mantenido > SEGUNDOS_PARA_SUPERAR:
                    postura_actual_idx += 1
                    postura_tiempo_inicio = None
                    if postura_actual_idx >= len(LISTA_POSTURAS):
                        estado_juego = "TERMINADO"
            else:
                postura_tiempo_inicio = None
                draw_text_with_background(lienzo, "Alinea tu cuerpo con la postura", 
                                        (30, 160), 
                                        font=cv2.FONT_HERSHEY_DUPLEX,
                                        font_scale=0.9, 
                                        text_color=(255, 200, 100), 
                                        bg_color=(0, 0, 0), 
                                        thickness=2, 
                                        padding=10,
                                        border_radius=15)

        cv2.imshow("Profesor de Yoga - IPM", lienzo)

        # Control de inputs
        key = cv2.waitKey(5) & 0xFF
        
        if key == 27:  # ESC
            break
            
        if estado_juego == "INICIO":
            if key == 32:  # ESPACIO
                estado_juego = "JUGANDO"
                start_time = time.time()
                timestamp = 0
                
        elif estado_juego == "JUGANDO":
            if key == 13:  # ENTER
                print(f"Saltando postura: {LISTA_POSTURAS[postura_actual_idx]}")
                postura_actual_idx += 1
                postura_tiempo_inicio = None 
                if postura_actual_idx >= len(LISTA_POSTURAS):
                    estado_juego = "TERMINADO"

    cap.release()
    cv2.destroyAllWindows()