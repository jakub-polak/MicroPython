# This file is executed on every boot (including wake-boot from deepsleep)

import gc
import webrepl
import isp
import machine
import time

webrepl.start()
gc.collect()

# PINS
pin_temp = machine.Pin(2)  # D4
pin_light = machine.ADC(0)  # A0

mig_mig = machine.Pin(12, machine.Pin.OUT) #D6
mig_mig.on()

# CONNECTION
name = 'TP-LINK_95663F'
password = ''
isp.connect_wifi(name, password)

mig_mig.off()

# OneWire
ds, x = isp.connect_onewire(pin_temp)

# MQTT
c = isp.connect_MQTT()

while True:
    c.publish(b"micropython/2", isp.get_temp(ds, x))
    time.sleep_ms(1000)
