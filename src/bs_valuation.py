import pandas as pd
import numpy as np 
import datetime as dt
import matplotlib.pyplot as plt
import scipy.stats as si

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
    #Remove weekends, holidays, and non-trade days:
    df = df[df['spotPrice'] != 0]

    return df

    

def transform(df, rf, maturity):
    """Calculando Volatilidad Realizada del Precio Spot / Subyacente """
    #Utilizando algo tan sencillo como: https://www.macroption.com/historical-volatility-excel
    #Suponiendo que cada muestra es "un dia" y convirtiendo el rdo en un % anualizado multiplicando por muestras al dia promedio.

    spot = df['spotPrice']
    log_returns= np.log(spot/spot.shift(1)) #B&S assumes log normal dist => we use log returns not abs returns.

    grouped_data = df.groupby(pd.Grouper(key='created_at', freq='D'))
    samples_per_day = grouped_data['spotPrice'].count()
    samples = int(samples_per_day.mean())                                                       #  Hay alrededor de 77 muestras x dia.
    average_time = (df['created_at'] - df['created_at'].shift(1)).mean().total_seconds() /60    #  Una muestra cada 18 minutos.
    time_in_mins =  480 / average_time #480 mins x rueda.
    df['realized_vol'] = (log_returns.rolling(window=samples).std()*np.sqrt(365 * int(time_in_mins)))

    """Calculando Volatilidad Implicita de la valuacion del Call con B&S """
    #Call's IV depends on Vega:
    #from: https://www.linkedin.com/pulse/discussing-implied-volatility-python-script-calculate-akash-pathak/
    
    def bs_price(c_p, S, K, r, t, sigma):
        N = si.norm.cdf
        d1 = (np.log(S/K) + (r+sigma**2/2)*t) / (sigma*np.sqrt(t))
        d2 = d1 - sigma * np.sqrt(t)

        if c_p == 'c':
            return N(d1) * S - N(d2) * K * np.exp(-r*t)
        elif c_p == 'p':
            return N(-d2) * K * np.exp(-r*t) - N(-d1) * S
        else:
            return "Please specify call or put options."
    
    ONE_CENT = 0.01
    step = 0.0001

    def brute_force(c_p, S, K, r, t, market_price, med_sigma):
            _sigma = med_sigma
            for i in range(1000): #max number of calculations
                bs_ = bs_price(c_p, S, K, r, t, sigma = _sigma)
                diff = market_price - bs_
                if diff > ONE_CENT:
                    _sigma = _sigma + step
                elif diff < 0 and abs(diff) > ONE_CENT:
                    _sigma = _sigma - step
                elif abs(diff) < ONE_CENT:
                    return _sigma
            return _sigma
    

    def iv_newton(c_p, S, K, r, t, market_price, med_sigma):
        MAX_TRY = 1000

        _sigma = med_sigma

        d1 = (np.log(S/K) + (r+_sigma**2/2)*t) / (_sigma*np.sqrt(t))

        for i in range(MAX_TRY):
            _bs_price = bs_price(c_p,S, K, r, t, sigma=_sigma)
            diff = market_price - _bs_price
            vega = S*si.norm.pdf(d1)*np.sqrt(t)
            if abs(diff) < ONE_CENT:
                return _sigma
            _sigma += diff/vega
        return _sigma

    
        
    df['time_till_exp']  = ((maturity - df['created_at']) / np.timedelta64(1, 'D')) / 365
    df['rf'] = rf / (((maturity - df['created_at']) / np.timedelta64(1, 'D')) * samples)
    meany = float( df['realized_vol'].mean())
    df['mean_vol'] = meany
    #print(df['mean_vol'])
    #iv = call_imp_vol(df['spotPrice'], df['strike'], df['rf'], df['time_till_exp'], df['callPrice'], df['mean_vol'])
    #df['implied_vol'] = iv
    
    
    #Ref: https://pythoninoffice.com/calculate-option-implied-volatility-in-python/


    def d1(S, K, r, sigma, T):
        return (np.log(S/K)+(r+sigma**2/2)*T)/(sigma*np.sqrt(T))
    def d2(S, K, r, sigma, T):
        return (np.log(S/K)+(r-sigma**2/2)*T)/(sigma*np.sqrt(T))

    def call_price(S, K, r, sigma, T):
        return S*si.norm.cdf(d1(S, K, r, sigma, T), 0.0, 1.0)-K*np.exp(-r*T)*si.norm.cdf(d2(S, K, r, sigma, T), 0.0, 1.0)
    
    def call_vega(S, K, r, sigma, T):
        return S*np.sqrt(T)*si.norm.pdf(d1(S, K, r, sigma, T), 0.0, 1.0)
    
    def call_imp_vol(S, K, r, T, C0, sigma_est, it=1000):
        for i in range(it):
            sigma_est -= ((call_price(S, K, r, sigma_est, T)-C0)/call_vega(S, K, r, sigma_est, T))
        return np.abs(sigma_est)


    df['implied_vol2'] = call_imp_vol(df['spotPrice'], df['strike'], df['rf'], df['time_till_exp'], df['callPrice'], meany)

    df.index = np.arange(0,len(df))

    all_sigmas = []
    for index, row in df.iterrows():
        if index == 0:
            sigma = iv_newton('c', row['spotPrice'], row['strike'], row['rf'], row['time_till_exp'], row['callPrice'], row['mean_vol'])
            #print(sigma)
            all_sigmas.append(sigma)
        else:
            #print(df.iloc[index-1, 8])
            last_price = df.iloc[index-1, 8]
            if row['callPrice'] == last_price:
                all_sigmas.append(all_sigmas[index-1])
            if row['callPrice'] != last_price:
                sigma = iv_newton('c', row['spotPrice'], row['strike'], row['rf'], row['time_till_exp'], row['callPrice'], row['mean_vol'])
                #print(sigma)
                all_sigmas.append(sigma)
        


    sigmas = pd.DataFrame(all_sigmas)
    df['implied_vol'] = sigmas
    
    df['realized_vol'] = df['realized_vol'].shift(-samples)

    print(df)
    
    ### Plot Spot Pri
    
    fig, ax = plt.subplots(figsize=(12,4))
    ax.plot(df['spotPrice'], color='tab:blue')
    ax2=ax.twinx()
    ax2.plot(df['realized_vol']*100, color='tab:red')
    ax2.plot(df['implied_vol']*100, color='tab:green')
    #ax2.plot(df['implied_vol2']*100, color='tab:blue')

    # set x-axis label
    ax.set_xlabel("Tïme", fontsize = 14)
    # set y-axis label
    ax.set_ylabel("Stock Price (USD $)",
                color="tab:blue",
                fontsize=14)

    ax2.set_ylabel("Volatility (%)",color="tab:red",fontsize=14)
    plt.show() 
    

    return df




def load():
    print("Loading")
    
    
def visualize():
    print('Visuals')


def get_vol(rf, maturity): 
    df = extract()
    df_vol = transform(df, rf, maturity)



rf = 1 
maturity = dt.datetime(2024, 10, 18) 
get_vol(rf, maturity)