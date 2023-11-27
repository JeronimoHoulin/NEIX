# NEIX
## NEIX Algorithmic Trader Task.


### Aquí los pasos que tomé para resolver este ejercicio:

ENTER

- Recibir y limpiar datos de entrada.
  - Leer CSV. 
  - Renombrar columnas. 
  - Cambiar muestras a tipos de datos adecuados.
  - Deshacerse de NA's y muestras vacias (<1% de los datos).
  - Como se puede apreciar en la siguiente imagen, el precio de mercado del Call ha visto cotizaciones atípicss que podrían deberse a mala entrada de datos o aperturas después de días no hábiles muy volatiles.

  IMAGEN

- Agregar datos.
  - Precio de Call / Subyacente promedio.
  - Volatilidad Realizada.
    - Desvio estandar de los retornos lognormales.
    - Supuestos:
        - 252 dias habiles, 6hrs x rueda.
        - Se ha calculado el promedio de muestras al dia y de minutos entre cada muestra para llegar a un descuento intra-diario.
  - Volatilidad Implícita.
    - Con el modelo de B&S hemos logrado el Sigma (Volatilidad Implícita) a fuerza bruta. 
    - Probando el moodelo y ajustando el Vega derivada de B&S ne funcion de volaitlidad (σ).
    - Le damos al modelo un maximo de intentos, y unatolerancia de 1% como rango de error. 

- Visualizar los datos.
    - Grafico de precio Spot de GGAL (subyacente) vs las volatilidades.

    IMAGEN.


Este trabajo fue escrito en Python, y las visuales con la librería matplotlib.
Uno puede correr el script "main.py" en la carpeta "python" y podrá observar el grafico en questión.
El trabajo tamién esta escrito en C++ tomando la misma estructura y supuestos, corriendo el script "main.cpp" en "c++".
Sin gráficar, pero la salida de datos del script en C++ se puede ver en "output.csv").