import serial
import time
import json
import os

# ─── Configuration ───────────────────────────────────────────────────────────
PORT      = "COM5"
BAUDRATE  = 115200
TIMEOUT   = 2
JSON_FILE = "sensor_data.json"

# ─── Connect to ESP32 ────────────────────────────────────────────────────────
try:
    ser = serial.Serial(PORT, BAUDRATE, timeout=TIMEOUT)
    time.sleep(2)
    print(f"✅ Connected to ESP on {PORT} at {BAUDRATE} baud")
    print(f"📁 Data will be saved to: {os.path.abspath(JSON_FILE)}\n")
except serial.SerialException as e:
    print(f"❌ Could not connect to {PORT}: {e}")
    exit(1)

# ─── Save to JSON ─────────────────────────────────────────────────────────────
def save_to_json(turbidity, ph, conductivity, status, timestamp):
    data = {
        "last_updated": timestamp,
        "sensors": {
            "turbidity": {
                "value": turbidity,
                "unit": "Raw ADC"
            },
            "ph": {
                "value": round(ph, 2),
                "unit": "pH"
            },
            "conductivity": {
                "value": conductivity,
                "unit": "Raw ADC"
            },
            "status": status
        }
    }

    with open(JSON_FILE, "w") as f:
        json.dump(data, f, indent=4)

# ─── Print Data ───────────────────────────────────────────────────────────────
def print_sensor_data(turbidity, ph, conductivity, status, timestamp):
    print("\n" + "="*50)
    print(f"🕐 Timestamp        : {timestamp}")
    print(f"🌊 Turbidity        : {turbidity}")
    print(f"🧪 pH Value         : {ph:.2f}")
    print(f"⚡ Conductivity     : {conductivity}")
    print(f"📊 Status           : {status}")
    print("="*50)

# ─── Main Loop ───────────────────────────────────────────────────────────────
print("📡 Reading sensor values... (Press Ctrl+C to stop)\n")

try:
    while True:
        if ser.in_waiting > 0:
            try:
                line = ser.readline().decode("utf-8", errors="ignore").strip()
            except:
                continue

            if not line:
                continue

            print("RAW:", line)  # Debug

            try:
                parts = line.split(",")

                # Expected format:
                # turb_raw, ph_raw, ph_real, cond_raw, status
                if len(parts) != 5:
                    continue

                turbidity    = int(parts[0])
                ph           = float(parts[2])   # ✅ real pH
                conductivity = int(parts[3])
                status       = parts[4]

                timestamp = time.strftime("%Y-%m-%d %H:%M:%S")

                print_sensor_data(
                    turbidity, ph, conductivity, status, timestamp
                )

                save_to_json(
                    turbidity, ph, conductivity, status, timestamp
                )

                print(f"✅ JSON updated → {JSON_FILE}")

            except Exception as e:
                print("⚠️ Parse error:", e)

        time.sleep(0.1)

except KeyboardInterrupt:
    print("\n🛑 Stopped by user.")

finally:
    if 'ser' in locals() and ser.is_open:
        ser.close()
        print(f"🔌 Serial port {PORT} closed.")
