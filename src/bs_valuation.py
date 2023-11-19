import pandas as pd
import numpy as np 

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

    return df

    

def transform(df):
    """Calculando Volatilidad Realizada del Precio Spot / Subyacente """
    spot = df['spotPrice']
    log_returns = np.log(spot/spot.shift(1)) #B&S assumes log normal dist 0> use log returns not abs returns.s
    TRADING_DAYS = 21                        #Assuming 21 trading days in a month & 252 in a year. 
    df['realized_vol'] = log_returns.rolling(window=TRADING_DAYS).std()*np.sqrt(252)
    ''' Calculated RV for 30d window. Src: https://people.unipi.it/fulvio_corsi/wp-content/uploads/sites/473/2018/08/FulvioCorsi_Tesi_2005.pdf'''
    #print(df.tail())

    """Calculando Volatilidad Implicita de la valuacion del Call con B&S """
    print("Calculating B&S....")


def load():
    print("Loading")
    

def get_vol():
    #rf, strike, maturity 
    df = extract()
    transform(df)

get_vol()