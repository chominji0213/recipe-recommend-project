"""
StateGraph 4노드 구성: intent_node -> search_node -> branch_node -> generate_node

지금까지 만든 챗봇(날씨/오늘뭐먹지/영화/도서)은 전부 선형 StateGraph였는데,
이 프로젝트에서 branch_node의 조건부 분기(conditional edge)를 처음 도입한다.

TODO(3일차): 각 노드 함수 구현
TODO(4일차): StateGraph 연결 + SqliteSaver 체크포인터 (기존 프로젝트와 동일한 패턴 재사용)
"""

from typing import TypedDict, Literal

import recipe_data


class RecipeState(TypedDict, total=False):
    query: str                # 사용자 원문 입력
    ingredients: list[str]    # intent_node가 뽑아낸 재료
    diet: str                 # "vegan" | "vegetarian" | "general" 등 intent_node가 판단
    search_results: list[dict]
    answer: str
    history: list[tuple[str, str]]  # (query, answer) 누적 - 도서봇 패턴 재사용 예정


def intent_node(state: RecipeState) -> RecipeState:
    """사용자 입력에서 재료/원하는 요리 조건 + diet(비건/일반 등)를 추출한다.

    TODO: LLM 호출로 재료 리스트 + diet 값을 구조화해서 뽑아내기
    """
    raise NotImplementedError


def search_node(state: RecipeState) -> RecipeState:
    """recipe_data 모듈로 레시피 후보를 검색한다.

    TODO: state["ingredients"]/state["query"] 기반으로 recipe_data.search_recipes_by_name 호출
    """
    raise NotImplementedError


def branch_router(state: RecipeState) -> Literal["vegan", "general"]:
    """diet 값에 따라 다음 노드 경로를 결정하는 조건부 엣지 함수.

    v1: 비건/일반 2갈래만 (TheMealDB category 파라미터만 갈아끼우는 수준).
    TODO(5일차 여유): 알레르기 키워드 매칭 추가
    """
    raise NotImplementedError


def branch_node(state: RecipeState) -> RecipeState:
    """branch_router가 고른 경로에 맞게 검색 결과를 필터링/보강한다.

    TODO: diet == "vegan"이면 recipe_data.search_recipes_by_category("Vegan")으로 재검색
    """
    raise NotImplementedError


def generate_node(state: RecipeState) -> RecipeState:
    """검색/분기 결과를 종합해 최종 추천 답변을 생성한다.

    TODO: LLM 호출로 답변 생성
    TODO: history에 (query, answer) 누적 반환 (도서봇 패턴 재사용)
    """
    raise NotImplementedError


def build_graph():
    """StateGraph를 조립해서 반환한다.

    TODO: from langgraph.graph import StateGraph
    TODO: add_node 4개 + add_edge(intent->search->branch) + add_conditional_edges(branch_router)
    TODO: SqliteSaver 체크포인터 연결 (checkpoint.db)
    """
    raise NotImplementedError


def ask(thread_id: str, user_message: str) -> str:
    """그래프를 1회 호출해서 답변을 반환한다. (스트리밍은 이번 v1에서는 생략, 필요시 추가)"""
    raise NotImplementedError


if __name__ == "__main__":
    # 단독 실행 테스트용 (4일차 통합 테스트에서 여기부터 확인)
    print(ask(thread_id="test", user_message="계란이랑 감자로 만들 수 있는 요리 추천해줘"))
