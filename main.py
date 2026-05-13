import time
import sys
from scraper import search
from notifier import notify_new_items, notify_search_summary, notify_price_drop, test_webhook
from config import (
    load_config, save_config,
    load_keywords, save_keywords,
    save_results, load_previous_results,
    RESULTS_DIR
)
import os
import json


def clear():
    os.system("cls" if os.name == "nt" else "clear")


def print_header():
    print("=" * 55)
    print("        WallapopScraper  —  Menu Principal")
    print("=" * 55)


def print_item(item: dict, index: int = None):
    prefix = f"  [{index}]" if index is not None else "  •"
    price = f"{item['price']} {item.get('currency', 'EUR')}" if item.get("price") else "Sin precio"
    city = item.get("city") or "—"
    print(f"{prefix} {item['title'][:45]}")
    print(f"        PRICE: {price}  | CITY: {city}")
    print(f"        URL: {item['url']}")
    print()


def run_scrape_all(config: dict, keywords: list, notify: bool = True):
    if not keywords:
        print("[!] No keywords configured. Add some first.")
        return

    webhook_url = config.get("discord_webhook_url", "")
    max_price_alert = config.get("max_price_alert")
    summary = []

    print(f"\n[*] Scraping {len(keywords)} keyword(s)...\n")

    for entry in keywords:
        query = entry["query"]
        category = entry.get("category", "—")
        print(f"  '{query}' ({category})")

        previous = load_previous_results(query)
        previous_ids = {item["id"] for item in previous if item.get("id")}

        items = search(query, config)
        new_items = [i for i in items if i.get("id") not in previous_ids]

        if items:
            save_results(items, query)

        print(f"     Found {len(items)} items | {len(new_items)} new\n")
        summary.append({"keyword": query, "count": len(items), "new": len(new_items)})

        if notify and webhook_url and new_items:
            notify_new_items(webhook_url, query, new_items, max_price_alert)

        if notify and webhook_url:
            _check_price_drops(webhook_url, query, previous, items)

    if notify and webhook_url:
        notify_search_summary(webhook_url, summary)

    print("\n[+] Done.\n")


def _check_price_drops(webhook_url: str, keyword: str, previous: list, current: list):
    prev_by_id = {i["id"]: i for i in previous if i.get("id")}
    for item in current:
        item_id = item.get("id")
        if not item_id or item_id not in prev_by_id:
            continue
        old = prev_by_id[item_id]
        if old.get("price") and item.get("price") and item["price"] < old["price"]:
            notify_price_drop(webhook_url, keyword, item, old["price"], item["price"])


def run_single_search(config: dict):
    query = input("\n  Búsqueda: ").strip()
    if not query:
        print("[!] Empty query.")
        return

    print()
    items = search(query, config)

    if not items:
        print("  [!] No results found.")
        return

    print(f"\n  ── {len(items)} resultado(s) para '{query}' ──\n")
    for i, item in enumerate(items, 1):
        print_item(item, i)

    save_opt = input("  ¿Guardar resultados? (s/N): ").strip().lower()
    if save_opt == "s":
        path = save_results(items, query)
        print(f"  [+] Saved to {path}")

    webhook_url = config.get("discord_webhook_url", "")
    if webhook_url:
        notify_opt = input("  ¿Notificar en Discord? (s/N): ").strip().lower()
        if notify_opt == "s":
            notify_new_items(webhook_url, query, items)


def manage_keywords(keywords: list) -> list:
    while True:
        print("\n── Keywords ──")
        if keywords:
            for i, kw in enumerate(keywords, 1):
                print(f"    [{i}] {kw['query']} ({kw.get('category', '—')})")
        else:
            print("    (ninguna)")

        print("\n  [A] Añadir  [D] Borrar  [V] Volver")
        choice = input("  > ").strip().upper()

        if choice == "A":
            query = input("  Query: ").strip()
            category = input("  Categoría (opcional): ").strip() or "general"
            if query:
                keywords.append({"query": query, "category": category})
                save_keywords(keywords)

        elif choice == "D":
            idx = input("  Número a borrar: ").strip()
            if idx.isdigit() and 1 <= int(idx) <= len(keywords):
                removed = keywords.pop(int(idx) - 1)
                save_keywords(keywords)
                print(f"  [+] Removed: {removed['query']}")
            else:
                print("  [!] Invalid index.")

        elif choice == "V":
            break

    return keywords


