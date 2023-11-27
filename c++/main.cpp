#include <iostream>
#include <fstream>
#include <sstream>
#include <vector>
#include <string>
#include <filesystem>
#include <iomanip>
#include <algorithm>
#include <stdexcept>
#include <cmath>
#include <algorithm>
#include <chrono>
#include <numeric>
#include <ctime>


struct LineData {
    std::chrono::system_clock::time_point created_at; // Timestamp
    double strike;
    double timetomat;
    double callPrice;
    double spotPrice;
    double realizedVol;
    double impliedVol;
};


// Function to convert string with commas to double
double convertToDouble(const std::string& value) {
    std::string cleanedValue = value;

    // Replace commas with decimal points
    std::replace(cleanedValue.begin(), cleanedValue.end(), ',', '.');

    // Convert the cleaned value to double
    return std::stod(cleanedValue);
}


// Function to check if a string is a valid float
bool isFloat(const std::string& s) {
    try {
        std::stof(s);
        return true;
    } catch (const std::invalid_argument& e) {
        return false;
    } catch (const std::out_of_range& e) {
        return false;
    }
}

float calculateRollingSD(const std::vector<double>& data, size_t windowSize) {
    if (data.size() < windowSize) {
        return NAN;
    }

    auto start = data.end() - windowSize;
    auto end = data.end();

    float sum = std::accumulate(start, end, 0.0);
    float mean = sum / windowSize;
    float standardDeviation = 0.0;

    for (auto it = start; it != end; ++it) {
        standardDeviation += pow(*it - mean, 2);
    }

    return sqrt(standardDeviation / windowSize);
}

// Function to calculate cumulative distribution function (CDF) of standard normal distribution
double N(double x) {
    return 0.5 * (1.0 + std::erf(x / std::sqrt(2.0)));
}

// Function to calculate probability density function (PDF) of standard normal distribution
double N1(double x) {
    return (1.0 / std::sqrt(2.0 * M_PI)) * std::exp(-0.5 * x * x);
}


// Function to calculate d1 in Black-Scholes formula
double d1(double S, double K, double r, double sigma, double T) {
    return (std::log(S / K) + (r + 0.5 * sigma * sigma) * T) / (sigma * std::sqrt(T));
}

// Function to calculate d2 in Black-Scholes formula
double d2(double S, double K, double r, double sigma, double T) {
    return (std::log(S / K) + (r - 0.5 * sigma * sigma) * T) / (sigma * std::sqrt(T));
}

// Function to calculate call price using Black-Scholes formula
double call_price(double S, double K, double r, double sigma, double T) {
    double N_d1 = N(d1(S, K, r, sigma, T));
    double N_d2 = N(d2(S, K, r, sigma, T));
    return S * N_d1 - K * std::exp(-r * T) * N_d2;
}

// Function to calculate vega (sensitivity of the option price to volatility) in Black-Scholes formula
double call_vega(double S, double K, double r, double sigma, double T) {
    double N_d1 = N(d1(S, K, r, sigma, T));
    return S * std::sqrt(T) * N1(d1(S, K, r, sigma, T));
}

// Function to calculate implied volatility using Black-Scholes formula
double call_imp_vol(double S, double K, double r, double T, double C0, double sigma_est, double tol) {
    double price = call_price(S, K, r, sigma_est, T);
    double vega = call_vega(S, K, r, sigma_est, T);
    double sigma = - (price - C0) / vega + sigma_est;

    double iter = 0;
    double max_iter = 100000000000;

    // Iterative approach to refine the estimate
    //std::cout << "Atcual Price: " << C0 << std::endl;
    while (  price / C0  -1 > tol  && iter < max_iter) {
        //std::cout << price << std::endl;
        price = price - 5;
        vega = call_vega(S, K, r, sigma, T);
        sigma = std::abs((price - C0) / vega + sigma_est);
        iter++;
    }
    //std::cout << "---" << std::endl;
    while ( price / C0 -1 <  tol && iter < max_iter) {
        //std::cout << price << std::endl;
        price = price + 5;
        vega = call_vega(S, K, r, sigma, T);
        sigma = std::abs((price - C0) / vega + sigma_est);
        iter++;
    }
    //std::cout << "---" << std::endl;
    return sigma;
}





