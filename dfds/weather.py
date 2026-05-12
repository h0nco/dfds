import requests

def get_weather(city: str = None):
    url = "https://wttr.in/"
    if city:
        url += city
    params = {
        "format": "%l:+%c+%t+%w+%h+%p",
        "lang": "en",
        "m": ""
    }
    try:
        resp = requests.get(url, params=params, timeout=10)
        resp.raise_for_status()
        text = resp.text.strip()
        if not text:
            print("No weather data received")
            return
        if text.startswith("<"):
            print("Weather service returned HTML (possibly invalid city)")
            return
        lines = text.splitlines()
        if lines:
            print(lines[0])
        else:
            print(text)
    except requests.Timeout:
        print("Weather request timed out. Try again later.")
    except requests.ConnectionError:
        print("Network error while fetching weather.")
    except requests.RequestException as e:
        print(f"Weather error: {e}")
    except Exception as e:
        print(f"Unexpected weather error: {e}")