from flask import Flask, render_template, request
import requests

app = Flask(__name__)

API_KEY = 'C4CLBymeUAuGVpr6F3pDMbiLF0S5VxAB'
BASE_URL = 'http://dataservice.accuweather.com/'


def get_weather_data(location_key):
    url = f"{BASE_URL}currentconditions/v1/{location_key}?apikey={API_KEY}&language=ru"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()[0]
    else:
        return None


def check_bad_weather(temperature, wind_speed, precipitation_probability):
    if temperature < 0 or temperature > 35:
        return "Плохая погода: экстремальная температура."
    if wind_speed > 50:
        return "Плохая погода: сильный ветер."
    if precipitation_probability > 70:
        return "Плохая погода: высокая вероятность осадков."
    return "Хорошая погода."


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        start_city = request.form['start_city']
        end_city = request.form['end_city']

        start_location_key = get_location_key(start_city)
        end_location_key = get_location_key(end_city)

        start_weather = get_weather_data(start_location_key)
        end_weather = get_weather_data(end_location_key)

        if start_weather and end_weather:
            try:
                start_temp = start_weather['Temperature']['Metric']['Value']
                end_temp = end_weather['Temperature']['Metric']['Value']

                start_wind_speed = start_weather.get('Wind', {}).get('Speed', {}).get('Metric', {}).get('Value', 0)
                end_wind_speed = end_weather.get('Wind', {}).get('Speed', {}).get('Metric', {}).get('Value', 0)

                start_precipitation_prob = 100 if start_weather.get('HasPrecipitation') else 0
                end_precipitation_prob = 100 if end_weather.get('HasPrecipitation') else 0

                start_condition_text = start_weather.get('WeatherText', 'Нет данных')
                end_condition_text = end_weather.get('WeatherText', 'Нет данных')

                start_condition = check_bad_weather(start_temp, start_wind_speed, start_precipitation_prob)
                end_condition = check_bad_weather(end_temp, end_wind_speed, end_precipitation_prob)

                return render_template('result.html',
                                       start_condition=start_condition,
                                       end_condition=end_condition,
                                       start_condition_text=start_condition_text,
                                       end_condition_text=end_condition_text)

            except KeyError as e:
                error_message = f"Ошибка в данных о погоде: {e}"
                return render_template('index.html', error=error_message)
        else:
            error_message = "Ошибка получения данных о погоде. Проверьте названия городов."
            return render_template('index.html', error=error_message)

    return render_template('index.html')


def get_location_key(city_name):
    url = f"{BASE_URL}locations/v1/cities/search?apikey={API_KEY}&q={city_name}&language=ru"
    response = requests.get(url)
    if response.status_code == 200 and response.json():
        return response.json()[0]['Key']
    return None


if __name__ == '__main__':
    app.run(debug=True)