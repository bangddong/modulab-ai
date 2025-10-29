from typing import List, TypedDict, Literal
from langgraph.graph import StateGraph, START, END
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

# .env 환경변수 로드
load_dotenv()

# LLM 인스턴스 생성
llm = ChatOpenAI(model="gpt-4.1-mini")


from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma

# OpenAI 임베딩 모델 생성
embeddings_openai = OpenAIEmbeddings(model="text-embedding-3-small")

# 한국어 문서로 저장되어 있는 벡터 저장소 로드
db_korean = Chroma(
    embedding_function=embeddings_openai,
    collection_name="db_korean_cosine_metadata",
    persist_directory="./chroma_db",
    )

print(f"한국어 문서 수: {db_korean._collection.count()}")

# 영어 문서를 저장하는 벡터 저장소 로드
db_english = Chroma(
    embedding_function=embeddings_openai,
    collection_name="eng_db_openai",
    persist_directory="./chroma_db",
    )

print(f"영어 문서 수: {db_english._collection.count()}")


# state 스키마 
class EelectricCarState(TypedDict):
    user_query: str
    is_korean: bool
    search_results: List[str]
    final_answer: str

def analyze_input(state: EelectricCarState) -> EelectricCarState:
    """ 사용자 입력이 한국어인지 판단하는 함수 """

    # 사용자 의도를 분석하기 위한 템플릿
    analyze_template = """
    사용자의 입력을 분석하여 한국어인지 판단하세요.

    사용자 입력: {user_query}

    한국어인 경우 "True", 아니면 "False"로 답변하세요.

    답변:
    """

    # 사용자 입력을 분석하여 한국어인지 판단
    analyze_prompt = ChatPromptTemplate.from_template(analyze_template)
    analyze_chain = analyze_prompt | llm | StrOutputParser()
    result = analyze_chain.invoke({"user_query": state['user_query']})
    is_korean = result.strip().lower() == "true"
    
    # 결과를 상태에 업데이트 
    return {"is_korean": is_korean}


def korean_rag_search(state: EelectricCarState) -> EelectricCarState:
    """ 한국어 문서 검색 함수 """

    # 3개의 검색 결과를 가져옴
    results = db_korean.similarity_search(state['user_query'], k=3)

    # 페이지 내용만 추출
    search_results = [doc.page_content for doc in results]

    # 검색 결과를 상태에 저장
    return {"search_results": search_results}


def english_rag_search(state: EelectricCarState) -> EelectricCarState:
    """ 영어 문서 검색 함수 """

    # 3개의 검색 결과를 가져옴
    results = db_english.similarity_search(state['user_query'], k=3)

    # 페이지 내용만 추출
    search_results = [doc.page_content for doc in results]

    # 검색 결과를 상태에 저장
    return {"search_results": search_results}


def generate_response(state: EelectricCarState) -> EelectricCarState:
    """ 답변 생성 함수 """

    # 답변 템플릿
    response_template = """
    사용자 입력: {user_query}
    검색 결과: {search_results}

    위 정보를 바탕으로 사용자의 질문에 대한 상세한 답변을 생성하세요. 
    검색 결과의 정보를 활용하여 정확하고 유용한 정보를 제공하세요.

    답변 (Answer in {language}):
    """

    # 답변 생성
    response_prompt = ChatPromptTemplate.from_template(response_template)
    response_chain = response_prompt | llm | StrOutputParser()
    
    final_answer = response_chain.invoke(
        {
            "user_query": state['user_query'],   # 사용자 입력 (상태에서 가져옴)
            "search_results": state['search_results'],  # 검색 결과 (상태에서 가져옴)
            "language": "한국어" if state['is_korean'] else "영어" # 언어 정보
        }
    )
    
    # 결과를 상태에 저장
    return {"final_answer": final_answer}

def decide_next_step(
        state: EelectricCarState
    ) -> Literal["korean_rag_search", "english_rag_search"]:
    """ 다음 실행 단계를 결정하는 함수 """

    # 한국어인 경우 한국어 문서 검색 함수 실행
    if state['is_korean']:
        return "korean_rag_search"  
    
    # 영어인 경우 영어 문서 검색 함수 실행
    else:
        return "english_rag_search"
    
# 그래프 구성
builder = StateGraph(EelectricCarState)

# 노드 추가: 입력 분석, 한국어 문서 검색, 영어 문서 검색, 답변 생성
builder.add_node("analyze_input", analyze_input)
builder.add_node("korean_rag_search", korean_rag_search)
builder.add_node("english_rag_search", english_rag_search)
builder.add_node("generate_response", generate_response)

# 엣지 추가: 시작 -> 사용자 입력 분석 -> 조건부 엣지 -> 한국어 문서 검색 또는 영어 문서 검색 -> 답변 생성 -> 끝
builder.add_edge(START, "analyze_input")

# 조건부 엣지 추가
builder.add_conditional_edges(
    "analyze_input",
    decide_next_step
)

builder.add_edge("korean_rag_search", "generate_response")
builder.add_edge("english_rag_search", "generate_response")
builder.add_edge("generate_response", END)

# 그래프 컴파일
app = builder.compile()