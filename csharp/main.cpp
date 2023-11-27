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

struct LineData {
    std::chrono::system_clock::time_point created_at; // Timestamp
    double strike;
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

        // Print the vector elements
        for (const auto& data : cleanedLines) {
            std::cout << "Strike: " << data.strike << ", ";
            std::cout << "Timestamp: " << std::chrono::system_clock::to_time_t(data.created_at) << ", ";
            std::cout << "Call Price: " << data.callPrice << ", ";
            std::cout << "Spot Price: " << data.spotPrice << ", ";
            std::cout << "Realized Volatility: " << data.realizedVol << ", ";
            std::cout << "Implied Volatility: " << data.impliedVol << std::endl;
        }

        return 0;
    } else {
        std::cerr << "Error: Unable to determine the executable path." << std::endl;
    }

    return 0;
}