# 레시피 추천봇 (recipe-recommend-project)

재료나 원하는 요리 조건을 입력하면 레시피를 추천해주는 챗봇.
회사 개인공부 트랙(파이썬 챗봇 심화) — 노드 4개 프로젝트.

## 핵심 목표
지금까지 만든 챗봇(날씨/오늘뭐먹지/영화/도서)은 전부 선형 StateGraph였는데,
이 프로젝트에서 조건부 분기(conditional edge)를 처음 도입한다.

## 그래프 구조
intent_node -> search_node -> branch_node(조건부 분기: vegan / general) -> generate_node

## 기술 스택
Gemini API + LangChain/LangGraph + Streamlit + TheMealDB API

## 실행 방법
```bash
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # GOOGLE_API_KEY 채워넣기
streamlit run app.py
```

## 진행 상태
- [ ] recipe_data.py 구현
- [ ] StateGraph 4노드 구현
- [ ] 통합 테스트
- [ ] UI 연결

(작업 순서는 노션 로드맵의 개발 태스크 DB 참고)
