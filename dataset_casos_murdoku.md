# DATASET OFICIAL MURDOKU: 10 CASOS LÓGICOS (EXCEL READY)

> **Instrucciones para Excel / Google Sheets:** selecciona cualquier tabla, cópiala (`Ctrl + C`) y pégala (`Ctrl + V`) en una hoja de cálculo; se distribuirá en celdas individuales.
>
> Documento **generado** por `scripts/generar_dataset_md.py` desde `casos/casos.json`: no editar a mano (edita el JSON y vuelve a generarlo). Cada caso tiene **solución única** verificada con `python scripts/validar_dataset.py`.
>
> **Convenciones:** filas y columnas desde 0; "al lado de" = adyacencia ortogonal (arriba, abajo, izquierda o derecha); "al norte/sur/este/oeste de X" = estrictamente arriba/abajo/derecha/izquierda de X, no necesariamente contiguo; las sillas se pueden ocupar, las mesas, plantas y laptops no.
>
> **Imágenes:** se guardan como `static/casos/caso_NN.png` (por ejemplo `caso_04.png`). En cuanto exista el archivo, la tarjeta del caso se habilita en la web.

---

## 1. TABLA RESUMEN GENERAL DEL DATASET

| ID | Archivo de imagen | Nombre del Caso | Dimensión | Habitaciones | Víctima | Culpable Deducido | Imagen |
| :---: | :--- | :--- | :---: | :--- | :--- | :--- | :---: |
| **01** | `caso_01.png` | La Tienda | $6 \times 6$ | Bar, Baño, Sala Principal | Henry | **Barbara** | lista |
| **02** | `caso_02.png` | La Oficina | $6 \times 6$ | Gerencia, Archivo, Open Office | David | **Carlos** | lista, actualizar tarjeta |
| **03** | `caso_03.png` | La Biblioteca Colonial | $6 \times 6$ | Sala de Lectura, Depósito, Vestíbulo | Arthur | **Beatriz** | lista, actualizar tarjeta |
| **04** | `caso_04.png` | El Centro Tecnológico | $6 \times 6$ | Servidores, Laboratorio, Recepción | Walter | **Ramiro** | pendiente |
| **05** | `caso_05.png` | La Galería Minimalista | $6 \times 6$ | Bóveda, Taller, Galería Central | Vincent | **Sofía** | pendiente |
| **06** | `caso_06.png` | El Cafetín Universitario | $6 \times 6$ | Terraza, Cocina, Comedor Central | Hector | **Gabriel** | pendiente |
| **07** | `caso_07.png` | La Agencia de Diseño | $6 \times 6$ | Creativa, Pasillo Central, Reuniones | Galileo | **Valeria** | pendiente |
| **08** | `caso_08.png` | El Coworking Urbano | $6 \times 6$ | Cabina Privada, Comedor, Zona Lounge | Mario | **Lucas** | pendiente |
| **09** | `caso_09.png` | La Mansión de Cristal | $8 \times 8$ | Invernadero, Estudio, Salón Principal | Jack | **Irene** | pendiente |
| **10** | `caso_10.png` | La Sala de Prensa | $8 \times 8$ | Cabina de Grabación, Redacción, Auditorio | Howard | **Marcos** | pendiente |

---

## CASO 01: LA TIENDA ($6 \times 6$)

* **Archivo de imagen:** `static/casos/caso_01.png`
* **Dificultad:** Intermedio
* **Revisión:** Sin cambios: la solución ya era única.

### A. Matriz del Tablero (Plano de Habitaciones y Muebles)

* **Habitaciones:** H1 = Bar | H2 = Baño | H3 = Sala Principal

| Fila \ Col | Columna 0 | Columna 1 | Columna 2 | Columna 3 | Columna 4 | Columna 5 |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Fila 0** | [Bar] Libre | [Bar] Libre | [Bar] Libre | [Bar] **Mesa** | [Baño] Libre | [Baño] **Silla** |
| **Fila 1** | [Bar] Libre | [Bar] Libre | [Bar] Libre | [Bar] **Mesa** | [Baño] Libre | [Baño] Libre |
| **Fila 2** | [Bar] Libre | [Bar] **Laptop** | [Bar] **Mesa** | [Bar] **Mesa** | [Sala Principal] **Silla** | [Sala Principal] **Mesa** |
| **Fila 3** | [Sala Principal] Libre | [Sala Principal] **Silla** | [Sala Principal] **Mesa** | [Sala Principal] **Mesa** | [Sala Principal] **Silla** | [Sala Principal] Libre |
| **Fila 4** | [Sala Principal] Libre | [Sala Principal] Libre | [Sala Principal] **Silla** | [Sala Principal] **Silla** | [Sala Principal] **Mesa** | [Sala Principal] Libre |
| **Fila 5** | [Sala Principal] **Silla** | [Sala Principal] Libre | [Sala Principal] **Planta** | [Sala Principal] Libre | [Sala Principal] **Silla** | [Sala Principal] **Planta** |

### B. Tarjetas de Personajes (Distribución Espacial $2 \times 3$)

| Fila de Tarjetas | Columna 1 (Izquierda) | Columna 2 (Centro) | Columna 3 (Derecha) |
| :--- | :--- | :--- | :--- |
| **Fila 1 (Superior)** | **JUANA**<br>Ella estaba al lado de una planta. Ella no estaba sentada en una silla. | **BARBARA**<br>Ella estaba al lado de una computadora. | **ANA**<br>Ella estaba en la segunda columna. |
| **Fila 2 (Inferior)** | **PAULO**<br>Él estaba al norte de Ana. Él estaba en la SALA PRINCIPAL. | **CRISTIAN**<br>Él estaba sentado en una silla. Él no estaba al lado de una mesa. | **HENRY [VÍCTIMA]**<br>La Víctima. Él estaba en el último área restante, solo con el asesino. |

#### Lista Detallada de Personajes (Para Registros en Excel)

