import requests

def convert_currency(amount: float, from_curr: str, to_curr: str):
    url = f"https://api.exchangerate.host/convert?from={from_curr.upper()}&to={to_curr.upper()}&amount={amount}"
    resp = requests.get(url, timeout=10)
    resp.raise_for_status()
    data = resp.json()
    result = data.get("result")
    if result is not None:
        print(f"{amount} {from_curr.upper()} = {result:.4f} {to_curr.upper()}")
    else:
        print("Conversion failed")