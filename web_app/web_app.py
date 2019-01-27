from flask import Flask, render_template, request
import paho.mqtt.publish as publish
import paho.mqtt.subscribe as subscribe
from DBcm import UseDatabase
import plotly
import plotly.graph_objs as go
import pandas as pd
import json


app = Flask(__name__)

app.config['db_config'] = {'host': '127.0.0.1',
                           'user': 'templight',
                           'password': 'agh1995',
                           'database': 'isp2018',
                           }

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


@app.route('/')
@app.route('/entry')
def entry_page():
    send_msg(topic_button)
    light, temp = wait_msg_current(topic_temp_out, topic_light_out)
    # temp = 0
    # light = 0
    return render_template('entry.html',
                           the_title='Bezprzewodowy system do pomiaru natężenia światła i temperatury',
                           cur_temp=temp,
                           cur_light=light)


@app.route('/database_view')
def view_database():
    with UseDatabase(app.config['db_config']) as cursor:
        _SQL = """select date, hour, temp, light from templight_test"""

        cursor.execute(_SQL)
        contents = cursor.fetchall()

    titles = ('Data', 'Godzina', 'Temperatura', 'Natezenie swiatla')

    return render_template('viewlog.html',
                           the_title='Widok logu',
                           the_row_titles=titles,
                           the_data=contents, )


@app.route('/database_update')
def update_database():
    send_msg(topic_send_database_in)
    data = wait_msg_database(topic_send_database_out)
    listed_data = prepare_data(data)
    log_to_database(listed_data)

    return render_template('todb.html')


@app.route('/plot_database', methods=['POST'])
def plot_database():
    date_from = request.form['date_from']
    date_to = request.form['date_to']

    data_db = get_data_between(date_from, date_to)
    data_pd = db_to_pd(data_db)

    plotek = create_plot(data_pd)
    return render_template('plotek.html', plot=plotek)


@app.route('/swiatelko', methods=['POST'])
def plot_database2():
    date_from = request.form['date_from']
    date_to = request.form['date_to']

    data_db = get_data_between(date_from, date_to)
    data_pd = db_to_pd(data_db)

    plotek = create_plot(data_pd)
    return render_template('plotek.html', plot=plotek)


def send_msg(topic):
    publish.single(topic, "Nadaje z WebApp na {}".format(topic), hostname="broker.hivemq.com", retain=True)


def wait_msg_current(topic1_, topic2_):
    m = subscribe.simple([topic1_, topic2_], hostname="broker.hivemq.com", msg_count=2)
    light = m[0].payload.decode("utf-8")
    temp = m[1].payload.decode("utf-8")

    return light, temp


def wait_msg_database(topic):
    m = subscribe.simple(topic, hostname="broker.hivemq.com", msg_count=1)
    data = m.payload.decode("utf-8")
    print(data)
    return data


def prepare_data(data):
    listed_data = []
    data = data.split('|')
    data.pop()

    for line in data:
        listed_line = line.split(',')
        listed_data.append(listed_line)

    return listed_data


def log_to_database(data):
    with UseDatabase(app.config['db_config']) as cursor:
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
    with UseDatabase(app.config['db_config']) as cursor:
        _SQL = """select * from templight_test where `date` between (%s) and (%s)"""

        cursor.execute(_SQL, (date_from, date_to))
        contents = cursor.fetchall()

        return contents


def db_to_pd(data):
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


def create_plot(data_pd):
    df = data_pd
    data1 = [go.Scatter(x=df['date'], y=df['temp'])]

    graph_json = json.dumps(data1, cls=plotly.utils.PlotlyJSONEncoder)

    return graph_json


if __name__ == '__main__':
    app.run()
