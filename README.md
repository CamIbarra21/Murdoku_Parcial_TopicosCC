# Murdoku: Solver con Visión Computacional y Constraint Programming

**Curso:** CC58 – Tópicos en Ciencia de la Computación
**Trabajo 1:** Constraint Programming (integración End-to-End de Visión Computacional y CP)

**Integrantes:**
- Camila Adriana Ibarra Cabrera
- Sofia Gabriel Miranda Cardenas
- Lizbeth Teresita Olivera Alvarez

## Descripción


Sistema *end-to-end* que recibe la **imagen de un acertijo Murdoku**, extrae su estado inicial con visión computacional, lo modela como un **problema de satisfacción de restricciones (CSP)** resuelto con **Google OR-Tools CP-SAT** y proyecta la solución sobre la imagen original. Incluye un **tutor interactivo**: el jugador ubica personas en el tablero y el solver le da pistas progresivas y valida su avance sin revelar la solución.

### Reglas del Murdoku modeladas
- Cada persona ocupa exactamente una celda; nadie comparte fila ni columna con otra (estilo Sudoku).
- Las celdas con mesas, plantas o laptop no se pueden ocupar; las sillas sí.
- El asesino es el único sospechoso que está en la misma habitación que la víctima.
- Pistas: columna/fila (ordinales, "última"), habitación, dirección relativa (norte, sur, este, oeste), sobre una silla, no sobre una silla, al lado de un mueble y no al lado de un mueble ("al lado" = adyacencia ortogonal).

### Formato de las imágenes
Todos los casos comparten el mismo diseño: **6 tarjetas en 3 columnas × 2 filas** a la izquierda (5 sospechosos y, en la última, la víctima), y el **tablero** a la derecha, rotulado con etiquetas de color por habitación. Solo varía el tamaño de la grilla (6×6 u 8×8) y las habitaciones.

## Demo

https://youtu.be/FfXyWsArZNQ

## Pipeline

```
Imagen ──► Visión (OpenCV, K-Means, MobileNetV3, Tesseract) ──► Parser de pistas
       ──► Modelo CP-SAT (OR-Tools) ──► Solución ──► Overlay visual / Web / Tutor
```

| Fase | Módulo | Técnica |
|---|---|---|
| 1. Extracción | `src/vision.py` | Localiza el tablero (umbral + contornos) y estima N contando líneas; **K-Means en CIELAB** para habitaciones; **OCR de las etiquetas de color** (Tesseract) para nombrar cada habitación y asignarla a su cluster por matiz; **embeddings MobileNetV3-small + similitud coseno** para muebles; **OCR por tarjeta** (3×2) para nombres y testimonios |
| 1b. Pistas | `src/parser_pistas.py` | Parser determinista en español (ordinales, salas, adyacencia, direcciones). **Ollama** (`llama3.2:3b`) solo como respaldo para frases no reconocidas |
| 2. Modelado CP | `src/solver.py` | **OR-Tools CP-SAT** con booleanas de ocupación `celda[p,r,c]` y proyección a enteras `X` (fila), `Y` (columna) y `Z` (habitación); validación estricta de pistas y verificación de **solución única** |
| 3. Visualización | `src/visualizer.py` | Superposición de la solución sobre el tablero; el culpable se marca en rojo |
| Tutor | `src/tutor.py` | Pistas deterministas: el solver revisa las ubicaciones del jugador con **pistas reificadas** (señala qué testimonio contradice) y calcula las casillas posibles de la persona más acotada; 3 niveles de ayuda |
| Redacción | `src/agent.py` | Ollama (opcional) solo reformula el mensaje del tutor; una guardia descarta cualquier texto que agregue números, nombres o razonamiento |
| Catálogo | `src/catalogo.py`, `casos/casos.json` | Fuente única de los 10 casos y de sus imágenes |
| Interfaz | `app.py`, `static/index.html` | API FastAPI y SPA web |

