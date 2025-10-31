# IPM - Práctica 2 

![mediapipe_game_ipm](https://github.com/user-attachments/assets/1c51471e-8b4b-4f56-bd25-9cebfacb2af2)


## Resumen

En esta práctica veremos como realizar interfaces para la interacción persona-máquina (IPM o HCI) basadas en visión por computador. La interacción, como hemos visto en teoría no tiene porqué limitarse al diseño y desarrollo de interfaces para la manipulación de sistemas operativos, aunque sí existe también esa vertiente. Existen multitud de aplicaciones en videojuegos o juegos ‘serios’ para rehabilitación u otras finalidades. También existen aplicaciones en interacción persona-entorno, en domótica avanzada (casas inteligentes, edificios inteligentes), que no dejan de ser sistemas informáticos distribuidos con los que se interactúa. La idea es que estos sistemas puedan responder a las necesidades de las personas que los habitan y ayudar o apoyar sus tareas en el día a día. También pueden ‘pasivamente’ analizar lo que ocurre (interacción pasiva) y evitar accidentes o evaluar el estado de salud entre otros (salud electrónica, e-Health, teleasistencia, etc.).



Este repositorio contiene un juego sencillo usando la librería de MediaPipe que puede servir como guía para el desarrollo de la práctica. Para crear vuesto videojuego, podeis hacer uso de los modelos que ofrece MediaPipe en su página oficial:

- *```Pose Landmarker```* (usado en este repositorio), [aquí](https://ai.google.dev/edge/mediapipe/solutions/vision/pose_landmarker?hl=es-419).
- *```Hand Landmarker```*, [aquí](https://ai.google.dev/edge/mediapipe/solutions/vision/hand_landmarker?hl=es-419).
- *```Face Landmarker```*, [aquí](https://ai.google.dev/edge/mediapipe/solutions/vision/face_landmarker/index?hl=es-419).
- *```Holistic Landmarker```*, [aquí](https://ai.google.dev/edge/mediapipe/solutions/vision/holistic_landmarker?hl=es-419).

## Prerequisitos

Tener instalado **Conda**, [instalar aquí](https://www.anaconda.com/docs/getting-started/miniconda/install#macos-linux-installation).

## Requisitos

Crear un entorno de conda:
```bash
conda create -n IPM python=3.12
conda activate IPM
```

## Instalación

Se instalan las siguientes dependencias:
```bash
pip install -r requirements.txt
```

## Descargar pesos

Script para poder descargar los peso del modelo *Pose Landmarker*:
```bash
python download_models
```

Para descargar los pesos de otros modelos como _Hand Landmarker_, _Face Landmarker_ u _Holisitc Landmarker_ debes de descargarlos de los [enlaces](https://github.com/CarloHSUA/IPM/edit/main/README.md#resumen) de la página oficial de MediaPipe

## Ejecución
```bash
python app.py
```
