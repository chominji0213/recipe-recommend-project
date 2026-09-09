# 🍳 레시피 추천봇 (recipe-recommend-project)

재료나 원하는 요리 조건(비건/베지테리언/일반)을 말하면, TheMealDB API에서 레시피를 검색하고
알레르기 유발 재료를 확인해서 추천해주는 챗봇입니다.

개인공부(파이썬 챗봇 심화) 중 **노드 4개 프로젝트**로, LangGraph의
`StateGraph`에 조건부 분기(conditional edge)를 처음 도입해보는 것을 목표로 만들었습니다.

## 왜 만들었나

기존에 만들어봤던 챗봇(날씨/오늘 뭐 먹지/영화/도서 추천봇)은 전부 노드가 순서대로만
이어지는 선형(linear) 구조였습니다. 이번 프로젝트에서는:

- 노드 개수를 하나씩 늘려가며 LangGraph 개념을 단계적으로 익히는 트랙의 일환이고 (3개 → **4개(이 프로젝트)** → 5개),
- 그중에서도 **조건부 분기(conditional edge)** 를 새로 배워보는 것이 핵심 목표였습니다.

## 그래프 구조

```
        ┌─────────┐     ┌────────┐     ┌────────┐     ┌──────────┐
START → │ intent  │ →   │ search │ →   │ branch │ →   │ generate │ → END
        └─────────┘     └────────┘     └────────┘     └──────────┘
                                            │
                                    (조건부 분기: branch_router)
```

| 노드            | 역할                                                                                                                                                               |
| --------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `intent_node`   | 사용자 문장에서 식단 조건(`diet`: vegan/vegetarian/general)과 언급된 재료/요리명(`ingredients`)을 LLM(Gemini)으로 추출. 재료명은 영어로 번역해서 반환하도록 지시함 |
| `search_node`   | `diet`가 vegan/vegetarian이면 카테고리 검색, 아니면 재료별로 개별 검색해서 후보 레시피 목록을 모음                                                                 |
| `branch_node`   | 각 레시피의 재료를 조회해서 알레르기 유발 성분(견과류/유제품/글루텐/계란/해산물/생선/대두)이 있는지 태깅                                                           |
| `branch_router` | `branch_node`가 만든 결과가 있는지 없는지에 따라 다음 노드로 가는 조건부 엣지                                                                                      |
| `generate_node` | 태깅된 레시피 목록을 참고해서 LLM이 최종 추천 답변 생성 (알레르기 있으면 경고 문구 포함)                                                                           |

## 기술 스택

- **LLM**: Gemini (`gemini-3.1-flash-lite`), LangChain `init_chat_model` + `with_structured_output`
- **그래프**: LangGraph `StateGraph`, `SqliteSaver`(대화 이력 저장)
- **레시피 데이터**: [TheMealDB](https://www.themealdb.com/api.php) (무료 테스트 API 키 사용)
- **UI**: Streamlit

## 프로젝트 구조

```
recipe-recommend-project/
├── recipe_data.py   # TheMealDB API 연동 함수 + 알레르기 판별 로직
├── llm_client.py    # RecipeState, 4개 노드, 그래프 조립(build_graph), 진입점(ask)
├── app.py           # Streamlit 채팅 UI
├── requirements.txt
├── .env.example     # GOOGLE_API_KEY 등 환경변수 예시
└── README.md
```

## 실행 방법

```powershell
# 가상환경 생성 및 활성화
python -m venv venv
.\venv\Scripts\Activate.ps1

# 패키지 설치
pip install -r requirements.txt

# 환경변수 설정
copy .env.example .env
# .env 파일 열어서 GOOGLE_API_KEY 채워넣기 (Google AI Studio에서 발급)

# 실행
streamlit run app.py
```

`recipe_data.py`, `llm_client.py`는 각각 파일 하단 `if __name__ == "__main__":`에
간단한 테스트 코드가 있어서, `python recipe_data.py` / `python llm_client.py`로도
개별 동작을 확인할 수 있습니다.

## 알려진 제약사항

프로젝트를 진행하며 직접 확인한 한계들입니다. 4노드 학습 프로젝트 범위상 해결하지 않고
"알고 있는 제약사항"으로 남겨둔 부분들입니다.

- **무료 TheMealDB API는 재료 필터(`filter.php?i=`)에 재료 하나만 넣을 수 있습니다.**
  사용자가 여러 재료를 언급하면 각 재료를 따로따로 검색해서 결과를 합치는 방식으로 처리했습니다.
- **재료 필터는 "구체적인 원재료명"에서만 잘 동작합니다.** 예를 들어 `chicken`, `garlic`은 잘
  검색되지만, `pasta`처럼 재료라기보다 요리/카테고리 성격에 가까운 단어는 매칭되지 않을 수
  있습니다. (검색 결과가 없으면 다른 검색 방식으로 재시도하는 로직은, 다음 프로젝트인
  5노드 자기검증 루프 프로젝트의 개념과 겹쳐서 이번 프로젝트에는 의도적으로 넣지 않았습니다.)
- **알레르기 판별은 "흔한 알레르기 유발 성분 전체"를 항상 검사합니다.** 사용자가 실제로 어떤
  알레르기가 있는지는 아직 입력받지 않고, 매칭되는 성분이 있으면 무조건 경고 문구를 붙여서
  추천하는 방식입니다.
- TheMealDB는 영미권/유럽 요리 위주라 일부 요리(예: 이탈리안 요리 일부)는 데이터베이스에
  아예 없을 수 있습니다.

## 배운 점

- LangGraph에서 `add_conditional_edges`로 분기를 만들 때, 라우팅 함수의 반환값을 실제
  노드 이름으로 매핑하는 `path_map`을 따로 지정해야 한다는 것
- 딕셔너리를 `for x in dict`로 순회하면 키만 나온다는 것, `A in B` 연산자의 방향(포함 관계)
  등 기본기에서 실수하기 쉬운 부분들을 직접 여러 번 겪으며 확인
- 리스트를 다룰 때 `append`(중첩)와 `extend`(평탄화)의 차이

## 다음 프로젝트

노드 5개짜리 자기검증 루프(self-check loop) 프로젝트로 이어질 예정입니다. 이번 프로젝트에서
"검색 결과가 없으면 어떻게 할까" 하고 미뤄뒀던 재시도/재검증 개념을 여기서 다룰 계획입니다.
