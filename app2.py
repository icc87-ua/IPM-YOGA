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
    # Si los puntos no son visibles, no podemos calcular un ángulo fiable
    if a.visibility < 0.5 or b.visibility < 0.5 or c.visibility < 0.5:
        return None

    # Coordenadas de los landmarks (solo x, y)
    A = np.array([a.x, a.y])
    B = np.array([b.x, b.y])
    C = np.array([c.x, c.y])
    
    # Vectores
    ba = A - B
    bc = C - B
    
    # Producto escalar y magnitud
    prod_escalar = np.dot(ba, bc)
    magnitud_ba = np.linalg.norm(ba)
    magnitud_bc = np.linalg.norm(bc)
    
    # Evitar división por cero
    if magnitud_ba == 0 or magnitud_bc == 0:
        return None # Devolvemos None
        
    # Ángulo en radianes
    cos_theta = prod_escalar / (magnitud_ba * magnitud_bc)
    cos_theta = np.clip(cos_theta, -1.0, 1.0) # Corregir posibles errores de precisión
    angulo_rad = np.arccos(cos_theta)
    
    # Convertir a grados  
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
    
    # Redimensionar la imagen
    resized_img = cv2.resize(image, (new_w, new_h))
    
    # Crear un lienzo del color de fondo
    canvas = np.full((target_h, target_w, 3), bg_color, dtype=np.uint8)
    
    # Calcular la posición para centrar la imagen
    x_center = (target_w - new_w) // 2
    y_center = (target_h - new_h) // 2
    
    # Pegar la imagen redimensionada en el centro del lienzo
    canvas[y_center:y_center+new_h, x_center:x_center+new_w] = resized_img
    
    return canvas

try:
    # (Usa el nombre del fondo que te generé y guardaste)
    fondo_playa = cv2.imread("fotos/fondo_yoga.png") 
    LIENZO_SHAPE = (1280, 720) # Ancho, Alto
    fondo_playa = cv2.resize(fondo_playa, LIENZO_SHAPE)
except Exception as e:
    print(f"Error cargando fondo_playa: {e}")
    # Crear un fondo negro si falla
    fondo_playa = np.zeros((LIENZO_SHAPE[1], LIENZO_SHAPE[0]), dtype=np.uint8)

W_LIENZO, H_LIENZO = LIENZO_SHAPE
W_PROFESOR = W_LIENZO // 3
W_USUARIO = W_LIENZO - W_PROFESOR

MAPEO_IMAGENES = {
    "FLEXION": "flexion.png",
    "GUERRERO_4": "guerrero 4.png",
    "PERRO_BOCA_ABAJO": "perro boca abajo.png",
    "PERRO_BOCA_ARRIBA": "perro boca arriba.png",
    "PINZA_DE_PIE": "pinza de pie.png",
    "PINZA_SENTADA": "pinza sentada.png",
    "ARBOL": "pose arbol yoga.png",
    "POSE_FACIL": "pose facil.png",
    "TRIANGULO_EXTENDIDO": "pose triangulo extendido.png",
    "BARCA": "postura de la barca.png",
    "SENTADILLA": "sentadilla.png",
    "GUERRERO_2": "postura guerrero 2.png",
    "PLANCHA_LATERAL": "postura plancha lateral.png",
    "GUERRERO_3": "postura guerrero 3.png",
    "GUERRERO_1": "postura guerrero 1.png",
    "MESA": "postura del gato.png"
}