| # Tarjeta | Posición Gráfica | Personaje | Rol | Testimonio / Pista Exacta |
| :---: | :---: | :--- | :---: | :--- |
| 1 | Fila 1, Col 1 | JUANA | Sospechoso | Ella estaba al lado de una planta. Ella no estaba sentada en una silla. |
| 2 | Fila 1, Col 2 | BARBARA | Culpable | Ella estaba al lado de una computadora. |
| 3 | Fila 1, Col 3 | ANA | Sospechoso | Ella estaba en la segunda columna. |
| 4 | Fila 2, Col 1 | PAULO | Sospechoso | Él estaba al norte de Ana. Él estaba en la SALA PRINCIPAL. |
| 5 | Fila 2, Col 2 | CRISTIAN | Sospechoso | Él estaba sentado en una silla. Él no estaba al lado de una mesa. |
| 6 | Fila 2, Col 3 | HENRY | VÍCTIMA | La Víctima. Él estaba en el último área restante, solo con el asesino. |

### C. Solución Ground Truth (Posiciones Verificadas)

* **Juana:** Fila 5, Columna 3 (Habitación: Sala Principal)
* **Barbara [CULPABLE]:** Fila 2, Columna 0 (Habitación: Bar)
* **Ana:** Fila 4, Columna 1 (Habitación: Sala Principal)
* **Paulo:** Fila 3, Columna 4 (Habitación: Sala Principal)
* **Cristian:** Fila 0, Columna 5 (Habitación: Baño)
* **Henry [VÍCTIMA]:** Fila 1, Columna 2 (Habitación: Bar)

---

## CASO 02: LA OFICINA ($6 \times 6$)

* **Archivo de imagen:** `static/casos/caso_02.png`
* **Dificultad:** Principiante
* **Revisión:** La solución original tenía filas repetidas y el planteamiento admitía 3 soluciones. Se agrega una frase a Felipe para que sea única (la imagen debe actualizarse).
* **ACTUALIZAR LA IMAGEN:** la tarjeta de FELIPE debe decir «Él estaba al lado de una planta. Él no estaba sentado en una silla. Él estaba en la cuarta fila.» (hoy dice «Él estaba al lado de una planta. Él no estaba sentado en una silla.»).

### A. Matriz del Tablero (Plano de Habitaciones y Muebles)

* **Habitaciones:** H1 = Gerencia | H2 = Archivo | H3 = Open Office

| Fila \ Col | Columna 0 | Columna 1 | Columna 2 | Columna 3 | Columna 4 | Columna 5 |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Fila 0** | [Gerencia] Libre | [Gerencia] Libre | [Gerencia] **Laptop** | [Archivo] Libre | [Archivo] **Mesa** | [Archivo] Libre |
| **Fila 1** | [Gerencia] Libre | [Gerencia] **Silla** | [Gerencia] Libre | [Archivo] Libre | [Archivo] Libre | [Archivo] **Silla** |
| **Fila 2** | [Gerencia] Libre | [Gerencia] Libre | [Gerencia] Libre | [Archivo] **Mesa** | [Archivo] Libre | [Archivo] Libre |
| **Fila 3** | [Open Office] Libre | [Open Office] **Mesa** | [Open Office] Libre | [Open Office] Libre | [Open Office] **Mesa** | [Open Office] Libre |
| **Fila 4** | [Open Office] **Planta** | [Open Office] Libre | [Open Office] Libre | [Open Office] Libre | [Open Office] **Silla** | [Open Office] Libre |
| **Fila 5** | [Open Office] Libre | [Open Office] Libre | [Open Office] **Silla** | [Open Office] Libre | [Open Office] Libre | [Open Office] **Planta** |

### B. Tarjetas de Personajes (Distribución Espacial $2 \times 3$)

| Fila de Tarjetas | Columna 1 (Izquierda) | Columna 2 (Centro) | Columna 3 (Derecha) |
| :--- | :--- | :--- | :--- |
| **Fila 1 (Superior)** | **FELIPE**<br>Él estaba al lado de una planta. Él no estaba sentado en una silla. Él estaba en la cuarta fila. | **CARLOS**<br>Él estaba al lado de una laptop. Él estaba en la primera fila. | **DIANA**<br>Ella estaba sentada en una silla en la Gerencia. |
| **Fila 2 (Inferior)** | **ELENA**<br>Ella estaba en la tercera columna, en el Open Office. | **GABRIEL**<br>Él estaba al sur de Carlos. Él estaba en la última columna. | **DAVID [VÍCTIMA]**<br>La Víctima. Hallado en el Archivo, solo con el asesino. |

#### Lista Detallada de Personajes (Para Registros en Excel)

| # Tarjeta | Posición Gráfica | Personaje | Rol | Testimonio / Pista Exacta |
| :---: | :---: | :--- | :---: | :--- |
| 1 | Fila 1, Col 1 | FELIPE | Sospechoso | Él estaba al lado de una planta. Él no estaba sentado en una silla. Él estaba en la cuarta fila. |
| 2 | Fila 1, Col 2 | CARLOS | Culpable | Él estaba al lado de una laptop. Él estaba en la primera fila. |
| 3 | Fila 1, Col 3 | DIANA | Sospechoso | Ella estaba sentada en una silla en la Gerencia. |
| 4 | Fila 2, Col 1 | ELENA | Sospechoso | Ella estaba en la tercera columna, en el Open Office. |
| 5 | Fila 2, Col 2 | GABRIEL | Sospechoso | Él estaba al sur de Carlos. Él estaba en la última columna. |
| 6 | Fila 2, Col 3 | DAVID | VÍCTIMA | La Víctima. Hallado en el Archivo, solo con el asesino. |

### C. Solución Ground Truth (Posiciones Verificadas)

* **Felipe:** Fila 3, Columna 0 (Habitación: Open Office)
* **Carlos [CULPABLE]:** Fila 0, Columna 3 (Habitación: Archivo)
* **Diana:** Fila 1, Columna 1 (Habitación: Gerencia)
* **Elena:** Fila 5, Columna 2 (Habitación: Open Office)
* **Gabriel:** Fila 4, Columna 5 (Habitación: Open Office)
* **David [VÍCTIMA]:** Fila 2, Columna 4 (Habitación: Archivo)

---

## CASO 03: LA BIBLIOTECA COLONIAL ($6 \times 6$)

