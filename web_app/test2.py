from DBcm import UseDatabase
import datetime
import pandas as pd
import paho.mqtt.subscribe as subscribe
import paho.mqtt.publish as publish

data_base = "2019-01-19,15:52,27.1198,72.5|2019-01-19,15:53,27.0417,69.25|2019-01-19,15:54,26.8698,68.8333|2019-01-19,15:55,26.8073,65.9167|2019-01-19,15:56,26.9271,63.5833|2019-01-19,15:57,27.1042,63.4167|2019-01-19,15:58,27.1146,63.9167|2019-01-19,15:59,27.1302,60.75|2019-01-19,16:00,27.0417,43.1667|2019-01-19,16:01,26.8802,30.5|2019-01-19,16:02,26.9844,37.5|2019-01-19,16:03,27.0365,40.25|2019-01-19,16:04,27.0625,40.6667|2019-01-19,16:05,27.0625,39.8333|2019-01-20,11:59,25.875,266.333|2019-01-20,12:00,25.8073,264.167|2019-01-20,12:01,25.8438,263.75|2019-01-20,12:02,25.9271,262.5|2019-01-20,12:03,26.0469,264.75|2019-01-20,12:04,26.151,267.167|2019-01-20,12:05,26.2448,264.75|2019-01-20,12:06,26.3333,261.5|"

data2 = "1500-01-20,12:13,26.7969,319.0|1050-01-20,12:14,26.7708,315.583|"

config = {'db_config': {'host': '127.0.0.1',
                        'user': 'templight',
                        'password': 'agh1995',
                        'database': 'isp2018',
                        }}


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
    publish.single(topic, "Nadaje z WebApp na {}".format(topic), hostname="broker.hivemq.com", retain=True)


def prepare_data(data):
    listed_data = []
    data = data.split('|')
    data.pop()

    for line in data:
        listed_line = line.split(',')
        listed_data.append(listed_line)

    return listed_data


def log_to_database(data):
    with UseDatabase(config['db_config']) as cursor:
        _SQL = """insert into templight_test
                            (date, hour, temp, light)
                            values
                            (%s, %s, %s, %s)"""

        for line in data:
            date = line[0]
            hour = line[1]
            temp = line[2]
            light = line[3]

            cursor.execute(_SQL, (date,
                                  hour,
                                  temp,
                                  light,
                                  ))


def get_data_between(date_from, date_to):
    with UseDatabase(config['db_config']) as cursor:
        _SQL = """select * from templight_test where `date` between (%s) and (%s)"""

        cursor.execute(_SQL, (date_from, date_to))

        contents = cursor.fetchall()
        return contents


date_from_ = datetime.date(2000, 1, 1)
date_to_ = datetime.date(2020, 1, 1)


def db_to_json(data):
    date_hour = []
    temp = []
    light = []

    for measurement in data:
        date = measurement[0]
        hour = measurement[1]
        date_hour.append(str(date) + ' ' + hour)
        temp.append(measurement[2])
        light.append(measurement[3])

    df = pd.DataFrame(
        {'date': date_hour,
         'temp': temp,
         'light': light,
         })

    return df


def wait_msg_database(topic):
    m = subscribe.simple(topic, hostname="broker.hivemq.com", msg_count=1)
    data = m.payload.decode("utf-8")
    print(data)
    return data


send_msg(topic_send_database_in)
data = wait_msg_database(topic_send_database_out)
listed_data = prepare_data(data)
log_to_database(listed_data)