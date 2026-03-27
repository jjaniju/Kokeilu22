import cantools
import serial
import time
from datetime import datetime, timedelta

dbc_file = "GGG.DBC"  
db = cantools.database.load_file(dbc_file)

# Initialize a list to store fuel data with timestamps
fuel_data = []

# Open a log file for writing FuelLevel data
fuel_log_file = open("fuel_log.txt", "a")

# Function to log data to a text file with inline cleanup logic
def log_to_file(fuelrate, timestamp):
    current_time = datetime.now()
    max_age = timedelta(minutes=5)

    # Read all lines and filter out old ones
    try:
        with open("fuel_log.txt", "r") as file:
            lines = file.readlines()

        with open("fuel_log.txt", "w") as file:
            for line in lines:
                try:
                    timestamp_str, _ = line.split(" | ", 1)
                    log_timestamp = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
                    if current_time - log_timestamp <= max_age:
                        file.write(line)
                except ValueError:
                    continue
    except FileNotFoundError:
        pass

    # Append the new entry with formatted timestamp
    with open("fuel_log.txt", "a") as file:
        formatted_timestamp = timestamp.strftime("%Y-%m-%d %H:%M:%S")
        file.write(f"{formatted_timestamp} | FuelRate: {fuelrate:.3f} L/h\n")

# Function to calculate the average fuel consumption over the last 5 minutes
def calculate_average():
    global fuel_data
    current_time = datetime.now()

    # Remove data older than 5 minutes
    fuel_data = [(rate, ts) for rate, ts in fuel_data if ts > current_time - timedelta(minutes=5)]

    # Calculate the average fuel rate
    if fuel_data:
        average = sum(rate for rate, _ in fuel_data) / len(fuel_data)
    else:
        average = None

    return average

# Function to log fuel level with inline cleanup logic
def log_fuel_level(fuel_level):
    current_time = datetime.now()
    max_age = timedelta(minutes=5)

    # Read all lines and filter out old ones
    try:
        with open("fuel_level.txt", "r") as file:
            lines = file.readlines()

        with open("fuel_level.txt", "w") as file:
            for line in lines:
                try:
                    timestamp_str, _ = line.split(" | ", 1)
                    log_timestamp = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
                    if current_time - log_timestamp <= max_age:
                        file.write(line)
                except ValueError:
                    continue
    except FileNotFoundError:
        pass

    # Append the new entry
    with open("fuel_level.txt", "a") as file:
        formatted_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        file.write(f"{formatted_timestamp} | {fuel_level}\n")

# Function to log fuel rate with inline cleanup logic
def log_fuel_rate(fuel_rate):
    current_time = datetime.now()
    max_age = timedelta(minutes=5)

    # Read all lines and filter out old ones
    try:
        with open("fuel_log.txt", "r") as file:
            lines = file.readlines()

        with open("fuel_log.txt", "w") as file:
            for line in lines:
                try:
                    timestamp_str, _ = line.split(" | ", 1)
                    log_timestamp = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
                    if current_time - log_timestamp <= max_age:
                        file.write(line)
                except ValueError:
                    continue
    except FileNotFoundError:
        pass

    # Append the new entry with formatted timestamp
    with open("fuel_log.txt", "a") as file:
        formatted_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        file.write(f"{formatted_timestamp} | FuelRate: {fuel_rate:.3f} L/h\n")

try:
    print("Ohjelma käynnistyy...")

    # Yritetään avata sarjaportti vain kerran
    try:
        ser = serial.Serial('COM3', 115200, timeout=1)
        print("Yhdistetty sarjaporttiin COM3")
    except serial.SerialException as e:
        print(f"Virhe sarjaportin avaamisessa: {e}")
        exit(1)

    while True:
        line = ser.readline().decode('ascii', errors='ignore').strip()
        if line:
            parts = line.split()
            if len(parts) < 7:
                continue

            try:
                can_id = int(parts[3], 16)
                data = bytes(int(byte, 16) for byte in parts[5:])
                message = db.get_message_by_frame_id(can_id)
                decoded = message.decode(data)

                # Suodata vain FuelLevel ja FuelRate signaalit
                fuellevel = decoded.get("FuelLevel", None)
                fuelrate = decoded.get("FuelRate", None)

                if fuellevel is not None:
                    # Muunna prosentit litroiksi (tankin koko 230L)
                    fuellevel_liters = (fuellevel / 100) * 230
                    print(f"FuelLevel: {fuellevel_liters:.2f}")

                    # Ensure FuelLevel is logged to its own text file
                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    log_fuel_level(fuellevel)

                if fuelrate is not None:
                    timestamp = datetime.now()
                    fuel_data.append((fuelrate, timestamp))
                    log_to_file(fuelrate, timestamp)

                    # Calculate and print the average fuel consumption
                    average = calculate_average()
                    if average is not None:
                        print(f"Keskikulutus: {average:.3f}")

                        # Calculate and display the estimated time the fuel will last
                        if fuellevel is not None and average > 0:
                            time_remaining = fuellevel_liters / average
                            print(f"Polttoainetta riittää: {time_remaining:.2f} h")
                    else:
                        print(f"Keskikulutus: {fuelrate:.3f} L/h")

            except (ValueError, KeyError):
                # Ohita virheelliset viestit ilman tulostusta
                continue

except serial.SerialException as e:
    print(f"Sarjaporttivirhe: {e}")
except KeyboardInterrupt:
    print("\nOhjelma keskeytetty käyttäjän toimesta.")
    ser.close()

# Close the log file when the program ends
fuel_log_file.close()