* **Archivo de imagen:** `static/casos/caso_03.png`
* **Dificultad:** Principiante
* **Revisión:** La asesina original no estaba al lado de la laptop y el planteamiento admitía 2 soluciones. Se agrega una frase a Daniel para que sea única (la imagen debe actualizarse).
* **ACTUALIZAR LA IMAGEN:** la tarjeta de DANIEL debe decir «Él estaba en la tercera columna, en el Vestíbulo. Él estaba en la última fila.» (hoy dice «Él estaba en la tercera columna, en el Vestíbulo.»).

### A. Matriz del Tablero (Plano de Habitaciones y Muebles)

* **Habitaciones:** H1 = Sala de Lectura | H2 = Depósito | H3 = Vestíbulo

| Fila \ Col | Columna 0 | Columna 1 | Columna 2 | Columna 3 | Columna 4 | Columna 5 |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Fila 0** | [Sala de Lectura] Libre | [Sala de Lectura] **Mesa** | [Sala de Lectura] Libre | [Depósito] Libre | [Depósito] **Silla** | [Depósito] Libre |
| **Fila 1** | [Sala de Lectura] Libre | [Sala de Lectura] Libre | [Sala de Lectura] **Laptop** | [Depósito] Libre | [Depósito] **Mesa** | [Depósito] Libre |
| **Fila 2** | [Sala de Lectura] Libre | [Sala de Lectura] Libre | [Sala de Lectura] Libre | [Depósito] Libre | [Depósito] Libre | [Depósito] **Planta** |
| **Fila 3** | [Vestíbulo] Libre | [Vestíbulo] Libre | [Vestíbulo] **Silla** | [Vestíbulo] Libre | [Vestíbulo] Libre | [Vestíbulo] Libre |
| **Fila 4** | [Vestíbulo] **Planta** | [Vestíbulo] Libre | [Vestíbulo] Libre | [Vestíbulo] **Mesa** | [Vestíbulo] Libre | [Vestíbulo] **Silla** |
| **Fila 5** | [Vestíbulo] Libre | [Vestíbulo] Libre | [Vestíbulo] Libre | [Vestíbulo] Libre | [Vestíbulo] **Mesa** | [Vestíbulo] Libre |

### B. Tarjetas de Personajes (Distribución Espacial $2 \times 3$)

| Fila de Tarjetas | Columna 1 (Izquierda) | Columna 2 (Centro) | Columna 3 (Derecha) |
| :--- | :--- | :--- | :--- |
| **Fila 1 (Superior)** | **BEATRIZ**<br>Ella estaba en la Sala de Lectura, al lado de una laptop. | **CAMILO**<br>Él estaba sentado en una silla en el Depósito. | **DANIEL**<br>Él estaba en la tercera columna, en el Vestíbulo. Él estaba en la última fila. |
| **Fila 2 (Inferior)** | **ESTHER**<br>Ella estaba en la última columna, sentada en una silla. | **FABIAN**<br>Él estaba al sur de Camilo. Él no estaba en una silla. | **ARTHUR [VÍCTIMA]**<br>La Víctima. Quedó atrapado en la Sala de Lectura con el asesino. |

#### Lista Detallada de Personajes (Para Registros en Excel)

| # Tarjeta | Posición Gráfica | Personaje | Rol | Testimonio / Pista Exacta |
| :---: | :---: | :--- | :---: | :--- |
| 1 | Fila 1, Col 1 | BEATRIZ | Culpable | Ella estaba en la Sala de Lectura, al lado de una laptop. |
| 2 | Fila 1, Col 2 | CAMILO | Sospechoso | Él estaba sentado en una silla en el Depósito. |
| 3 | Fila 1, Col 3 | DANIEL | Sospechoso | Él estaba en la tercera columna, en el Vestíbulo. Él estaba en la última fila. |
| 4 | Fila 2, Col 1 | ESTHER | Sospechoso | Ella estaba en la última columna, sentada en una silla. |
| 5 | Fila 2, Col 2 | FABIAN | Sospechoso | Él estaba al sur de Camilo. Él no estaba en una silla. |
| 6 | Fila 2, Col 3 | ARTHUR | VÍCTIMA | La Víctima. Quedó atrapado en la Sala de Lectura con el asesino. |

### C. Solución Ground Truth (Posiciones Verificadas)

* **Beatriz [CULPABLE]:** Fila 1, Columna 1 (Habitación: Sala de Lectura)
* **Camilo:** Fila 0, Columna 4 (Habitación: Depósito)
* **Daniel:** Fila 5, Columna 2 (Habitación: Vestíbulo)
* **Esther:** Fila 4, Columna 5 (Habitación: Vestíbulo)
* **Fabian:** Fila 3, Columna 3 (Habitación: Vestíbulo)
* **Arthur [VÍCTIMA]:** Fila 2, Columna 0 (Habitación: Sala de Lectura)

---

## CASO 04: EL CENTRO TECNOLÓGICO ($6 \times 6$)

* **Archivo de imagen:** `static/casos/caso_04.png`
* **Dificultad:** Intermedio
* **Revisión:** Las pistas originales eran contradictorias (Nuria no podía estar al lado de la laptop en Servidores). Se reemplaza el testimonio de Nuria.

### A. Matriz del Tablero (Plano de Habitaciones y Muebles)

* **Habitaciones:** H1 = Servidores | H2 = Laboratorio | H3 = Recepción

| Fila \ Col | Columna 0 | Columna 1 | Columna 2 | Columna 3 | Columna 4 | Columna 5 |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Fila 0** | [Servidores] Libre | [Servidores] **Mesa** | [Servidores] Libre | [Servidores] Libre | [Servidores] **Mesa** | [Servidores] Libre |
| **Fila 1** | [Servidores] **Laptop** | [Servidores] Libre | [Servidores] Libre | [Servidores] **Planta** | [Servidores] Libre | [Servidores] Libre |
| **Fila 2** | [Laboratorio] Libre | [Laboratorio] Libre | [Laboratorio] **Mesa** | [Laboratorio] Libre | [Laboratorio] **Silla** | [Laboratorio] Libre |
| **Fila 3** | [Laboratorio] Libre | [Laboratorio] **Silla** | [Laboratorio] Libre | [Laboratorio] Libre | [Laboratorio] Libre | [Laboratorio] **Mesa** |
| **Fila 4** | [Recepción] Libre | [Recepción] Libre | [Recepción] Libre | [Recepción] **Mesa** | [Recepción] Libre | [Recepción] **Silla** |
| **Fila 5** | [Recepción] **Planta** | [Recepción] Libre | [Recepción] **Silla** | [Recepción] Libre | [Recepción] Libre | [Recepción] Libre |