### Modelo matemático (resumen)
- **Variables:** `celda[p,r,c] ∈ {0,1}`; `X_p, Y_p ∈ {0..N-1}`; `Z_p ∈ {id de habitaciones}`.
- **Restricciones:** una celda por persona; como máximo una persona por fila y por columna; obstáculos físicos; regla víctima-asesino con restricciones reificadas (`OnlyEnforceIf`); una restricción por cada pista extraída.
- El modelo se construye a partir del diccionario `puzzle_data` generado por la visión; nada del solver depende de un caso concreto.

## Estructura del repositorio

```
├── main.py                  # Pipeline por línea de comandos (--caso caso_02)
├── app.py                   # API FastAPI (sirve también la web)
├── casos/casos.json         # Catálogo: salas, muebles, testimonios y solución de los 10 casos
├── src/
│   ├── catalogo.py          # Carga el catálogo y resuelve rutas de imágenes
│   ├── vision.py            # Extracción: tablero, salas, muebles, tarjetas
│   ├── parser_pistas.py     # Testimonios en español -> restricciones
│   ├── solver.py            # Modelo CP-SAT
│   ├── visualizer.py        # Overlay de la solución
│   ├── tutor.py             # Pistas y validación del jugador (solver)
│   └── agent.py             # Redacción opcional con Ollama
├── static/
│   ├── index.html           # Interfaz web
│   └── casos/caso_NN.png    # Imágenes de los casos (única ubicación)
├── scripts/
│   ├── validar_dataset.py   # Comprueba solución única de cada caso
│   ├── evaluar.py           # Métricas de visión + solver sobre las imágenes disponibles
│   └── generar_dataset_md.py# Regenera dataset_casos_murdoku.md
├── tests/                   # pytest: parser, solver, catálogo y tutor
├── dataset_casos_murdoku.md # Los 10 casos (guía para dibujar las imágenes)
├── resultados/evaluacion.md # Última tabla de evaluación
├── assets/templates/        # Plantillas de muebles (silla, mesa, planta, laptop)
├── tessdata/                # spa.traineddata para Tesseract
└── requirements.txt
```

## Instalación

### Requisitos previos
1. **Python 3.10 o superior** (desarrollado con 3.13).
2. **Tesseract OCR**. El código lo busca en `C:\Program Files\Tesseract-OCR\tesseract.exe` (Windows) o en el `PATH`.
   ```powershell
   # Windows (PowerShell)
   winget install --id UB-Mannheim.TesseractOCR
   ```
   ```bash
   # Ubuntu / Debian
   sudo apt install tesseract-ocr
   # macOS
   brew install tesseract
   ```
   También puedes usar el instalador de Windows de https://github.com/UB-Mannheim/tesseract/wiki.

   **Datos de idioma español:** el código lee `spa.traineddata` desde la carpeta `tessdata/` del proyecto. Si no está, descárgalo:
   ```powershell
   # Windows (PowerShell)
   New-Item -ItemType Directory -Force tessdata
   Invoke-WebRequest -Uri "https://github.com/tesseract-ocr/tessdata_fast/raw/main/spa.traineddata" -OutFile "tessdata\spa.traineddata"
   ```
   ```bash
   # Linux / macOS
   mkdir -p tessdata
   curl -L -o tessdata/spa.traineddata https://github.com/tesseract-ocr/tessdata_fast/raw/main/spa.traineddata
   ```
   Verifica la instalación con `tesseract --version`.
