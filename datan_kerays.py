import sqlite3
import cantools
import serial
from datetime import datetime, timedelta


# DBC-tiedoston lataus
dbc_file = "GGG.DBC"
db = cantools.database.load_file(dbc_file)

# Tietokannan asetukset
def setup_database():
    conn = sqlite3.connect("data.db")
    cursor = conn.cursor()

    # Luo taulut FuelLevel ja FuelRate
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS fuel_level (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            value REAL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS fuel_rate (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            value REAL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()

def collect_data():
    setup_database()
    conn = sqlite3.connect("data.db")
    cursor = conn.cursor()

    try:
        print("Aloitetaan datan kerääminen...")

        # Sarjaportin avaaminen
        try:
            ser = serial.Serial('/dev/ttyUSB0', 115200, timeout=1)
            print("Yhdistetty sarjaporttiin /dev/ttyUSB0")
        except serial.SerialException as e:
            print(f"Virhe sarjaportin avaamisessa: {e}")
            return

        while True:
            # Poista yli 5 minuuttia vanhat tiedot
            expiration_threshold = datetime.now() - timedelta(minutes=5)
            cursor.execute("DELETE FROM fuel_level WHERE timestamp < ?", (expiration_threshold,))
            cursor.execute("DELETE FROM fuel_rate WHERE timestamp < ?", (expiration_threshold,))
            conn.commit()

            # Lue CAN-viesti
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

                    # Tallenna FuelLevel ja FuelRate
                    fuellevel = decoded.get("FuelLevel", None)
                    fuelrate = decoded.get("FuelRate", None)

                    if fuellevel is not None:
                        fuellevel_liters = (fuellevel / 100) * 230
                        cursor.execute("INSERT INTO fuel_level (value) VALUES (?)", (fuellevel_liters,))

                    if fuelrate is not None:
                        cursor.execute("INSERT INTO fuel_rate (value) VALUES (?)", (fuelrate,))

                    conn.commit()

                except (ValueError, KeyError):
                    continue

    except KeyboardInterrupt:
        print("\nDatan kerääminen keskeytetty käyttäjän toimesta.")
    finally:
        if 'ser' in locals() and ser.is_open:
            ser.close()
            print("Sarjaportti suljettu.")
        conn.close()

if __name__ == "__main__":
    collect_data()