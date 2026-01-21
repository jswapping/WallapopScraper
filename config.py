import os
import json

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "config" ,"config.json")
KEYWORDS_PATH = os.path.join(os.path.dirname(__file__), "config" ,"keywords.json")
RESULTS_PATH = os.path.join(os.path.dirname(__file__), "results")

def check_file(path):
    if not os.path.exists(path):
        print(f"File {path} not found. Creating...")
        os.mkdir(path)
    

def load_config():
    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as file:
            config = json.load(file)
            return config
    except Exception:
        config = {}

    return {
        "min_price" : config.get("min_price"),
        "max_price": config.get("max_price"),
        "latitude": config.get("latitude"),
        "longitude": config.get("longitude"),
        "distance_km": config.get("longitude"),
        "relevance": config.get("relevance")
    }

def load_keywords():
    check_file(KEYWORDS_PATH)

    try:
        with open(KEYWORDS_PATH, "r" , encoding="utf-8") as file:
            data = json.load(file)
            if not isinstance(data, list):
                raise ValueError("Lista no encontrada")
            return data
    except json.JSONDecodeError as e:
        print(f"Incorrect JSON format. {e}")
        return []
    

def save_data(wallapop_data, keyword):
    os.makedirs(RESULTS_PATH, exist_ok=True)

    products_path = os.path.join(RESULTS_PATH, f"{keyword.replace(" ", "-")}.json")

    with open(products_path, "w", encoding="utf-8") as file:
        json.dump(wallapop_data, file, ensure_ascii=False, indent=2)

    
