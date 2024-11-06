from flask import Flask, jsonify, json, render_template
from flask_cors import CORS
from flask_socketio import SocketIO, emit
import random
import time
import paho.mqtt.client as mqtt
import psycopg2
from datetime import datetime

# Konfigurasi Flask dan SocketIO
app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

@app.route('/')
def index():
    return render_template('index.html')

# Konfigurasi MQTT
MQTT_BROKER = "mqtt.eclipseprojects.io"
MQTT_PORT = 1883
MQTT_TOPIC_SUBSCRIBE = "evomo/telkomiot/voltage"
MQTT_TOPIC_PUBLISH = "evomo/telkomiot/final_data"

# Konfigurasi PostgreSQL
DB_HOST = "34.123.56.222"
DB_PORT = "5432"
DB_NAME = "metrics_data"
DB_USER = "postgres"
DB_PASSWORD = "keren123"

# Koneksi ke PostgreSQL
try:
    conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )
    cursor = conn.cursor()
    print("Koneksi ke database PostgreSQL berhasil.")
except Exception as e:
    print(f"Gagal menghubungkan ke database: {e}")
    exit(1)

# Simulasi data tegangan historis
def generate_voltage_data():
    data = []
    start_time = int(time.time())
    for i in range(100):  # Data untuk 10 titik waktu
        time_point = start_time + i * 60  # waktu bertambah setiap 60 detik
        voltage = round(random.uniform(0, 5), 2)  # Tegangan acak antara 0 dan 5 volt
        data.append({"time": time_point, "voltage": voltage})
    return data

@app.route('/api/voltage', methods=['GET'])
def get_voltage_data():
    # Akses data dari database atau gunakan data simulasi
    # Uncomment bagian ini untuk menggunakan data dari database:
    # cursor.execute("SELECT * FROM energy_data ORDER BY reading_time DESC LIMIT 100")
    # rows = cursor.fetchall()
    # data = [{"time": row[0].timestamp(), "voltage": row[7]} for row in rows]  # row[7] adalah kolom voltage
    data = generate_voltage_data()  # Gunakan data simulasi
    print(data)
    return jsonify(data)

# Callback MQTT untuk menerima pesan
def on_message(client, userdata, msg):
    try:
        # Decode dan load JSON
        payload = json.loads(msg.payload.decode())

        # Ambil data yang dibutuhkan
        data = payload["data"]
        
        reading_time = data.get("reading_time")
        active_energy_import = data.get("active_energy_import")
        active_energy_export = data.get("active_energy_export")
        reactive_energy_import = data.get("reactive_energy_import")
        reactive_energy_export = data.get("reactive_energy_export")
        apparent_energy_import = data.get("apparent_energy_import")
        apparent_energy_export = data.get("apparent_energy_export")
        instantaneous_voltage_L1 = data.get("instantaneous_voltage_L1")
        instantaneous_voltage_L2 = data.get("instantaneous_voltage_L2")
        instantaneous_voltage_L3 = data.get("instantaneous_voltage_L3")
        instantaneous_current_L1 = data.get("instantaneous_current_L1")
        instantaneous_current_L2 = data.get("instantaneous_current_L2")
        instantaneous_current_L3 = data.get("instantaneous_current_L3")
        instantaneous_net_frequency = data.get("instantaneous_net_frequency")
        instantaneous_power_factor = data.get("instantaneous_power_factor")

        # Simpan data ke database
        reading_time_dt = datetime.strptime(reading_time, "%Y-%m-%d %H:%M:%S") if reading_time else None

        # Masukkan data ke dalam tabel PostgreSQL
        cursor.execute("""
            INSERT INTO energy_data (reading_time, active_energy_import, active_energy_export, reactive_energy_import, 
                                     reactive_energy_export, apparent_energy_import, apparent_energy_export)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (reading_time_dt, active_energy_import, active_energy_export, reactive_energy_import, 
              reactive_energy_export, apparent_energy_import, apparent_energy_export))

        # Commit untuk menyimpan perubahan
        conn.commit()
        print("Data berhasil disimpan ke database PostgreSQL.")
        
        # Publikasi data ke mqtt
        payload_to_publish = {
            "reading_time": reading_time,
            "active_energy_import": active_energy_import,
            "active_energy_export": active_energy_export,
            "reactive_energy_import": reactive_energy_import,
            "reactive_energy_export": reactive_energy_export,
            "apparent_energy_import": apparent_energy_import,
            "apparent_energy_export": apparent_energy_export,
            "instantaneous_voltage_L1": instantaneous_voltage_L1,
            "instantaneous_voltage_L2": instantaneous_voltage_L2,
            "instantaneous_voltage_L3": instantaneous_voltage_L3,
            "instantaneous_current_L1": instantaneous_current_L1,
            "instantaneous_current_L2": instantaneous_current_L2,
            "instantaneous_current_L3": instantaneous_current_L3,
            "instantaneous_net_frequency": instantaneous_net_frequency,
            "instantaneous_power_factor": instantaneous_power_factor
        }

        payload_json = json.dumps(payload_to_publish)

        # Publish pesan ke topik "evomo/telkomiot/final_data"
        result = client.publish(MQTT_TOPIC_PUBLISH, payload_json)
        
        # Cek status publish
        if result[0] == 0:
            print(f"Data terkirim ke {MQTT_TOPIC_PUBLISH}: {payload_json}")
        else:
            print("Gagal mengirim data")

    except json.JSONDecodeError:
        print("Error: Payload bukan JSON atau format JSON salah.")
    except KeyError as e:
        print(f"Error: Field yang dibutuhkan tidak ditemukan - {e}")

# Callback MQTT ketika terhubung
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Berhasil terkoneksi ke broker MQTT")
        client.subscribe(MQTT_TOPIC_SUBSCRIBE)
        print(f"Subscribed ke topik: {MQTT_TOPIC_SUBSCRIBE}")
    else:
        print(f"Gagal terkoneksi, return code: {rc}")

# Inisialisasi client MQTT
mqtt_client = mqtt.Client()
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message
mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)

# Memulai loop client MQTT
def mqtt_loop():
    mqtt_client.loop_start()

if __name__ == '__main__':
    socketio.start_background_task(mqtt_client.loop_forever)  # Jalankan loop MQTT di thread terpisah
    socketio.run(app, host='0.0.0.0', port='5000', debug=False)
