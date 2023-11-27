# NEIX
## NEIX Algorithmic Trader Task

### Aquí los pasos que tomé para resolver este ejercicio:

<br />

- **Recibir y limpiar datos de entrada:**
  - Leer CSV.
  - Renombrar columnas.
  - Cambiar muestras a tipos de datos adecuados.
  - Deshacerse de NA's y muestras vacías (<1% de los datos).
  - Como se puede apreciar en la siguiente imagen, el precio de mercado del Call ha visto cotizaciones atípicas que podrían deberse a mala entrada de datos o aperturas después de días no hábiles muy volátiles.

  ![Imagen](URL_DE_LA_IMAGEN)

- **Agregar datos:**
  - Precio de Call / Subyacente promedio.
  - Volatilidad Realizada.
    - Desviación estándar de los retornos lognormales.
    - Supuestos:
      - 252 días hábiles, 6 horas por rueda.
      - Se ha calculado el promedio de muestras al día y de minutos entre cada muestra para llegar a un descuento intra-diario.
  - Volatilidad Implícita.
    - Con el modelo de B&S hemos logrado el Sigma (Volatilidad Implícita) a fuerza bruta.
    - Probando el modelo y ajustando el Vega derivada de B&S en función de la volatilidad (σ).
    - Le damos al modelo un máximo de intentos y una tolerancia del 1% como rango de error.

- **Visualizar los datos:**
  - Gráfico de precio Spot de GGAL (subyacente) vs las volatilidades.

  ![Imagen](URL_DE_LA_IMAGEN)

Este trabajo fue escrito en Python, y las visualizaciones con la librería matplotlib. Puedes ejecutar el script `main.py` en la carpeta `python` para observar el gráfico en cuestión. El trabajo también está escrito en C++ tomando la misma estructura y supuestos, ejecutando el script `main.cpp` en `c++`. Sin gráficos, pero la salida de datos del script en C++ se puede ver en `output.csv`.
