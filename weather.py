import requests

def get_location():
    try:
        response = requests.get('http://ipinfo.io')
        data = response.json()
        location = data['loc'].split(',')
        return location
    except Exception as e:
        print(f"Error getting location: {e}")
        return None

def get_weather(api_key, latitude, longitude):
    base_url = "https://api.weather.com/v3/wx/forecast/daily/3day"
    params = {
        "apiKey": api_key,
        "format": "json",
        "language": "en-US",
        "geocode": f"{latitude},{longitude}",
        "units": "m"
    }
    response = requests.get(base_url, params=params)
    
    if response.status_code == 200:
        try:
            data = response.json()
            weather_info = {
                "day1_forecast": data.get("daypart")[0].get("narrative")[0],
                "day2_forecast": data.get("daypart")[0].get("narrative")[2],
                "day3_forecast": data.get("daypart")[0].get("narrative")[4]
            }
            return weather_info
        except requests.exceptions.JSONDecodeError as e:
            print(f"JSON decode error: {e}")
            print(f"Response content: {response.text}")
            return {"error": "Failed to parse weather data"}
    else:
        print(f"Error fetching weather data: HTTP {response.status_code}")
        print(f"Response content: {response.text}")
        if response.status_code == 401:
            print("Check your API key and permissions.")
        return {"error": "Could not fetch weather data"}

# Example usage:
api_key = "3769d4edebe64b13a9d4edebe6cb138d"  # Ensure this is correct and valid
location = get_location()
if location:
    latitude, longitude = location
    weather_info = get_weather(api_key, latitude, longitude)
    print(weather_info)
else:
    print("Could not determine location")


#3769d4edebe64b13a9d4edebe6cb138d