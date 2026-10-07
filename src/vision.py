"""
Módulo de Visión Computacional para Murdoku.
Realiza la extracción automatizada de:
1. Cuadrícula y mapa de habitaciones (K-Means en CIELAB) y sus nombres (OCR de etiquetas).
2. Mobiliario en cada celda (Embeddings MobileNetV3 + Similitud Coseno).
3. Sospechosos, víctima y pistas (OCR por tarjeta + parser de testimonios).

Todas las imágenes comparten el mismo diseño: 6 tarjetas en 3 columnas x 2 filas a la
izquierda (la última es la víctima) y el tablero a la derecha. Solo varía el tamaño de
la grilla (6x6 u 8x8) y los nombres de las salas.
"""

import difflib
import os
import re
from functools import lru_cache
from pathlib import Path

import cv2
import numpy as np
import pytesseract
import torch
import torch.nn as nn
from PIL import Image
from scipy.optimize import linear_sum_assignment
from sklearn.cluster import KMeans
from torchvision import models, transforms

from src.parser_pistas import construir_pistas, normalizar

RAIZ = Path(__file__).resolve().parent.parent
DIR_PLANTILLAS = RAIZ / "assets" / "templates"

# -------------------------------------------------------------
# CONFIGURACIÓN DEL EXTRACTOR SEMÁNTICO (MobileNetV3)
# -------------------------------------------------------------
_dispositivo = torch.device("cpu")
_modelo_extractor = models.mobilenet_v3_small(weights=models.MobileNet_V3_Small_Weights.DEFAULT)
_modelo_extractor.classifier = nn.Identity()
_modelo_extractor.eval()

