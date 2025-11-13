POSTURAS_YOGA = {
    
    # 1. flexión.jpg (Lateral)
    "FLEXION": {
        # Asumimos que la cámara ve un perfil.
        # Solo comprobamos un lado (ej. izquierdo).
        # En el CÓDIGO, comprobaremos la visibilidad.
        "angulo_codo_izq": 170,
        "angulo_hombro_izq": 80,
        "angulo_cadera_izq": 175,
        "angulo_rodilla_izq": 175,
        "tolerancia": 25
    },

    # 2. guerrero 4.jpg (Lateral)
    "GUERRERO_4": {
        # ¡IMPORTANTE! Esta postura es asimétrica y lateral.
        # Es imposible comprobar "codo_izq" y "codo_der".
        # Vamos a definir "brazos", "pierna_delantera" y "pierna_trasera".
        # El código tendrá que ser inteligente y ver QUÉ pierna está delante.
        
        # Por ahora, simplifiquemos asumiendo PIERNA IZQUIERDA DELANTE:
        "angulo_codo_izq": 170,     # Brazo visible
        "angulo_hombro_izq": 170,   # Brazo visible
        "angulo_cadera_izq": 130,   # Cadera pierna delantera
        "angulo_rodilla_izq": 100,  # Rodilla delantera DOBLADA
        "angulo_rodilla_der": 175,  # Rodilla trasera RECTA (esta SÍ suele verse)
        "tolerancia": 30
    },

    # 3. perro boca abajo.jpg (Lateral)
    "PERRO_BOCA_ABAJO": {
        # Solo comprobamos un lado.
        "angulo_codo_izq": 175,
        "angulo_hombro_izq": 170,
        "angulo_cadera_izq": 90,
        "angulo_rodilla_izq": 175,
        "tolerancia": 30
    },

    # 4. perro boca arriba.jpg (Lateral)
    "PERRO_BOCA_ARRIBA": {
        # Solo comprobamos un lado.
        "angulo_codo_izq": 170,
        "angulo_hombro_izq": 90,
        "angulo_cadera_izq": 175,
        "angulo_rodilla_izq": 175,
        "tolerancia": 25
    },

    # 5. pinza de pie.jpg (Lateral O Frontal)
    # Si es lateral, se aplica la misma lógica (comprobar 1 lado).
    # Si es frontal, se pueden ver ambos.
    "PINZA_DE_PIE": {
        "angulo_cadera_izq": 20,
        "angulo_rodilla_izq": 175,
        "angulo_cadera_der": 20, # Opcional si es visible
        "angulo_rodilla_der": 175, # Opcional si es visible
        "tolerancia": 35 
    },

    # 6. pinza sentada.jpg (Lateral)
    "PINZA_SENTADA": {
        "angulo_cadera_izq": 45,
        "angulo_rodilla_izq": 175,
        "tolerancia": 25
    },

    # 7. pose arbol yoga.jpg (Frontal - Aquí SÍ comprobamos ambos)
    "ARBOL": {
        # Asimétrica FRONTAL. Asumimos pierna IZQUIERDA levantada.
        "angulo_codo_izq": 40,
        "angulo_codo_der": 40,
        "angulo_cadera_izq": 100,   # Pierna levantada
        "angulo_cadera_der": 175,   # Pierna de apoyo
        "angulo_rodilla_izq": 45,   # Pierna DOBLADA
        "angulo_rodilla_der": 175,  # Pierna de apoyo RECTA
        "tolerancia": 25
    },

    # 8. pose facil.jpg (Frontal)
    "POSE_FACIL": {
        # Simétrica FRONTAL.
        "angulo_cadera_izq": 100,
        "angulo_rodilla_izq": 45,
        "angulo_codo_izq": 160,
        "angulo_cadera_der": 100, # Comprobamos ambos
        "angulo_rodilla_der": 45,
        "angulo_codo_der": 160,
        "tolerancia": 30
    },

    # 9. pose triangulo extendido.jpg (Frontal)
    "TRIANGULO_EXTENDIDO": {
        # Asimétrica FRONTAL. Asumimos inclinación a la IZQUIERDA.
        "angulo_codo_izq": 175,
        "angulo_codo_der": 175,
        "angulo_hombro_izq": 90,
        "angulo_hombro_der": 90,
        "angulo_rodilla_izq": 175,
        "angulo_rodilla_der": 175,
        "tolerancia": 30
    },

    # 10. postura de la barca.jpg (Lateral)
    "BARCA": {
        "angulo_cadera_izq": 90,
        "angulo_rodilla_izq": 90,
        "angulo_codo_izq": 170,
        "tolerancia": 25
    },

    # 11. sentadilla.jpg (Sentadilla profunda o Malasana) 
    "SENTADILLA": {
        # Vista: Frontal.
        # Simétrica, comprobamos ambos lados.
        "angulo_codo_izq": 40,      # Codos doblados, manos juntas
        "angulo_codo_der": 40,
        "angulo_cadera_izq": 45,    # Cadera muy flexionada
        "angulo_cadera_der": 45,
        "angulo_rodilla_izq": 45,   # Rodilla muy flexionada
        "angulo_rodilla_der": 45,
        "tolerancia": 30
    },

    # 12. postura guerrero 2.jpg
    "GUERRERO_2": {
        # Vista: Lateral.
        # Asimétrica. Asumimos PIERNA IZQUIERDA ADELANTE.
        "angulo_codo_izq": 175,     # Brazo delantero recto
        "angulo_codo_der": 175,     # Brazo trasero recto
        "angulo_hombro_izq": 90,    # Brazo delantero en T (ángulo Hombro-Cadera-Codo)
        "angulo_hombro_der": 90,    # Brazo trasero en T
        "angulo_rodilla_izq": 90,   # Rodilla delantera DOBLADA
        "angulo_rodilla_der": 175,  # Rodilla trasera RECTA
        "tolerancia": 25
    },

    # 13. postura plancha lateral.jpg
    "PLANCHA_LATERAL": {
        # Vista: Lateral.
        # Asimétrica. Asumimos BRAZO IZQUIERDO DE APOYO.
        "angulo_codo_izq": 175,     # Brazo de apoyo recto
        "angulo_codo_der": 175,     # Brazo de arriba recto
        "angulo_hombro_der": 90,    # Brazo de arriba extendido (ángulo Hombro-Cadera-Codo)
        "angulo_cadera_izq": 175,   # Cuerpo recto (ángulo Hombro-Cadera-Tobillo)
        "angulo_rodilla_izq": 175,  # Piernas rectas
        "tolerancia": 25
    },

    # 14. postura guerrero 3.jpg
    "GUERRERO_3": {
        # Vista: Lateral.
        # Asimétrica. Asumimos PIERNA IZQUIERDA DE APOYO.
        "angulo_codo_izq": 175,     # Brazos rectos (visibles)
        "angulo_rodilla_izq": 175,  # Pierna de apoyo recta
        "angulo_rodilla_der": 175,  # Pierna elevada recta
        "angulo_cadera_izq": 90,    # Ángulo Torso-Pierna de apoyo (forma de T)
        "angulo_cadera_der": 175,   # Pierna elevada alineada con torso (Cadera_Izq - Cadera_Der - Rodilla_Der)
        "tolerancia": 30
    },

    # 15. postura guerrero 1.jpg
    "GUERRERO_1": {
        # Vista: Frontal.
        # Asimétrica. Asumimos PIERNA IZQUIERDA ADELANTE.
        "angulo_codo_izq": 160,     # Brazos arriba (ligeramente doblados)
        "angulo_codo_der": 160,
        "angulo_hombro_izq": 170,   # Brazos elevados
        "angulo_hombro_der": 170,
        "angulo_rodilla_izq": 100,  # Rodilla delantera DOBLADA
        "angulo_rodilla_der": 175,  # Rodilla trasera RECTA
        "tolerancia": 30
    },

    # 16. postura del gato.jpg (Esta es la Postura de la Mesa, o "Mesa")
    "MESA": {
        # Vista: Lateral.
        # Simétrica, pero vista de lado. Comprobamos un lado.
        "angulo_codo_izq": 170,     # Brazos rectos
        "angulo_hombro_izq": 90,    # Hombros sobre muñecas (ángulo Cadera-Hombro-Muñeca)
        "angulo_cadera_izq": 90,    # Caderas sobre rodillas (ángulo Hombro-Cadera-Rodilla)
        "angulo_rodilla_izq": 90,   # Rodillas dobladas (ángulo Cadera-Rodilla-Tobillo)
        "tolerancia": 25
    }
}