### B. Tarjetas de Personajes (Distribución Espacial $2 \times 3$)

| Fila de Tarjetas | Columna 1 (Izquierda) | Columna 2 (Centro) | Columna 3 (Derecha) |
| :--- | :--- | :--- | :--- |
| **Fila 1 (Superior)** | **NURIA**<br>Ella estaba al lado de una silla. | **MATEO**<br>Él estaba en la segunda columna, en el Laboratorio. | **OSCAR**<br>Él estaba sentado en una silla, en la quinta columna. |
| **Fila 2 (Inferior)** | **PATRICIA**<br>Ella estaba al oeste de Mateo. Ella estaba en la Recepción. | **RAMIRO**<br>Él estaba en la cuarta columna, al lado de una mesa. | **WALTER [VÍCTIMA]**<br>La Víctima. Encontrado en Servidores, solo con el agresor. |

#### Lista Detallada de Personajes (Para Registros en Excel)

| # Tarjeta | Posición Gráfica | Personaje | Rol | Testimonio / Pista Exacta |
| :---: | :---: | :--- | :---: | :--- |
| 1 | Fila 1, Col 1 | NURIA | Sospechoso | Ella estaba al lado de una silla. |
| 2 | Fila 1, Col 2 | MATEO | Sospechoso | Él estaba en la segunda columna, en el Laboratorio. |
| 3 | Fila 1, Col 3 | OSCAR | Sospechoso | Él estaba sentado en una silla, en la quinta columna. |
| 4 | Fila 2, Col 1 | PATRICIA | Sospechoso | Ella estaba al oeste de Mateo. Ella estaba en la Recepción. |
| 5 | Fila 2, Col 2 | RAMIRO | Culpable | Él estaba en la cuarta columna, al lado de una mesa. |
| 6 | Fila 2, Col 3 | WALTER | VÍCTIMA | La Víctima. Encontrado en Servidores, solo con el agresor. |

### C. Solución Ground Truth (Posiciones Verificadas)

* **Nuria:** Fila 5, Columna 5 (Habitación: Recepción)
* **Mateo:** Fila 3, Columna 1 (Habitación: Laboratorio)
* **Oscar:** Fila 2, Columna 4 (Habitación: Laboratorio)
* **Patricia:** Fila 4, Columna 0 (Habitación: Recepción)
* **Ramiro [CULPABLE]:** Fila 0, Columna 3 (Habitación: Servidores)
* **Walter [VÍCTIMA]:** Fila 1, Columna 2 (Habitación: Servidores)

---

## CASO 05: LA GALERÍA MINIMALISTA ($6 \times 6$)

* **Archivo de imagen:** `static/casos/caso_05.png`
* **Dificultad:** Intermedio
* **Revisión:** Las pistas originales eran contradictorias. Se reemplazan los testimonios de Ursula y Ximena.

### A. Matriz del Tablero (Plano de Habitaciones y Muebles)

* **Habitaciones:** H1 = Bóveda | H2 = Taller | H3 = Galería Central

| Fila \ Col | Columna 0 | Columna 1 | Columna 2 | Columna 3 | Columna 4 | Columna 5 |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Fila 0** | [Bóveda] Libre | [Bóveda] **Mesa** | [Galería Central] Libre | [Galería Central] **Planta** | [Taller] Libre | [Taller] Libre |
| **Fila 1** | [Bóveda] **Laptop** | [Bóveda] Libre | [Galería Central] Libre | [Galería Central] Libre | [Taller] **Mesa** | [Taller] **Silla** |
| **Fila 2** | [Bóveda] Libre | [Bóveda] Libre | [Galería Central] **Silla** | [Galería Central] Libre | [Taller] Libre | [Taller] Libre |
| **Fila 3** | [Galería Central] Libre | [Galería Central] Libre | [Galería Central] **Mesa** | [Galería Central] **Mesa** | [Galería Central] Libre | [Galería Central] Libre |
| **Fila 4** | [Galería Central] Libre | [Galería Central] **Silla** | [Galería Central] Libre | [Galería Central] Libre | [Galería Central] **Silla** | [Galería Central] Libre |
| **Fila 5** | [Galería Central] Libre | [Galería Central] Libre | [Galería Central] **Planta** | [Galería Central] Libre | [Galería Central] Libre | [Galería Central] Libre |

### B. Tarjetas de Personajes (Distribución Espacial $2 \times 3$)

| Fila de Tarjetas | Columna 1 (Izquierda) | Columna 2 (Centro) | Columna 3 (Derecha) |
| :--- | :--- | :--- | :--- |
| **Fila 1 (Superior)** | **SOFÍA**<br>Ella estaba en la Bóveda, al lado de una laptop. | **TOMAS**<br>Él estaba sentado en una silla en el Taller. | **URSULA**<br>Ella estaba en la cuarta columna. |
| **Fila 2 (Inferior)** | **VICTOR**<br>Él estaba al norte de Ursula, en la tercera columna. | **XIMENA**<br>Ella no estaba sentada en una silla. | **VINCENT [VÍCTIMA]**<br>La Víctima. Asesinado en la Bóveda de obras maestras. |

#### Lista Detallada de Personajes (Para Registros en Excel)

| # Tarjeta | Posición Gráfica | Personaje | Rol | Testimonio / Pista Exacta |
| :---: | :---: | :--- | :---: | :--- |
| 1 | Fila 1, Col 1 | SOFÍA | Culpable | Ella estaba en la Bóveda, al lado de una laptop. |
| 2 | Fila 1, Col 2 | TOMAS | Sospechoso | Él estaba sentado en una silla en el Taller. |
| 3 | Fila 1, Col 3 | URSULA | Sospechoso | Ella estaba en la cuarta columna. |
| 4 | Fila 2, Col 1 | VICTOR | Sospechoso | Él estaba al norte de Ursula, en la tercera columna. |
| 5 | Fila 2, Col 2 | XIMENA | Sospechoso | Ella no estaba sentada en una silla. |
| 6 | Fila 2, Col 3 | VINCENT | VÍCTIMA | La Víctima. Asesinado en la Bóveda de obras maestras. |

