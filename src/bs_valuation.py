import pandas as pd
import numpy as np 
import datetime as dt
import matplotlib.pyplot as plt
from scipy.optimize import fsolve
from scipy.stats import norm
import math

def extract():
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

    '''
    grouped_data = df.groupby(pd.Grouper(key='created_at', freq='D'))
    samples_per_day = grouped_data['callPrice'].count()
    # Identify days with no trading activity
    no_activity_days = samples_per_day[samples_per_day == 0].index
    # Check if these weekends/holidays are in the dataset
    non_trading_activity = df['created_at'].dt.strftime("%Y-%d-%m").isin(no_activity_days)
    '''


    


    return df

    

def transform(df, rf, maturity):
    """Calculando Volatilidad Realizada del Precio Spot / Subyacente """
    #Utilizando algo tan sencillo como: https://www.macroption.com/historical-volatility-excel
    #Suponiendo que cada muestra es "un dia" y convirtiendo el rdo en un % anualizado multiplicando por muestras al dia promedio.

    spot = df['spotPrice']
    log_returns= np.log(spot/spot.shift(1)) #B&S assumes log normal dist => we use log returns not abs returns.

    #Getting average number of trades a day
    samples_a_day = df.groupby(pd.Grouper(key='day')).count()
    samples = int(samples_a_day['spotPrice'].mean())
    time_in_mins = (df['created_at'] - df['created_at'].shift(1)).mean().total_seconds() /60  
    df['realized_vol'] = log_returns.rolling(window=samples).std()*np.sqrt(365 * int(time_in_mins))
    #Volatilidad calculada segun retornos historicos de la rueda anterior. 


    """Calculando Volatilidad Implicita de la valuacion del Call con B&S """
    
    #Call's IV depends on Vega:
    #from: https://www.linkedin.com/pulse/discussing-implied-volatility-python-script-calculate-akash-pathak/

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
    
    def call_imp_vol(S, K, r, T, C0, sigma_est, tol=0.05):
        sigma_bs = 2*sigma_est
        for i in range(0, 100):
            while sigma_bs > sigma_est:
                price = call_price(S, K, r, sigma_est, T)
                vega = call_vega(S, K, r, sigma_est, T)
                sigma_bs -= (price - C0) / vega
                return sigma_bs
    

    df['time_till_exp']  = ((maturity - df['created_at']) / np.timedelta64(1, 'D')) / 242
    df['rf'] = ((rf * df['time_till_exp'])  *(time_in_mins / (60*6)) ) / df['time_till_exp']          #Creating a "15minute yield"... rf / (242*60*6) 
    mean_volat = float( df['realized_vol'].mean())
    df['mean_vol'] = mean_volat
    iterations = 1
    tolerance = 0.01
    df.index = np.arange(0,len(df))
    df['implied_vol'] = 0
    df['implied_vol'] = df['implied_vol'].astype(float)

    #call_imp_vol(df['spotPrice'][0], df['strike'][0], df['rf'][0], df['time_till_exp'][0], df['callPrice'][0],df[df['realized_vol']>0]['realized_vol'].mean(), iterations, tolerance)
    for i, row in df.iterrows():
        iv = call_imp_vol(row['spotPrice'], row['strike'], row['rf'], row['time_till_exp'], row['callPrice'], mean_volat)
        df.at[i, 'implied_vol'] = iv

    print(df)
    
    
    '''
    
    for index, row in df.iterrows():
        #Detect a price change in the Call:
        if index == 0:
            iv = call_imp_vol(row['spotPrice'], row['strike'], row['rf'], row['time_till_exp'], row['callPrice'], row['mean_vol'], iterations, tolerance)
            df.at[index, 'implied_vol'] = iv
        else:
            last_price = df.at[index-1, 'callPrice']
            curr_price = row['callPrice']
            if curr_price == last_price:
                df.at[index, 'implied_vol'] = df.at[index -1, 'implied_vol']    
            else:                                                                                                       #Guess is now mean past IV !
                iv = call_imp_vol(row['spotPrice'], row['strike'], row['rf'], row['time_till_exp'], row['callPrice'],df[df['realized_vol']>0]['realized_vol'].mean(), iterations, tolerance)
                df.at[index, 'implied_vol'] = iv if not np.isnan(iv) and iv >=0.8*df[df['realized_vol']>0]['realized_vol'].min() and iv <= 0.8*df['realized_vol'].max() else df.at[index - 1, 'implied_vol']
    
    '''

    #Realized Vol is backwards looking whilst IV is foward looking, so for visuals I will shift the RV back 1 day.
    df['realized_vol'] = df['realized_vol'].shift(-samples)

    return df




def load():
    print("Loading")
    
    
def visualize(df):
        ### Plot 
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
    


def get_vol(rf, maturity): 
    df = extract()
    df_vol = transform(df, rf, maturity)
    visualize(df_vol)



rf = 1 
maturity = dt.datetime(2024, 10, 18) 
get_vol(rf, maturity)