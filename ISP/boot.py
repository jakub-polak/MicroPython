# This file is executed on every boot (including wake-boot from deepsleep)

import gc
import webrepl
from isp import *
import utime
from ntptime import settime
from umqtt.simple import MQTTClient
import machine

webrepl.start()
gc.collect()


#  PINS
pin_temp = machine.Pin(2)  # D4
pin_light = machine.ADC(0)  # A0

mig_mig = machine.Pin(12, machine.Pin.OUT)  # D6
mig_mig.on()

blink(mig_mig, 200, 2000)
blink(mig_mig, 200, 2000)

# topics
# topics
topic_temp_out = b'micropython/1'
topic_light_out = b'micropython/2'
topic_temp_data_out = b'tdo/1'
topic_light_data_out = b'tlo/1'
topic_send_database_out = b'micropython/3'

topic_time_in = b'Oppkk/2'
topic_button = b'micropython/4'
topic_send_database_in = b'micropython/5'

#  WiFi
name = 'TP-LINK_95663F'
password = ''
connect_wifi(name, password)

#  MQTT

mqtt_client = connect_MQTT()

mqtt_client.subscribe(topic_time_in)
mqtt_client.subscribe(topic_button)
mqtt_client.subscribe(topic_send_database_in)

#  OneWire
ds, x = connect_onewire(pin_temp)

# additional variable
minutes_done = list()  # list with measurements in such minutes in current hour
data24 = dict()  # dictionary with averages measurements in last 24 hours
data_temp = list()  # temperature values in current hour
data_light = list()  # light values in current hour

blink(mig_mig, 200, 2000)
blink(mig_mig, 200, 2000)

# sub_cb
def sub_cb(topic, msg):
    if msg != None:
        print(msg.decode("utf-8"), topic.decode("utf-8"))
        msg = msg.decode("utf-8")

        if topic == topic_button:
            mqtt_client.publish(topic_temp_out, get_temp(ds, x))
            mqtt_client.publish(topic_light_out, get_light(pin_light))

        elif topic == topic_time_in:
            hour = int(msg)
            mqtt_client.publish(topic_temp_data_out, data24.get(hour)[0])
            mqtt_client.publish(topic_light_data_out, data24.get(hour)[1])


mqtt_client.set_callback(sub_cb)

blink(mig_mig, 200, 2000)
blink(mig_mig, 200, 2000)

#  time settings
settime()

# main loop
while True:

    # set current time
    date = utime.localtime()
    hour = date[3] + 1
    minute = date[4]

    # waiting for messange to send actual indications
    mqtt_client.wait_msg()

    # measurements are taken every 5 minuts in current hour
    if minute not in minutes_done:
        if minute % 5 == 0:
            minutes_done.append(minute)
            print(minutes_done)  # only to debug

        # new  hour is coming - add data to dict and reset
        if minute == 56:
            temp_avg = mean(data_temp)  # average in current hour
            light_avg = mean(data_light)

            data24[hour] = (temp_avg, light_avg)

            minutes_done = []
            data_temp = []
            data_light = []

mig_mig.value(1)
