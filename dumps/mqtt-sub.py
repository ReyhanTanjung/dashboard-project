import paho.mqtt.client as mqtt
import psycopg2
import json
from datetime import datetime

# Konfigurasi MQTT
MQTT_BROKER = "mqtt.eclipseprojects.io"
MQTT_PORT = 1883
MQTT_TOPIC_SUBSCRIBE = "evomo/telkomiot/voltage"
MQTT_TOPIC_PUBLISH = "evomo/telkomiot/final_data"

# Konfigurasi PostgreSQL
DB_HOST = "localhost"
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


# Callback ketika berhasil terkoneksi
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Berhasil terkoneksi ke broker MQTT")
        client.subscribe(MQTT_TOPIC_SUBSCRIBE)
        print(f"Subscribed ke topik: {MQTT_TOPIC_SUBSCRIBE}")
    else:
        print(f"Gagal terkoneksi, return code: {rc}")

# Callback ketika menerima pesan dari broker
def on_message(client, userdata, msg):
    print(f"Pesan diterima dari topik {msg.topic}:")
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

        # # Konversi waktu ke format yang dapat disimpan di PostgreSQL
        # reading_time_dt = datetime.strptime(reading_time, "%Y-%m-%d %H:%M:%S") if reading_time else None

        # # Masukkan data ke dalam tabel PostgreSQL
        # cursor.execute("""
        #     INSERT INTO energy_data (reading_time, active_energy_import, active_energy_export, reactive_energy_import, 
        #                              reactive_energy_export, apparent_energy_import, apparent_energy_export)
        #     VALUES (%s, %s, %s, %s, %s, %s, %s)
        # """, (reading_time_dt, active_energy_import, active_energy_export, reactive_energy_import, 
        #       reactive_energy_export, apparent_energy_import, apparent_energy_export))

        # # Commit untuk menyimpan perubahan
        # conn.commit()
        # print("Data berhasil disimpan ke database PostgreSQL.")

        # Format payload untuk publikasi
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

        # Convert payload ke JSON string untuk publikasi
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

# Inisialisasi client MQTT
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

# Koneksi ke broker
print("Menghubungkan ke broker MQTT...")
client.connect(MQTT_BROKER, MQTT_PORT, 60)

# Memulai loop client untuk menunggu pesan
try:
    client.loop_forever()
except KeyboardInterrupt:
    print("Program dihentikan.")
finally:
    # Tutup koneksi database saat program dihentikan
    cursor.close()
    conn.close()
    print("Koneksi ke database PostgreSQL ditutup.")

