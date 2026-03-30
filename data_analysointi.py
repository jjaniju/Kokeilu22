import sqlite3
import time
from datetime import datetime, timedelta

def analyze_data():
    conn = sqlite3.connect("data.db")
    cursor = conn.cursor()
    prev_fuelrate = None  # Track the previous fuel rate
    while True:  # Jatkuva analysointi
        cursor.execute("SELECT AVG(value) FROM data")
        avg_fuelrate = cursor.fetchone()[0]

        cursor.execute("SELECT value FROM data ORDER BY timestamp DESC LIMIT 1")
        result = cursor.fetchone()
        latest_fuellevel = float(result[0]) if result else None

        if avg_fuelrate != prev_fuelrate:  # Print only if the value changes
            print(f"FuelRate Average: {avg_fuelrate:.3f} L/h")
            prev_fuelrate = avg_fuelrate

        if latest_fuellevel is not None:
            print(f"FuelLevel: {latest_fuellevel:.2f} L")

        time.sleep(4)  # Simuloi analysoinnin viivettä
    conn.close()

if __name__ == "__main__":
    analyze_data()