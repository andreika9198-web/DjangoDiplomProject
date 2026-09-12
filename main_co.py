import network
import time
import urequests
import json
import gc
from machine import Pin, ADC
from onewire import OneWire, DS18X20

# ===== НАСТРОЙКИ =====
SSID = "TP-Link_0260"
PASSWORD = "14579721"
SERVER_URL = "http://192.168.0.106:8000/api/sensor-data/"
STATE_URL = "http://192.168.0.106:8000/api/state/"

# Датчик влажности
sensor = ADC(Pin(34))
sensor.atten(ADC.ATTN_11DB)
raw_dry = 3200
raw_wet = 1700

# Датчик температуры
ow = OneWire(Pin(33))
ds = DS18X20(ow)
roms = ds.roms

# Реле 1 — насос (полив)
relay_pump = Pin(26, Pin.OUT)
relay_pump.value(0)

# Реле 2 — свет
relay_light = Pin(27, Pin.OUT)
relay_light.value(0)

automatic = True


def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(SSID, PASSWORD)
    timeout = 15
    while timeout > 0:
        if wlan.isconnected():
            print("Wi-Fi OK")
            return True
        time.sleep(1)
        timeout -= 1
    print("Wi-Fi Error")
    return False


def read_humidity():
    raw = sensor.read()
    h = ((raw - raw_dry) / (raw_wet - raw_dry)) * 100
    if h < 0:
        h = 0
    if h > 100:
        h = 100
    return round(h, 1)


def read_temperature():
    if not roms:
        return None
    ds.start_conversion()
    time.sleep_ms(750)
    t = ds.read_temp_async()
    if t is not None:
        return round(t, 1)
    return None

def relay_light_control(light_state):
    if light_state:
        relay_light.value(1)
        print("Свет: ВКЛ")
    else:
        relay_light.value(0)
        print("Свет: ВЫКЛ")

def relay_work_automatic():
    h = read_humidity()
    if h > 70:
        relay_pump.value(0)
        print("Насос: ВЫКЛ (влажно)")
        relay_light_control(False)
    else:
        relay_pump.value(1)
        relay_light_control(True)
        print("Насос: ВКЛ (сухо)")


def relay_work_manual(pump_state):
    if pump_state:
        relay_pump.value(1)
        print("Насос: ВКЛ (вручную)")
    else:
        relay_pump.value(0)
        print("Насос: ВЫКЛ (вручную)")

def send_data(h, t):
    gc.collect()
    data = json.dumps({"plant": 1, "humidity": h, "temperature": t})
    try:
        r = urequests.post(SERVER_URL, data=data, headers={"Content-Type": "application/json"}, timeout=5)
        print("Ответ сервера:", r.text)
        r.close()
        return True
    except Exception as e:
        print("Ошибка отправки:", e)
        return False


def get_state_from_server():
    try:
        r = urequests.get(STATE_URL, timeout=5)
        if r.status_code == 200:
            data = r.json()
            r.close()
            return data
        r.close()
    except Exception as e:
        print("Ошибка получения состояния:", e)
    return None


# ===== СТАРТ =====
if connect_wifi():
    print("Умный полив запущен!")
    while True:
        state = get_state_from_server()

        if state:
            automatic = state.get("automatic", True)
            pump = state.get("pump", False)
            light = state.get("light", False)
            print("Состояние:", state)
        else:
            automatic = True
            pump = False
            light = False

        h = read_humidity()
        t = read_temperature()

        # Управление насосом
        if automatic:
            relay_work_automatic()
        else:
            relay_work_manual(pump)
            relay_light_control(light)


        print("Humidity:", h, "Temp:", t)
        send_data(h, t)
        time.sleep(30)
else:
    print("Нет Wi-Fi")