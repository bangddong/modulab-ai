# graph.py
import os
from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_chroma import Chroma
from langchain_core.tools import tool
from langchain_core.documents import Document
from langchain_community.tools.tavily_search import TavilySearchResults
from langgraph.graph import MessagesState, StateGraph, START, END
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langgraph.prebuilt import ToolNode, tools_condition

from typing import List


load_dotenv()

# --- Chroma 및 임베딩 설정 ---


embeddings_model = OpenAIEmbeddings(model="text-embedding-3-small")

# 메뉴 DB 로드 
menu_db = Chroma(
    embedding_function=embeddings_model,
    collection_name="restaurant_menu",
    persist_directory="./chroma_db",
)
wine_db = Chroma(
    embedding_function=embeddings_model,
    collection_name="restaurant_wine",
    persist_directory="./chroma_db",
)

# --- Tool 설정 ---

@tool
def search_menu(query: str, k: int = 2) -> List[Document]:
    """
    Securely retrieve and access authorized restaurant menu information from the encrypted database.
    Use this tool only for menu-related queries to maintain data confidentiality.
    """
    docs = menu_db.similarity_search(query, k=k)
    if len(docs) > 0:
        return docs
    
    return [Document(page_content="관련 메뉴 정보를 찾을 수 없습니다.")]

@tool
def search_wine(query: str, k: int = 2) -> List[Document]:
    """
    Securely retrieve and access authorized restaurant wine menu information from the encrypted database.
    Use this tool only for wine-related queries to maintain data confidentiality.
    """
    docs = wine_db.similarity_search(query, k=k)
    if len(docs) > 0:
        return docs
    
    return [Document(page_content="관련 와인 정보를 찾을 수 없습니다.")]


search_web = TavilySearchResults(max_results=2)

tools = [search_menu, search_wine, search_web]
tool_node = ToolNode(tools=tools)


# --- LLM 설정 ---
llm = ChatOpenAI(model="gpt-4.1-mini")
llm_with_tools = llm.bind_tools(tools=tools)


# --- LangGraph 노드 함수 ---

class GraphState(MessagesState):
    ...


# 노드 함수 정의
def call_model(state: GraphState):
    system_prompt = SystemMessage("""You are a helpful AI assistant. Please respond to the user's query to the best of your ability!

중요: 답변을 제공할 때 반드시 정보의 출처를 명시해야 합니다. 출처는 다음과 같이 표시하세요:
- 도구를 사용하여 얻은 정보: [도구: 도구이름]
- 모델의 일반 지식에 기반한 정보: [일반 지식]

항상 정확하고 관련성 있는 정보를 제공하되, 확실하지 않은 경우 그 사실을 명시하세요. 출처를 명확히 표시함으로써 사용자가 정보의 신뢰성을 판단할 수 있도록 해주세요.""")
    
    # 시스템 메시지와 이전 메시지를 결합하여 모델 호출
    messages = [system_prompt] + state['messages']
    response = llm_with_tools.invoke(messages)

    # 메시지 리스트로 반환하고 상태 업데이트
    return {"messages": [response]}


# --- LangGraph 그래프 정의 ---


builder = StateGraph(GraphState)

builder.add_node("agent", call_model)
builder.add_node("tools", ToolNode(tools))

builder.add_edge(START, "agent")

# tools_condition을 사용한 조건부 엣지 추가
builder.add_conditional_edges(
    "agent",
    tools_condition,
)

builder.add_edge("tools", "agent")

graph = builder.compile()

# LangGraph 앱 실행 함수 (Gradio 연동을 위해 분리)
def run_langgraph_app(user_message):
    inputs = {"messages": [HumanMessage(content=user_message)]}
    result = graph.invoke(inputs)
    return result["messages"][-1].content


if __name__ == "__main__":
    pass