import requests
import json
from datetime import datetime


def _post_to_discord(webhook_url: str, payload: dict) -> bool:
    try:
        response = requests.post(
            webhook_url,
            data=json.dumps(payload),
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        response.raise_for_status()
        return True
    except requests.exceptions.HTTPError as e:
        print(f"  [X] Discord webhook HTTP error: {e}")
    except Exception as e:
        print(f"  [X] Discord notification failed: {e}")
    return False


def notify_new_items(webhook_url: str, keyword: str, new_items: list, max_price_alert: float = None):
    if not webhook_url or not new_items:
        return

    filtered = new_items
    if max_price_alert is not None:
        filtered = [i for i in new_items if i.get("price") is not None and i["price"] <= max_price_alert]

    if not filtered:
        return

    timestamp = datetime.now().strftime("%d/%m/%Y %H:%M")
    fields = []

    for item in filtered[:10]:
        price_str = f"{item['price']} {item.get('currency', 'EUR')}" if item.get("price") else "Sin precio"
        city_str = item.get("city") or "Desconocida"
        fields.append({
            "name": f"{item['title'][:50]}",
            "value": f"**{price_str}** | {city_str}\n [Ver anuncio]({item['url']})",
            "inline": False
        })

    payload = {
        "embeds": [{
            "title": f"{len(filtered)} nuevo(s) resultado(s) para: `{keyword}`",
            "color": 0x00BFFF,
            "fields": fields[:25],
            "footer": {"text": f"WallapopScraper • {timestamp}"}
        }]
    }

    if _post_to_discord(webhook_url, payload):
        print(f"  [+] Discord: notified {len(filtered)} new items for '{keyword}'.")


def notify_search_summary(webhook_url: str, summary: list):
    if not webhook_url or not summary:
        return

    timestamp = datetime.now().strftime("%d/%m/%Y %H:%M")
    lines = []
    for entry in summary:
        status = "OK" if entry["count"] > 0 else "ERROR"
        lines.append(f"{status} **{entry['keyword']}** — {entry['count']} items")

    payload = {
        "embeds": [{
            "title": "Resumen del scraping",
            "description": "\n".join(lines),
            "color": 0x9B59B6,
            "footer": {"text": f"WallapopScraper • {timestamp}"}
        }]
    }

    _post_to_discord(webhook_url, payload)
    print("  [+] Discord: summary sent.")


def notify_price_drop(webhook_url: str, keyword: str, item: dict, old_price: float, new_price: float):
    if not webhook_url:
        return

    drop = old_price - new_price
    percent = (drop / old_price) * 100
    timestamp = datetime.now().strftime("%d/%m/%Y %H:%M")

    payload = {
        "embeds": [{
            "title": f"Bajada de precio: `{keyword}`",
            "color": 0xFF4500,
            "fields": [
                {"name": "Artículo", "value": item["title"], "inline": False},
                {"name": "Precio anterior", "value": f"{old_price} EUR", "inline": True},
                {"name": "Precio actual", "value": f"{new_price} EUR", "inline": True},
                {"name": "Bajada", "value": f"-{drop:.2f} EUR ({percent:.1f}%)", "inline": True},
                {"name": "Link", "value": f"[Ver anuncio]({item['url']})", "inline": False}
            ],
            "footer": {"text": f"WallapopScraper • {timestamp}"}
        }]
    }

    if _post_to_discord(webhook_url, payload):
        print(f"[+] Discord: price drop alert sent for '{item['title']}'.")


def test_webhook(webhook_url: str) -> bool:
    if not webhook_url:
        print("[!] No webhook URL configured.")
        return False

    payload = {
        "embeds": [{
            "title": "WallapopScraper conectado",
            "description": "El webhook de Discord está funcionando correctamente.",
            "color": 0x2ECC71,
            "footer": {"text": "WallapopScraper • Test"}
        }]
    }

    success = _post_to_discord(webhook_url, payload)
    if success:
        print("[+] Webhook test successful!")
    return success
