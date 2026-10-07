"""
Módulo de Visualización para Murdoku.
Superpone las soluciones (avatares, nombres, marcas de sospechosos y asesino)
directamente sobre la imagen del tablero.
"""

import cv2
import numpy as np


def dibujar_solucion_sobre_tablero(tablero_bgr, resultado_solver, N=6):
    """
    Toma la imagen recortada de la grilla y dibuja sobre ella los nombres
    de cada persona en sus celdas asignadas, resaltando al culpable.
    """
    canvas = tablero_bgr.copy()
    h, w, _ = canvas.shape
    alto_c = h // N
    ancho_c = w // N

    posiciones = resultado_solver["posiciones"]
    victima = resultado_solver["victima"]
    asesino = resultado_solver["asesino"]

    for nombre, datos in posiciones.items():
        r = datos["fila"]
        c = datos["columna"]

        x1 = c * ancho_c
        y1 = r * alto_c
        x2 = x1 + ancho_c
        y2 = y1 + alto_c
        cx = x1 + ancho_c // 2
        cy = y1 + alto_c // 2

        # 1. Definir color del badge según rol
        if nombre == asesino:
            color_badge = (0, 0, 220)       # Rojo intenso (Asesino)
            color_texto = (255, 255, 255)
            etiqueta = f"{nombre} [CULPABLE]"
        elif nombre == victima:
            color_badge = (40, 40, 40)       # Negro / Gris oscuro (Víctima)
            color_texto = (200, 200, 200)
            etiqueta = f"{nombre} (Victima)"
        else:
            color_badge = (240, 180, 50)     # Azul / Cian (Inocente)
            color_texto = (20, 20, 20)
            etiqueta = nombre

        # 2. Dibujar overlay semitransparente en la celda
        sub_img = canvas[y1:y2, x1:x2]
        overlay = sub_img.copy()
        cv2.rectangle(overlay, (2, 2), (ancho_c - 2, alto_c - 2), color_badge, -1)
        # Mezcla con 45% de opacidad para que el fondo del cuarto siga visible
        cv2.addWeighted(overlay, 0.45, sub_img, 0.55, 0, sub_img)

        # 3. Dibujar marco exterior a la celda
        cv2.rectangle(canvas, (x1, y1), (x2, y2), color_badge, 2 if nombre != asesino else 4)

        # 4. Colocar texto centrado
        font = cv2.FONT_HERSHEY_SIMPLEX
        thickness = 1
        # Ajusta el tamaño del texto para que quepa en la celda (6x6 u 8x8)
        (ancho_base, _), _ = cv2.getTextSize(etiqueta, font, 1.0, thickness)
        scale = min(0.45, 0.9 * ancho_c / ancho_base)
        (tw, th), _ = cv2.getTextSize(etiqueta, font, scale, thickness)
        
        cv2.putText(canvas, etiqueta, (cx - tw // 2, cy + th // 2),
                    font, scale, color_texto, thickness, cv2.LINE_AA)

    return canvas