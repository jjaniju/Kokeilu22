import tkinter as tk
from tkinter import ttk
from threading import Thread
import cantools
import serial
import time
from datetime import datetime, timedelta

# Initialize the DBC file and database
dbc_file = "GGG.DBC"
db = cantools.database.load_file(dbc_file)

# Initialize a list to store fuel data with timestamps
fuel_data = []

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

# GUI Application class
class FuelMonitorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Fuel Monitor")

        # Create UI elements
        self.start_button = ttk.Button(root, text="Start", command=self.start_monitoring)
        self.start_button.grid(row=0, column=0, padx=10, pady=10)

        self.stop_button = ttk.Button(root, text="Stop", command=self.stop_monitoring, state=tk.DISABLED)
        self.stop_button.grid(row=0, column=1, padx=10, pady=10)

        # Adjust label styles to fit fullscreen
        self.fuel_level_label = ttk.Label(root, text="Fuel Level: N/A")
        self.fuel_level_label.config(font=("Helvetica", 36), anchor="center")
        self.fuel_level_label.grid(row=1, column=0, columnspan=2, padx=10, pady=10)

        self.average_label = ttk.Label(root, text="Average Consumption: N/A")
        self.average_label.config(font=("Helvetica", 36), anchor="center")
        self.average_label.grid(row=3, column=0, columnspan=2, padx=10, pady=10)

        self.time_remaining_label = ttk.Label(root, text="Time Remaining: N/A")
        self.time_remaining_label.config(font=("Helvetica", 36), anchor="center")
        self.time_remaining_label.grid(row=4, column=0, columnspan=2, padx=10, pady=10)

        self.running = False
        self.last_valid_average = None  # Store the last valid "Average Consumption" value
        self.last_valid_time_remaining = None  # Store the last valid "Time Remaining" value

        # Automatically start monitoring when the application launches
        self.start_monitoring()

    def start_monitoring(self):
        self.running = True
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.monitor_thread = Thread(target=self.monitor_fuel, daemon=True)
        self.monitor_thread.start()

    def stop_monitoring(self):
        self.running = False
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)

    def monitor_fuel(self):
        try:
            ser = serial.Serial('/dev/ttyUSB0', 115200, timeout=1)
            while self.running:
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

                        # Extract FuelLevel and FuelRate
                        fuellevel = decoded.get("FuelLevel", None)
                        fuelrate = decoded.get("FuelRate", None)

                        if fuellevel is not None:
                            fuellevel_liters = (fuellevel / 100) * 230
                            self.fuel_level_label.config(text=f"Fuel Level: {fuellevel_liters:.2f} L")
                            log_fuel_level(fuellevel)

                        if fuelrate is not None:
                            timestamp = datetime.now()
                            fuel_data.append((fuelrate, timestamp))
                            log_to_file(fuelrate, timestamp)

                        # Calculate average consumption and time remaining
                        average = calculate_average()
                        if average is not None:
                            self.last_valid_average = average  # Update last valid average
                        if self.last_valid_average is not None:
                            self.average_label.config(text=f"Average Consumption: {self.last_valid_average:.3f} L/h")

                        if self.last_valid_average is not None and fuellevel is not None:
                            if fuellevel_liters > 0:
                                time_remaining = fuellevel_liters / self.last_valid_average
                                self.last_valid_time_remaining = time_remaining  # Update last valid time remaining
                            if self.last_valid_time_remaining is not None:
                                self.time_remaining_label.config(text=f"Time Remaining: {self.last_valid_time_remaining:.2f} h")

                    except (ValueError, KeyError):
                        continue
        except serial.SerialException as e:
            print(f"Serial port error: {e}")
        except Exception as e:
            print(f"Unexpected error: {e}")

# Run the application
if __name__ == "__main__":
    root = tk.Tk()
    app = FuelMonitorApp(root)
    # Make the application fullscreen
    root.attributes('-fullscreen', True)
    root.bind('<Escape>', lambda e: root.attributes('-fullscreen', False))
    root.mainloop()