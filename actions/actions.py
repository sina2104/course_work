# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions

from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher


from .funcs import *


class ActionTempTomorrow(Action):

    def name(self) -> Text:
        return "action_weather_temps_tomorrow"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        message = ''
        city_name = tracker.latest_message['entities'][0]['value']
        if find_coordinates(city_name) == None:
            dispatcher.utter_message(text=f'Города "{normalize_city(city_name)}" нет в нашей базе данных!')
            return []
        message += yandex_forecast_specific_day(city_name, 1)
        dispatcher.utter_message(text=message)
        message = open_meteo_forecast_specific_day(city_name, 1)
        dispatcher.utter_message(text='----------------\n')
        dispatcher.utter_message(text=message)
        return []


class ActionTempInNDays(Action):

    def name(self) -> Text:
        return "action_weather_temps_in_N_days"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        # Extract the value of the 'N' entity from the user's message
        message = ''
        n_value = tracker.latest_message['entities'][0]['value']
        try:
            N = int(n_value)
        except ValueError:
            dispatcher.utter_message(text=f'Пожалуйста, сначала напишите название города, а потом количество дней!')
            return []
        city_name = tracker.latest_message['entities'][1]['value']
        if find_coordinates(city_name) == None:
            dispatcher.utter_message(text=f'Города "{normalize_city(city_name)}" нет в нашей базе данных!')
            return []
        elif 0 > N > 6:
            dispatcher.utter_message(text=f'Прогнозы можно получить только до 6 дней!')
            return []
        message += yandex_forecast_specific_day(city_name, N)
        dispatcher.utter_message(text=message)
        message = open_meteo_forecast_specific_day(city_name, N)
        dispatcher.utter_message(text='----------------\n')
        dispatcher.utter_message(text=message)
        return []


class ActionTempsWeek(Action):

    def name(self) -> Text:
        return "action_weather_temps_next_week"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        message = ''        
        dispatcher.utter_message(text='Прогнозы Яндекса":\n')
        city_name = tracker.latest_message['entities'][0]['value']
        if find_coordinates(city_name) == None:
            dispatcher.utter_message(text=f'Города "{normalize_city(city_name)}" нет в нашей базе данных!')
            return []
        message += yandex_forecast_days(city_name, 6)
        dispatcher.utter_message(text=message)
        dispatcher.utter_message(text='----------------\nПрогнозы Open-meteo:\n')
        message = open_meteo_forecast_days(city_name, 6)
        dispatcher.utter_message(text=message)
        return []
