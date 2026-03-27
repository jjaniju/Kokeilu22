import os
from datetime import datetime
import time

# Function to read the latest fuel level from fuel_level.txt
def get_latest_fuel_level():
    try:
        with open("fuel_level.txt", "r") as file:
            lines = file.readlines()
            if lines:
                # Get the last line and extract the fuel level in liters
                last_line = lines[-1]
                _, fuel_level_str = last_line.split(" | ")
                return float(fuel_level_str.strip().split()[0])
    except (FileNotFoundError, ValueError):
        pass
    return None

# Function to calculate the average fuel consumption from fuel_log.txt
def calculate_average_fuel_consumption():
    try:
        with open("fuel_log.txt", "r") as file:
            lines = file.readlines()
            if lines:
                fuel_rates = []
                for line in lines:
                    try:
                        _, fuel_rate_str = line.split(" | FuelRate: ")
                        fuel_rates.append(float(fuel_rate_str.strip().split()[0]))
                    except ValueError:
                        continue
                if fuel_rates:
                    return sum(fuel_rates) / len(fuel_rates)
    except FileNotFoundError:
        pass
    return None

# Main logic to calculate and print the result in a loop
if __name__ == "__main__":
    try:
        while True:
            latest_fuel_level = get_latest_fuel_level()
            average_fuel_consumption = calculate_average_fuel_consumption()

            if latest_fuel_level is not None and average_fuel_consumption is not None:
                try:
                    result = latest_fuel_level / average_fuel_consumption
                    print(f"Keskikulutus: {average_fuel_consumption:.3f} L/h")
                    print(f"Bensan määrä jaettuna keskikulutuksella: {result:.3f} h")
                except ZeroDivisionError:
                    print("Keskikulutus on nolla, jako ei mahdollinen.")
            else:
                print("Tietoja ei voitu laskea. Tarkista, että molemmat tiedostot sisältävät tarvittavat tiedot.")

            time.sleep(1)  # Wait for 1 second before repeating
    except KeyboardInterrupt:
        print("\nOhjelma keskeytetty käyttäjän toimesta.")