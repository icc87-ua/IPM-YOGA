# Instructor de Yoga AI (Visión Artificial)

Este proyecto es una aplicación interactiva de escritorio que actúa como un instructor de yoga personal. Utilizando **Python**, **OpenCV** y **MediaPipe**, el sistema analiza la postura del usuario en tiempo real a través de la cámara web, calcula los ángulos corporales y proporciona retroalimentación visual inmediata (corrección de postura) comparándola con una base de datos de asanas predefinidas.

## Características

* **Detección de Pose en Tiempo Real:** Utiliza el modelo avanzado de MediaPipe Pose Landmarker.
* **Feedback Visual:**
    * 🔴 **Rojo:** La articulación no está en el ángulo correcto.
    * 🟢 **Verde:** La articulación está correctamente alineada.
* **Sistema de Progresión:** Barra de tiempo que se llena cuando mantienes la postura correcta por los segundos definidos.
* **Interfaz Gráfica (UI):** Pantallas de inicio y fin, superposiciones informativas y guías visuales.
* **Tolerancia Ajustable:** Configuración de márgenes de error para diferentes niveles de dificultad.

## Requisitos Previos

Necesitas tener instalado **Python 3.8** o superior.

### Librerías necesarias

Puedes instalar todas las dependencias ejecutando el siguiente comando:

```bash
pip install requirements.txt
pip install opencv-python mediapipe numpy
```

## Estructura del Proyecto

Para que el código funcione correctamente, debes organizar tus carpetas y archivos de la siguiente manera:

```text
PROYECTO_YOGA/
│
├── app.py                # Script principal (Lógica del juego y bucle de video)
├── config.py              # Configuraciones globales (tiempos, rutas)
├── posturas.py            # Base de datos de ángulos y tolerancias
├── angulos.py             # Mapeo de landmarks de MediaPipe
│
├── models/                # Carpeta para el modelo de IA
│   └── pose_landmarker_full.task  <-- [IMPORTANTE: Descargar este archivo]
│
└── fotos/                 # Carpeta para las imágenes de referencia
    ├── inicio.jpg         # (Opcional) Fondo de pantalla de inicio
    ├── final.jpg          # (Opcional) Fondo de pantalla final
    ├── arbol.jpg          # Imágenes de las posturas...
    ├── perro boca abajo.jpg
    ├── ...
    └── [Otras imágenes definidas en main.py]
```

## Instalación y Configuración

## Ejecución y Uso

Para iniciar la aplicación, ejecuta el archivo principal desde tu terminal:

```bash
python app.py
```

### Controles

* **ESPACIO:** En la pantalla de título, inicia la sesión.
* **ENTER:** Durante la sesión, salta la postura actual (útil si no logras completarla).
* **ESC:** Cierra la aplicación en cualquier momento.

### Cómo funciona

1. El sistema te mostrará una imagen de la postura objetivo.
2. Alinéate frente a la cámara (asegura buena iluminación).
3. Verás puntos sobre tus articulaciones en la pantalla. Ajusta tu cuerpo hasta que todos los puntos se vuelvan **verdes**.
4. Mantén la posición hasta que la barra de progreso se complete.

## Personalización

### Modificar Tiempos (`config.py`)

Puedes cambiar la duración del juego o los tiempos de espera editando este archivo:

```python
self.game_time = 20     # Duración total
self.padding = 100      # Márgenes visuales
```

### Añadir o Calibrar Posturas (`posturas.py`)

Si deseas agregar nuevas posturas o ajustar la dificultad:

1. Abre `posturas.py`.
2. Modifica los ángulos objetivo o el valor de `tolerancia` (actualmente en 40 grados).
    * *Bajar la tolerancia (ej. a 20) hace el juego más difícil.*
    * *Subir la tolerancia (ej. a 50) lo hace más fácil.*

---

