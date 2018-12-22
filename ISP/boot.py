# This file is executed on every boot (including wake-boot from deepsleep)

import gc
import webrepl
import isp
import machine
from machine import Pin
import time

webrepl.start()
gc.collect()

# PINS
pin_temp = machine.Pin(2)  # D4
pin_light = machine.ADC(0)  # A0

mig_mig = Pin(12, Pin.OUT) #D6
mig_mig.on()

# CONNECTION
name = 'TP-LINK_95663F'
password = ''
isp.connect_wifi(name, password)

mig_mig.off()

# OneWire
ds, x = isp.connect_onewire(pin_temp)

for i in range(2):
    mig_mig.value(1)
    time.sleep_ms(100)
    mig_mig.value(0)
    time.sleep_ms(100)
    mig_mig.value(1)
    time.sleep_ms(100)
    mig_mig.value(0)
    time.sleep_ms(100)
    mig_mig.value(1)
    time.sleep_ms(100)
    mig_mig.value(0)
    time.sleep_ms(2000)

# MQTT
c = isp.connect_MQTT()

for i in range(2):
    mig_mig.value(1)
    time.sleep_ms(100)
    mig_mig.value(0)
    time.sleep_ms(100)
    mig_mig.value(1)
    time.sleep_ms(100)
    mig_mig.value(0)
    time.sleep_ms(100)
    mig_mig.value(1)
    time.sleep_ms(100)
    mig_mig.value(0)
    time.sleep_ms(2000)

while True:
    c.publish(b"micropython/2", isp.get_temp(ds, x))
    time.sleep_ms(1000)

while True:
    mig_mig.value(1)
    time.sleep_ms(100)
    mig_mig.value(0)
    time.sleep_ms(100)
