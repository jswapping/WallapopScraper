import os
import json

BASE_DIR = os.path.dirname(__file__)
CONFIG_PATH = os.path.join(BASE_DIR, "config", "config.json")
KEYWORDS_PATH = os.path.join(BASE_DIR,"config", "keywords.json")
RESULTS_DIR = os.path.join(BASE_DIR, "results")
LOGS_DIR = os.path.join(BASE_DIR, "logs")

DEFAULT_CONFIG = {
    "min_price": 0,
    "max_price": 600,
    "latitude": 37.339677,
    "longitude": -5.841805,
    "distance_km": 50,
    "order_by": "newest",
    "discord_webhook_url": "",
    "notify_on_new_items": True,
    "max_price_alert": None,
    "check_interval_minutes": 30
}

def load_config() -> dict:
    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        config = DEFAULT_CONFIG.copy()
        config.update(data)
        return config
    except FileNotFoundError:
        print(f"[!] config.json not found at {CONFIG_PATH}. Using defaults.")
        return DEFAULT_CONFIG.copy()
    except json.JSONDecodeError as e:
        print(f"[!] config.json has invalid JSON: {e}. Using defaults.")
        return DEFAULT_CONFIG.copy()


def save_config(config: dict):
    os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=2)
    print("[✓] Config saved.")


def load_keywords() -> list:
    try:
        with open(KEYWORDS_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, list):
            raise ValueError("keywords.json must be a list.")
        return data
    except FileNotFoundError:
        print(f"[!] keywords.json not found at {KEYWORDS_PATH}. Returning empty list.")
        return []
    except (json.JSONDecodeError, ValueError) as e:
        print(f"[!] Error loading keywords: {e}")
        return []


def save_keywords(keywords: list):
    os.makedirs(os.path.dirname(KEYWORDS_PATH), exist_ok=True)
    with open(KEYWORDS_PATH, "w", encoding="utf-8") as f:
        json.dump(keywords, f, ensure_ascii=False, indent=2)
    print(f"[✓] {len(keywords)} keywords saved.")


def save_results(items: list, keyword: str):
    os.makedirs(RESULTS_DIR, exist_ok=True)
    filename = keyword.replace(" ", "-").lower() + ".json"
    path = os.path.join(RESULTS_DIR, filename)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(items, f, ensure_ascii=False, indent=2)
    return path


def load_previous_results(keyword: str) -> list:
    filename = keyword.replace(" ", "-").lower() + ".json"
    path = os.path.join(RESULTS_DIR, filename)
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []
