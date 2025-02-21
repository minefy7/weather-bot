from config import tg_token, weather_token, weather_url
import telebot, requests
from telebot.types import Message

bot = telebot.TeleBot(token=tg_token)
user_city = {}
@bot.message_handler(commands=['start'])
def start(mess):
    bot.send_message(mess.chat.id, 'Это бот для информации о погоде.'
                                   '\n Погода - погода в вашем городе на данный момент'
                                   '\n Город - выбор города'
                                   '\n Погода на 7 дней вперед - прогноз'
                                   '\n Погода на завтра это погода на завтра')
    create_buttons(mess)




def create_buttons(mess):
    markup = telebot.types.ReplyKeyboardMarkup(row_width=2)
    btn1 = telebot.types.KeyboardButton("Город")
    btn2 = telebot.types.KeyboardButton("Погода")
    btn3 = telebot.types.KeyboardButton("Погода на 7 дней вперед")
    btn4 = telebot.types.KeyboardButton("Погода на завтра")
    markup.add(btn1, btn2, btn3,btn4)
    bot.send_message(mess.chat.id, text="Выберите функцию", reply_markup=markup)
def forecast_days(data, mess:Message):
    city_name = data['location']['name'].capitalize()
    forecast_days_data = data['forecast']['forecastday'][1:]            #[1]['day']
    for forecast_day in forecast_days_data:
        max_temp_c = forecast_day['day']['maxtemp_c']
        min_temp_c = forecast_day['day']['mintemp_c']
        avg_temp_c = forecast_day['day']['avgtemp_c']
        city_info = (f'{city_name} {forecast_day["date"]} \nИнфо:\nМаксимальная температура: {max_temp_c}\nСамая низкая температура:'
                 f'{min_temp_c}\nСредняя температура: {avg_temp_c}' )
        bot.send_message(mess.chat.id, f'Вот информация о погоде\n {city_info}')

def weather(data,mess:Message):
    city_name = data['location']['name'].capitalize()
    temp_c = data['current']['temp_c']
    temp_f = data['current']['temp_f']
    city_info = f'{city_name}\n'
    city_info += f'Инфо:\n'
    city_info += f'Погода в градусах цельсия: {temp_c}\n'
    city_info += f'Погода в фаренгейтах: {temp_f}\n'
    bot.send_message(mess.chat.id, f'Вот информация о погоде в этом городе \n {city_info}')
    bot.send_photo(mess.chat.id, 'http:' + data['current']['condition']['icon'])
@bot.message_handler(func=lambda call: True)
def message_handler(mess):
    if mess.text == 'Город':
        bot.send_message(mess.chat.id, 'Напишите свой город'
                                       '\n пример:Moscow')
        bot.register_next_step_handler(mess, set_city)
    elif mess.text == 'Погода':
        weather_today(mess)
    elif mess.text == 'Погода на 7 дней вперед':
        forecast_7_days(mess)
    elif mess.text == 'Погода на завтра':
        forecast(mess)

def weather_today(mess:Message):
    if not user_city.get(mess.chat.id):
        bot.send_message(mess.chat.id, 'Закрепите ваш город')
        return
    response = requests.get(weather_url + '/current.json' + f'?key={weather_token}' + f'&q={user_city[mess.chat.id]}')
    data = response.json()
    weather(data, mess)
def set_city(mess:Message):
    city = mess.text
    user_city[mess.chat.id] = city
    response = requests.get(weather_url + '/current.json' + f'?key={weather_token}' + f'&q={user_city[mess.chat.id]}')
    data = response.json()
    req_data_error = data.get('error')
    if req_data_error:
        if req_data_error.get('code') == 1006:
            bot.send_message(mess.chat.id, 'Бот не знает этого города, пожалуйста напишите еще раз')
            bot.register_next_step_handler(mess, set_city)
    else:
        bot.send_message(mess.chat.id, 'Ваш город добавлен!')

def forecast_7_days(mess:Message):
    if not user_city.get(mess.chat.id):
        bot.send_message(mess.chat.id, 'Закрепите ваш город')
        return
    response = requests.get(
        weather_url + '/forecast.json' + f'?key={weather_token}' + f'&q={user_city[mess.chat.id]}' + f'&days={8}')
    data = response.json()
    forecast_days(data,mess)
def forecast(mess:Message):
    if not user_city.get(mess.chat.id):
        bot.send_message(mess.chat.id, 'Закрепите ваш город')
        return
    response = requests.get(weather_url + '/forecast.json' + f'?key={weather_token}' + f'&q={user_city[mess.chat.id]}' + f'&days={2}')
    data = response.json()
    req_data_error = data.get('error')
    forecast_days(data, mess)













if __name__ == "__main__":
    bot.polling()