### C. Solución Ground Truth (Posiciones Verificadas)

* **Sofía [CULPABLE]:** Fila 0, Columna 0 (Habitación: Bóveda)
* **Tomas:** Fila 1, Columna 5 (Habitación: Taller)
* **Ursula:** Fila 5, Columna 3 (Habitación: Galería Central)
* **Victor:** Fila 4, Columna 2 (Habitación: Galería Central)
* **Ximena:** Fila 3, Columna 4 (Habitación: Galería Central)
* **Vincent [VÍCTIMA]:** Fila 2, Columna 1 (Habitación: Bóveda)

---

## CASO 06: EL CAFETÍN UNIVERSITARIO ($6 \times 6$)

* **Archivo de imagen:** `static/casos/caso_06.png`
* **Dificultad:** Intermedio
* **Revisión:** La solución original repetía columna y el planteamiento admitía 2 soluciones. Se agrega una frase a Julia.

### A. Matriz del Tablero (Plano de Habitaciones y Muebles)

* **Habitaciones:** H1 = Terraza | H2 = Cocina | H3 = Comedor Central

| Fila \ Col | Columna 0 | Columna 1 | Columna 2 | Columna 3 | Columna 4 | Columna 5 |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Fila 0** | [Terraza] Libre | [Terraza] **Planta** | [Terraza] Libre | [Terraza] **Mesa** | [Terraza] **Silla** | [Terraza] Libre |
| **Fila 1** | [Terraza] Libre | [Terraza] Libre | [Terraza] **Silla** | [Terraza] Libre | [Terraza] Libre | [Terraza] **Planta** |
| **Fila 2** | [Cocina] **Mesa** | [Cocina] Libre | [Cocina] Libre | [Cocina] **Mesa** | [Cocina] Libre | [Cocina] Libre |
| **Fila 3** | [Cocina] Libre | [Cocina] **Laptop** | [Cocina] Libre | [Cocina] Libre | [Cocina] **Silla** | [Cocina] Libre |
| **Fila 4** | [Comedor Central] Libre | [Comedor Central] **Mesa** | [Comedor Central] **Mesa** | [Comedor Central] Libre | [Comedor Central] Libre | [Comedor Central] **Silla** |
| **Fila 5** | [Comedor Central] **Silla** | [Comedor Central] Libre | [Comedor Central] Libre | [Comedor Central] Libre | [Comedor Central] Libre | [Comedor Central] **Planta** |

### B. Tarjetas de Personajes (Distribución Espacial $2 \times 3$)

| Fila de Tarjetas | Columna 1 (Izquierda) | Columna 2 (Centro) | Columna 3 (Derecha) |
| :--- | :--- | :--- | :--- |
| **Fila 1 (Superior)** | **GABRIEL**<br>Él estaba en la Terraza, sentado en una silla. | **HELENA**<br>Ella estaba al lado de una laptop en la Cocina. | **IGNACIO**<br>Él estaba en la quinta columna, en la Cocina. |
| **Fila 2 (Inferior)** | **JULIA**<br>Ella estaba en la primera columna, en el Comedor Central. Ella estaba en la última fila. | **KLAUS**<br>Él estaba al este de Julia, en el Comedor Central. | **HECTOR [VÍCTIMA]**<br>La Víctima. Asfixiado en la Terraza junto al culpable. |

#### Lista Detallada de Personajes (Para Registros en Excel)

| # Tarjeta | Posición Gráfica | Personaje | Rol | Testimonio / Pista Exacta |
| :---: | :---: | :--- | :---: | :--- |
| 1 | Fila 1, Col 1 | GABRIEL | Culpable | Él estaba en la Terraza, sentado en una silla. |
| 2 | Fila 1, Col 2 | HELENA | Sospechoso | Ella estaba al lado de una laptop en la Cocina. |
| 3 | Fila 1, Col 3 | IGNACIO | Sospechoso | Él estaba en la quinta columna, en la Cocina. |
| 4 | Fila 2, Col 1 | JULIA | Sospechoso | Ella estaba en la primera columna, en el Comedor Central. Ella estaba en la última fila. |
| 5 | Fila 2, Col 2 | KLAUS | Sospechoso | Él estaba al este de Julia, en el Comedor Central. |
| 6 | Fila 2, Col 3 | HECTOR | VÍCTIMA | La Víctima. Asfixiado en la Terraza junto al culpable. |

### C. Solución Ground Truth (Posiciones Verificadas)

* **Gabriel [CULPABLE]:** Fila 1, Columna 2 (Habitación: Terraza)
* **Helena:** Fila 2, Columna 1 (Habitación: Cocina)
* **Ignacio:** Fila 3, Columna 4 (Habitación: Cocina)
* **Julia:** Fila 5, Columna 0 (Habitación: Comedor Central)
* **Klaus:** Fila 4, Columna 3 (Habitación: Comedor Central)
* **Hector [VÍCTIMA]:** Fila 0, Columna 5 (Habitación: Terraza)

---

## CASO 07: LA AGENCIA DE DISEÑO ($6 \times 6$)

* **Archivo de imagen:** `static/casos/caso_07.png`
* **Dificultad:** Avanzado
* **Revisión:** La solución original repetía columna y ubicaba a Elisa sobre una planta; admitía 2 soluciones. Se agrega una frase a Bruno.

### A. Matriz del Tablero (Plano de Habitaciones y Muebles)

* **Habitaciones:** H1 = Creativa | H2 = Pasillo Central | H3 = Reuniones

| Fila \ Col | Columna 0 | Columna 1 | Columna 2 | Columna 3 | Columna 4 | Columna 5 |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Fila 0** | [Creativa] Libre | [Creativa] **Laptop** | [Creativa] Libre | [Pasillo Central] Libre | [Pasillo Central] **Planta** | [Pasillo Central] Libre |
| **Fila 1** | [Creativa] **Mesa** | [Creativa] Libre | [Creativa] Libre | [Pasillo Central] Libre | [Pasillo Central] Libre | [Pasillo Central] **Silla** |
| **Fila 2** | [Creativa] Libre | [Creativa] **Silla** | [Creativa] Libre | [Pasillo Central] **Planta** | [Pasillo Central] Libre | [Pasillo Central] Libre |
| **Fila 3** | [Reuniones] Libre | [Reuniones] Libre | [Reuniones] **Mesa** | [Reuniones] **Mesa** | [Reuniones] Libre | [Reuniones] Libre |
| **Fila 4** | [Reuniones] **Silla** | [Reuniones] Libre | [Reuniones] Libre | [Reuniones] Libre | [Reuniones] **Laptop** | [Reuniones] Libre |
| **Fila 5** | [Reuniones] Libre | [Reuniones] Libre | [Reuniones] **Planta** | [Reuniones] Libre | [Reuniones] Libre | [Reuniones] **Silla** |

