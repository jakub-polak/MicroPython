import network
import time
import ds18x20
import onewire
from umqtt.simple import MQTTClient


def blink(pin_name, t1, t2):
    pin_name.on()
    time.sleep_ms(t1)
    pin_name.off()
    time.sleep_ms(t2)


def connect_wifi(wifi_name, wifi_password):
    wifi = network.WLAN(network.STA_IF)
    wifi.active(True)
    wifi.scan()
    wifi.connect(wifi_name, wifi_password)

    print("\nConnecting with {}".format(wifi_name))
    while not wifi.isconnected():
        print('...')
        time.sleep_ms(250)
    else:
        print("Connected with {} successfully!".format(wifi_name))


def connect_onewire(pin_temp):
    ds = ds18x20.DS18X20(onewire.OneWire(pin_temp))
    sens = ds.scan()
    x = sens[0]
    return ds, x


def get_temp(ds, x):
    ds.convert_temp()
    temp = ds.read_temp(x)
    return str(temp)


def get_light(pin_light):
    light = pin_light.read()
    return str(light)


def mean(nums):
    nums = list(map(float, nums))
    return sum(nums) / len(nums)
