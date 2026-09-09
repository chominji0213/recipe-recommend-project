import requests
from rich import print as rprint

BASE_URL = "https://www.themealdb.com/api/json/v1/1"
ALLERGEN_KEYWORDS = {
    "nut": ["peanut", "almond", "walnut", "cashew", "pecan", "hazelnut", "pistachio", "macadamia"],
    "dairy": ["milk", "cream", "cheese", "butter", "yogurt", "yoghurt", "whey"],
    "gluten": ["flour", "wheat", "pasta", "bread", "noodle", "barley", "rye"],
    "egg": ["egg"],
    "seafood": ["shrimp", "prawn", "crab", "lobster", "squid", "octopus"],
    "fish": ["salmon", "tuna", "cod", "anchovy", "fish sauce"],
    "soy": ["soy", "soya", "tofu"],
}


def search_recipes_by_name(query: str) -> list[dict]:
    """검색어(요리명/재료명)로 레시피 후보를 검색한다."""
    try:
        query = query.strip()
        res = requests.get(f"{BASE_URL}/search.php", params={"s": query}, timeout=5)
        res.raise_for_status()
        data = res.json()['meals']

        if not data:
            return []   

        return data
    except requests.RequestException as e:
        print(f"레시피를 찾는 도중에 문제가 생겼습니다.: {e}")
        return []
        

def search_recipes_by_category(category: str) -> list[dict]:
    """카테고리(Vegan/Vegetarian 등)로 레시피 후보를 검색한다."""
    try:
        c = category.strip()
        res = requests.get(f'{BASE_URL}/filter.php', params={'c': c}, timeout=5)
        res.raise_for_status()
        data = res.json()['meals']

        if not data:
            return []
        
        return data
    except requests.RequestException as e:
            print(f"레시피를 찾는 도중에 문제가 생겼습니다.: {e}")

            return []


def search_recipes_by_ingredient(ingredient: str) -> list[dict]:
    """
    재료 하나로 그 재료에 들어간 레시피 후보를 검색한다.
    """
    try:
        i = ingredient.strip()
        res = requests.get(f'{BASE_URL}/filter.php', params={'i': i}, timeout=5)
        res.raise_for_status()
        data = res.json()['meals']

        if not data:
            return []

        return data        
    except requests.RequestException as e:
        print(f'레시피를 찾는 도중에 문제가 생겼습니다. : {e}')

        return []
   

def get_recipe_detail(meal_id: str) -> dict:
    """레시피 상세 정보(재료 목록 + 조리법)를 조회한다."""
    try:
        res = requests.get(f'{BASE_URL}/lookup.php', params={'i': meal_id}, timeout=5)
        res.raise_for_status()
        data = res.json()['meals'][0]
        ingredients = []
        for key, value in data.items():
            if not value:
                continue

            if 'strIngredient' in key:
                ingredients.append({key: value})

        instructions = data.get('strInstructions', '')
        return {'ingredients': ingredients, 'instructions': instructions}
    except requests.RequestException as e:
        print(f"레시피를 찾는 도중에 문제가 생겼습니다.: {e}")

        return {'ingredients': [], 'instructions': ''}

def is_allergy_safe(ALLERGEN_KEYWORDS: dict, food_list: list) -> bool:
    """알레르기 여부 판별 함수"""
    allergen_list = []
    for food in food_list:
        for key, value in food.items():            
            allergen_list.append(value)

    for key, value in ALLERGEN_KEYWORDS.items():        
        for allergen in allergen_list:
            for v in value:
                if v.lower() in allergen.lower():
                    return True

    return False

if __name__ == "__main__":
    #테스트코드
    detail = get_recipe_detail('53392')
    rprint(search_recipes_by_ingredient('onion'))
