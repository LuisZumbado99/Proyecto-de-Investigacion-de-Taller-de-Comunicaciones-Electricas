# Scripts del Proyecto

A continuación se presenta el listado de los scripts utilizados en el flujo de simulación electromagnética FDTD, procesamiento Touchstone y graficado del proyecto, junto con su función principal.

## Scripts de Simulación (`openEMS` / `CSXCAD`)

* **`simular_crosstalk.py`**
  * **Propósito:** Ejecuta simulaciones FDTD de 4 puertos sobre líneas microstrip acopladas en el rango sub-GHz (`0` a `1 GHz`), exportando matrices de parámetros $S$ en formato Touchstone (`.s4p`) dentro de `data/` e imprimiendo el resumen en dB a `100 MHz`, `500 MHz` y `1 GHz`[cite: 2].
  * **Configuración base:** Utiliza $\varepsilon_r = 4.3$, ancho de pista de `3.0 mm`, largo de `50.0 mm` y sustrato de `1.6 mm`[cite: 2].

* **`simular_crosstalk_2.py`**
  * **Propósito:** Variante de simulación FDTD de 4 puertos que ajusta el dominio geométrico, la malla y los parámetros físicos del modelo respecto a la corrida base, generando su respectivo archivo `.s4p` y resumen en consola.

* **`simular_crosstalk_apantallamiento.py`**
  * **Propósito:** Simula el sistema de 4 puertos incorporando apantallamiento con pista de guarda entre trazas para evaluar su efecto en el acoplamiento y la respuesta de transmisión/reflexión en el rango de `0` a `1 GHz`, exportando el archivo `.s4p` correspondiente.

* **`simular_crosstalk_via_fencing.py`**
  * **Propósito:** Simula el sistema de 4 puertos incorporando *via fencing* (vías conductoras referidas a masa) para analizar la contención del campo y el aislamiento entre líneas en el rango sub-GHz, generando su archivo `.s4p` de salida.

* **`simular_crosstalk_via_fencing_y_apantallamiento.py`**
  * **Propósito:** Evalúa de forma conjunta la combinación de apantallamiento y *via fencing* sobre la estructura de 4 puertos en `openEMS`, exportando el resultado en formato Touchstone (`.s4p`).

## Scripts de Post-procesamiento y Graficado

* **`plot_comparativa_crosstalk.py`**
  * **Propósito:** Lee archivos Touchstone `.s4p` de 4 puertos (`# GHz S RI R 50`), convierte las magnitudes complejas a decibelios (`dB`) y genera una figura comparativa en cuadrícula `2x2` para $S_{31}$ (NEXT), $S_{41}$ (FEXT), $S_{11}$ (reflexión) y $S_{21}$ (transmisión) en PNG[cite: 13].

## Scripts de Automatización por Lotes

* **`ejecutar_todo.sh`**
  * **Propósito:** Script de Bash diseñado para encadenar ejecuciones secuenciales de las simulaciones y facilitar corridas prolongadas en segundo plano (por ejemplo, mediante `nohup` redirigiendo la salida a un archivo de registro `.out`).
