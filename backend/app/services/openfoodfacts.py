import httpx
from typing import Optional

OPENFOODFACTS_API = "https://world.openfoodfacts.org/api/v2"


async def search_food(query: str, page: int = 1, page_size: int = 20) -> dict:
    """Search for food products in Open Food Facts database"""
    
    async with httpx.AsyncClient() as client:
        params = {
            "search_terms": query,
            "page": page,
            "page_size": page_size,
            "fields": "code,product_name,brands,image_front_small_url,nutriments,serving_size",
            "json": 1
        }
        
        response = await client.get(
            f"{OPENFOODFACTS_API}/search",
            params=params,
            timeout=10
        )
        
        if response.status_code != 200:
            return {"products": [], "count": 0}
        
        data = response.json()
        products = []
        
        for product in data.get("products", []):
            nutriments = product.get("nutriments", {})
            
            products.append({
                "barcode": product.get("code"),
                "name": product.get("product_name", "Unbekannt"),
                "brand": product.get("brands", ""),
                "image_url": product.get("image_front_small_url"),
                "serving_size": product.get("serving_size", "100g"),
                "calories_per_100g": nutriments.get("energy-kcal_100g", 0),
                "protein_per_100g": nutriments.get("proteins_100g", 0),
                "carbs_per_100g": nutriments.get("carbohydrates_100g", 0),
                "fat_per_100g": nutriments.get("fat_100g", 0),
                "fiber_per_100g": nutriments.get("fiber_100g", 0),
                "sugar_per_100g": nutriments.get("sugars_100g", 0),
                "source": "openfoodfacts"
            })
        
        return {
            "products": products,
            "count": data.get("count", 0),
            "page": page,
            "page_size": page_size
        }


async def get_product_by_barcode(barcode: str) -> Optional[dict]:
    """Get product details by barcode"""
    
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{OPENFOODFACTS_API}/product/{barcode}",
            params={"fields": "code,product_name,brands,image_front_small_url,nutriments,serving_size"},
            timeout=10
        )
        
        if response.status_code != 200:
            return None
        
        data = response.json()
        
        if data.get("status") != 1:
            return None
        
        product = data.get("product", {})
        nutriments = product.get("nutriments", {})
        
        return {
            "barcode": product.get("code"),
            "name": product.get("product_name", "Unbekannt"),
            "brand": product.get("brands", ""),
            "image_url": product.get("image_front_small_url"),
            "serving_size": product.get("serving_size", "100g"),
            "calories_per_100g": nutriments.get("energy-kcal_100g", 0),
            "protein_per_100g": nutriments.get("proteins_100g", 0),
            "carbs_per_100g": nutriments.get("carbohydrates_100g", 0),
            "fat_per_100g": nutriments.get("fat_100g", 0),
            "fiber_per_100g": nutriments.get("fiber_100g", 0),
            "sugar_per_100g": nutriments.get("sugars_100g", 0),
            "source": "openfoodfacts"
        }
