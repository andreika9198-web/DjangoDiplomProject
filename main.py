import network
import time
import urequests
import json
from machine import Pin, ADC
from onewire import OneWire, DS18X20

# ===== НАСТРОЙКИ Wi-Fi =====
SSID = "TP-Link_0260"
PASSWORD = "1457921"

# ===== НАСТРОЙКИ СЕРВЕРА =====
SERVER_URL = "http://192.168.0.106:8000/api/sensor-data/"

# ===== ДАТЧИК ВЛАЖНОСТИ (D34) =====
sensor = ADC(Pin(34))
sensor.atten(ADC.ATTN_11DB)

# Калибровка (подставь свои значения!)
raw_dry = 2951  # Значение в сухом воздухе
raw_wet = 1383  # Значение в воде

# ===== ДАТЧИК ТЕМПЕРАТУРЫ (D33) =====
ow = OneWire(Pin(33))
ds = DS18X20(ow)
roms = ds.roms  # Поиск датчиков


# ===== ПОДКЛЮЧЕНИЕ К WI-FI =====
def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(SSID, PASSWORD)
    timeout = 10
    while timeout > 0:
        if wlan.isconnected():
            print("✅ Wi-Fi подключен")
            print("IP:", wlan.ifconfig()[0])
            return True
        time.sleep(1)
        timeout -= 1
    print("❌ Ошибка подключения к Wi-Fi")
    return False


# ===== ЧТЕНИЕ ВЛАЖНОСТИ =====
def read_humidity():
    raw = sensor.read()
    humidity = ((raw - raw_dry) / (raw_wet - raw_dry)) * 100
    if humidity < 0:
        humidity = 0
    if humidity > 100:
        humidity = 100
    return round(humidity, 1)


# ===== ЧТЕНИЕ ТЕМПЕРАТУРЫ =====
def read_temperature():
    if not roms:
        return None
    ds.start_conversion()
    time.sleep_ms(750)
    temp = ds.read_temp_async()
    if temp is not None:
        return round(temp, 1)
    return None


# ===== ОТПРАВКА ДАННЫХ НА СЕРВЕР =====
def send_data(humidity, temperature):
    data = json.dumps({
        "plant": 1,  # ID растения в Django
        "humidity": humidity,
        "temperature": temperature
    })
    try:
        response = urequests.post(
            SERVER_URL,
            data=data,
            headers={"Content-Type": "application/json"}
        )
        print("📤 Ответ сервера:", response.text)
        response.close()
        return True
    except Exception as e:
        print("❌ Ошибка отправки:", e)
        return False


# ===== ГЛАВНЫЙ ЦИКЛ =====
if not connect_wifi():
    print("⛔ ESP32 перезагрузится через 10 секунд...")
    time.sleep(10)
    machine.reset()

print("🌱 Умный полив запущен!")

while True:
    humidity = read_humidity()
    temperature = read_temperature()

    print(f"🌡️ Влажность: {humidity}%, Температура: {temperature}°C")

    # Отправка на сервер
    if humidity is not None:
        send_data(humidity, temperature)
    else:
        print("⚠️ Ошибка чтения датчика влажности")

    # Пауза 60 секунд перед следующим циклом
    time.sleep(60)