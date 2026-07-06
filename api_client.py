import requests

BASE_URL = "https://world.openfoodfacts.org/api/v2"
HEADERS = {"User-Agent": "InventoryManagementApp/1.0 (student project)"}


def fetch_product_by_barcode(barcode):
    """Return a normalized product record from OpenFoodFacts for a barcode."""
    url = f"{BASE_URL}/product/{barcode}.json"
    response = requests.get(url, headers=HEADERS, timeout=5)

    if response.status_code != 200:
        return None

    data = response.json()

    if data.get("status") != 1:
        return None

    product = data.get("product", {})
    return {
        "name": product.get("product_name", "Unknown"),
        "barcode": barcode,
        "brand": product.get("brands", ""),
        "category": product.get("categories", "")
    }


def fetch_product_by_name(name):
    """Return the first normalized OpenFoodFacts search result for a name."""
    url = "https://search.openfoodfacts.org/search"
    params = {
        "q": name,
        "page_size": 1
    }
    response = requests.get(url, headers=HEADERS, params=params, timeout=5)

    if response.status_code != 200:
        return None

    data = response.json()
    products = data.get("hits", [])

    if not products:
        return None

    product = products[0]
    return {
        "name": product.get("product_name", "Unknown"),
        "barcode": product.get("code", ""),
        "brand": product.get("brands", ""),
        "category": product.get("categories", "")
    }
