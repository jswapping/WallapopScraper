from wallascrapper import scrape_wallapop, get_items
from config import load_keywords, save_data

# main.py example.

KEYWORDS = load_keywords()

if __name__ == "__main__":
    for keyword in KEYWORDS:
        query = keyword["query"]
        category = keyword["category"]

        print(f"Searching for {query} in category {category}")

        wallapop_data = scrape_wallapop(query)
        items = get_items(wallapop_data)

        productos_analisis = []
        for item in items:
            if item["price"] is None:
                continue

            productos_analisis.append({
                "nombre": item["title"],
                "precio": item["price"],
                "categoria": category,
                "url" : item["url"]
            })

        print(f"Added {len(items)} items.")
        save_data(productos_analisis, query)