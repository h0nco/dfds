import requests

def public_ip() -> str | None:
    try:
        resp = requests.get('https://api.ipify.org?format=json', timeout=10)
        resp.raise_for_status()
        data = resp.json()
        return data['ip']
    except (requests.RequestException, KeyError, ValueError):
        return None

def ip_info(ip: str = None):
    if ip is None:
        try:
            ip = public_ip()
            if ip is None:
                print("Could not determine your public IP: service unavailable")
                return
        except Exception as e:
            print(f"Could not determine your public IP: {e}")
            return
    try:
        url = f'http://ip-api.com/json/{ip}?fields=status,country,regionName,city,zip,lat,lon,isp,org,as,query,timezone'
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        if data.get('status') == 'fail':
            print(f"Error: {data.get('message', 'unknown')}")
            return
        print(f"IP: {data['query']}")
        print(f"Country: {data.get('country', 'N/A')}")
        print(f"Region: {data.get('regionName', 'N/A')}")
        print(f"City: {data.get('city', 'N/A')}")
        print(f"Zip: {data.get('zip', 'N/A')}")
        print(f"Coordinates: {data.get('lat', 'N/A')}, {data.get('lon', 'N/A')}")
        print(f"ISP: {data.get('isp', 'N/A')}")
        print(f"Organization: {data.get('org', 'N/A')}")
        print(f"AS: {data.get('as', 'N/A')}")
        print(f"Timezone: {data.get('timezone', 'N/A')}")
    except requests.Timeout:
        print("IP information request timed out.")
    except requests.ConnectionError:
        print("Network error while fetching IP information.")
    except requests.RequestException as e:
        print(f"Failed to retrieve IP information: {e}")
    except ValueError:
        print("Invalid JSON response from IP API.")
    except Exception as e:
        print(f"Unexpected error: {e}")