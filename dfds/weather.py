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
        lines = resp.text.strip().splitlines()
        if lines:
            print(lines[0])
        else:
            print(resp.text.strip())
    except requests.RequestException as e:
        print(f"Weather error: {e}")