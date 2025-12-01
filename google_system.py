import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GOOGLE_CSE_ID = os.getenv("GOOGLE_CSE_ID")
NEWS_API_KEY = os.getenv("NEWS_API_KEY")
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")

def perform_google_search(query):
    """
    Searches Google using the Custom Search JSON API.
    Returns a summary string of the top result.
    """
    if not GOOGLE_API_KEY or not GOOGLE_CSE_ID:
        return "Google API keys are missing. Please check your configuration."

    url = "https://www.googleapis.com/customsearch/v1"
    params = {
        "key": GOOGLE_API_KEY,
        "cx": GOOGLE_CSE_ID,
        "q": query,
        "num": 1
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()

        if "items" in data:
            first_result = data["items"][0]
            title = first_result.get("title", "No title")
            snippet = first_result.get("snippet", "No snippet available.")
            return f"Here is what I found: {title}. {snippet}"
        else:
            return "I couldn't find any results for that query."

    except Exception as e:
        print(f"Google Search Error: {e}")
        return "Sorry, I encountered an error while searching Google."

def get_top_news():
    """
    Fetches top headlines using NewsAPI.
    Returns a list of strings (headlines).
    """
    if not NEWS_API_KEY:
        return ["News API key is missing."]

    url = "https://newsapi.org/v2/top-headlines"
    params = {
        "country": "us", # Default to US, can be changed
        "apiKey": NEWS_API_KEY,
        "pageSize": 5
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()

        if data.get("status") == "ok":
            articles = data.get("articles", [])
            headlines = []
            for article in articles:
                source = article["source"]["name"]
                title = article["title"]
                headlines.append(f"{source}: {title}")
            
            if not headlines:
                return ["No news headlines found at the moment."]
            return headlines
        else:
            return ["Could not fetch news at this time."]

    except Exception as e:
        print(f"News API Error: {e}")
        return ["Sorry, I encountered an error while fetching the news."]

def get_weather(city):
    """
    Fetches current weather for a city using OpenWeatherMap.
    Returns a summary string.
    """
    if not WEATHER_API_KEY:
        return "Weather API key is missing."

    url = "http://api.openweathermap.org/data/2.5/weather"
    params = {
        "q": city,
        "appid": WEATHER_API_KEY,
        "units": "metric" # Use metric by default
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()

        weather_desc = data["weather"][0]["description"]
        temp = data["main"]["temp"]
        feels_like = data["main"]["feels_like"]
        humidity = data["main"]["humidity"]

        return f"The weather in {city} is currently {weather_desc} with a temperature of {temp} degrees Celsius. It feels like {feels_like} degrees. Humidity is at {humidity} percent."

    except Exception as e:
        print(f"Weather API Error: {e}")
        return f"Sorry, I couldn't get the weather for {city}. Please check the city name."