_transformacion = transforms.Compose([
    transforms.Resize((128, 128)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
])

# -------------------------------------------------------------
# CONFIGURACIÓN TESSERACT OCR
# -------------------------------------------------------------
ruta_tesseract_windows = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
if os.path.exists(ruta_tesseract_windows):
    pytesseract.pytesseract.tesseract_cmd = ruta_tesseract_windows

# TESSDATA_PREFIX debe ser la ruta absoluta de la carpeta con spa.traineddata
os.environ["TESSDATA_PREFIX"] = str(RAIZ / "tessdata")

# Cajas de las 6 tarjetas (x1, y1, x2, y2) sobre una imagen de referencia de 1920x1080.
# Orden de lectura: fila superior (3 tarjetas) y fila inferior (3 tarjetas, la última es la víctima).
REF_ANCHO, REF_ALTO = 1920, 1080
# El alto de cada caja deja margen para testimonios de hasta 4 líneas.
CAJAS_TARJETAS = [
    (70, 470, 390, 625), (410, 488, 730, 640), (735, 446, 1055, 600),
    (60, 858, 380, 1015), (400, 900, 720, 1050), (780, 878, 1100, 1035),
]


def obtener_embedding(imagen_bgr_o_rgba):
    """Extrae el embedding de características semánticas normalizado L2."""
    if len(imagen_bgr_o_rgba.shape) == 3 and imagen_bgr_o_rgba.shape[2] == 4:
        alpha = imagen_bgr_o_rgba[:, :, 3] / 255.0
        bgr = imagen_bgr_o_rgba[:, :, :3]
        img_comp = (bgr * alpha[:, :, None] + 255 * (1 - alpha[:, :, None])).astype(np.uint8)
        img_rgb = cv2.cvtColor(img_comp, cv2.COLOR_BGR2RGB)
    elif len(imagen_bgr_o_rgba.shape) == 3:
        img_rgb = cv2.cvtColor(imagen_bgr_o_rgba, cv2.COLOR_BGR2RGB)
    else:
        img_rgb = cv2.cvtColor(imagen_bgr_o_rgba, cv2.COLOR_GRAY2RGB)

    pil_img = Image.fromarray(img_rgb)
    tensor = _transformacion(pil_img).unsqueeze(0).to(_dispositivo)

    with torch.no_grad():
        embedding = _modelo_extractor(tensor)
        embedding = nn.functional.normalize(embedding, p=2, dim=1)

    return embedding


def celda_tiene_objeto(celda_bgr, umbral_std=14.0):
    """Descarta celdas de suelo liso sin muebles."""
    h, w, _ = celda_bgr.shape
    centro = celda_bgr[int(h * 0.18):int(h * 0.82), int(w * 0.18):int(w * 0.82)]
    gray = cv2.cvtColor(centro, cv2.COLOR_BGR2GRAY)
    return np.std(gray) > umbral_std, np.std(gray)


# -------------------------------------------------------------
# 1. SEGMENTACIÓN Y COLOR
# -------------------------------------------------------------
def localizar_tablero(imagen_bgr):
    """Localiza el marco cuadrado de la grilla en la mitad derecha."""
    alto, ancho, _ = imagen_bgr.shape
    mitad_der = imagen_bgr[:, int(ancho * 0.5):]
    gray = cv2.cvtColor(mitad_der, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 60, 255, cv2.THRESH_BINARY_INV)

    contornos, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    mejor_cnt = None
    max_area = 0

    for c in contornos:
        area = cv2.contourArea(c)
        if area > (alto * mitad_der.shape[1] * 0.20):
            x, y, w, h = cv2.boundingRect(c)
            ratio = float(w) / h
            if 0.8 <= ratio <= 1.2 and area > max_area:
                max_area = area
                mejor_cnt = (x + int(ancho * 0.5), y, w, h)

    if mejor_cnt is not None:
        gx, gy, gw, gh = mejor_cnt
        return imagen_bgr[gy+4:gy+gh-4, gx+4:gx+gw-4], (gx, gy, gw, gh)
    else:
        corte = imagen_bgr[int(alto * 0.27):int(alto * 0.84), int(ancho * 0.60):int(ancho * 0.96)]
        return corte, (int(ancho * 0.60), int(alto * 0.27), corte.shape[1], corte.shape[0])


def estimar_N(tablero_bgr):
    """
    Estima la dimensión NxN contando las líneas negras internas de la grilla.
    Devuelve None si no se distingue una cuadrícula.
    """
    gray = cv2.cvtColor(tablero_bgr, cv2.COLOR_BGR2GRAY)
    oscuro = gray < 60

    def lineas_internas(perfil):
        activos = perfil > 0.6
        centros, inicio = [], None
        for i, a in enumerate(np.append(activos, False)):
            if a and inicio is None:
                inicio = i
            elif not a and inicio is not None:
                centros.append((inicio + i - 1) / 2 / len(perfil))
                inicio = None
        # Las líneas pegadas al borde son el marco exterior, no separan celdas
        return [c for c in centros if 0.04 < c < 0.96]

    n_v = len(lineas_internas(oscuro.mean(axis=0))) + 1
    n_h = len(lineas_internas(oscuro.mean(axis=1))) + 1
    if n_v == n_h and 3 <= n_v <= 12:
        return n_v
    return None


def extraer_color_fondo(celda_bgr):
    """Muestrea las 4 esquinas interiores para aislar el color del suelo."""
    h, w, _ = celda_bgr.shape
    mh = max(2, int(h * 0.12))
    mw = max(2, int(w * 0.12))

    muestras = np.vstack([
        celda_bgr[2:mh, 2:mw].reshape(-1, 3),
        celda_bgr[2:mh, w - mw:-2].reshape(-1, 3),
        celda_bgr[h - mh:-2, 2:mw].reshape(-1, 3),
        celda_bgr[h - mh:-2, w - mw:-2].reshape(-1, 3)
    ])
    muestras_lab = cv2.cvtColor(muestras.reshape(-1, 1, 3), cv2.COLOR_BGR2LAB).reshape(-1, 3)
    return np.median(muestras_lab, axis=0)


def _lab_a_matiz(lab):
    """Matiz HSV (0-179) de un color CIELAB."""
    bgr = cv2.cvtColor(np.uint8([[np.clip(lab, 0, 255)]]), cv2.COLOR_LAB2BGR)
    return float(cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV)[0, 0, 0])


def _distancia_matiz(a, b):
    d = abs(a - b)
    return min(d, 180 - d)


# -------------------------------------------------------------
# 2. DETECCIÓN DE MUEBLES POR EMBEDDINGS (MobileNetV3)
# -------------------------------------------------------------
@lru_cache(maxsize=1)
def _cargar_plantillas(templates_dir=str(DIR_PLANTILLAS)):
    """Embeddings de las plantillas de muebles (se calculan una sola vez)."""
    vectores = {}
    for archivo in sorted(os.listdir(templates_dir)):
        if archivo.lower().endswith((".png", ".jpg")):
            img_tmpl = cv2.imread(os.path.join(templates_dir, archivo), cv2.IMREAD_UNCHANGED)
            if img_tmpl is not None:
                vectores[os.path.splitext(archivo)[0].lower()] = obtener_embedding(img_tmpl)
    return vectores


