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

def get_hourly_forecast(api_key, latitude, longitude, duration="2day"):
    base_url = f"https://api.weather.com/v3/wx/forecast/hourly/{duration}"
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
            return data
        except requests.exceptions.JSONDecodeError as e:
            print(f"JSON decode error: {e}")
            print(f"Response content: {response.text}")
            return {"error": "Failed to parse hourly forecast data"}
    else:
        print(f"Error fetching hourly forecast data: HTTP {response.status_code}")
        print(f"Response content: {response.text}")
        if response.status_code == 401:
            print("Check your API key and permissions.")
        return {"error": "Could not fetch hourly forecast data"}

# Example usage:
api_key = "3769d4edebe64b13a9d4edebe6cb138d"  # Your provided API key
location = get_location()
if location:
    latitude, longitude = location
    hourly_forecast_info = get_hourly_forecast(api_key, latitude, longitude, duration="2day")
    if isinstance(hourly_forecast_info, dict) and "error" in hourly_forecast_info:
        print(hourly_forecast_info["error"])
    else:
        print("Hourly Forecast Information:")
        for time, precip_chance in zip(hourly_forecast_info['validTimeLocal'], hourly_forecast_info['precipChance']):
            print(f"Time: {time}, Precipitation Chance: {precip_chance}%")
else:
    print("Could not determine location")
