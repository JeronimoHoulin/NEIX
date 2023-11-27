import datetime as dt
import os
import sys


# Get the current script's directory
current_script_directory = os.path.dirname(os.path.abspath(__file__))

# Append the 'scripts' directory to the path
scripts_directory = os.path.join(current_script_directory, 'src')
sys.path.append(scripts_directory)

from bs_valuation import get_vol

# Constantes de la especie (opcion Call Europeo):
"""
SUBYACENTE
GGAL
TIPO DE OPCIÓN
Call
VENCIMIENTO
18/10/2024
PRECIO DEL EJERCICIO
1033
"""

tasa_anual = 1 #Tasa libre de riesgo. 
vencimiento = dt.datetime(2024, 10, 18) 
tolerancia = 0.01 #La Tolerancia que le damos al modelo de B&S (diferencia entre Sigma calculado y esperado). Recomendado rango: 1% - 3%

if __name__ == '__main__':
    get_vol(tasa_anual, vencimiento, tolerancia)