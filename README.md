# WallapopScraper

Scraper para Wallapop con notificaciones de Discord, modo monitor automático, alertas de bajada de precio y menú interactivo.

## Estructura

```
WallapopScraper/
├── main.py             # Punto de entrada con menú
├── scraper.py          # Lógica de scraping (peticiones & parseo)
├── notifier.py         # Notificaciones por Discord (Webhook)
├── config.py           # Carga/guardado de configuración y resultados
├── requirements.txt
├── config/
│   ├── config.json     # Configuración principal
│   └── keywords.json   # Lista de búsquedas
└── results/            # Resultados guardados por keyword
```

## Instalación

```bash
git clone https://github.com/jswapping/WallapopScraper.git
cd WallapopScraper
pip install -r requirements.txt
python main.py
```

## Configuración (`config/config.json`)

| Campo                   | Descripción                                      | Ejemplo           |
|-------------------------|--------------------------------------------------|-------------------|
| `min_price`             | Precio mínimo                                    | `0`               |
| `max_price`             | Precio máximo en búsqueda                        | `600`             |
| `latitude`              | Latitud de tu ubicación                          | `37.339677`       |
| `longitude`             | Longitud de tu ubicación                         | `-5.841805`       |
| `distance_km`           | Radio de búsqueda en km                          | `50`              |
| `order_by`              | `newest`, `price_asc`, `price_desc`, `closest`   | `"newest"`        |
| `discord_webhook_url`   | URL del webhook de Discord                       | `"https://..."`   |
| `notify_on_new_items`   | Notificar solo artículos nuevos                  | `true`            |
| `max_price_alert`       | Solo notificar si precio ≤ este valor (`null` = todos) | `300`       |
| `check_interval_minutes`| Minutos entre checks en modo monitor            | `30`              |

## Keywords (`config/keywords.json`)

```json
[
  { "query": "iPhone 11 128GB", "category": "smartphones" },
  { "query": "PS5", "category": "consolas" }
]
```

## Discord Webhook

1. En tu servidor Discord: **Ajustes del canal → Integraciones → Webhooks → Nuevo Webhook**
2. Copia la URL del webhook
3. Pégala en `discord_webhook_url` dentro de `config.json` o usa el menú de configuración

### Tipos de notificaciones:
- **Nuevos items** — cuando aparecen artículos que no estaban antes
- **Bajada de precio** — cuando un artículo ya visto baja de precio
- **Resumen** — al terminar el scrape de todos los keywords

## Menú interactivo

```
[1] Buscar ahora (todos los keywords)
[2] Búsqueda manual (query libre)
[3] Gestionar keywords
[4] Ver resultados guardados
[5] Modo monitor (auto-scrape)
[6] Configuración
[7] Probar webhook de Discord
[0] Salir
```

## Formato de resultados

```json
[
  {
    "id": "abc123",
    "title": "iPhone 11 128GB Negro",
    "price": 199.0,
    "currency": "EUR",
    "city": "Sevilla",
    "image": "https://...",
    "url": "https://es.wallapop.com/item/...",
    "description": "Buen estado, sin rayones..."
  }
]
```

> **Aviso**: No abuses de la API. Este proyecto es solo para aprendizaje.
