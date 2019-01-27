import gc
import webrepl
from isp import *
import utime
from ntptime import settime
from umqtt.simple import MQTTClient
import machine
import os

webrepl.start()
gc.collect()


#  PINS
pin_temp = machine.Pin(2)  # D4
pin_light = machine.ADC(0)  # A0

mig_mig = machine.Pin(12, machine.Pin.OUT)  # D6
mig_mig.on()

blink(mig_mig, 200, 2000)
blink(mig_mig, 200, 2000)

#  OneWire
ds, x = connect_onewire(pin_temp)
print(ds, x)

# WiFi
name = 'Jakub'
password = '19951995'
connect_wifi(name, password)

#  MQTT
mqtt_client = MQTTClient(client_id="house_1", server="broker.hivemq.com", port=1883, keepalive=0)
mqtt_client.connect()

# topics to response on
topic_temp_out = b'isp2018/1'
topic_light_out = b'isp2018/2'
topic_temp_data_out = b'isp2018/3'
topic_light_data_out = b'isp2018/4'
topic_send_database_out = b'isp2018/8'
topic_send_data24_out = b'isp2018/9'

# topics to subscribe
topic_time_in = 'isp2018/5'
topic_button = 'isp2018/6'
topic_send_database_in = 'isp2018/7'
topic_send_data24_in = 'isp2018/10'


def sub_cb(topic, msg):
    
    if msg != None:
        msg = msg.decode("utf-8")
        topic = topic.decode("utf-8")
        #print("msg: {} - topic: {}".format(msg, topic))

        if topic == topic_button:
            print('\nquery about actual data') 
            print('\tresponse: temp {}, light {}'.format(get_temp(ds, x), get_temp(ds, x)))
            mqtt_client.publish(topic_temp_out, get_temp(ds, x))
            mqtt_client.publish(topic_light_out, get_light(pin_light))
    
        elif topic == topic_time_in:
            print("\nquery about data at {} o'clock'".format(msg))
            
            if msg in data24:
                print('\t response: temp {}, light {}'.format(data24.get(msg)[0], data24.get(msg)[1]))
                mqtt_client.publish(topic_temp_data_out, str(data24.get(msg)[0]))
                mqtt_client.publish(topic_light_data_out, str(data24.get(msg)[1]))
                
            else:
                print('\t response: no data')
                mqtt_client.publish(topic_temp_data_out, 'no data')
                
        elif topic == topic_send_database_in:
            print("\nquery about data in .log file")
            with open('data.log') as data:
                database = data.read()
            mqtt_client.publish(topic_send_database_out, database)
            print("\tdata.log send on topic: topic_send_database_out")
            open('data.log', 'w').close()
            
            
        elif topic == topic_send_data24_in:
            print('\nquery about 24h/(60min/) data')
            str_data24 = str(data24)
            mqtt_client.publish(topic_send_data24_out, str_data24)
            print("\tdata23 dict send on topic: topic_send_data24_out")
                
        time.sleep_ms(200)


mqtt_client.set_callback(sub_cb)

mqtt_client.subscribe(topic_time_in)
mqtt_client.subscribe(topic_button)
mqtt_client.subscribe(topic_send_database_in)
mqtt_client.subscribe(topic_send_data24_in)

# additional variables
minutes_done = list()       # list with measurements in such minutes in current hour
data24 = dict()             # dictionary with averages measurements in last 24 hours
data_temp = list()          # temperature values in current hour
data_light = list()         # light values in current hour


#  time settings
settime()

# main loop
flag = True
seconds_done = list()

while True:

    # set current time
    year, day, month, hour, minute, second, _, _ = utime.localtime()
    hour += 1

    # waiting for messange to send actual indications
    mqtt_client.check_msg()

        

    if second == 1:
        flag = True

    # measurements are taken every k minuts in current hour
    k = 5
    if second not in seconds_done:
        if second % k == 0:
            seconds_done.append(second)
            data_temp.append(get_temp(ds, x))
            data_light.append(get_light(pin_light))
            print("\n{:02d}:{:02d} - measurement".format(minute, second))
            print("\ttemp {}, light {}".format(get_temp(ds, x), get_light(pin_light)))

    # new  hour is coming - add data to dict, file and reset
    if second == 56 and flag:
        print("\n{:02d}:{:02d} - new  minute is coming - add data to dict, file and reset".format(minute, second))
        flag = False

        # average in current hour
        temp_avg = mean(data_temp)
        light_avg = mean(data_light)
        print("\t{:02d}:00 average temp {}, light {}".format(minute, temp_avg, light_avg))

        minute_ = str(minute)
        data24[minute_] = (temp_avg, light_avg)
        
        # adding data into file
        with open('data.log', 'a') as data:
            print("{}-{:02d}-{:02d},{:02d}:{:02d},{},{}".format(year, day, month, hour, minute, temp_avg, light_avg), file=data, end="|")

        
        print("\nAll data:")
        for minute in data24:
            print("\t{:02d}:00 - temp {}, light {}".format(int(minute), data24.get(minute)[0], data24.get(minute)[1]))

        seconds_done = []
        data_temp = []
        

        data_light = []

