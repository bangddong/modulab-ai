# app.py
import gradio as gr
import os
from graph import run_langgraph_app  # graph.py에서 LangGraph 실행 함수 import

def gradio_interface(message, history):
    """Gradio 챗 인터페이스 함수: 사용자 메시지를 LangGraph 앱에 전달하고 응답을 반환"""
    langgraph_response = run_langgraph_app(message) # LangGraph 앱 실행
    return langgraph_response

# Gradio 인터페이스 정의
demo = gr.ChatInterface(
    gradio_interface, 
    type="messages",
    title="레스토랑 메뉴 RAG 챗봇",
    description="질문을 입력하세요. 레스토랑에서 메뉴와 와인에 대한 정보를 제공합니다.",
    examples=["오늘의 메뉴는 무엇인가요?", "와인 추천해주세요.", "스테이크 메뉴의 가격은 얼마인가요?"],
    theme="soft",
    cache_examples=False,
    analytics_enabled=False,
)

# Cloud Run에서 실행될 때 필요한 서버 설정
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    # Gradio가 Cloud Run에서 작동하도록 서버 설정 변경
    demo.launch(
        server_name="0.0.0.0",  # 모든 IP에서 접근 가능하도록
        server_port=port,       # PORT 환경 변수에서 포트 가져오기
        share=False,            # share 기능 비활성화
        # inbrowser=False,        # 브라우저 자동 실행 비활성화  (GCP 배포할 때는 주석 해제)
        # show_error=True,        # 오류 표시
        # debug=True              # 디버그 모드 활성화
    )