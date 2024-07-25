import requests
from geopy.geocoders import Nominatim
from datetime import datetime, timedelta

def weather_query():
    def get_coordinates(city):
        geolocator = Nominatim(user_agent="weather_app")
        location = geolocator.geocode(city)
        if location:
            return location.latitude, location.longitude
        else:
            return None, None

    def get_weather(city, datetime_str, params):
        latitude, longitude = get_coordinates(city)
        if latitude is None or longitude is None:
            return None

        base_url = f"https://api.tomorrow.io/v4/weather/forecast?location={latitude},{longitude}&apikey=7RFBloanzbfhs0UKYPUmww1VlM1P40Nn"

        response = requests.get(base_url)
        if response.status_code == 200:
            data = response.json()
            if 'timelines' in data and 'minutely' in data['timelines']:
                minutely_data = data['timelines']['minutely']
                for entry in minutely_data:
                    if entry['time'] == datetime_str:
                        return entry['values']
            if 'timelines' in data and 'hourly' in data['timelines']:
                hourly_data = data['timelines']['hourly']
                for entry in hourly_data:
                    if entry['time'] == datetime_str:
                        return entry['values']
                return None
            else:
                print("Your inputs are incorrect")
                return None
        else:
            print("Request failed, returning None")
            return None

    def get_location():
        try:
            ipAdd = requests.get('https://api.ipify.org').text
            url = f"https://api.ipfind.com/me?auth=a5e76e2d-3b98-456b-9298-6c6fbd387975&ip={ipAdd}"
            response = requests.get(url)
            data = response.json()
            city = data.get('city')  # Use .get() to safely retrieve 'city' from data
            return city
        except Exception as e:
            print("Something went wrong:", e)
            return None

    now = datetime.now()
    current_date = now.strftime("%Y-%m-%d")
    current_hour = now.hour
    next_hour = (now - timedelta(hours=3)).hour

    city = get_location()
    current_date = (now + timedelta(days=1)).strftime("%Y-%m-%d")
    datetime_str = f"{current_date}T{current_hour}:00:00Z"
    params = ['temperature', 'humidity', 'windSpeed']
    weather_data = get_weather(city, datetime_str, params)
    if weather_data:
        output = f"{city} on {datetime_str.split('T')[0]} "
        for param in params:
            if param in weather_data:
                output += f"{param} is {weather_data[param]}, "
            else:
                output += f"{param} is not available, "
        return output[:-2]  # Remove the last comma and space
    else:
        return f"Weather data not available for {city} at {datetime_str}. Please check input."

# Uncomment the following line to execute the weather_query function directly when running temp2.py
#weather_query()
