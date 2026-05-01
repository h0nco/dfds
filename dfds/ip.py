import requests

def public_ip() -> str:
    resp = requests.get('https://api.ipify.org?format=json', timeout=10)
    return resp.json()['ip']

def ip_info(ip: str = None):
    if ip is None:
        try:
            ip = public_ip()
        except Exception as e:
            print(f"Could not determine your public IP: {e}")
            return
    try:
        url = f'http://ip-api.com/json/{ip}?fields=status,country,regionName,city,zip,lat,lon,isp,org,as,query,timezone'
        resp = requests.get(url, timeout=10)
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
    except Exception as e:
        print(f"Failed to retrieve IP information: {e}")