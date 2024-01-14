import pymorphy2
from bs4 import BeautifulSoup as our_BS
import json
import requests
from translate import Translator

morph = pymorphy2.MorphAnalyzer()

def normalize_city(city_name):
    parsed_city = morph.parse(city_name)
    normalized_city = parsed_city[0].normal_form
    return normalized_city

def find_coordinates(city_name):
    file_path = '/mnt/c/Users/sinaa/Downloads/rasa-bot/course_work/cities.json'
    with open(file_path, 'r', encoding='utf-8-sig') as file:
        cities_data = json.load(file)
    normalized_city_name = normalize_city(city_name) 
    if normalized_city_name in cities_data:
        coordinates = cities_data[normalized_city_name]
        return coordinates
    else:
        return None 
def yandex_forecast_days(city_name, days_num):
    coordinates = find_coordinates(city_name)
    if coordinates == None:
        return 0
    elif days_num > 6:
        return 1
    request = requests.get(f"https://www.yandex.com/weather/segment/details?offset=0&lat={coordinates['latitude']}&lon={coordinates['longitude']}&geoid=213&limit=10", headers = {'User-Agent':'Mozilla/5.0'})
    soup = our_BS(request.content, 'lxml')
    translator= Translator(from_lang="english", to_lang="russian")
    days = 0
    message = ''
    for card in soup.select('.card:not(.adv)'):
        date = ' '.join([i.text for i in card.select('[class$=number],[class$=month]')])
        if date != '':
            message += f'{translator.translate(date)}\n'
        temps = list(zip(
                        [i.text for i in card.select('.weather-table__daypart')]
                        , [i.text for i in card.select('.weather-table__body-cell_type_feels-like .temp__value')]
                        , [i.text for i in card.select('.weather-table__body-cell_type_humidity')] 
                        , [i.text for i in card.select('.weather-table__body-cell_type_condition')]
                        , [i.text for i in card.select('.weather-table__body-cell_type_wind .wind-speed')]
                    ))   
        for i in temps:
            if i[0] != 'day':
                message += f'{translator.translate(i[0])}: {i[1]}° | Влажность:{i[2]} | Погодные условия: {translator.translate(i[3])} | Скорость ветра:{i[4]} m/c\n'
        if days > days_num:
            break
        days += 1
    return message

def yandex_forecast_specific_day(city_name, n_days):
    coordinates = find_coordinates(city_name)
    if coordinates == None:
        return 0
    elif n_days > 6:
        return 1
    request = requests.get(f"https://www.yandex.com/weather/segment/details?offset=0&lat={coordinates['latitude']}&lon={coordinates['longitude']}&geoid=213&limit=10", headers = {'User-Agent':'Mozilla/5.0'})
    soup = our_BS(request.content, 'lxml')
    translator= Translator(from_lang="english", to_lang="russian")
    message = ''
    cards = soup.select('.card:not(.adv)')
    correct_cards = []
    for i in range(len(cards)):
        if ' '.join([i.text for i in cards[i].select('[class$=number],[class$=month]')]) != '':
            correct_cards.append(cards[i])
    card = correct_cards[n_days]
    date = ' '.join([i.text for i in card.select('[class$=number],[class$=month]')])
    message += f'Прогнозы Яндекса на {translator.translate(date.split()[1])} {date.split()[0]}:\n'
    temps = list(zip(
                    [i.text for i in card.select('.weather-table__daypart')]
                    , [i.text for i in card.select('.weather-table__body-cell_type_feels-like .temp__value')]
                    , [i.text for i in card.select('.weather-table__body-cell_type_humidity')] 
                    , [i.text for i in card.select('.weather-table__body-cell_type_condition')]
                    , [i.text for i in card.select('.weather-table__body-cell_type_wind .wind-speed')]
                    ))  

    for i in temps:
        if i[0] != 'day':
            message += f'{translator.translate(i[0])}: {i[1]}° | Влажность: {i[2]} | Погодные условия: {translator.translate(i[3])} | Скорость ветра:{i[4]} m/c\n'
    return message
                    
