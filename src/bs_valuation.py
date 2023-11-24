import pandas as pd
import numpy as np 
import datetime as dt
import matplotlib.pyplot as plt
from scipy.stats import norm
import matplotlib.pyplot as plt
from matplotlib import cm
import numpy as np


def extract():
    print("Linpiando la base de datos...")
    df  = pd.read_csv("data/Exp_Octubre.csv", sep=';', decimal = ',')
    df.rename({"underAst":"underAsk"}, axis = "columns", inplace = True)
    df = df.replace(r'^\s*$', np.NaN, regex=True)  #Replace possible blank values wiht NaN.
    df = df.replace('\\N', np.NaN)                 #Replace \N with NaN.
    df=df.dropna()                                 #Only 31 rows with NaN values; <1% => Drop all rows ocntaining NAN.
    #Changing types
    df['description'].to_string()
    df['bid'] = [x.replace(',', '.') for x in df['bid']]
    df['bid'] = df['bid'].astype(float)
    df['ask'] = [x.replace(',', '.') for x in df['ask']]
    df['ask'] = df['ask'].astype(float)
    df['created_at'] = pd.to_datetime(df['created_at'])
    #print(df.dtypes)
    df['callPrice'] = df[['bid', 'ask']].mean(axis=1)
    df['spotPrice'] = df[['underBid', 'underAsk']].mean(axis=1)
    #print(df.head())
    df['day'] = df['created_at'].dt.strftime("%Y-%d-%m")
    #Check if removing weekends, holidays, and non-trade days is necesary:

    #Call price generates a lot of outliers:
    q = df["callPrice"].quantile(0.6)
    df = df[df['callPrice'] < q]

    


    return df

    

def transform(df, rf, maturity, tolerance):

    """Calculando Volatilidad Realizada del Precio Spot / Subyacente """
    spot = df['spotPrice']
    log_returns= np.log(spot/spot.shift(1))                                                             #B&S asume una distribucion Normal Logarítmica => por eso usamos Retornos Logaritmicos, no absolutos. 
    samples_a_day = df.groupby(pd.Grouper(key='day')).count()
    samples = int(samples_a_day['spotPrice'].mean())                                                     #Promedio de muestras x rueda.
    time_in_mins = (df['created_at'] - df['created_at'].shift(1)).mean().total_seconds() /60             #Apromedio de intervalo de tiempo por muestra (en minutos).
    df['realized_vol'] = log_returns.rolling(window=samples).std()*np.sqrt(252 * int(time_in_mins))      #Volatilidad calculada segun retornos historicos de la rueda anterior. 


    """Calculando Volatilidad Implicita de la valuacion del Call con B&S """

    #B&S
    N = norm.cdf
    N1 = norm.pdf
    def d1(S, K, r, sigma, T):
        d1 = (np.log(S/K)+(r+sigma**2/2)*T)/(sigma*np.sqrt(T))
        return d1
    def d2(S, K, r, sigma, T):
        d2 = (np.log(S/K)+(r-sigma**2/2)*T)/(sigma*np.sqrt(T))
        return d2
    def call_price(S, K, r, sigma, T):
        call_p = S*N(d1(S, K, r, sigma, T))-K*np.exp(-r*T)*N(d2(S, K, r, sigma, T))
        return call_p
    def call_vega(S, K, r, sigma, T):
        v = S*np.sqrt(T)*N1(d1(S, K, r, sigma, T))
        return v
    def call_imp_vol(S, K, r, T, C0, sigma_est, tol):
        #El desvio estandar (σ) no se puede despejar d ela funcion B&S, se puede unicamente acercar a un valor esperado usando prueba y error.
        price = call_price(S, K, r, sigma_est, T)
        vega = call_vega(S, K, r, sigma_est, T)
        sigma = - (price - C0) / vega + sigma_est
        #Cambiamos el precio del Call en la formula de B&S para cambiar Vega, la derivada de B&S en terminos de volatilidad.
        while sigma > sigma_est +tol:
            price = price + 30
            vega = call_vega(S, K, r, sigma_est, T)
            sigma = np.abs((price - C0) / vega + sigma_est)
        while sigma < sigma_est - tol:
            price = price - 4
            vega = call_vega(S, K, r, sigma_est, T)
            sigma = np.abs((price - C0) / vega + sigma_est)
        return sigma




    df['time_till_exp']  = ((maturity - df['created_at']) / np.timedelta64(1, 'D')) / 242
    df['rf'] = ((rf * (252/365)) / (252*6*60)) / time_in_mins                                           #Crea una taasa intra-diaria (cada 15mins) x dias habiles de mercado.
    df.index = np.arange(0,len(df))
    df['implied_vol'] = 0
    df['implied_vol'] = df['implied_vol'].astype(float)

    #Estimamos Sigma (σ) via B&S por cada muestra.
    print("Calculanfo el Sigma de B&S a fuerza bruta...")
    for i, row in df.iterrows():                                                                        #Sigma estimado va a ser la VR anterior.
        iv = call_imp_vol(row['spotPrice'], row['strike'], row['rf'], row['time_till_exp'], row['callPrice'], df.at[i,'realized_vol'], tolerance)
        df.at[i, 'implied_vol'] = iv
    return df
    
    
def visualize(df):
    """Visualizacion del precio Spot de GGAL y las volatilidades Realizadas e Implicitas"""
    fig, ax = plt.subplots(figsize=(12,4))
    ax.plot(df['spotPrice'], color='tab:blue')
    ax2=ax.twinx()
    ax2.plot(df['realized_vol']*100, color='tab:red')
    ax2.plot(df['implied_vol']*100, color='tab:purple')

    # set x-axis label
    ax.set_xlabel("Tïme", fontsize = 14)
    # set y-axis label
    ax.set_ylabel("Spot Price ($)",
                color="tab:blue",
                fontsize=14)

    ax2.set_ylabel("Volatility (%)",color="tab:red",fontsize=14)
    plt.show() 
    



def get_vol(rf, maturity, tolerance): 
    df = extract()
    df = transform(df, rf, maturity, tolerance)
    visualize(df)