3. **Ollama** (https://ollama.com) con el modelo descargado (se usa para el tutor y como respaldo del parser):
   ```bash
   ollama pull llama3.2:3b
   ```
   Ollama debe estar corriendo en `http://localhost:11434`. El pipeline principal funciona sin Ollama; solo el tutor y el respaldo del parser lo necesitan.

### Dependencias de Python
```bash
git clone https://github.com/CamIbarra21/Murdoku_TopicosCC.git
cd Murdoku_TopicosCC

python -m venv venv
# Windows (PowerShell)
venv\Scripts\Activate.ps1
# Linux / macOS
# source venv/bin/activate

pip install -r requirements.txt
```

La primera ejecución descarga los pesos preentrenados de MobileNetV3 (torchvision).

## Ejecución

### Línea de comandos
```bash
python main.py --lista            # casos y si su imagen existe
python main.py                    # caso_01 (La Tienda)
python main.py --caso caso_02     # cualquier caso disponible
```
Muestra el tablero, los muebles y las pistas extraídas, resuelve el caso, imprime las posiciones y el asesino, y guarda `tablero_resuelto_<caso>.png`.

### Interfaz web
```bash
python app.py
```
Abre http://127.0.0.1:8000. La galería se genera desde el catálogo: los casos con imagen en `static/casos/` están habilitados y el resto aparece como "Próximamente". Endpoints:

| Método | Ruta | Función |
|---|---|---|
| GET | `/api/casos` | Catálogo con el campo `disponible` |
| POST | `/api/analizar?caso=caso_02` | Ejecuta la visión y devuelve el estado del tablero |
| POST | `/api/resolver?caso=caso_02` | Resuelve el caso con CP-SAT |
| POST | `/api/tutor?caso=caso_02` | Pista para el siguiente paso. Body: `{"colocaciones": {"Ana": [fila, col]}, "nivel": 1, "usar_llm": false}` (índices desde 0) |
| POST | `/api/validar?caso=caso_02` | Indica si las ubicaciones del jugador contradicen algún testimonio, sin revelar la solución |

### Despliegue como demo (Cloudflare Tunnel)
La app procesa todo en la máquina local (Tesseract, torch, CP-SAT y el modelo de Ollama, ~2 GB), por lo que no cabe en un hosting gratuito. Para mostrarla a otras personas se publica el puerto 8000 con un túnel, sin cuenta ni cambios en el código: el frontend usa rutas relativas y Ollama solo se consume por `localhost`, sin exponerse.

1. **Una sola vez:** `winget install Cloudflare.cloudflared` y abrir una terminal nueva para que reconozca el comando.
2. **Terminal 1, Ollama** (opcional; si no está, el tutor usa el mensaje del solver): `ollama pull llama3.2:3b` y `ollama serve`. Si ya corre en segundo plano, el aviso de puerto en uso es normal.
3. **Terminal 2, la app:** `python app.py` y esperar `Uvicorn running on http://127.0.0.1:8000`.
4. **Terminal 3, el túnel:**
   ```bash
   cloudflared tunnel --url http://127.0.0.1:8000
   ```
   Imprime una URL `https://<algo>.trycloudflare.com` que cualquiera puede abrir desde otra red.

Notas:
- Usar `127.0.0.1` y no `localhost`: `cloudflared` resuelve `localhost` a IPv6 (`[::1]`), pero uvicorn escucha solo en IPv4 y la conexión se rechaza.
- Si la app no está corriendo, la URL falla con error 502 y el log de `cloudflared` muestra `Unable to reach the origin service`.
- La URL cambia en cada ejecución y solo funciona mientras la PC, la app y el túnel sigan activos. No conviene dejar que la PC se suspenda.
- Cualquiera con el link puede usar la app (no hay autenticación) y cada petición consume CPU de la PC anfitriona. Cerrar el túnel con `Ctrl+C` al terminar.
- Antes de presentar, pedir una pista de prueba: la primera consulta a `llama3.2:3b` es lenta y, si pasa de 25 s, el tutor responde con el mensaje determinista (`fuente: "solver"` en vez de `"solver+llm"`).

## Dataset de casos

El dataset son 10 casos (8 de 6×6 y 2 de 8×8); su descripción completa está en [`dataset_casos_murdoku.md`](dataset_casos_murdoku.md) y su fuente única en `casos/casos.json`. Las imágenes se nombran `caso_01.png` … `caso_10.png` y viven solo en `static/casos/`.

**Agregar un caso nuevo:** copiar la imagen como `static/casos/caso_NN.png`. Si el caso ya está en `casos.json`, su tarjeta se habilita sola, sin tocar el código. Después:
```bash
python scripts/validar_dataset.py   # comprueba que el caso tenga solución única
python scripts/evaluar.py caso_NN   # mide la visión contra la verdad terreno
```

## Modo tutor
En la web, elige una persona de la paleta y toca una casilla para ubicarla (toca de nuevo para quitarla).
- **Validar:** el solver comprueba tus ubicaciones contra todas las pistas. Si hay contradicción, indica qué testimonio la causa; si no, informa cuántas llevas bien. Al ubicar a las 6 sin contradicciones, el caso queda resuelto.
- **Pedir pista:** elige a la persona con menos casillas posibles y entrega ayuda progresiva: (1) qué testimonio mirar, (2) cuánto se reduce su posición y qué tipos de dato usar, (3) las casillas que quedan. Cada pulsación sube de nivel hasta que cambies el tablero.
- **Resolver caso:** muestra la solución completa del solver.

La decisión de la pista es determinista (CP-SAT). Opcionalmente, Ollama puede reformular el texto; si añade algún número, nombre o razonamiento nuevo, se descarta y se muestra el mensaje del solver.

## Evaluación y pruebas
```bash
pytest                         # parser, solver, tutor y validez del dataset
python scripts/validar_dataset.py
python scripts/evaluar.py      # escribe resultados/evaluacion.md
```
`evaluar.py` mide por caso: estimación de N, % de celdas con la sala correcta, precisión/recall de muebles, nombres leídos por OCR, pistas extraídas vs. esperadas, unicidad de la solución, culpable correcto y tiempos (visión y CP-SAT). Ver [`resultados/evaluacion.md`](resultados/evaluacion.md).

**Definición de precisión y recall de muebles.** Una detección es un acierto (TP) si coincide el tipo y la celda con el catálogo: `precisión = TP / detectados` y `recall = TP / reales`.

### Qué reconoce la visión en cada casilla
```bash
python scripts/inspeccionar_vision.py --etiqueta base      # todos los casos disponibles
python scripts/inspeccionar_vision.py caso_10 --etiqueta base
```
Guarda en `resultados/vision/<etiqueta>/<caso>/`: `tablero_anotado.png`, `celdas.csv` (una fila por casilla con sala, plantilla ganadora, similitud coseno, tipo detectado, tipo real y estado) y `deteccion.json`; más un `resumen.md` con los aciertos, sobrantes, faltantes y tipos incorrectos de todos los casos. Si una casilla falla, compara primero la imagen con `casos/casos.json`: el error puede estar en el dibujo y no en la visión.

### Figuras para el informe y comparación antes/después
```bash
python scripts/evaluar.py --etiqueta base            # guarda resultados/evaluacion_base.json
# ... se corrigen cosas ...
python scripts/evaluar.py --etiqueta mejorado        # otra corrida
python scripts/graficar_evaluacion.py base mejorado  # figuras + tabla de cambios
```
Las figuras (PNG a 300 dpi y PDF vectorial para LaTeX) quedan en `resultados/figuras/`: mapa de calor de métricas por caso, tiempos de visión y solver, y la comparación antes → después (`fig_comparacion_*`, más `comparacion_*.md` con los promedios y su variación).

## Pendientes conocidos
- Faltan las imágenes de los casos 04 al 10 (sus planteamientos ya están en el catálogo y validados).
- Las imágenes de los casos 02 y 03 deben actualizarse con una frase adicional en una tarjeta cada una (ver `dataset_casos_murdoku.md`); sin ella, esos acertijos admiten más de una solución.
- El dataset de robustez pedido por el enunciado necesita variantes de cada puzzle con otra iluminación, ángulo ligero e impresión; hoy solo hay versiones digitales y no hay corrección de perspectiva.
- Informe técnico (LaTeX) y video demostrativo.

#Informe en Overleaf

https://www.overleaf.com/read/fytxtscfnqmn#c8f6d9

## Referencias
- Murdoku: https://nl.wikipedia.org/wiki/Murdoku
- Google OR-Tools CP-SAT: https://developers.google.com/optimization
- MobileNetV3: Howard et al., *Searching for MobileNetV3*, ICCV 2019.
- Tesseract OCR: https://github.com/tesseract-ocr/tesseract
- Ollama: https://ollama.com
