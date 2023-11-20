import sys
import datetime as dt
sys.path.append('./src')

from bs_valuation import get_vol

# Constantes de la especie (opcion call europea):
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
rf = 1 #Tasa libre de riesgo 100% 
maturity = dt.datetime(2024, 10, 18) 


if __name__ == '__main__':
    get_vol(rf, maturity)