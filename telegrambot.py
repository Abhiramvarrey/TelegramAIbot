import telebot
import google.generativeai as ai
from flask import Flask
import requests
from threading import Thread

app = Flask('')


@app.route('/')
def home():
    return "Bot is running!"


def run():
    app.run(host='0.0.0.0', port=8080)


def keep_alive():
    t = Thread(target=run)
    t.start()


# Replace with your actual API key
YOUR_GOOGLE_API_KEY = 'YOUR_API_KEY'
ai.configure(api_key=YOUR_GOOGLE_API_KEY)
model = ai.GenerativeModel('gemini-1.0-pro-latest')

# Replace with your actual Telegram bot token
YOUR_BOT_TOKEN = 'YOUR_BOT_TOKEN'
bot = telebot.TeleBot(YOUR_BOT_TOKEN)

# Replace with your actual News API key
YOUR_NEWS_API_KEY = 'YOUR_NEWS_API_KEY'
NEWS_API_URL = f'https://newsapi.org/v2/everything?q={{query}}&apiKey={YOUR_NEWS_API_KEY}'

def get_weather(location):
    url = f'https://api.openweathermap.org/data/2.5/weather?q=' + location + '&units=metric&appid=YOUR_OPEN_WEATHER_MAP_API_KEY'  # Replace with your OpenWeatherMap API key
    print(url)
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        print(data)
        # Extract coordinates
        coord = data.get('coord', {})
        lon = coord.get('lon', None)
        lat = coord.get('lat', None)

        # Extract weather information
        weather = data.get('weather', [])
        if weather:
            weather_main = weather[0].get('main', None)
            weather_description = weather[0].get('description', None)
        else:
            weather_main = None
            weather_description = None

        # Extract main weather data
        main_data = data.get('main', {})
        temp = main_data.get('temp', None)
        feels_like = main_data.get('feels_like', None)
        temp_min = main_data.get('temp_min', None)
        temp_max = main_data.get('temp_max', None)
        humidity = main_data.get('humidity', None)

        # Extract wind data
        wind_data = data.get('wind', {})
        wind_speed = wind_data.get('speed', None)

        # Extract city name
        city_name = data.get('name', None)

        # Format the text string
        text = ""
        if city_name:
            text += f"Location: {city_name}\n"
        if lat and lon:
            text += f"Coordinates: (Lon: {lon:.4f}, Lat: {lat:.4f})\n"
        if weather_main and weather_description:
            text += f"Weather: {weather_main} ({weather_description})\n"
        if temp is not None:
            text += f"Temperature: {temp:.2f}°C\n"
        if feels_like is not None:
            text += f"Feels Like: {feels_like:.2f}°C\n"
        if temp_min is not None and temp_max is not None:
            text += f"Temp Range: {temp_min:.2f}°C - {temp_max:.2f}°C\n"
        if humidity is not None:
            text += f"Humidity: {humidity}%\n"
        if wind_speed is not None:
            text += f"Wind Speed: {wind_speed:.2f} m/s\n"

        return text
    else:
        return "Error: Could not retrieve weather data."

def get_news(query):
    url = NEWS_API_URL.format(query=query)
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        articles = data['articles'][:5]  # Get top 5 articles
        news_message = '\n\n'.join([
            f"**{article['title']}**\n{article['description']}\n{article['url']}"
            for article in articles
        ])
        print(news_message)
        return news_message
    else:
        return 'Failed to fetch news, use format /news topic'


@bot.message_handler(func=lambda message: True)
def handle_text(message):
    print(message.text)
    if message.text.lower() == '/start' or message.text.lower() == '/hello' or message.text.lower() == '/hi' or message.text.lower() == 'hi':
        bot.reply_to(
            message,
            "Hi there! this bot was created by Varrey Abhiram Sai Ganesh contact @abhiramvarrey else use comands in menu or type your query to respond with ai bot"
        )
    elif '/news' in message.text:
        received_message = message.text.strip('/news ')
        if received_message == "":
            bot.reply_to(message, "please use format /news topic")
        else:
            news_message = get_news(received_message)
            bot.reply_to(message, news_message)
    elif '/weather' in message.text:
        received_message = message.text.strip('/weather ')
        if received_message == "":
            bot.reply_to(message, "please use format /weather cityname")
        else:
            received_message = get_weather(received_message)
            bot.reply_to(message, received_message)
    else:
        response = model.generate_content(message.text)
        bot.reply_to(message, response.text)

if __name__ == '__main__':
    keep_alive()
    bot.infinity_polling()
