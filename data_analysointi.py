import sqlite3
import time
from datetime import datetime, timedelta

def analyze_data():
    conn = sqlite3.connect("data.db")
    cursor = conn.cursor()
    while True:  # Jatkuva analysointi
        cursor.execute("SELECT * FROM data ORDER BY timestamp DESC LIMIT 5")
        rows = cursor.fetchall()
        print("Latest data:")
        for row in rows:
            print(row)

        average_threshold = datetime.now() - timedelta(minutes=15)
        cursor.execute("SELECT AVG(value) FROM data WHERE timestamp >= ?", (average_threshold,))
        avg_fuelrate = cursor.fetchone()[0]

        cursor.execute("SELECT value FROM data ORDER BY timestamp DESC LIMIT 1")
        latest_fuellevel = cursor.fetchone()[0]

        if avg_fuelrate and latest_fuellevel:
            remaining_time = float(latest_fuellevel) / float(avg_fuelrate)
            print(f"Ennuste: Polttoainetta riittää noin {remaining_time:.2f} tuntia.")

        time.sleep(5)  # Simuloi analysoinnin viivettä
    conn.close()

if __name__ == "__main__":
    analyze_data()