import sqlite3
import time

def analyze_data():
    conn = sqlite3.connect("data.db")
    cursor = conn.cursor()
    while True:  # Jatkuva analysointi
        cursor.execute("SELECT * FROM data ORDER BY timestamp DESC LIMIT 5")
        rows = cursor.fetchall()
        print("Latest data:")
        for row in rows:
            print(row)
        time.sleep(5)  # Simuloi analysoinnin viivettä
    conn.close()

if __name__ == "__main__":
    analyze_data()