import paho.mqtt.publish as publish
import paho.mqtt.subscribe as subscribe

# topics to response on
topic_temp_out = 'isp2018/1'
topic_light_out = 'isp2018/2'
topic_temp_data_out = 'isp2018/3'
topic_light_data_out = 'isp2018/4'
topic_send_database_out = 'isp2018/8'
topic_send_data24_out = 'isp2018/9'

# topics to subscribe
topic_time_in = 'isp2018/5'
topic_button = 'isp2018/6'
topic_send_database_in = 'isp2018/7'
topic_send_data24_in = 'isp2018/10'


def send_msg(topic):
    publish.single(topic, "Nadaje na {}".format(topic), hostname="broker.hivemq.com", retain=True)


def wait_msg_current(topic1_, topic2_):
    m = subscribe.simple([topic1_, topic2_], hostname="broker.hivemq.com", msg_count=2)
    temp = m[0].payload.decode("utf-8")
    light = m[1].payload.decode("utf-8")

    return temp, light


def wait_msg_database(topic):
    m = subscribe.simple(topic, hostname="broker.hivemq.com", msg_count=1)
    data = m.payload.decode("utf-8")
    prepare_data(data)


def prepare_data(data):
    listed_data = []
    data = data.split('|')
    data.pop()
    for line in data:
        listed_line = line.split(',')
        listed_data.append(listed_line)

    print(listed_data)


wait_msg_database(topic_send_database_out)