# Prefijo del nombre de la plantilla -> tipo de mueble que consume el solver
_TIPOS_MUEBLE = {"silla": "sillas", "mesa": "mesas", "planta": "plantas",
                 "computadora": "computadora", "laptop": "computadora"}


def clasificar_celdas(celdas_dict, templates_dir=str(DIR_PLANTILLAS), umbral_coseno=0.45):
    """
    Analiza cada celda y devuelve el detalle de la decisión:
      {(fila, col): {"std": desviación de grises, "tiene_objeto": bool,
                     "similitudes": {plantilla: coseno}, "plantilla": mejor plantilla o None,
                     "similitud": coseno de la mejor, "tipo": mueble asignado o None}}
    Una celda recibe 'tipo' solo si tiene objeto y su mejor similitud supera el umbral.
    """
    plantillas_vectores = _cargar_plantillas(templates_dir)
    detalle = {}

    for (r, c), celda_bgr in celdas_dict.items():
        tiene_obj, desviacion = celda_tiene_objeto(celda_bgr)
        info = {"std": round(float(desviacion), 2), "tiene_objeto": bool(tiene_obj),
                "similitudes": {}, "plantilla": None, "similitud": None, "tipo": None}
        detalle[(r, c)] = info
        if not tiene_obj:
            continue

        h_c, w_c, _ = celda_bgr.shape
        centro = celda_bgr[int(h_c * 0.10):int(h_c * 0.90), int(w_c * 0.10):int(w_c * 0.90)]
        vec_celda = obtener_embedding(centro)

        for nombre_tmpl, vec_tmpl in plantillas_vectores.items():
            info["similitudes"][nombre_tmpl] = round(torch.cosine_similarity(vec_celda, vec_tmpl).item(), 4)
        if info["similitudes"]:
            info["plantilla"] = max(info["similitudes"], key=info["similitudes"].get)
            info["similitud"] = info["similitudes"][info["plantilla"]]

        if info["plantilla"] is not None and info["similitud"] >= umbral_coseno:
            for prefijo, tipo in _TIPOS_MUEBLE.items():
                if info["plantilla"].startswith(prefijo):
                    info["tipo"] = tipo
                    break

    return detalle


def muebles_desde_detalle(detalle):
    """Agrupa las celdas clasificadas por tipo de mueble: {tipo: [(fila, col), ...]}."""
    muebles = {tipo: [] for tipo in dict.fromkeys(_TIPOS_MUEBLE.values())}
    for celda, info in detalle.items():
        if info["tipo"]:
            muebles[info["tipo"]].append(celda)
    return muebles


def detectar_muebles_en_celdas(celdas_dict, templates_dir=str(DIR_PLANTILLAS), umbral_coseno=0.45):
    """Clasifica los muebles de cada celda mediante similitud de embeddings."""
    return muebles_desde_detalle(clasificar_celdas(celdas_dict, templates_dir, umbral_coseno))


