import sys
import cv2
import mediapipe as mp
import numpy as np
import time
from config import config
from posturas import POSTURAS_YOGA
from angulos import ANGULO_LANDMARKS_MAP
import os
import glob


# Configuración de la tarea
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
    Calcula el ángulo en el vértice 'b'.
    """
    if a.visibility < 0.5 or b.visibility < 0.5 or c.visibility < 0.5:
        return None

    A = np.array([a.x, a.y])
    B = np.array([b.x, b.y])
    C = np.array([c.x, c.y])
    
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

def redimensionar_imagen(image, target_shape, bg_color=(0, 0, 0)):
    """
    Redimensiona una imagen a target_shape (w, h) manteniendo la relación de aspecto
    y rellenando el espacio sobrante con bg_color.
    """
    target_w, target_h = target_shape
    h, w, _ = image.shape
    
    scale = min(target_w / w, target_h / h)
    
    new_w, new_h = int(w * scale), int(h * scale)
    
    resized_img = cv2.resize(image, (new_w, new_h))
    
    canvas = np.full((target_h, target_w, 3), bg_color, dtype=np.uint8)
    
    x_center = (target_w - new_w) // 2
    y_center = (target_h - new_h) // 2
    
    canvas[y_center:y_center+new_h, x_center:x_center+new_w] = resized_img
    
    return canvas

def draw_text_with_background(img, text, pos, font=cv2.FONT_HERSHEY_SIMPLEX, 
                               font_scale=1, text_color=(255, 255, 255), 
                               bg_color=(0, 0, 0), thickness=2, padding=10):
    """
    Dibuja texto con fondo semi-transparente para mejor legibilidad
    """
    x, y = pos
    text_size = cv2.getTextSize(text, font, font_scale, thickness)[0]
    
    # Crear overlay semi-transparente
    overlay = img.copy()
    cv2.rectangle(overlay, 
                  (x - padding, y - text_size[1] - padding), 
                  (x + text_size[0] + padding, y + padding), 
                  bg_color, -1)
    
    # Mezclar overlay con imagen original (transparencia)
    alpha = 0.7
    cv2.addWeighted(overlay, alpha, img, 1 - alpha, 0, img)
    
    # Dibujar texto
    cv2.putText(img, text, (x, y), font, font_scale, text_color, thickness)

try:
    # Ya no necesitamos cargar un fondo separado porque cada imagen lo tiene
    fondo_playa = np.full((720, 1280, 3), (200, 150, 100), dtype=np.uint8)  # Solo para inicio
    LIENZO_SHAPE = (1280, 720)
except Exception as e:
    print(f"Error: {e}")
    fondo_playa = np.zeros((720, 1280, 3), dtype=np.uint8)

W_LIENZO, H_LIENZO = LIENZO_SHAPE

# NUEVO DISEÑO: Cámara más pequeña en esquina
W_CAMARA_DISPLAY = 900  # Ancho de la cámara en pantalla
H_CAMARA_DISPLAY = 700  # Alto de la cámara en pantalla
MARGEN = 10  # Margen desde los bordes

MAPEO_IMAGENES = {
    "FLEXION": "flexion.png",
    "GUERRERO_4": "guerrero 4.png",
    "PERRO_BOCA_ABAJO": "perro boca abajo.png",
    "PERRO_BOCA_ARRIBA": "perro boca arriba.png",
    "PINZA_DE_PIE": "pinza de pie.png",
    "PINZA_SENTADA": "pinza sentada.png",
    "ARBOL": "pose arbol yoga.png",
    "POSE_FACIL": "fondo con pose facil.png",
    "TRIANGULO_EXTENDIDO": "pose triangulo extendido.png",
    "BARCA": "postura de la barca.png",
    "SENTADILLA": "sentadilla.png",
    "GUERRERO_2": "postura guerrero 2.png",
    "PLANCHA_LATERAL": "postura plancha lateral.png",
    "GUERRERO_3": "postura guerrero 3.png",
    "GUERRERO_1": "postura guerrero 1.png",
    "MESA": "postura del gato.png"
}

# Cargar imágenes del muñeco CON FONDO (ya vienen completas)
POSTURAS_IMAGENES = {}
for nombre_postura, nombre_archivo in MAPEO_IMAGENES.items():
    try:
        img = cv2.imread(f'fotos/{nombre_archivo}')
        # Las imágenes ya tienen el fondo, solo las cargamos
        POSTURAS_IMAGENES[nombre_postura] = img
    except Exception as e:
        print(f"Error cargando {nombre_archivo}: {e}")
        # Fondo azul de emergencia
        POSTURAS_IMAGENES[nombre_postura] = np.full((720, 1280, 3), (200, 150, 100), dtype=np.uint8)

LISTA_POSTURAS = [
    "POSE_FACIL",
    "MESA",
    "PERRO_BOCA_ABAJO",
    "PERRO_BOCA_ARRIBA",
    "PINZA_DE_PIE",
    "PINZA_SENTADA",
    "SENTADILLA",
    "FLEXION",
    "PLANCHA_LATERAL",
    "ARBOL",
    "GUERRERO_1",
    "GUERRERO_2",
    "GUERRERO_3",
    "GUERRERO_4",
    "TRIANGULO_EXTENDIDO",
    "BARCA"
]

# Inicializar landmarker
with PoseLandmarker.create_from_options(options) as landmarker:
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: No se puede abrir la cámara.")
        sys.exit()

    H_CAM = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    W_CAM = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))

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

        frame = cv2.flip(frame, 1)

        # Preparar el Lienzo con fondo completo
        lienzo = fondo_playa.copy()
        
        if estado_juego == "INICIO":
            # Pantalla de inicio mejorada
            draw_text_with_background(lienzo, "BIENVENIDO A LA CLASE DE YOGA", 
                                    (W_LIENZO // 2 - 400, H_LIENZO // 2 - 100), 
                                    font_scale=1.8, text_color=(255, 255, 255), 
                                    bg_color=(0, 100, 200), thickness=3, padding=20)
            
            draw_text_with_background(lienzo, "Pulsa ESPACIO para iniciar", 
                                    (W_LIENZO // 2 - 250, H_LIENZO // 2 + 100), 
                                    font_scale=1.2, text_color=(255, 255, 0), 
                                    bg_color=(50, 50, 50), thickness=2, padding=15)

        elif estado_juego == "TERMINADO":
            draw_text_with_background(lienzo, "¡HAS COMPLETADO LA SESION!", 
                                    (W_LIENZO // 2 - 350, H_LIENZO // 2), 
                                    font_scale=1.8, text_color=(0, 255, 0), 
                                    bg_color=(0, 0, 0), thickness=3, padding=20)
            
            draw_text_with_background(lienzo, "Pulsa ESC para salir", 
                                    (W_LIENZO // 2 - 180, H_LIENZO // 2 + 80), 
                                    font_scale=1.2, text_color=(255, 255, 255), 
                                    bg_color=(50, 50, 50), thickness=2, padding=15)
        
        elif estado_juego == "JUGANDO":
            nombre_postura = LISTA_POSTURAS[postura_actual_idx]
            definicion_postura = POSTURAS_YOGA[nombre_postura]
            img_profesor = POSTURAS_IMAGENES[nombre_postura]
            
            # Redimensionar como siempre
            img_completa = cv2.resize(img_profesor, (W_LIENZO, H_LIENZO))

            # Crear lienzo vacío
            lienzo = np.zeros_like(img_completa)

            # Desplazamiento hacia la izquierda (en píxeles)
            shift = 150

            # Copiar la imagen desplazada hacia la izquierda
            lienzo[:, :W_LIENZO - shift] = img_completa[:, shift:]

            # Detección de Pose
            end_time = time.time()
            t = end_time - start_time
            start_time = end_time
            timestamp += int(t * 1000)

            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame)
            result = landmarker.detect_for_video(mp_image, timestamp)
            all_angles_correct = False

            # Lógica de Ángulos
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
                        
                        color_articulacion = (0, 0, 255)
                        
                        if angulo_usuario is None:
                            all_angles_correct = False
                        else:
                            error = abs(angulo_usuario - angulo_objetivo)
                            if error <= definicion_postura["tolerancia"]:
                                color_articulacion = (0, 255, 0)
                            else:
                                all_angles_correct = False
                        feedback_colores[p2_idx] = color_articulacion

                    # Dibujar Feedback en el frame
                    for articulacion_idx, color in feedback_colores.items():
                        articulacion = person_landmarks[articulacion_idx]
                        x, y = int(articulacion.x * W_CAM), int(articulacion.y * H_CAM)
                        cv2.circle(frame, (x, y), 15, color, -1)
                        cv2.circle(frame, (x, y), 15, (255, 255, 255), 2)
                
                except Exception as e:
                    all_angles_correct = False

            # NUEVO: Redimensionar cámara más pequeña
            frame_resized = cv2.resize(frame, (W_CAMARA_DISPLAY, H_CAMARA_DISPLAY))
            
            # Posicionar cámara en la esquina superior derecha con borde elegante
            x_cam = W_LIENZO - W_CAMARA_DISPLAY 
            y_cam = MARGEN
            
            # Dibujar borde blanco alrededor de la cámara
            cv2.rectangle(lienzo, 
                         (x_cam - 5, y_cam - 5), 
                         (x_cam + W_CAMARA_DISPLAY + 5, y_cam + H_CAMARA_DISPLAY + 5), 
                         (255, 255, 255), 5)
            
            # Pegar cámara del usuario
            lienzo[y_cam:y_cam+H_CAMARA_DISPLAY, x_cam:x_cam+W_CAMARA_DISPLAY] = frame_resized
            
            # Título de la postura (arriba a la izquierda, con fondo)
            draw_text_with_background(lienzo, nombre_postura.replace("_", " "), 
                                    (30, 60), font_scale=1.5, 
                                    text_color=(255, 255, 0), 
                                    bg_color=(0, 0, 0), thickness=3, padding=15)
            
            # Instrucciones (abajo a la izquierda)
            draw_text_with_background(lienzo, "Presiona ENTER para saltar", 
                                    (30, H_LIENZO - 550), font_scale=0.7,
                                    text_color=(255, 255, 255), 
                                    bg_color=(50, 50, 50), thickness=2, padding=10)

            # Barra de progreso y estado
            if all_angles_correct:
                if postura_tiempo_inicio is None:
                    postura_tiempo_inicio = time.time()
                tiempo_mantenido = time.time() - postura_tiempo_inicio
                
                # Barra de progreso debajo de la cámara
                barra_width = W_CAMARA_DISPLAY - 20
                progreso = int((tiempo_mantenido / SEGUNDOS_PARA_SUPERAR) * barra_width)
                progreso = min(progreso, barra_width)
                
                x_barra = x_cam + 10
                y_barra = y_cam + H_CAMARA_DISPLAY + 20
                
                # Fondo de la barra
                cv2.rectangle(lienzo, (x_barra, y_barra), 
                            (x_barra + barra_width, y_barra + 30), (0, 0, 0), -1)
                # Progreso
                cv2.rectangle(lienzo, (x_barra, y_barra), 
                            (x_barra + progreso, y_barra + 30), (0, 255, 0), -1)
                # Borde
                cv2.rectangle(lienzo, (x_barra, y_barra), 
                            (x_barra + barra_width, y_barra + 30), (255, 255, 255), 2)
                
                # Texto del tiempo
                cv2.putText(lienzo, f"Mantén: {int(tiempo_mantenido)+1}s / {SEGUNDOS_PARA_SUPERAR}s", 
                           (x_barra + 10, y_barra + 20), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

                if tiempo_mantenido > SEGUNDOS_PARA_SUPERAR:
                    postura_actual_idx += 1
                    postura_tiempo_inicio = None
                    if postura_actual_idx >= len(LISTA_POSTURAS):
                        estado_juego = "TERMINADO"
            else:
                postura_tiempo_inicio = None
                # Mensaje de alineación
                draw_text_with_background(lienzo, "Alinea tu cuerpo", 
                                        (30, 120), font_scale=1.2, 
                                        text_color=(255, 100, 100), 
                                        bg_color=(0, 0, 0), thickness=2, padding=10)

        cv2.imshow("Profesor de Yoga - IPM", lienzo)

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