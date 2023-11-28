# NEIX
## NEIX Algorithmic Trader Task

### Aquí los pasos que tomé para resolver este ejercicio:

<br />

- **Recibir y limpiar datos de entrada:**
  - Leer CSV.
  - Renombrar columnas.
  - Cambiar muestras a tipos de datos adecuados.
  - Deshacerse de NA's y muestras vacías (<1% de los datos).
  - Como se puede apreciar en la siguiente imagen, el precio de mercado del Call ha visto cotizaciones atípicas que podrían deberse a mala entrada de datos o aperturas después de días no hábiles muy volátiles (estos picos fueron descartados).

  ![Imagen](https://github.com/JeronimoHoulin/NEIX/blob/main/content/call_outliers.jpeg)

- **Agregar datos calculados:**
  - Precio de Call / Subyacente promedio.
  - Volatilidad Realizada (VR).
    - Desviación estándar de los retornos lognormales.
    - Supuestos:
      - 252 días hábiles, 6 horas por rueda.
      - Se ha calculado el promedio de muestras al día y de minutos entre cada muestra para llegar a una VR anualizada.
  - Volatilidad Implícita (VI).
    - Con el modelo de B&S hemos logrado el Sigma (Volatilidad Implícita) a fuerza bruta.
    - Tasa libre de riesgo (rf) ha sido convertida a intra-diaria para lograr un descuento adecuado de los datos (promedio de 18min x nueva cotizacion).
    - Probamos el modelo por cada nuevo precio del Call y ajustamos el Vega; la derivada de B&S en función de la volatilidad (`σ`).
    - Le damos al modelo un máximo de intentos y una tolerancia del 1% como rango de error en su resultado de `σ`.

- **Visualizar los datos:**
  - Gráfico de precio Spot de GGAL (subyacente) vs las volatilidades (VR en rojo y VI en violeta).

  ![Imagen](https://github.com/JeronimoHoulin/NEIX/blob/main/content/Final.png)

Este trabajo fue escrito en `python`, y las visualizaciones con la librería `matplotlib`. Puedes ejecutar el script `main.py` en la carpeta `python` para observar el gráfico en cuestión. El trabajo también está escrito en `c++` tomando la misma estructura y supuestos, ejecutando el script `main.cpp` en `c++`. Sin gráficos, pero la salida de datos del script en `c++` se puede ver en `output.csv`.

Ejemplo de salida esperada en `c++`:

![Funny GIF](https://github.com/JeronimoHoulin/NEIX/blob/main/content/main_cpp.gif)