### B. Tarjetas de Personajes (Distribución Espacial $2 \times 3$)

| Fila de Tarjetas | Columna 1 (Izquierda) | Columna 2 (Centro) | Columna 3 (Derecha) |
| :--- | :--- | :--- | :--- |
| **Fila 1 (Superior)** | **VALERIA**<br>Ella estaba en la sala Creativa, sentada en una silla. | **BRUNO**<br>Él estaba en la última columna, en el Pasillo Central. Él estaba en la segunda fila. | **CELIA**<br>Ella estaba al lado de una laptop, en la cuarta fila. |
| **Fila 2 (Inferior)** | **DANTE**<br>Él estaba en la primera columna, en la sala de Reuniones. | **ELISA**<br>Ella estaba al este de Dante, al lado de una planta. | **GALILEO [VÍCTIMA]**<br>La Víctima. Atacado en la sala Creativa con su agresor. |

#### Lista Detallada de Personajes (Para Registros en Excel)

| # Tarjeta | Posición Gráfica | Personaje | Rol | Testimonio / Pista Exacta |
| :---: | :---: | :--- | :---: | :--- |
| 1 | Fila 1, Col 1 | VALERIA | Culpable | Ella estaba en la sala Creativa, sentada en una silla. |
| 2 | Fila 1, Col 2 | BRUNO | Sospechoso | Él estaba en la última columna, en el Pasillo Central. Él estaba en la segunda fila. |
| 3 | Fila 1, Col 3 | CELIA | Sospechoso | Ella estaba al lado de una laptop, en la cuarta fila. |
| 4 | Fila 2, Col 1 | DANTE | Sospechoso | Él estaba en la primera columna, en la sala de Reuniones. |
| 5 | Fila 2, Col 2 | ELISA | Sospechoso | Ella estaba al este de Dante, al lado de una planta. |
| 6 | Fila 2, Col 3 | GALILEO | VÍCTIMA | La Víctima. Atacado en la sala Creativa con su agresor. |

### C. Solución Ground Truth (Posiciones Verificadas)

* **Valeria [CULPABLE]:** Fila 2, Columna 1 (Habitación: Creativa)
* **Bruno:** Fila 1, Columna 5 (Habitación: Pasillo Central)
* **Celia:** Fila 3, Columna 4 (Habitación: Reuniones)
* **Dante:** Fila 4, Columna 0 (Habitación: Reuniones)
* **Elisa:** Fila 5, Columna 3 (Habitación: Reuniones)
* **Galileo [VÍCTIMA]:** Fila 0, Columna 2 (Habitación: Creativa)

---

## CASO 08: EL COWORKING URBANO ($6 \times 6$)

* **Archivo de imagen:** `static/casos/caso_08.png`
* **Dificultad:** Avanzado
* **Revisión:** Las pistas originales eran contradictorias. Se reemplazan los testimonios de Miriam y Nicolas.

### A. Matriz del Tablero (Plano de Habitaciones y Muebles)

* **Habitaciones:** H1 = Cabina Privada | H2 = Comedor | H3 = Zona Lounge

| Fila \ Col | Columna 0 | Columna 1 | Columna 2 | Columna 3 | Columna 4 | Columna 5 |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Fila 0** | [Cabina Privada] Libre | [Cabina Privada] **Laptop** | [Cabina Privada] Libre | [Comedor] Libre | [Comedor] **Mesa** | [Comedor] Libre |
| **Fila 1** | [Cabina Privada] **Silla** | [Cabina Privada] Libre | [Cabina Privada] Libre | [Comedor] **Silla** | [Comedor] Libre | [Comedor] **Planta** |
| **Fila 2** | [Zona Lounge] Libre | [Zona Lounge] **Mesa** | [Zona Lounge] Libre | [Zona Lounge] Libre | [Zona Lounge] **Silla** | [Zona Lounge] Libre |
| **Fila 3** | [Zona Lounge] Libre | [Zona Lounge] Libre | [Zona Lounge] **Planta** | [Zona Lounge] Libre | [Zona Lounge] Libre | [Zona Lounge] Libre |
| **Fila 4** | [Zona Lounge] **Planta** | [Zona Lounge] Libre | [Zona Lounge] Libre | [Zona Lounge] **Mesa** | [Zona Lounge] Libre | [Zona Lounge] **Silla** |
| **Fila 5** | [Zona Lounge] Libre | [Zona Lounge] **Silla** | [Zona Lounge] Libre | [Zona Lounge] Libre | [Zona Lounge] Libre | [Zona Lounge] Libre |

### B. Tarjetas de Personajes (Distribución Espacial $2 \times 3$)

| Fila de Tarjetas | Columna 1 (Izquierda) | Columna 2 (Centro) | Columna 3 (Derecha) |
| :--- | :--- | :--- | :--- |
| **Fila 1 (Superior)** | **LUCAS**<br>Él estaba en la Cabina Privada, sentado en una silla. | **MIRIAM**<br>Ella estaba en la segunda columna. | **NICOLAS**<br>Él estaba en la quinta columna. |
| **Fila 2 (Inferior)** | **OLGA**<br>Ella estaba en la última columna, sentada en una silla. | **PABLO**<br>Él estaba al sur de Nicolas, en la última fila. | **MARIO [VÍCTIMA]**<br>La Víctima. Hallado en la Cabina Privada, solo con el agresor. |

#### Lista Detallada de Personajes (Para Registros en Excel)