def open_meteo_forecast_specific_day(city_name, n_days):
    coordinates = find_coordinates(city_name)
    if coordinates == None:
        return 
    elif n_days > 6:
        return 1
    message = ''
    try:
        request = requests.get(f"https://api.open-meteo.com/v1/forecast?latitude={coordinates['latitude']}&longitude={coordinates['longitude']}&daily=temperature_2m_max,temperature_2m_min,sunrise,sunset,rain_sum,snowfall_sum,wind_speed_10m_max&wind_speed_unit=ms&forecast_days=7", headers = {'User-Agent':'Mozilla/5.0'})
    except requests.exceptions.HTTPError as errh:
        return f"HTTP Error: {errh}" 
    except requests.exceptions.ConnectionError as errc:
        return f"Error Connecting: {errc}"
    except requests.exceptions.Timeout as errt:
        return f"Timeout Error: {errt}"
    except requests.exceptions.RequestException as err:
        return f"Request Error: {err}"
    soup = our_BS(request.content, 'lxml')
    json_soup = json.loads(soup.find('p').string)
    daily_data = json_soup.get('daily', {})
    time_data = daily_data.get('time', [])
    max_temp_data = daily_data.get('temperature_2m_max', [])
    min_temp_data = daily_data.get('temperature_2m_min', [])
    sunrise_data = daily_data.get('sunrise', [])
    sunset_data = daily_data.get('sunset', [])
    rain_sum_data = daily_data.get('rain_sum', [])
    snowfall_sum_data = daily_data.get('snowfall_sum', [])
    wind_speed_max_data = daily_data.get('wind_speed_10m_max', [])

    message += f"Прогнозы open-meteo на {time_data[n_days]}:\nМин темп: {min_temp_data[n_days]}° | Макс темп:{max_temp_data[n_days]}° \nСумма суточного дождя: {rain_sum_data[n_days]} mm |Сумма суточного снега:{snowfall_sum_data[n_days]} mm| Скорость ветра: {wind_speed_max_data[n_days]} m/s\nРассвет:{sunrise_data[n_days][-5:]} | Закат: {sunset_data[n_days][-5:]}\n"
            
    return message

def open_meteo_forecast_days(city_name, days_num):
    coordinates = find_coordinates(city_name)
    if coordinates == None:
        return 0
    elif days_num > 6:
        return 1
    message = ''
    try:
        request = requests.get(f"https://api.open-meteo.com/v1/forecast?latitude={coordinates['latitude']}&longitude={coordinates['longitude']}&daily=temperature_2m_max,temperature_2m_min,sunrise,sunset,rain_sum,snowfall_sum,wind_speed_10m_max&wind_speed_unit=ms&forecast_days=7", headers = {'User-Agent':'Mozilla/5.0'})
    except requests.exceptions.HTTPError as errh:
        return f"HTTP Error: {errh}" 
    except requests.exceptions.ConnectionError as errc:
        return f"Error Connecting: {errc}"
    except requests.exceptions.Timeout as errt:
        return f"Timeout Error: {errt}"
    except requests.exceptions.RequestException as err:
        return f"Request Error: {err}"    
    soup = our_BS(request.content, 'lxml')
    json_soup = json.loads(soup.find('p').string)
    daily_data = json_soup.get('daily', {})
    time_data = daily_data.get('time', [])
    max_temp_data = daily_data.get('temperature_2m_max', [])
    min_temp_data = daily_data.get('temperature_2m_min', [])
    sunrise_data = daily_data.get('sunrise', [])
    sunset_data = daily_data.get('sunset', [])
    rain_sum_data = daily_data.get('rain_sum', [])
    snowfall_sum_data = daily_data.get('snowfall_sum', [])
    wind_speed_max_data = daily_data.get('wind_speed_10m_max', [])

    for i in range(days_num):
        message += f"{time_data[i]}:\nМин темп: {min_temp_data[i]}° | Макс темп:{max_temp_data[i]}° \nСумма суточного дождя: {rain_sum_data[i]} mm |Сумма суточного снега:{snowfall_sum_data[i]} mm| Скорость ветра: {wind_speed_max_data[i]} m/s\nРассвет:{sunrise_data[i][-5:]} | Закат: {sunset_data[i][-5:]}\n"
            
    return message