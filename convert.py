import requests

def convert_currency(amount: float, from_curr: str, to_curr: str):
    url = f"https://api.exchangerate.host/convert?from={from_curr.upper()}&to={to_curr.upper()}&amount={amount}"
    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        result = data.get("result")
        if result is not None:
            print(f"{amount} {from_curr.upper()} = {result:.4f} {to_curr.upper()}")
        else:
            error_info = data.get("error", {}).get("info", "unknown error")
            print(f"Conversion failed: {error_info}")
    except requests.Timeout:
        print("Currency conversion timeout.")
    except requests.ConnectionError:
        print("Network error while converting currency.")
    except requests.RequestException as e:
        print(f"Conversion error: {e}")
    except ValueError:
        print("Invalid JSON response from exchange rate API.")