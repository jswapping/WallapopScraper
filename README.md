# Wallapop Scraper
Scraper para obtener productos de Wallapop según distintos criterios como búsqueda, precio, localización, etc. Los datos se pueden exportar a formatos como JSON para su posterior análisis.

## Instalación:

Instalamos el repositorio:
```
git clone https://github.com/jswapping/WallapopScraper.git
```
Instalamos las dependencias:
```
pip install -r requirements.txt
```
Editamos el archio de configuración a nuestras necesidades:
```
{
  "min_price" : 0,
  "max_price": 600,
  "latitude": 10,
  "longitude": 10,
  "distance_km": 50,
  "order_by" : "newest"
}
```
Añadimos items a buscar en la web:
```
[
  { "query": "iPhone 11 128GB", "category": "smartphones (Esto no importa mucho)" },
  ...
]
```

> [!NOTE]
> Mejora el código a tus necesidades. Esto es solo una fase de prueba.

## Output

En **/results** se generará los resultados, donde el límite de momento es **40 por item**.

```
[
  {
    "nombre": "iPhone 11 128GB Negro",
    "precio": 100.0,
    "categoria": "smartphones",
    "url": "https://es.wallapop.com/item/iphone-ejemplo"
  },
]
```

> [!WARNING]
> No abuses de la api, puesto que puedes recibir limitaciones. Esto es simplemente un ejemplo para aprender.
