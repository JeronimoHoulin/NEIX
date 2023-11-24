import sys
import datetime as dt
sys.path.append('./src')

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
tolerancia = 0.01 #La Tolerancia que le damos al modelo de B&S (diferencia entre Sigma calculado y esperado). Recomendado rango: 0.01 : 0.09

if __name__ == '__main__':
    get_vol(tasa_anual, vencimiento, tolerancia)