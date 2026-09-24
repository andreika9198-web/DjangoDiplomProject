# import network
# import time
# import urequests
# import json
# import gc
# from machine import Pin, ADC
# from onewire import OneWire, DS18X20
#
# # ===== SETTINGS =====
# SSID = "TP-Link_0260"
# PASSWORD = "14579721"
# SERVER_URL = "http://192.168.0.103:8000/api/sensor-data/"
# STATE_URL = "http://192.168.0.103:8000/api/state/"
# LOG_URL = "http://192.168.0.103:8000/api/watering-log/"
# DEVICE_ID = 1
#
# # Humidity sensor
# sensor = ADC(Pin(34))
# sensor.atten(ADC.ATTN_11DB)
# raw_dry = 3200
# raw_wet = 1700
#
# # Temperature sensor
# ow = OneWire(Pin(33))
# ds = DS18X20(ow)
# roms = ds.roms
#
# # Relay 1 - pump
# relay_pump = Pin(26, Pin.OUT)
# relay_pump.value(0)
#
# # Relay 2 - light
# relay_light = Pin(25, Pin.OUT)
# relay_light.value(0)
#
# automatic = True
# is_watering = False
# start_time = 0
# start_time_str = ""
#
#
# def connect_wifi():
#     wlan = network.WLAN(network.STA_IF)
#     wlan.active(True)
#     wlan.connect(SSID, PASSWORD)
#     timeout = 15
#     while timeout > 0:
#         if wlan.isconnected():
#             print("Wi-Fi OK")
#             return True
#         time.sleep(1)
#         timeout -= 1
#     print("Wi-Fi Error")
#     return False
#
#
# def read_humidity():
#     raw = sensor.read()
#     h = ((raw - raw_dry) / (raw_wet - raw_dry)) * 100
#     if h < 0:
#         h = 0
#     if h > 100:
#         h = 100
#     return round(h, 1)
#
#
# def read_temperature():
#     if not roms:
#         return None
#
#     ds.start_conversion()
#     time.sleep_ms(750)
#     t = ds.read_temp_async()
#     if t is not None:
#         return round(t, 1)
#     return None
#
#
# def relay_light_control(light_state):
#     if light_state:
#         relay_light.value(1)
#         print("Light: ON")
#     else:
#         relay_light.value(0)
#         print("Light: OFF")
#
#
# def start_watering(source='auto'):
#     """Start watering (pump only!)"""
#     global is_watering, start_time, start_time_str
#     if is_watering:
#         return
#     is_watering = True
#     start_time = time.time()
#
#     now = time.localtime()
#     start_time_str = "{:02d}:{:02d}:{:02d}".format(now[3], now[4], now[5])
#
#     relay_pump.value(1)
#     print("Watering START ({}) at {}".format(source, start_time_str))
#
#
# def stop_watering(source='auto'):
#     """Stop watering (pump only!)"""
#     global is_watering, start_time_str
#     if not is_watering:
#         return
#     is_watering = False
#     end_time = time.time()
#     duration = int(end_time - start_time)
#
#     now = time.localtime()
#     end_time_str = "{:02d}:{:02d}:{:02d}".format(now[3], now[4], now[5])
#
#     relay_pump.value(0)
#
#     print("Watering STOP at {} ({} sec)".format(end_time_str, duration))
#
#     send_watering_log(duration, source, start_time_str, end_time_str)
#
#
# def relay_work_automatic():
#     """Automatic mode"""
#     h = read_humidity()
#     if h < 30:
#         start_watering('auto')
#     elif h > 70:
#         stop_watering('auto')
#
#     if is_watering:
#         relay_light.value(1)  # light ON with watering
#         print("Light: ON (auto)")
#     else:
#         relay_light.value(0)  # light OFF
#         print("Light: OFF (auto)")
#
#
# def relay_work_manual(pump_state):
#     """Manual mode (pump and light)"""
#     if pump_state:
#         start_watering('manual')
#     else:
#         stop_watering('manual')
#
#
# def send_data(h, t):
#     gc.collect()
#     data = json.dumps({"device": DEVICE_ID, "humidity": h, "temperature": t})
#     try:
#         r = urequests.post(SERVER_URL, data=data, headers={"Content-Type": "application/json"}, timeout=5)
#         print("Server:", r.text)
#         r.close()
#     except Exception as e:
#         print("Send error:", e)
#
#
# def send_watering_log(duration, source='auto', start_str='', end_str=''):
#     gc.collect()
#     data = json.dumps({
#         "device": DEVICE_ID,
#         "duration": duration,
#         "source": source,
#         "start_watering_time": start_str,
#         "end_watering_time": end_str,
#     })
#     try:
#         r = urequests.post(LOG_URL, data=data, headers={"Content-Type": "application/json"}, timeout=5)
#         print("Log sent:", r.text)
#         r.close()
#     except Exception as e:
#         print("Log error:", e)
#
#
# def get_state_from_server():
#     try:
#         r = urequests.get(STATE_URL, timeout=5)
#         if r.status_code == 200:
#             data = r.json()
#             r.close()
#             return data
#         r.close()
#     except Exception as e:
#         print("State error:", e)
#     return None
#
#
# # ===== START =====
# if connect_wifi():
#     print("Smart watering started!")
#     while True:
#         state = get_state_from_server()
#
#         if state:
#             automatic = state.get("automatic", True)
#             pump = state.get("pump", False)
#             light = state.get("light", False)
#             print("State:", state)
#         else:
#             automatic = True
#             pump = False
#             light = False
#
#         h = read_humidity()
#         t = read_temperature()
#
#         if automatic:
#             relay_work_automatic()
#         else:
#             relay_work_manual(pump)
#             relay_light_control(light)
#
#         print("Humidity:", h, "Temp:", t)
#         send_data(h, t)
#         time.sleep(10)
# else:
#     print("No Wi-Fi")
