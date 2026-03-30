import sqlite3
import time
from datetime import datetime, timedelta

def analyze_data():
    conn = sqlite3.connect("data.db")
    cursor = conn.cursor()
    while True:  # Jatkuva analysointi
        cursor.execute("SELECT * FROM data ORDER BY timestamp DESC LIMIT 5")
        rows = cursor.fetchall()
        if rows:
            print("Latest data:")
            for row in rows:
                print(row)
        else:
            continue

        cursor.execute("SELECT AVG(value) FROM data")
        avg_fuelrate = cursor.fetchone()[0]

        cursor.execute("SELECT value FROM data ORDER BY timestamp DESC LIMIT 1")
        result = cursor.fetchone()
        if result and avg_fuelrate:
            latest_fuellevel = float(result[0])
            remaining_time = avg_fuelrate / latest_fuellevel
            print(f"Polttoaineen keskikulutus jaettuna bensamäärällä: {remaining_time:.2f}")

        time.sleep(4)  # Simuloi analysoinnin viivettä
    conn.close()

if __name__ == "__main__":
    analyze_data()