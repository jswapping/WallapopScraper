import requests
from config import load_config

WALLAPOP_API = "https://api.wallapop.com/api/v3/search"

HEADERS = {
    "Host": "api.wallapop.com",
    "Connection": "keep-alive",
    "deviceos": "0",
    "sec-ch-ua-platform": '"Windows"',
    "accept-language": "es,es-ES;q=0.9",
    "x-appversion": "88570",
    "sec-ch-ua-mobile": "?0",
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/138.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json, text/plain, */*",
    "x-deviceos": "0",
    "Origin": "https://es.wallapop.com",
    "Referer": "https://es.wallapop.com/",
    "Accept-Encoding": "gzip, deflate, br, zstd"
}

ORDER_OPTIONS = {
    "newest": "newest",
    "price_asc": "price_low_to_high",
    "price_desc": "price_high_to_low",
    "closest": "closest"
}


def build_url(query: str, config: dict) -> str:
    params = {
        "keywords": query.replace(" ", "+"),
        "source": "side_bar_filters",
        "latitude": config.get("latitude", 37),
        "longitude": config.get("longitude", -5),
        "distance_in_km": config.get("distance_km", 50),
        "order_by": ORDER_OPTIONS.get(config.get("order_by", "newest"), "newest"),
    }

    if config.get("min_price") is not None:
        params["min_sale_price"] = config["min_price"]
    if config.get("max_price") is not None:
        params["max_sale_price"] = config["max_price"]

    query_string = "&".join(f"{k}={v}" for k, v in params.items())
    return f"{WALLAPOP_API}?{query_string}"


def fetch_raw(url: str) -> dict | None:
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e:
        print(f"[X] HTTP error: {e}")
    except requests.exceptions.ConnectionError:
        print("[X] Connection error. Check your internet.")
    except requests.exceptions.Timeout:
        print("[X] Request timed out.")
    except Exception as e:
        print(f"[X] Unexpected error: {e}")
    return None


def parse_items(raw_data: dict) -> list:
    items = (
        raw_data
        .get("data", {})
        .get("section", {})
        .get("payload", {})
        .get("items", [])
    )

    results = []
    for item in items:
        try:
            results.append({
                "id": item.get("id"),
                "title": item.get("title"),
                "price": item.get("price", {}).get("amount"),
                "currency": item.get("price", {}).get("currency", "EUR"),
                "city": item.get("location", {}).get("city"),
                "image": item.get("images", [{}])[0].get("urls", {}).get("medium"),
                "url": f"https://es.wallapop.com/item/{item.get('web_slug')}",
                "description": item.get("description", "")[:200]
            })
        except Exception as e:
            print(f"  [!] Skipped one item due to parse error: {e}")

    return results


def search(query: str, config: dict = None) -> list:
    if config is None:
        config = load_config()

    url = build_url(query, config)
    print(f"Fetching: {url[:80]}...")

    raw = fetch_raw(url)
    if raw is None:
        return []

    items = parse_items(raw)
    return items