def configure(config: dict) -> dict:
    print("\n── Configuración actual ──")
    for key, val in config.items():
        print(f"    {key}: {val}")

    print("\n  Escribe el nombre del campo a cambiar (o Enter para volver):")
    field = input("  > ").strip()
    if not field:
        return config
    if field not in config:
        print(f"  [!] '{field}' is not a valid config key.")
        return config

    value = input(f"  Nuevo valor para '{field}': ").strip()

    try:
        original = config[field]
        if isinstance(original, bool):
            config[field] = value.lower() in ("true", "1", "yes", "s")
        elif isinstance(original, int):
            config[field] = int(value)
        elif isinstance(original, float):
            config[field] = float(value)
        else:
            config[field] = value if value != "null" else None
    except ValueError:
        config[field] = value

    save_config(config)
    return config


def view_results():
    os.makedirs(RESULTS_DIR, exist_ok=True)
    files = [f for f in os.listdir(RESULTS_DIR) if f.endswith(".json")]

    if not files:
        print("\n  [!] No results saved yet.")
        return

    print("\n  ── Resultados guardados ──")
    for i, f in enumerate(files, 1):
        path = os.path.join(RESULTS_DIR, f)
        with open(path, encoding="utf-8") as fp:
            data = json.load(fp)
        print(f"    [{i}] {f}  ({len(data)} items)")

    idx = input("\n  Ver archivo número (Enter para volver): ").strip()
    if not idx.isdigit() or not (1 <= int(idx) <= len(files)):
        return

    path = os.path.join(RESULTS_DIR, files[int(idx) - 1])
    with open(path, encoding="utf-8") as fp:
        data = json.load(fp)

    print(f"\n  ── {files[int(idx)-1]} ({len(data)} items) ──\n")

    filter_max = input("  Filtrar por precio máximo (Enter para mostrar todos): ").strip()
    if filter_max:
        try:
            data = [i for i in data if i.get("price") and i["price"] <= float(filter_max)]
            print(f"  → {len(data)} items under {filter_max} EUR\n")
        except ValueError:
            pass

    for item in data:
        print_item(item)


def run_monitor_mode(config: dict, keywords: list):
    interval = config.get("check_interval_minutes", 30)
    print(f"\n  [*] Monitor mode started. Checking every {interval} min. (Ctrl+C -> Stop)\n")
    try:
        while True:
            print(f"  [*] Running scrape at {time.strftime('%H:%M:%S')}...")
            run_scrape_all(config, keywords, notify=True)
            print(f"  [*] Next check in {interval} minutes...\n")
            time.sleep(interval * 60)
    except KeyboardInterrupt:
        print("\n  [+] Monitor mode stopped.")


def main():
    config = load_config()
    keywords = load_keywords()

    while True:
        clear()
        print_header()
        print(f"\n  Keywords cargadas: {len(keywords)}")
        webhook_status = "Configurado" if config.get("discord_webhook_url") else "No configurado"
        print(f"  Discord webhook:  {webhook_status}\n")

        print("  [1] Buscar ahora (todos los keywords)")
        print("  [2] Búsqueda manual (query libre)")
        print("  [3] Gestionar keywords")
        print("  [4] Ver resultados guardados")
        print("  [5] Modo monitor (auto-scrape)")
        print("  [6] Configuración")
        print("  [7] Probar webhook de Discord")
        print("  [0] Salir\n")

        choice = input("  >> ").strip()

        if choice == "1":
            run_scrape_all(config, keywords)
            input("\n  Pulsa Enter para continuar...")

        elif choice == "2":
            run_single_search(config)
            input("\n  Pulsa Enter para continuar...")

        elif choice == "3":
            keywords = manage_keywords(keywords)

        elif choice == "4":
            view_results()
            input("\n  Pulsa Enter para continuar...")

        elif choice == "5":
            run_monitor_mode(config, keywords)
            input("\n  Pulsa Enter para continuar...")

        elif choice == "6":
            config = configure(config)
            input("\n  Pulsa Enter para continuar...")

        elif choice == "7":
            test_webhook(config.get("discord_webhook_url", ""))
            input("\n  Pulsa Enter para continuar...")

        elif choice == "0":
            print("\n  Cerrando... \n")
            sys.exit(0)

        else:
            print("\n  [!] Opción no válida.")
            time.sleep(1)


if __name__ == "__main__":
    main()