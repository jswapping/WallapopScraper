import requests
from config import load_config

WALLAPOP_ENDPOINT = "https://api.wallapop.com/api/v3/search?"
CONFIG = load_config()

headers = {
    "Host": "api.wallapop.com",
    "Connection": "keep-alive",
    "deviceos": "0",
    "sec-ch-ua-platform": "\"Windows\"",
    "accept-language": "es,es-ES;q=0.9",
    "sec-ch-ua": "\"Not)A;Brand\";v=\"8\", \"Chromium\";v=\"138\", \"Brave\";v=\"138\"",
    "x-appversion": "88570",
    "sec-ch-ua-mobile": "?0",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "x-deviceos": "0",
    "Sec-GPC": "1",
    "Origin": "https://es.wallapop.com",
    "Sec-Fetch-Site": "same-site",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Dest": "empty",
    "Referer": "https://es.wallapop.com/",
    "Accept-Encoding": "gzip, deflate, br, zstd"
}

def get_data(url):
    try: 
        res = requests.get(url, headers=headers, timeout=10)
        res.raise_for_status()
        return res.json()
    except Exception as e:
        print(f"Error making the request. URL: {url} . Status: {res.status_code}. Error Code: {e}")

def get_items(data):
    items = data.get("data", {}).get("section", {}).get("payload", {}).get("items", [])
    results = []
    
    for item in items:
        try:
            results.append({
                "id": item.get("id"),
                "title": item.get("title"),
                "price": item.get("price", {}).get("amount"),
                "currency": item.get("price", {}).get("currency"),
                "city": item.get("location", {}).get("city"),
                "image": item.get("images", [{}])[0].get("urls", {}).get("medium"),
                "url": f"https://es.wallapop.com/item/{item.get('web_slug')}"
            })
        except Exception as e:
            print(f"Error obtaining the data. Code {e}")
            continue

    return results

def scrape_wallapop(query):
    #url = f"https://api.wallapop.com/api/v3/search?keywords={query.replace(' ', '+')}&max_sale_price=600&source=side_bar_filters&latitude=37.339677&longitude=-5.841805&distance_in_km=5"
    
    max_price = CONFIG["max_price"]
    latitude = CONFIG["latitude"]
    longitude = CONFIG["longitude"]
    distance = CONFIG["distance_km"]
    
    url = f"{WALLAPOP_ENDPOINT}keywords={query.replace(' ', '+')}&max_sale_price={max_price}&source=side_bar_filters&latitude={latitude}&longitude={longitude}&distance_in_km={distance}"
    return get_data(url)
