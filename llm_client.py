"""
레시피 추천봇 - LangGraph StateGraph (4-node: intent -> search -> branch -> generate)
"""
from typing import TypedDict, Literal
from pydantic import BaseModel, Field
from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.sqlite import SqliteSaver
from dotenv import load_dotenv
import sqlite3
from recipe_data import search_recipes_by_name, search_recipes_by_category, get_recipe_detail, is_allergy_safe

from rich import print as rprint

load_dotenv()
ALLERGEN_KEYWORDS = {
    "nut": ["peanut", "almond", "walnut", "cashew", "pecan", "hazelnut", "pistachio", "macadamia"],
    "dairy": ["milk", "cream", "cheese", "butter", "yogurt", "yoghurt", "whey"],
    "gluten": ["flour", "wheat", "pasta", "bread", "noodle", "barley", "rye"],
    "egg": ["egg"],
    "seafood": ["shrimp", "prawn", "crab", "lobster", "squid", "octopus"],
    "fish": ["salmon", "tuna", "cod", "anchovy", "fish sauce"],
    "soy": ["soy", "soya", "tofu"],
}

class RecipeState(TypedDict, total=False):
    query: str                       # 사용자 원문 입력
    diet: Literal["vegan", "vegetarian", "general"]  
    ingredients: list[str]          
    search_results: list[dict]       
    safe_results: list[dict]       
    answer: str                    
    # history: list[tuple[str, str]]  

class IntentResult(BaseModel):
    diet: Literal["vegan", "vegetarian", "general"] = Field(
        description="사용자가 원하는 식단 제한. 특별한 언급이 없으면 general"
    )
    ingredients: list[str] = Field(
        default_factory=list,
        description="사용자가 언급한 구체적인 요리명/재료명 리스트. 없으면 빈 리스트"
    )

llm = init_chat_model('gemini-3.1-flash-lite', model_provider='google_genai')
structured_llm  = llm.with_structured_output(IntentResult)


def intent_node(state: RecipeState) -> RecipeState:
    """
    사용자 의도 파악 노드
    """    
    prompt = f"""
                너는 사용자의 문장에서 식단 조건(diet)과 언급된 재료/음식명(ingredients)을 추출하는 어시스턴트야.

                diet는 다음 세 가지 중 하나로 판단해:
                - "vegan": 고기, 생선, 해산물, 유제품, 계란, 꿀 등 동물성 재료를 전혀 원하지 않는다고 언급한 경우
                - "vegetarian": 고기/생선/해산물은 원하지 않지만 유제품이나 계란은 괜찮다고 언급했거나, 단순히 "채식"이라고만 말한 경우
                - "general": 특별한 식단 제한 언급이 없는 경우 (기본값)

                ingredients는 사용자가 문장에서 구체적으로 언급한 요리명이나 재료명만 리스트로 뽑아. 언급이 없으면 빈 리스트를 반환해. 없는 재료를 지어내지 마.

                그리고 요리명이나 재료명은 무조건 영어로 바꿔서 반환해

                사용자 문장: "{state['query']}"
            """
    try:
        raw_response = structured_llm.invoke(prompt)
        result = raw_response

    except Exception as e:
        return {'diet': 'general', 'ingredients': []}

    return {"diet": result.diet, "ingredients": result.ingredients}


def search_node(state: RecipeState) -> RecipeState:
    """
    검색 노드: state["diet"]/state["ingredients"]를 보고 recipe_data.py의 함수 중 어떤 걸 호출할지 결정해서 검색 결과를 채움.
    """    
    if state['diet'] == 'vegan' or state['diet'] == 'vegetarian':
        result = search_recipes_by_category(state['diet'].capitalize())

    else:
        if not state['ingredients']:
            return {'search_results': []}

        query = " ".join(state['ingredients'])    
        result = search_recipes_by_name(query)

    return {'search_results': result}


def branch_node(state: RecipeState) -> RecipeState:
    """
    분기 판단 노드: state["search_results"] 각 레시피에 대해 get_recipe_detail + is_allergy_safe로 알레르기 안전한 것만 골라 safe_results에 채움.
    """
    recipes = state['search_results']
    safe_results = []
    for recipe in recipes:
        detail_recipe = get_recipe_detail(recipe['idMeal'])
        is_allergy = is_allergy_safe(ALLERGEN_KEYWORDS, detail_recipe['ingredients'])

        if not is_allergy:
            safe_results.append({
                'name': recipe['strMeal'],
                'instructions': detail_recipe['instructions'],
            })

    return {'safe_results': safe_results}


def branch_router(state: RecipeState) -> str:
    """
    조건부 엣지 라우팅 함수
    """
    safe_recipe = state['safe_results']

    if not safe_recipe: 
        return '결과없음'
    
    return 'generate'


def generate_node(state: RecipeState) -> RecipeState:
    """
    답변 생성 노드: state["safe_results"]를 참고해서 LLM에게 최종 추천 답변을 만들게 함.
    """
    if not state['safe_results']:
        return {'answer' : '죄송합니다. 레시피를 찾지못했습니다.'}

    try:
        llm = init_chat_model('gemini-3.1-flash-lite', model_provider='google_genai')
        prompt = f"""
                    너는 사용자에게 레시피를 추천해주는 친절한 요리 어시스턴트야.

                    사용자 질문: "{state['query']}"

                    아래는 조건(식단 제한, 알레르기)에 맞는 안전한 레시피 목록이야:
                    {state['safe_results']}

                    이 목록을 참고해서 사용자에게 레시피를 추천해줘. 다음 사항을 지켜:
                    - 목록에 있는 레시피 중에서만 추천해. 목록에 없는 요리를 지어내지 마.
                    - 여러 개 있으면 그 중 가장 어울리는 걸 1~2개 골라서 추천하고, 각각 왜 추천하는지 간단히 설명해줘.
                    - 추천할 때 각 레시피의 조리법(instructions)을 참고해서 간단한 조리 방법도 함께 안내해줘.
                    - 자연스러운 대화체로 답변해줘.
                """
        result = llm.invoke([HumanMessage(content=prompt)])
        answer = result.content[0]['text']

    except Exception as e:
       answer = "죄송해요, 지금 답변을 생성하는 중 문제가 생겼어요. 잠시 후 다시 시도해 주세요." 

    return {'answer': answer}


def build_graph():
    """
    그래프 조립
    """
    conn = sqlite3.connect('checkpoint.db', check_same_thread=False)
    memory = SqliteSaver(conn)

    graph = StateGraph(RecipeState)

    graph.add_node('intent', intent_node)
    graph.add_node('search', search_node)
    graph.add_node('branch', branch_node)
    graph.add_node('generate', generate_node)

    graph.add_edge(START, 'intent')
    graph.add_edge('intent', 'search')
    graph.add_edge('search', 'branch')
    graph.add_conditional_edges(
        'branch',
        branch_router,
        {'generate': 'generate', '결과없음' : 'generate' }
    )
    graph.add_edge('generate', END)

    agent = graph.compile(checkpointer=memory)

    return agent


def ask(agent, user_message: str, thread_id: str) -> str:
    """
    외부(app.py)에서 호출할 수 있는 진입점.
    """

    config = {'configurable': {'thread_id': thread_id}}
    result = agent.invoke({'query': user_message}, config)

    return result['answer']


if __name__ == "__main__":
    agent = build_graph()

    print(ask(agent, "닭고기랑 마늘 들어간 요리 추천해줘", "test-thread-3"))

    #rprint(intent_node({"query": "닭고기 요리 추천해줘"}))