# -------------------------------------------------------------
# 3. TARJETAS: OCR POR TARJETA (nombre + testimonio)
# -------------------------------------------------------------
def _ocr(crop_bgr, psm=6):
    gray = cv2.cvtColor(crop_bgr, cv2.COLOR_BGR2GRAY)
    gray = cv2.resize(gray, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
    _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    return pytesseract.image_to_string(thresh, config=f"--psm {psm} -l spa")


def _separar_nombre_y_texto(texto_ocr, indice):
    """
    El testimonio empieza en la primera línea que arranca con 'El/Ella/La'; el nombre es la
    palabra en MAYÚSCULAS de la línea inmediatamente anterior. Las líneas de ruido del marco
    de la foto se descartan.
    """
    lineas = [l.strip() for l in texto_ocr.splitlines() if l.strip()]
    inicio = next((i for i, l in enumerate(lineas) if re.match(r"(el|ella|la)\b", normalizar(l))), None)
    if inicio is None:  # respaldo: primera línea con minúsculas
        inicio = next((i for i, l in enumerate(lineas) if re.search(r"[a-záéíóúñ]{2}", l)), len(lineas))
    nombre = None
    for linea in reversed(lineas[:inicio]):
        palabras = re.findall(r"[A-ZÁÉÍÓÚÜÑ]{2,}", linea)
        if palabras:
            nombre = palabras[-1].title()
            break
    if nombre is None:
        nombre = f"Persona{indice + 1}"
    return nombre, " ".join(lineas[inicio:])


def leer_tarjetas(imagen_bgr):
    """OCR de las 6 tarjetas (3 columnas x 2 filas). Devuelve [{'nombre', 'texto'}]."""
    alto, ancho, _ = imagen_bgr.shape
    tarjetas = []
    for i, (x1, y1, x2, y2) in enumerate(CAJAS_TARJETAS):
        crop = imagen_bgr[int(y1 / REF_ALTO * alto):int(y2 / REF_ALTO * alto),
                          int(x1 / REF_ANCHO * ancho):int(x2 / REF_ANCHO * ancho)]
        nombre, texto = _separar_nombre_y_texto(_ocr(crop), i)
        tarjetas.append({"nombre": nombre, "texto": texto})
    return tarjetas


# -------------------------------------------------------------
# 4. ETIQUETAS DE LAS SALAS (OCR + color)
# -------------------------------------------------------------
def leer_etiquetas_salas(imagen_bgr, bbox_tablero):
    """
    Busca las etiquetas de color que rotulan cada sala (encima y debajo del tablero).
    Devuelve [{'texto', 'matiz'}] con el texto OCR y el matiz HSV del color de la etiqueta.
    """
    gx, gy, gw, gh = bbox_tablero
    alto, ancho, _ = imagen_bgr.shape
    margen_v = int(alto * 0.085)
    margen_h = int(ancho * 0.03)
    x1, x2 = max(0, gx - margen_h), min(ancho, gx + gw + margen_h)
    bandas = [(max(0, gy - margen_v), gy), (gy + gh, min(alto, gy + gh + margen_v))]

    etiquetas = []
    for y1, y2 in bandas:
        banda = imagen_bgr[y1:y2, x1:x2]
        gray = cv2.cvtColor(banda, cv2.COLOR_BGR2GRAY)
        gray = cv2.resize(gray, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
        datos = pytesseract.image_to_data(gray, config="--psm 11 -l spa", output_type=pytesseract.Output.DICT)

        palabras = [(datos["left"][i], datos["top"][i], datos["width"][i], datos["height"][i], datos["text"][i])
                    for i in range(len(datos["text"]))
                    if datos["text"][i].strip() and float(datos["conf"][i]) > 30]
        # Cada banda tiene una sola fila de etiquetas: se agrupan palabras contiguas en x
        palabras.sort(key=lambda p: p[0])
        grupos = []
        for p in palabras:
            if grupos and 0 <= p[0] - (grupos[-1][-1][0] + grupos[-1][-1][2]) < 40:
                grupos[-1].append(p)
            else:
                grupos.append([p])

        for g in grupos:
            texto = " ".join(p[4] for p in g)
            gx1 = min(p[0] for p in g) // 2
            gy1 = min(p[1] for p in g) // 2
            gx2 = max(p[0] + p[2] for p in g) // 2
            gy2 = max(p[1] + p[3] for p in g) // 2
            region = banda[gy1:gy2, gx1:gx2]
            if region.size == 0:
                continue
            gris = cv2.cvtColor(region, cv2.COLOR_BGR2GRAY)
            pixeles = region[gris > 120]  # descarta el texto negro
            if len(pixeles) < 10:
                continue
            color = np.median(pixeles, axis=0).astype(np.uint8)
            matiz = float(cv2.cvtColor(color.reshape(1, 1, 3), cv2.COLOR_BGR2HSV)[0, 0, 0])
            etiquetas.append({"texto": texto, "matiz": matiz})
    return etiquetas


def asignar_nombres_a_salas(etiquetas, salas, matices_clusters):
    """
    Une cada sala del catálogo con un cluster de K-Means:
    1) la etiqueta cuyo texto más se parece al nombre de la sala,
    2) el cluster cuyo matiz de color es más cercano al de esa etiqueta.
    Devuelve {id_sala: id_cluster}.
    """
    sala_matiz = {}
    for sala in salas:
        nombres = [normalizar(sala["nombre"])] + [normalizar(a) for a in sala.get("alias", [])]
        mejor, mejor_ratio = None, 0.6
        for et in etiquetas:
            for n in nombres:
                ratio = difflib.SequenceMatcher(None, normalizar(et["texto"]), n).ratio()
                if ratio > mejor_ratio:
                    mejor, mejor_ratio = et, ratio
        if mejor is not None:
            sala_matiz[sala["id"]] = mejor["matiz"]

    if not sala_matiz:
        return {}
    ids_sala = list(sala_matiz)
    ids_cluster = list(matices_clusters)
    costo = np.array([[_distancia_matiz(sala_matiz[s], matices_clusters[c]) for c in ids_cluster]
                      for s in ids_sala])
    filas, cols = linear_sum_assignment(costo)
    return {ids_sala[i]: ids_cluster[j] for i, j in zip(filas, cols)}


# -------------------------------------------------------------
# 5. FUNCIÓN MAESTRA END-TO-END
# -------------------------------------------------------------
def extraer_puzzle_completo(imagen_path, N=None, salas=None, num_habitaciones=None,
                            modelo_ollama="llama3.2:3b", usar_llm=True):
    """
    Lee exclusivamente la imagen del disco y construye toda la estructura de datos
    mediante K-Means, MobileNetV3, OCR y el parser de testimonios.

    N: dimensión de la grilla (si es None se estima contando líneas).
    salas: [{'id', 'nombre', 'alias'?}] del caso; permite nombrar las salas y entender
           las pistas del tipo "en la Gerencia". Sin ellas, las salas se numeran por color.
    """
    img = cv2.imread(str(imagen_path))
    if img is None:
        raise FileNotFoundError(f"No se encontró la imagen en: {imagen_path}")

    # 1. Segmentación del tablero
    tablero_crop, bbox = localizar_tablero(img)
    N_estimado = estimar_N(tablero_crop)
    if N is None:
        N = N_estimado or 6
    ht, wt, _ = tablero_crop.shape
    alto_c = ht // N
    ancho_c = wt // N

    muestras_color = []
    claves_celdas = [(r, c) for r in range(N) for c in range(N)]
    celdas_dict = {}
    for r, c in claves_celdas:
        celda = tablero_crop[r * alto_c:(r + 1) * alto_c, c * ancho_c:(c + 1) * ancho_c]
        celdas_dict[(r, c)] = celda
        muestras_color.append(extraer_color_fondo(celda))

    # 2. Segmentación de habitaciones con K-Means en CIELAB
    k = len(salas) if salas else (num_habitaciones or 3)
    muestras = np.array(muestras_color)
    etiquetas_km = KMeans(n_clusters=k, random_state=42, n_init=10).fit_predict(muestras)
    habitaciones = {celda: int(etiquetas_km[i]) + 1 for i, celda in enumerate(claves_celdas)}

    # 3. Nombres de las salas: etiqueta (OCR) -> cluster por color
    salas_detectadas = []
    if salas:
        matices = {int(cl) + 1: _lab_a_matiz(muestras[etiquetas_km == cl].mean(axis=0)) for cl in range(k)}
        asignacion = asignar_nombres_a_salas(leer_etiquetas_salas(img, bbox), salas, matices)
        cluster_a_sala = {cl: sid for sid, cl in asignacion.items()}
        # Los clusters sin etiqueta reciben los ids de sala que quedaron libres
        libres = [s["id"] for s in salas if s["id"] not in asignacion]
        for cl in matices:
            if cl not in cluster_a_sala and libres:
                cluster_a_sala[cl] = libres.pop(0)
        habitaciones = {celda: cluster_a_sala.get(cl, cl) for celda, cl in habitaciones.items()}
        salas_detectadas = salas

    # 4. Detección de muebles con Embeddings de MobileNetV3
    detalle_celdas = clasificar_celdas(celdas_dict)
    muebles = muebles_desde_detalle(detalle_celdas)

    # 5. OCR por tarjeta + parser de testimonios
    tarjetas = leer_tarjetas(img)
    sospechosos, victima, pistas, no_reconocidas = construir_pistas(
        tarjetas, salas_detectadas, N, usar_llm=usar_llm, modelo=modelo_ollama
    )

    return {
        "N": N,
        "N_estimado": N_estimado,
        "tablero_img": tablero_crop,
        "celdas_detalle": detalle_celdas,
        "sospechosos": sospechosos,
        "victima": victima,
        "habitaciones": habitaciones,
        "muebles": muebles,
        "pistas": pistas,
        "salas": salas_detectadas,
        "tarjetas": tarjetas,
        "no_reconocidas": no_reconocidas,
        "obstaculos": ["mesas", "plantas", "computadora"],
    }