int main(int argc, char* argv[]) {
    if (argc > 0) {
        // Get the path to the current executable file
        std::filesystem::path executablePath = std::filesystem::absolute(std::filesystem::path(argv[0]));

        // Get the directory containing the executable file
        std::filesystem::path executableDir = executablePath.parent_path();

        // Set the current working directory to the directory of the executable file
        std::filesystem::current_path(executableDir);

        // Print the new current working directory
        //std::cout << "Current working directory: " << std::filesystem::current_path() << std::endl;

        // Specify the path to your CSV file
        std::string csvFilePath = "Exp_octubre.csv";

        // Open the CSV file
        std::ifstream inputFile(csvFilePath);

        // Check if the file is opened successfully
        if (!inputFile.is_open()) {
            std::cerr << "Error opening file: " << csvFilePath << std::endl;
            return 1;
        }

        std::vector<LineData> cleanedLines;  // Store cleaned lines to filter outliers later
        std::string line;

        while (std::getline(inputFile, line)) {
            LineData lineData; // Create an instance of LineData for each line

            // Replace "\\N" with NaN => remove NAN.
            std::replace(line.begin(), line.end(), ' ', 'N');
            std::replace(line.begin(), line.end(), '\\', ' ');
            std::replace(line.begin(), line.end(), 'N', ' ');
            // Drop empty lines
            line.erase(std::remove(line.begin(), line.end(), ' '), line.end());

            // Declare tokens vector here to clear it for each line
            std::vector<std::string> tokens;
            std::string token;

            // Split the line into individual values based on the ";" delimiter
            std::istringstream ss(line);
            while (std::getline(ss, token, ';')) {
                tokens.push_back(token);
            }

            // Calculate and print "callPrice" (new index 8) ('bid' and 'ask' are at indices 3 and 4)
            if (tokens.size() > 6) {
                try {
                    lineData.strike = std::stod(tokens[1]);
                    // Convert string timestamp to std::chrono::system_clock::time_point
                    std::istringstream timestampStream(tokens[7]);
                    std::tm tmStruct = {};
                    timestampStream >> std::get_time(&tmStruct, "%m/%d/%Y %H:%M");
                    if (!timestampStream.fail()) {
                        auto timePoint = std::chrono::system_clock::from_time_t(std::mktime(&tmStruct));
                        lineData.created_at = timePoint;
                        // Set fixed time to MATURITY: October 18, 2024
                        std::tm fixedTimeStruct = {0, 0, 0, 18, 9, 2024 - 1900, 0, 0, -1};
                        auto fixedTime = std::chrono::system_clock::from_time_t(std::mktime(&fixedTimeStruct));
                        auto duration = fixedTime - timePoint;
                        lineData.timetomat = std::chrono::duration_cast<std::chrono::duration<double>>(duration).count() / (365.25 * 24 * 60 * 60); // Convert seconds to years

                    } else {
                        // Handle timestamp parsing failure
                    }

                    double bid = convertToDouble(tokens[3]);
                    double ask = convertToDouble(tokens[4]);
                    lineData.callPrice = (bid + ask) / 2.0;

                    double underBid = convertToDouble(tokens[5]);
                    double underAsk = convertToDouble(tokens[6]);
                    lineData.spotPrice = (underBid + underAsk) / 2.0;

                    // Assuming these are the default values if not available in the data
                    lineData.realizedVol = 0;
                    lineData.impliedVol = 0;

                } catch (const std::invalid_argument& e) {
                    // Handle conversion errors if needed
                }

                // Append the LineData to the vector
                cleanedLines.push_back(lineData);
            }
        }

        // Calculate Realized & Implied volatilities
        std::vector<double> logReturns;

        const int windowSize = 114; // 114 samples a day on average. 
        // Sigma from B&S error tolerance compared to our estimated Sigma.
        const double tolerance = 0.01;
        double rf = 0.0000004; //Rf converted to a 15min yield. ((100% * (252/365)) / (252*6*60)) / 15 

        for (size_t i = 1; i < cleanedLines.size(); ++i) {
            double spotReturn = log(cleanedLines[i].spotPrice / cleanedLines[i - 1].spotPrice);
            logReturns.push_back(spotReturn);

            // Check if enough data points are available for calculation
            if (logReturns.size() >= windowSize) {
                cleanedLines[i].realizedVol = calculateRollingSD(logReturns, windowSize) * sqrt(252.0 * 18);
                // 18 MINS is average time between samples (to make IV an annual rate).
            }

            if(i == 0){
                double iv = call_imp_vol(cleanedLines[i].spotPrice,
                        cleanedLines[i].strike,
                        rf,
                        cleanedLines[i].timetomat, 
                        cleanedLines[i].callPrice,
                        cleanedLines[i].realizedVol,
                        tolerance);
                cleanedLines[i].impliedVol = iv;
            }else{
                double last_price = cleanedLines[i-1].callPrice;
                double curr_price = cleanedLines[i].callPrice;

                if (last_price != curr_price){
                    double iv = call_imp_vol(cleanedLines[i].spotPrice,
                                     cleanedLines[i].strike,
                                     rf,
                                     cleanedLines[i].timetomat, 
                                     cleanedLines[i].callPrice,
                                     cleanedLines[i-1].realizedVol,
                                     tolerance);
                    cleanedLines[i].impliedVol = iv;
                }else{
                    cleanedLines[i].impliedVol = cleanedLines[i-1].impliedVol;
                }
            }
        }


        // Print the vector elements
        
        for (const auto& data : cleanedLines) {
            std::cout << "Time To Mat: " << data.timetomat << " Years, ";
            std::cout << "Call Price: " << data.callPrice << ", ";
            std::cout << "Spot Price: " << data.spotPrice << ", ";
            std::cout << "Realized Volatility: " << data.realizedVol << ", ";
            std::cout << "Implied Volatility: " << data.impliedVol << std::endl;
        }
        
        // Create an output CSV file
        std::ofstream outputFile("output.csv");

        // Check if the file is opened successfully
        if (!outputFile.is_open()) {
            std::cerr << "Error opening output file: output.csv" << std::endl;
            return 1;
        }

        // Write header to the CSV file
        outputFile << "Time To Mat,Call Price,Spot Price,Realized Volatility,Implied Volatility\n";

        // Write data to the CSV file
        for (const auto& data : cleanedLines) {
            outputFile << data.timetomat << ",";        // Time To Mat
            outputFile << data.callPrice << ",";         // Call Price
            outputFile << data.spotPrice << ",";         // Spot Price
            outputFile << data.realizedVol << ",";       // Realized Volatility
            outputFile << data.impliedVol << "\n";       // Implied Volatility
        }

        // Close the output CSV file
        outputFile.close();

        return 0;
    } else {
        std::cerr << "Error: Unable to determine the executable path." << std::endl;
    }

    return 0;
}