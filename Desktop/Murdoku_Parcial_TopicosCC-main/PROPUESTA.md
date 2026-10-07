# Propuesta Técnica y Plan de Proyecto: Tutor y Solver de Murdoku

## 1. Marco Académico y Objetivos del Proyecto
- **Curso:** CC58 - Tópicos en Ciencia de la Computación  
- **Proyecto:** Trabajo 1 - Constraint Programming (Integración End-to-End de Visión Computacional y CP)  
- **Integrantes:** 2 a 3 estudiantes  
- **Fecha de Entrega:** Semana 7  

**Objetivo General:**  
Desarrollar un sistema automatizado capaz de recibir la imagen de un acertijo lógico, extraer su topología y estado inicial mediante Visión Computacional, modelarlo formalmente como un Problema de Satisfacción de Restricciones (CSP) con un solver de CP (Google OR-Tools), y proyectar la solución de forma interactiva y visual.

---

## 2. Acertijo Seleccionado: Murdoku Adaptado ("The Coffee Shop")
- **Estructura del Tablero:** Grilla bidimensional de 5 × 5 celdas subdividida en habitaciones o zonas (Bar, Restroom, Main Area).  
- **Entidades:** 5 sospechosos (Abigail, Barbara, Chloe, Dwayne, Everett) y 1 víctima (Vander).  
- **Mobiliario / Obstáculos:** Sillas, mesas, caja registradora, barra y plantas.  

**Reglas Básicas de Deducción:**
- Unicidad espacial: Ningún sospechoso comparte fila ni columna con otro (estilo Sudoku / N-Reinas).  
- Celdas bloqueadas: Las celdas con mobiliario no pueden ser ocupadas.  
- Ubicación de la víctima: Ocupa la última celda libre disponible.  
- Identificación del asesino: Es el único sospechoso presente en la misma habitación que la víctima.  
- Pistas relacionales: Restricciones de adyacencia espacial (norte, junto a, exclusión de muebles o columnas fijas).  

---

## 3. Arquitectura del Sistema (Pipeline End-to-End)
**Flujo:** Imagen → Representación → Solver → Solución  

- **Fase 1: Visión Computacional**
  - Corrección de perspectiva  
  - Máscaras HSV para habitaciones  
  - Segmentación de celdas (5x5)  
  - Template Matching / OCR (muebles)  

- **Fase 2: Constraint Programming (CP)**
  - Variables de coordenadas (X, Y, Z)  
  - Restricción global *AllDifferent*  
  - Restricciones relacionales  
  - Restricciones reificadas  

- **Fase 3: UI & Tutor Interactivo**
  - Frontend en Streamlit  
  - Grilla interactiva de deducción  
  - Botón "Pedir Pista" (LLM local)  
  - Botón "Resolver" (Overlay visual)  

---

## 4. Modelado Matemático Formal (CP-SAT / OR-Tools)
- **Variables de Decisión:**  
  - \(X_i \in \{0,1,2,3,4\}\): fila  
  - \(Y_i \in \{0,1,2,3,4\}\): columna  
  - \(Z_i \in \{1,2,3\}\): habitación  

- **Restricciones Globales:**  
  - AllDifferent en filas y columnas  

- **Restricciones Relacionales:**  
  - Chloe en columna 2  
  - Dwayne al norte de Chloe en Main Area  
  - Abigail junto a planta (distancia Manhattan = 1)  
  - Exclusión de muebles (no silla, no mesa adyacente)  

- **Restricciones Reificadas:**  
  - Variables booleanas para validar reglas y dar retroalimentación en modo tutor.  

---

## 5. Pipeline de Visión Computacional
- Preprocesamiento: escala de grises, filtrado Gaussiano, binarización adaptativa  
- Corrección de perspectiva (Four-Point Warp)  
- Segmentación HSV para clasificar habitaciones  
- División en 25 celdas  
- Template Matching para muebles  
- Exportación a JSON con coordenadas y pistas  

---

## 6. Agente LLM y Frontend Interactivo
- **Interfaz (Streamlit):**  
  - Sidebar con reglas y selector de casos  
  - Panel principal con grilla interactiva  
  - Botón "Validar / Pedir Pista"  
  - Botón "Resolver Caso"  

- **Agente Local (Ollama + Gemma/Llama):**  
  - Recibe estado resuelto y estado del usuario  
  - Genera pistas narrativas cortas sin dar la respuesta directa  

---

## 7. Requerimientos Iniciales del Entorno
**requirements.txt:**
