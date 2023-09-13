import RPi.GPIO as GPIO
from time import sleep
import Adafruit_ADS1x15
import Adafruit_DHT
import requests

# Inisialisasi GPIO
GPIO.setmode(GPIO.BCM)

# Inisialisasi sensor HX711
hx = HX711(dout_pin=5, pd_sck_pin=6)
hx.set_scale_ratio(10)  # Ganti scale_ratio dengan nilai kalibrasi Anda
hx.reset()

# Inisialisasi ADC ADS1115
adc = Adafruit_ADS1x15.ADS1115()
GAIN = 1  # Ganti sesuai kebutuhan

# Inisialisasi sensor DHT11
sensor_dht = Adafruit_DHT.DHT11
pin_dht = 23

# Token dan label perangkat Ubidots
TOKEN = "BBFF-ePCYt9XbSRlqKHywBLG3EDoWA03xLZ"
DEVICE_LABEL = "dinda"  # Ganti dengan label perangkat Anda di Ubidots

def get_dht_data():
    humidity, temperature = Adafruit_DHT.read_retry(sensor_dht, pin_dht)
    if humidity is not None:
        return humidity
    else:
        return None

def get_hx_data():
    berat = hx.get_raw_data_mean()
    return berat

def get_ads_data():
    ampere = adc.read_adc(0, gain=GAIN)  # Membaca data ampere dari pin A0 pada ADC ADS1115
    volt = adc.read_adc(1, gain=GAIN)   # Membaca data voltage dari pin A1 pada ADC ADS1115
    return ampere, volt

def update_ubidots(berat, ampere, volt, humidity):
    url = "http://industrial.api.ubidots.com/api/v1.6/devices/{}".format(DEVICE_LABEL)
    headers = {"X-Auth-Token": TOKEN, "Content-Type": "application/json"}

    payload = {
        "sensor-ampere": ampere,
        "sensor-volt": volt,
        "sensor-humidity": humidity
    }

    response = requests.post(url, headers=headers, json=payload)

    if response.status_code == 200:
        print("Data berhasil dikirim ke Ubidots")
    else:
        print("Gagal mengirim data ke Ubidots. Kode status:", response.status_code)

try:
    while True:
        berat = get_hx_data()
        ampere, volt = get_ads_data()
        humidity = get_dht_data()
        
        # Kirim data ke Ubidots
        update_ubidots(berat, ampere, volt, humidity)
        
        sleep(1)

except KeyboardInterrupt:
    GPIO.cleanup()
    print("Program terminated.")
