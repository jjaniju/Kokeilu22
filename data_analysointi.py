import sqlite3
import time

def analyze_data():
    conn = sqlite3.connect("data.db")
    cursor = conn.cursor()

    try:
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

            # Tarkista, että molemmat arvot ovat kelvollisia
            if avg_fuelrate is not None and avg_fuelrate > 0 and avg_fuellevel is not None:
                remaining_time = avg_fuellevel / avg_fuelrate
                print(f"Jäljellä oleva aika: {remaining_time:.2f} tuntia")
            else:
                if avg_fuelrate is None or avg_fuelrate <= 0:
                    print("Keskiarvoinen kulutus (FuelRate) ei ole saatavilla tai on nolla.")
                if avg_fuellevel is None:
                    print("Viimeisten 5 FuelLevel-arvon keskiarvoa ei voitu laskea.")

            time.sleep(4)  # Päivitä 4 sekunnin välein

    except KeyboardInterrupt:
        print("\nAnalysointi keskeytetty käyttäjän toimesta.")
    finally:
        conn.close()
        print("Tietokantayhteys suljettu.")

if __name__ == "__main__":
    analyze_data()