POSTURAS_IMAGENES = {}
for nombre_postura, nombre_archivo in MAPEO_IMAGENES.items():
    try:
        img = cv2.imread(f'fotos/{nombre_archivo}')
        # Redimensionar con relleno para que quepa en su mitad
        img_resized = redimensionar_imagen(img, (W_PROFESOR, H_LIENZO))
        POSTURAS_IMAGENES[nombre_postura] = img_resized
    except Exception as e:
        print(f"Error cargando {nombre_archivo}: {e}")
        # Poner una imagen negra si falla
        POSTURAS_IMAGENES[nombre_postura] = np.zeros((H_LIENZO, W_PROFESOR, 3), dtype=np.uint8)

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

    # Obtener dimensiones de la cámara (para cálculos)
    H_CAM = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    W_CAM = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))

    # --- Variables de estado del juego (MODIFICADO) ---
    estado_juego = "INICIO" # Estados: "INICIO", "JUGANDO", "TERMINADO"
    postura_actual_idx = 0
    postura_tiempo_inicio = None # Timer para saber cuánto tiempo mantiene la pose
    SEGUNDOS_PARA_SUPERAR = 3 

    # Timers para MediaPipe y Delta Time
    timestamp = 0
    start_time = time.time()

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            print("Error al leer frame.")
            break

        # Voltear el frame (efecto espejo)
        frame = cv2.flip(frame, 1)

        # --- 1. Preparar el Lienzo (UI) ---
        lienzo = fondo_playa.copy()
        
        # -----------------------------------------------------------------
        # --- LÓGICA DE ESTADOS ---
        # -----------------------------------------------------------------
        
        if estado_juego == "INICIO":
            # --- PANTALLA DE INICIO ---
            cv2.putText(lienzo, "Bienvenido a la clase de Yoga", (W_LIENZO // 2 - 400, H_LIENZO // 2 - 200), 
                        cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 0), 3)
            cv2.putText(lienzo, "Pulsa ESPACIO para iniciar", (W_LIENZO // 2 - 300, H_LIENZO // 2 + 250), 
                        cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 0), 3)

        elif estado_juego == "TERMINADO":
            # --- PANTALLA DE FIN DE JUEGO ---
            cv2.putText(lienzo, "HAS COMPLETADO LA SESION!", (W_LIENZO // 2 - 400, H_LIENZO // 2), 
                        cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 255, 0), 3)
            cv2.putText(lienzo, "Pulsa ESC para salir", (W_LIENZO // 2 - 150, H_LIENZO // 2 + 60), 
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        
        elif estado_juego == "JUGANDO":
            # --- INTERFAZ DE JUEGO NORMAL ---
            nombre_postura = LISTA_POSTURAS[postura_actual_idx]
            definicion_postura = POSTURAS_YOGA[nombre_postura]
            img_profesor = POSTURAS_IMAGENES[nombre_postura]
            
            # Pegar imagen del profesor (ya redimensionada)
            lienzo[0:H_LIENZO, 0:W_PROFESOR] = img_profesor
            
            # --- 2. Detección de Pose ---
            end_time = time.time()
            t = end_time - start_time
            start_time = end_time
            timestamp += int(t * 1000)

            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame)
            result = landmarker.detect_for_video(mp_image, timestamp)
            all_angles_correct = False

            # --- 3. Lógica de Ángulos ---
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
                        
                        if angulo_usuario is None: # Comprobación
                            all_angles_correct = False
                        else:
                            error = abs(angulo_usuario - angulo_objetivo)
                            if error <= definicion_postura["tolerancia"]:
                                color_articulacion = (0, 255, 0)
                            else:
                                all_angles_correct = False
                        feedback_colores[p2_idx] = color_articulacion

                    # --- 4. Dibujar Feedback en el frame ---
                    for articulacion_idx, color in feedback_colores.items():
                        articulacion = person_landmarks[articulacion_idx]
                        x, y = int(articulacion.x * W_CAM), int(articulacion.y * H_CAM)
                        cv2.circle(frame, (x, y), 15, color, -1)
                        cv2.circle(frame, (x, y), 15, (255, 255, 255), 2)
                
                except Exception as e:
                    all_angles_correct = False

            # Redimensionar frame del usuario y pegarlo
            frame_con_feedback = redimensionar_imagen(frame, (W_USUARIO, H_LIENZO))
            lienzo[0:H_LIENZO, W_PROFESOR:W_LIENZO] = frame_con_feedback
            
            # --- 5. Lógica de Estado del Juego ---
            cv2.putText(lienzo, nombre_postura.replace("_", " "), (20, 50), 
                        cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255, 255, 255), 3)
            cv2.putText(lienzo, "Presione ENTER para saltar", (10, 550), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.95, (255, 255, 255), 3)
            cv2.putText(lienzo, "  a la siguiente postura", (13, 600), 
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 3)

            if all_angles_correct:
                if postura_tiempo_inicio is None:
                    postura_tiempo_inicio = time.time()
                tiempo_mantenido = time.time() - postura_tiempo_inicio
                
                progreso = int((tiempo_mantenido / SEGUNDOS_PARA_SUPERAR) * (W_USUARIO - 40))
                progreso = min(progreso, W_USUARIO - 40)
                
                # La 'x' debe empezar en W_PROFESOR, no en W_USUARIO
                x_barra = W_PROFESOR + 20
                
                cv2.rectangle(lienzo, (x_barra, 80), (W_LIENZO - 20, 110), (0, 0, 0), -1)
                cv2.rectangle(lienzo, (x_barra, 80), (x_barra + progreso, 110), (0, 255, 0), -1)
                cv2.putText(lienzo, f"MANTEN: {int(tiempo_mantenido)+1}s", (x_barra + 10, 105), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)

                if tiempo_mantenido > SEGUNDOS_PARA_SUPERAR:
                    postura_actual_idx += 1
                    postura_tiempo_inicio = None
                    if postura_actual_idx >= len(LISTA_POSTURAS):
                        estado_juego = "TERMINADO" # <-- Cambio de estado
            else:
                postura_tiempo_inicio = None
                cv2.putText(lienzo, "Alinea tu cuerpo", (20, 100), 
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

        # -----------------------------------------------------------------
        # --- FIN LÓGICA DE ESTADOS ---
        # -----------------------------------------------------------------

        # --- 6. Mostrar resultado ---
        cv2.imshow("Profesor de Yoga - IPM", lienzo)

        # --- 7. Lógica de Teclas ---
        key = cv2.waitKey(5) & 0xFF
        
        # Salir con 'ESC' (funciona en todos los estados)
        if key == 27:
            break
            
        # Teclas que dependen del estado
        if estado_juego == "INICIO":
            if key == 32: # Código 32 es la barra ESPACIADORA
                estado_juego = "JUGANDO"
                start_time = time.time() # Reiniciar temporizadores del juego
                timestamp = 0
                
        elif estado_juego == "JUGANDO":
            if key == 13: # Código 13 es ENTER
                print(f"Saltando postura: {LISTA_POSTURAS[postura_actual_idx]}")
                postura_actual_idx += 1
                postura_tiempo_inicio = None 
                if postura_actual_idx >= len(LISTA_POSTURAS):
                    estado_juego = "TERMINADO" # Cambio de estado

    # --- Limpieza ---
    cap.release()
    cv2.destroyAllWindows()