import sqlite3
import time

def analyze_data():
    conn = sqlite3.connect("data.db")
    cursor = conn.cursor()

    while True:
        # Laske FuelRate:n keskiarvo
        cursor.execute("SELECT AVG(value) FROM fuel_rate")
        avg_fuelrate = cursor.fetchone()[0]

        # Hae viimeiset 5 FuelLevel-arvoa
        cursor.execute("SELECT value FROM fuel_level ORDER BY timestamp DESC LIMIT 5")
        recent_levels = cursor.fetchall()
        if recent_levels:
            avg_fuellevel = sum(row[0] for row in recent_levels) / len(recent_levels)
        else:
            avg_fuellevel = None

        # Laske jäljellä oleva aika
        if avg_fuelrate and avg_fuellevel:
            remaining_time = avg_fuellevel / avg_fuelrate
            print(f"Jäljellä oleva aika: {remaining_time:.2f} tuntia")
        else:
            print("Ei tarpeeksi dataa laskentaan.")

        time.sleep(4)  # Päivitä 4 sekunnin välein

if __name__ == "__main__":
    analyze_data()