import requests

COIN_ALIASES = {
    "btc": "bitcoin",
    "eth": "ethereum",
    "bitok": "bitcoin",
    "efir": "ethereum",
}

def get_price(coin_id: str):
    url = f"https://api.coingecko.com/api/v3/simple/price?ids={coin_id}&vs_currencies=usd,rub"
    resp = requests.get(url, timeout=10)
    resp.raise_for_status()
    data = resp.json()
    return data[coin_id]["usd"], data[coin_id]["rub"]

def show_crypto(coin_input: str):
    coin_id = COIN_ALIASES.get(coin_input.lower(), coin_input.lower())
    try:
        usd, rub = get_price(coin_id)
        print(f"{coin_id.upper()}:")
        print(f"  ${usd:,.2f} USD")
        print(f"  {rub:,.2f} RUB")
    except Exception as e:
        print(f"Failed to get data for {coin_input}: {e}")