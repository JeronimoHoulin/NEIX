#https://thepythoncode.com/assistant/code-converter/python/c++/
#include <iostream>
#include <fstream>
#include <sstream>
#include <vector>
#include <string>
#include <algorithm>
#include <cmath>
#include <ctime>
#include <iomanip>

#include "pandas.hpp"
#include "numpy.hpp"
#include "datetime.hpp"
#include "scipy_stats.hpp"

using namespace std;

pandas::DataFrame extract() {
    pandas::DataFrame df = pandas::read_csv("data/Exp_Octubre.csv", ';', ',');
    df.rename({"underAst"}, {"underAsk"});
    df.replace(r'^\s*$', numpy::NaN, true);
    df.replace("\\N", numpy::NaN);
    df.dropna();
    df["description"].to_string();
    df["bid"] = [x.replace(",", ".") for x in df["bid"]];
    df["bid"] = df["bid"].astype(float);
    df["ask"] = [x.replace(",", ".") for x in df["ask"]];
    df["ask"] = df["ask"].astype(float);
    df["created_at"] = pandas::to_datetime(df["created_at"]);
    df["callPrice"] = (df["bid"] + df["ask"]) / 2;
    df["spotPrice"] = (df["underBid"] + df["underAsk"]) / 2;
    df["day"] = df["created_at"].dt.strftime("%Y-%d-%m");
    double q = df["callPrice"].quantile(0.7);
    df = df[df["callPrice"] < q];
    return df;
}

pandas::DataFrame transform(pandas::DataFrame df, double rf, datetime::DateTime maturity, double tolerance) {
    numpy::Array spot = df["spotPrice"];
    numpy::Array log_returns = numpy::log(spot / spot.shift(1));
    pandas::DataFrame samples_a_day = df.groupby(pd::Grouper("day")).count();
    int samples = samples_a_day["spotPrice"].mean();
    double time_in_mins = (df["created_at"] - df["created_at"].shift(1)).mean().total_seconds() / 60;
    df["realized_vol"] = log_returns.rolling(samples).std() * sqrt(252 * int(time_in_mins));
    
    scipy::stats::norm N = scipy::stats::norm.cdf;
    scipy::stats::norm N1 = scipy::stats::norm.pdf;
    
    auto d1 = [](double S, double K, double r, double sigma, double T) {
        return (log(S / K) + (r + pow(sigma, 2) / 2) * T) / (sigma * sqrt(T));
    };
    
    auto d2 = [](double S, double K, double r, double sigma, double T) {
        return (log(S / K) + (r - pow(sigma, 2) / 2) * T) / (sigma * sqrt(T));
    };
    
    auto call_price = [](double S, double K, double r, double sigma, double T) {
        return S * N(d1(S, K, r, sigma, T)) - K * exp(-r * T) * N(d2(S, K, r, sigma, T));
    };
    
    auto call_vega = [](double S, double K, double r, double sigma, double T) {
        return S * sqrt(T) * N1(d1(S, K, r, sigma, T));
    };
    
    auto call_imp_vol = [](double S, double K, double r, double T, double C0, double sigma_est, double tol) {
        double price = call_price(S, K, r, sigma_est, T);
        double vega = call_vega(S, K, r, sigma_est, T);
        double sigma = - (price - C0) / vega + sigma_est;
        while (sigma > sigma_est + tol) {
            price = price + 5;
            vega = call_vega(S, K, r, sigma_est, T);
            sigma = abs((price - C0) / vega + sigma_est);
        }
        while (sigma < sigma_est - tol) {
            price = price - 5;
            vega = call_vega(S, K, r, sigma_est, T);
            sigma = abs((price - C0) / vega + sigma_est);
        }
        return sigma;
    };
    
    df["time_till_exp"] = ((maturity - df["created_at"]) / timedelta::timedelta(1, "D")) / 242;
    df["rf"] = ((rf * (252 / 365)) / (252 * 6 * 60)) / time_in_mins;
    df.index = numpy::arange(0, len(df));
    df["implied_vol"] = 0.0;
    df["implied_vol"] = df["implied_vol"].astype(float);
    
    for (int i = 0; i < len(df); i++) {
        if (i == 0) {
            double iv = call_imp_vol(df.at(i, "spotPrice"), df.at(i, "strike"), df.at(i, "rf"), df.at(i, "time_till_exp"), df.at(i, "callPrice"), df.at(i, "realized_vol"), tolerance);
            df.at(i, "implied_vol") = iv;
        } else {
            double last_price = df.at(i - 1, "callPrice");
            double curr_price = df.at(i, "callPrice");
            if (last_price == curr_price) {
                df.at(i, "implied_vol") = df.at(i - 1, "implied_vol");
            } else {
                double iv = call_imp_vol(df.at(i, "spotPrice"), df.at(i, "strike"), df.at(i, "rf"), df.at(i, "time_till_exp"), df.at(i, "callPrice"), df.at(i, "realized_vol"), tolerance);
                df.at(i, "implied_vol") = iv;
            }
        }
    }
    return df;
}

int main() {
    double tasa_anual = 1;
    datetime::DateTime vencimiento = datetime::DateTime(2024, 10, 18);
    double tolerancia = 0.01;
    pandas::DataFrame df = extract();
    df = transform(df, tasa_anual, vencimiento, tolerancia);
    return 0;
}