"""
레시피 검색 API 연동 모듈.

1순위 API: TheMealDB (https://www.themealdb.com/api.php)
- 무료 테스트키 "1"로 바로 사용 가능, 별도 키 발급 불필요.
- 비건/베지테리언은 API가 카테고리로 직접 지원 (filter.php?c=Vegan / c=Vegetarian).
- 알레르기(글루텐프리, 견과류 등) 필드는 없어서 재료 목록 기반 키워드 매칭을 추후 별도로 붙인다 (5일차 여유 태스크).

TODO(2일차): 아래 함수들을 실제로 구현하고, 그래프에 연결하기 전에
이 파일만 단독으로 실행해서 결과를 확인해볼 것 (도서봇 때와 동일한 방식).
"""

import requests

BASE_URL = "https://www.themealdb.com/api/json/v1/1"


def search_recipes_by_name(query: str) -> list[dict]:
    """검색어(요리명/재료명)로 레시피 후보를 검색한다.

    TODO: GET {BASE_URL}/search.php?s={query} 호출
    TODO: 결과 없음(meals가 None인 경우) 처리
    TODO: 타임아웃/네트워크 에러 처리
    """
    raise NotImplementedError


def search_recipes_by_category(category: str) -> list[dict]:
    """카테고리(Vegan/Vegetarian 등)로 레시피 후보를 검색한다.

    TODO: GET {BASE_URL}/filter.php?c={category} 호출
    """
    raise NotImplementedError


def get_recipe_detail(meal_id: str) -> dict:
    """레시피 상세 정보(재료 목록 포함)를 조회한다.

    TODO: GET {BASE_URL}/lookup.php?i={meal_id} 호출
    TODO: strIngredient1~20 필드를 하나의 ingredients 리스트로 정리해서 반환
    """
    raise NotImplementedError


if __name__ == "__main__":
    # 단독 실행 테스트용 (2일차에 여기서부터 확인)
    print(search_recipes_by_name("chicken"))
