import cantools
import serial


dbc_file = "GGG.DBC"  
db = cantools.database.load_file(dbc_file)


ser = serial.Serial('COM3', 115200, timeout=1) 

try:
    while True:
        
        line = ser.readline().decode('ascii', errors='ignore').strip()
        if line:
            
            parts = line.split()
            if len(parts) < 7:
                continue  

            try:
                
                can_id = int(parts[3], 16)  
                data = bytes(int(byte, 16) for byte in parts[5:])  # Data alkaa 6. osasta (indeksi 5)

                # Dekoodaa viesti DBC-tiedoston avulla
                message = db.get_message_by_frame_id(can_id)
                decoded = message.decode(data)

                # Track previous values to print only when a signal changes and is non-zero
                previous_values = {}

                # Filter and print only the specified signals
                signals_to_print = ["ActualEngPercentTorque", "FuelLevel", "EngineSpeed", "InjectionQuantitySetpoint"]
                for signal_name, signal_value in decoded.items():
                    if signal_name in signals_to_print:
                        if signal_value != 0 and (signal_name not in previous_values or previous_values[signal_name] != signal_value):
                            print(f"Signal: {signal_name}, Value: {signal_value}")
                            previous_values[signal_name] = signal_value

            except (ValueError, KeyError):
                # Ohita virheellinen tai tuntematon CAN-ID
                continue

except KeyboardInterrupt:
    print("\nOhjelma keskeytetty käyttäjän toimesta.")
    ser.close()