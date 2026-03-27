import sqlite3
import time
import cantools
import serial
from datetime import datetime, timedelta


#datan keräys ja tallennus 

def setup_database():
    conn = sqlite3.connect("data.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            value TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

# Load the DBC file
dbc_file = "GGG.DBC"
db = cantools.database.load_file(dbc_file)

# Asetukset (helposti muokattavissa)
AVERAGE_TIME_WINDOW = 15  # minuuttia
DATA_EXPIRATION_TIME = 15  # minuuttia

def collect_data():
    setup_database()
    try:
        print("Aloitetaan datan kerääminen...")

        # Open the serial port
        try:
            ser = serial.Serial('/dev/ttyUSB0', 115200, timeout=1)
            print("Yhdistetty sarjaporttiin /dev/ttyUSB0")
        except serial.SerialException as e:
            print(f"Virhe sarjaportin avaamisessa: {e}")
            return

        while True:
            # Poista yli 15 minuuttia vanhat tiedot
            expiration_threshold = datetime.now() - timedelta(minutes=DATA_EXPIRATION_TIME)
            cursor.execute("DELETE FROM data WHERE timestamp < ?", (expiration_threshold,))
            conn.commit()

            # Laske keskiarvo viimeisen 15 minuutin ajalta
            average_threshold = datetime.now() - timedelta(minutes=AVERAGE_TIME_WINDOW)
            cursor.execute("SELECT AVG(value) FROM data WHERE timestamp >= ?", (average_threshold,))
            avg_fuelrate = cursor.fetchone()[0]

            if avg_fuelrate:
                print(f"Keskiarvoinen polttoainekulutus viimeisen {AVERAGE_TIME_WINDOW} minuutin ajalta: {avg_fuelrate:.3f} L/h")

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

                    # Log FuelLevel and FuelRate signals
                    fuellevel = decoded.get("FuelLevel", None)
                    fuelrate = decoded.get("FuelRate", None)

                    if fuellevel is not None:
                        fuellevel_liters = (fuellevel / 100) * 230
                        print(f"FuelLevel: {fuellevel_liters:.2f} L")

                    if fuelrate is not None:
                        print(f"FuelRate: {fuelrate:.3f} L/h")

                        # Tallenna FuelRate tietokantaan
                        cursor = conn.cursor()
                        cursor.execute("INSERT INTO data (value) VALUES (?)", (fuelrate,))
                        conn.commit()

                except (ValueError, KeyError):
                    continue

    except KeyboardInterrupt:
        print("\nDatan kerääminen keskeytetty käyttäjän toimesta.")
    finally:
        if 'ser' in locals() and ser.is_open:
            ser.close()
            print("Sarjaportti suljettu.")