| # Tarjeta | Posición Gráfica | Personaje | Rol | Testimonio / Pista Exacta |
| :---: | :---: | :--- | :---: | :--- |
| 1 | Fila 1, Col 1 | LUCAS | Culpable | Él estaba en la Cabina Privada, sentado en una silla. |
| 2 | Fila 1, Col 2 | MIRIAM | Sospechoso | Ella estaba en la segunda columna. |
| 3 | Fila 1, Col 3 | NICOLAS | Sospechoso | Él estaba en la quinta columna. |
| 4 | Fila 2, Col 1 | OLGA | Sospechoso | Ella estaba en la última columna, sentada en una silla. |
| 5 | Fila 2, Col 2 | PABLO | Sospechoso | Él estaba al sur de Nicolas, en la última fila. |
| 6 | Fila 2, Col 3 | MARIO | VÍCTIMA | La Víctima. Hallado en la Cabina Privada, solo con el agresor. |

### C. Solución Ground Truth (Posiciones Verificadas)

* **Lucas [CULPABLE]:** Fila 1, Columna 0 (Habitación: Cabina Privada)
* **Miriam:** Fila 3, Columna 1 (Habitación: Zona Lounge)
* **Nicolas:** Fila 2, Columna 4 (Habitación: Zona Lounge)
* **Olga:** Fila 4, Columna 5 (Habitación: Zona Lounge)
* **Pablo:** Fila 5, Columna 3 (Habitación: Zona Lounge)
* **Mario [VÍCTIMA]:** Fila 0, Columna 2 (Habitación: Cabina Privada)

---

## CASO 09: LA MANSIÓN DE CRISTAL ($8 \times 8$)

* **Archivo de imagen:** `static/casos/caso_09.png`
* **Dificultad:** Experto
* **Revisión:** La solución original repetía filas y columnas; el 8x8 admitía muchas soluciones. Se agregan frases a Jorge, Karina y a la víctima.

### A. Matriz del Tablero (Plano de Habitaciones y Muebles)

* **Habitaciones:** H1 = Invernadero | H2 = Estudio | H3 = Salón Principal

| Fila \ Col | Columna 0 | Columna 1 | Columna 2 | Columna 3 | Columna 4 | Columna 5 | Columna 6 | Columna 7 |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Fila 0** | [Invernadero] Libre | [Invernadero] **Planta** | [Invernadero] Libre | [Invernadero] Libre | [Estudio] Libre | [Estudio] **Laptop** | [Estudio] Libre | [Estudio] Libre |
| **Fila 1** | [Invernadero] Libre | [Invernadero] Libre | [Invernadero] **Silla** | [Invernadero] Libre | [Estudio] Libre | [Estudio] Libre | [Estudio] **Mesa** | [Estudio] Libre |
| **Fila 2** | [Invernadero] **Planta** | [Invernadero] Libre | [Invernadero] Libre | [Invernadero] Libre | [Estudio] **Silla** | [Estudio] Libre | [Estudio] Libre | [Estudio] Libre |
| **Fila 3** | [Invernadero] Libre | [Invernadero] **Mesa** | [Invernadero] Libre | [Invernadero] Libre | [Estudio] Libre | [Estudio] Libre | [Estudio] **Silla** | [Estudio] **Planta** |
| **Fila 4** | [Salón Principal] Libre | [Salón Principal] Libre | [Salón Principal] Libre | [Salón Principal] **Mesa** | [Salón Principal] **Mesa** | [Salón Principal] Libre | [Salón Principal] Libre | [Salón Principal] Libre |
| **Fila 5** | [Salón Principal] **Silla** | [Salón Principal] Libre | [Salón Principal] Libre | [Salón Principal] Libre | [Salón Principal] Libre | [Salón Principal] **Silla** | [Salón Principal] Libre | [Salón Principal] Libre |
| **Fila 6** | [Salón Principal] Libre | [Salón Principal] **Laptop** | [Salón Principal] Libre | [Salón Principal] Libre | [Salón Principal] Libre | [Salón Principal] Libre | [Salón Principal] **Mesa** | [Salón Principal] Libre |
| **Fila 7** | [Salón Principal] Libre | [Salón Principal] Libre | [Salón Principal] **Planta** | [Salón Principal] Libre | [Salón Principal] Libre | [Salón Principal] Libre | [Salón Principal] Libre | [Salón Principal] **Silla** |

### B. Tarjetas de Personajes (Distribución Espacial $2 \times 3$)

| Fila de Tarjetas | Columna 1 (Izquierda) | Columna 2 (Centro) | Columna 3 (Derecha) |
| :--- | :--- | :--- | :--- |
| **Fila 1 (Superior)** | **IRENE**<br>Ella estaba en el Invernadero, sentada en una silla. | **JORGE**<br>Él estaba en el Estudio, al lado de una laptop. Él estaba en la séptima columna. | **KARINA**<br>Ella estaba en la primera columna, en el Salón Principal. Ella estaba en la séptima fila. |
| **Fila 2 (Inferior)** | **LEONARDO**<br>Él estaba en la sexta columna, sentado en una silla. | **MONICA**<br>Ella estaba al sur de Karina, al lado de una laptop. | **JACK [VÍCTIMA]**<br>La Víctima. Atrapado en el Invernadero con el asesino. Él estaba en la cuarta fila. |

#### Lista Detallada de Personajes (Para Registros en Excel)

| # Tarjeta | Posición Gráfica | Personaje | Rol | Testimonio / Pista Exacta |
| :---: | :---: | :--- | :---: | :--- |
| 1 | Fila 1, Col 1 | IRENE | Culpable | Ella estaba en el Invernadero, sentada en una silla. |
| 2 | Fila 1, Col 2 | JORGE | Sospechoso | Él estaba en el Estudio, al lado de una laptop. Él estaba en la séptima columna. |
| 3 | Fila 1, Col 3 | KARINA | Sospechoso | Ella estaba en la primera columna, en el Salón Principal. Ella estaba en la séptima fila. |
| 4 | Fila 2, Col 1 | LEONARDO | Sospechoso | Él estaba en la sexta columna, sentado en una silla. |
| 5 | Fila 2, Col 2 | MONICA | Sospechoso | Ella estaba al sur de Karina, al lado de una laptop. |
| 6 | Fila 2, Col 3 | JACK | VÍCTIMA | La Víctima. Atrapado en el Invernadero con el asesino. Él estaba en la cuarta fila. |

### C. Solución Ground Truth (Posiciones Verificadas)

* **Irene [CULPABLE]:** Fila 1, Columna 2 (Habitación: Invernadero)
* **Jorge:** Fila 0, Columna 6 (Habitación: Estudio)
* **Karina:** Fila 6, Columna 0 (Habitación: Salón Principal)
* **Leonardo:** Fila 5, Columna 5 (Habitación: Salón Principal)
* **Monica:** Fila 7, Columna 1 (Habitación: Salón Principal)
* **Jack [VÍCTIMA]:** Fila 3, Columna 3 (Habitación: Invernadero)

---

## CASO 10: LA SALA DE PRENSA ($8 \times 8$)

* **Archivo de imagen:** `static/casos/caso_10.png`
* **Dificultad:** Experto
* **Revisión:** La solución original repetía filas y columnas; el 8x8 admitía muchas soluciones. Se agregan frases a Quirino, Orlando, Natalia y a la víctima.

### A. Matriz del Tablero (Plano de Habitaciones y Muebles)

* **Habitaciones:** H1 = Cabina de Grabación | H2 = Redacción | H3 = Auditorio

| Fila \ Col | Columna 0 | Columna 1 | Columna 2 | Columna 3 | Columna 4 | Columna 5 | Columna 6 | Columna 7 |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Fila 0** | [Cabina de Grabación] Libre | [Cabina de Grabación] **Laptop** | [Cabina de Grabación] Libre | [Cabina de Grabación] Libre | [Redacción] Libre | [Redacción] **Mesa** | [Redacción] **Silla** | [Redacción] Libre |
| **Fila 1** | [Cabina de Grabación] **Silla** | [Cabina de Grabación] Libre | [Cabina de Grabación] Libre | [Cabina de Grabación] Libre | [Redacción] Libre | [Redacción] Libre | [Redacción] Libre | [Redacción] **Laptop** |
| **Fila 2** | [Cabina de Grabación] Libre | [Cabina de Grabación] Libre | [Cabina de Grabación] **Mesa** | [Cabina de Grabación] Libre | [Redacción] **Planta** | [Redacción] Libre | [Redacción] Libre | [Redacción] Libre |
| **Fila 3** | [Cabina de Grabación] Libre | [Cabina de Grabación] Libre | [Cabina de Grabación] Libre | [Cabina de Grabación] **Planta** | [Redacción] Libre | [Redacción] **Silla** | [Redacción] Libre | [Redacción] Libre |
| **Fila 4** | [Auditorio] Libre | [Auditorio] **Planta** | [Auditorio] Libre | [Auditorio] Libre | [Auditorio] Libre | [Auditorio] Libre | [Auditorio] **Mesa** | [Auditorio] Libre |
| **Fila 5** | [Auditorio] Libre | [Auditorio] Libre | [Auditorio] **Silla** | [Auditorio] Libre | [Auditorio] Libre | [Auditorio] Libre | [Auditorio] Libre | [Auditorio] Libre |
| **Fila 6** | [Auditorio] **Silla** | [Auditorio] Libre | [Auditorio] Libre | [Auditorio] **Mesa** | [Auditorio] Libre | [Auditorio] Libre | [Auditorio] Libre | [Auditorio] **Silla** |
| **Fila 7** | [Auditorio] Libre | [Auditorio] Libre | [Auditorio] Libre | [Auditorio] Libre | [Auditorio] **Planta** | [Auditorio] Libre | [Auditorio] Libre | [Auditorio] Libre |

### B. Tarjetas de Personajes (Distribución Espacial $2 \times 3$)

| Fila de Tarjetas | Columna 1 (Izquierda) | Columna 2 (Centro) | Columna 3 (Derecha) |
| :--- | :--- | :--- | :--- |
| **Fila 1 (Superior)** | **MARCOS**<br>Él estaba en la Cabina, al lado de una laptop. | **NATALIA**<br>Ella estaba sentada en una silla en la Redacción. Ella estaba en la sexta columna. | **ORLANDO**<br>Él estaba en la tercera columna, en el Auditorio. Él estaba en la quinta fila. |
| **Fila 2 (Inferior)** | **PAULA**<br>Ella estaba en la primera columna, sentada en una silla. | **QUIRINO**<br>Él estaba al este de Paula, en la última columna. Él estaba en la sexta fila. | **HOWARD [VÍCTIMA]**<br>La Víctima. Silenciado en la Cabina de Grabación con el culpable. Él estaba en la tercera fila. |

#### Lista Detallada de Personajes (Para Registros en Excel)

| # Tarjeta | Posición Gráfica | Personaje | Rol | Testimonio / Pista Exacta |
| :---: | :---: | :--- | :---: | :--- |
| 1 | Fila 1, Col 1 | MARCOS | Culpable | Él estaba en la Cabina, al lado de una laptop. |
| 2 | Fila 1, Col 2 | NATALIA | Sospechoso | Ella estaba sentada en una silla en la Redacción. Ella estaba en la sexta columna. |
| 3 | Fila 1, Col 3 | ORLANDO | Sospechoso | Él estaba en la tercera columna, en el Auditorio. Él estaba en la quinta fila. |
| 4 | Fila 2, Col 1 | PAULA | Sospechoso | Ella estaba en la primera columna, sentada en una silla. |
| 5 | Fila 2, Col 2 | QUIRINO | Sospechoso | Él estaba al este de Paula, en la última columna. Él estaba en la sexta fila. |
| 6 | Fila 2, Col 3 | HOWARD | VÍCTIMA | La Víctima. Silenciado en la Cabina de Grabación con el culpable. Él estaba en la tercera fila. |

### C. Solución Ground Truth (Posiciones Verificadas)

* **Marcos [CULPABLE]:** Fila 1, Columna 1 (Habitación: Cabina de Grabación)
* **Natalia:** Fila 3, Columna 5 (Habitación: Redacción)
* **Orlando:** Fila 4, Columna 2 (Habitación: Auditorio)
* **Paula:** Fila 6, Columna 0 (Habitación: Auditorio)
* **Quirino:** Fila 5, Columna 7 (Habitación: Auditorio)
* **Howard [VÍCTIMA]:** Fila 2, Columna 3 (Habitación: Cabina de Grabación)
