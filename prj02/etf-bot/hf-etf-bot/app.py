from enum import Enum
from typing import List, TypedDict, Annotated, Optional
from pydantic import BaseModel, Field
from decimal import Decimal
import ast
import re

from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_community.tools import QuerySQLDatabaseTool
from langchain_community.utilities import SQLDatabase
from langchain.agents.agent_toolkits import create_retriever_tool

from langgraph.graph import StateGraph, START, END

import gradio as gr
import os


##################################################################
# 환경 설정 / 데이터베이스 연결
##################################################################
from dotenv import load_dotenv
load_dotenv()

# OpenAI API Key 검증
if not os.getenv("OPENAI_API_KEY"):
    raise ValueError("OPENAI_API_KEY가 설정되지 않았습니다. .env 파일 또는 환경 변수를 확인하세요.")

db = SQLDatabase.from_uri("sqlite:///etf_database.db")

##################################################################
# 고유명사 DB 검색 (Entity Retrieval with RAG)
##################################################################

def query_as_list(db, query):
    """데이터베이스에서 고유명사 목록 추출"""
    res = db.run(query)
    res = [el for sub in ast.literal_eval(res) for el in sub if el]
    res = [re.sub(r"\b\d+\b", "", string).strip() for string in res]
    return list(set(res))

# 고유명사 추출
etfs = query_as_list(db, "SELECT DISTINCT 종목명 FROM ETFs")
fund_managers = query_as_list(db, "SELECT DISTINCT 운용사 FROM ETFs")
underlying_assets = query_as_list(db, "SELECT DISTINCT 기초지수 FROM ETFs")

# 임베딩 모델 생성
embeddings = OpenAIEmbeddings(model="text-embedding-3-large")

# 임베딩 벡터 저장소 생성
vector_store = InMemoryVectorStore(embeddings)

# ETF 종목명, 운용사, 기초지수를 임베딩 벡터로 변환
_ = vector_store.add_texts(etfs + fund_managers + underlying_assets)
retriever = vector_store.as_retriever(search_kwargs={"k": 20})

# 검색 프롬프트 생성
description = (
    "Use to look up values to filter on. Input is an approximate spelling "
    "of the proper noun, output is valid proper nouns. Use the noun most "
    "similar to the search."
)

# 검색 도구 생성
entity_retriever_tool = create_retriever_tool(
    retriever,
    name="search_proper_nouns",
    description=description,
)

##################################################################
# 상태 정보 타입 정의
##################################################################
class State(TypedDict):
    question: str               # 사용자 입력 질문
    user_profile: dict          # 사용자 프로필 정보
    query: str                  # 생성된 SQL 쿼리
    query_explanation: str      # 쿼리 설명
    candidates: list            # 후보 ETF 목록
    rankings: list              # 순위가 매겨진 ETF 목록
    diversity_analysis: dict    # 다양성 분석 결과
    explanation: str            # 추천 이유 설명
    final_answer: str           # 최종 추천 답변
    retry_count: int            # 재시도 횟수


##################################################################
# 사용자 프로필 분석
##################################################################
class RiskTolerance(str, Enum):
    """투자 위험 성향"""
    CONSERVATIVE = "conservative"  # 안정적 투자 선호
    MODERATE = "moderate"          # 중간 위험 허용
    AGGRESSIVE = "aggressive"      # 높은 위험 감수

class InvestmentHorizon(str, Enum):
    """투자 기간"""
    SHORT = "short"      # 1년 미만
    MEDIUM = "medium"    # 1-3년
    LONG = "long"        # 3년 이상

class InvestmentProfile(BaseModel):
    """투자자 프로필"""
    risk_tolerance: RiskTolerance = Field(
        description="투자자의 위험 성향 (conservative: 안정적, moderate: 중간, aggressive: 공격적)"
    )
    investment_horizon: InvestmentHorizon = Field(
        description="투자 기간 (short: 1년 미만, medium: 1-3년, long: 3년 이상)"
    )
    investment_goal: str = Field(
        description="투자의 주요 목적 (예: 노후 대비, 자산 증식, 배당 소득 등)"
    )
    preferred_sectors: List[str] = Field(
        default=[],
        description="선호하는 투자 섹터 또는 자산 유형 (예: IT, 헬스케어, 배당주, 채권 등)"
    )
    excluded_sectors: List[str] = Field(
        default=[],
        description="투자를 원하지 않는 섹터 또는 자산 유형"
    )
    monthly_investment: int = Field(
        description="월 투자 가능 금액 (원 단위)"
    )
    esg_preference: bool = Field(
        default=False,
        description="ESG (환경, 사회, 지배구조) 투자 선호 여부"
    )


# 사용자 프로필 분석 프롬프트 (개선된 버전)
PROFILE_TEMPLATE = """
당신은 전문 투자 상담사입니다. 사용자의 질문을 세심하게 분석하여 투자 프로필을 생성하세요.

사용자 질문: {question}

다음 지침을 따르세요:
1. 명시적으로 언급되지 않은 경우, 일반적인 투자자 특성을 기반으로 합리적인 추론을 수행하세요.
2. 위험 성향:
   - Conservative: "안정적", "보수적", "원금 보존" 등의 키워드
   - Moderate: "균형", "중간", "적당한 수익" 등의 키워드
   - Aggressive: "고수익", "공격적", "위험 감수" 등의 키워드
3. 투자 기간:
   - Short: 1년 미만, "단기", "곧 사용할 예정" 등
   - Medium: 1-3년, "중기" 등
   - Long: 3년 이상, "장기", "노후", "은퇴" 등
4. 선호/제외 섹터는 구체적인 산업명이나 자산 유형으로 추출하세요.
5. ESG 관련 키워드 ("친환경", "사회책임", "지속가능" 등)가 있으면 esg_preference를 true로 설정하세요.
"""

profile_prompt = ChatPromptTemplate.from_template(PROFILE_TEMPLATE)

# LLM 모델 생성
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
profile_llm = llm.with_structured_output(InvestmentProfile)

# 사용자 프로필 분석 함수
def analyze_profile(state: State) -> dict:
    """사용자 질문을 분석하여 투자 프로필 생성"""
    prompt = profile_prompt.invoke({"question": state["question"]})
    response = profile_llm.invoke(prompt)
    return {
        "user_profile": response.model_dump(),
        "retry_count": 0
    }


##################################################################
# SQL 쿼리 생성 (개선된 Text2SQL with Few-shot Examples)
##################################################################

# Few-shot 예제
FEW_SHOT_EXAMPLES = """
## 예제 쿼리

예제 1:
질문: "IT 섹터에 투자하고 싶은데 수익률이 높은 ETF를 추천해주세요."
SQL:
SELECT 종목코드, 종목명, 운용사, 수익률_최근1년, 총보수, 순자산총액
FROM ETFs
WHERE 기초지수 LIKE '%IT%' OR 기초지수 LIKE '%기술%' OR 기초지수 LIKE '%반도체%'
ORDER BY 수익률_최근1년 DESC
LIMIT 10;

예제 2:
질문: "배당 수익을 원하는데 안정적인 ETF가 좋아요."
SQL:
SELECT 종목코드, 종목명, 운용사, 수익률_최근1년, 총보수, 순자산총액, 분배금
FROM ETFs
WHERE 종목명 LIKE '%배당%' OR 기초지수 LIKE '%배당%'
ORDER BY 순자산총액 DESC, 수익률_최근1년 DESC
LIMIT 10;

예제 3:
질문: "미국 시장에 투자하고 싶어요."
SQL:
SELECT 종목코드, 종목명, 운용사, 수익률_최근1년, 총보수, 순자산총액
FROM ETFs
WHERE 기초지수 LIKE '%S&P%' OR 기초지수 LIKE '%나스닥%' OR 기초지수 LIKE '%미국%'
ORDER BY 순자산총액 DESC
LIMIT 10;
"""

# SQL Query Generation Template (개선된 버전)
QUERY_TEMPLATE = """
당신은 한국 ETF 시장 전문가이자 SQL 쿼리 작성 전문가입니다.
사용자의 투자 질문과 프로필을 바탕으로 최적의 ETF를 검색하는 {dialect} 쿼리를 작성하세요.

## 데이터베이스 스키마
{table_info}

## 관련 고유명사 (RAG 검색 결과)
{entity_info}

## Few-shot 예제
{few_shot_examples}

## 사용자 투자 프로필
{user_profile}

## 사용자 질문
{input}

## 쿼리 작성 지침
1. **컬럼 선택**: 종목코드, 종목명, 운용사, 수익률_최근1년, 총보수, 순자산총액, 분배금은 필수로 포함
2. **필터링 조건**:
   - 위험 성향에 따른 필터링:
     * Conservative: 순자산총액이 큰 ETF, 변동성이 낮은 ETF 우선
     * Moderate: 균형잡힌 조건
     * Aggressive: 수익률이 높은 ETF 우선
   - 선호 섹터가 있으면 기초지수나 종목명에 LIKE 조건 사용
   - 제외 섹터가 있으면 NOT LIKE 조건 사용
3. **정렬 기준**:
   - Conservative: ORDER BY 순자산총액 DESC, 총보수 ASC
   - Moderate: ORDER BY 수익률_최근1년 DESC, 순자산총액 DESC
   - Aggressive: ORDER BY 수익률_최근1년 DESC
4. **결과 개수**: 최대 {top_k}개
5. **한국어 매칭**: LIKE 조건 사용 시 유사한 키워드도 고려 (예: IT, 기술, 반도체)
6. **NULL 처리**: 수익률이나 중요한 지표가 NULL인 행은 제외

쿼리는 반드시 실행 가능해야 하며, 문법 오류가 없어야 합니다.
"""

# SQL Query Generation Prompt Template
query_prompt_template = ChatPromptTemplate.from_template(QUERY_TEMPLATE)

# SQL Query Output
class QueryOutput(TypedDict):
    """Generated SQL query with explanation."""
    query: Annotated[str, ..., "Syntactically valid SQL query"]
    explanation: Annotated[str, ..., "쿼리 작성 논리와 선택 기준 설명 (한국어)"]


def write_query(state: State) -> dict:
    """Generate SQL query to fetch ETF candidates with validation."""
    retry_count = state.get("retry_count", 0)

    # 재시도 횟수 제한
    if retry_count >= 3:
        return {
            "query": "SELECT 종목코드, 종목명, 운용사, 수익률_최근1년, 총보수, 순자산총액 FROM ETFs ORDER BY 순자산총액 DESC LIMIT 10",
            "query_explanation": "재시도 횟수 초과로 기본 쿼리를 사용합니다.",
            "retry_count": retry_count
        }

    prompt = query_prompt_template.invoke({
        "dialect": db.dialect,
        "top_k": 15,
        "table_info": db.get_table_info(),
        "input": state["question"],
        "entity_info": entity_retriever_tool.invoke(state["question"]),
        "user_profile": state["user_profile"],
        "few_shot_examples": FEW_SHOT_EXAMPLES
    })

    structured_llm = llm.with_structured_output(QueryOutput)
    result = structured_llm.invoke(prompt)

    # SQL 쿼리 검증
    try:
        # 쿼리가 SELECT로 시작하는지 확인
        query = result["query"].strip()
        if not query.upper().startswith("SELECT"):
            raise ValueError("쿼리는 SELECT로 시작해야 합니다.")

        # 위험한 키워드 체크
        dangerous_keywords = ["DROP", "DELETE", "INSERT", "UPDATE", "ALTER", "CREATE"]
        if any(keyword in query.upper() for keyword in dangerous_keywords):
            raise ValueError("위험한 SQL 명령어가 포함되어 있습니다.")

        return {
            "query": query,
            "query_explanation": result["explanation"],
            "retry_count": retry_count
        }

    except Exception as e:
        # 검증 실패 시 재시도
        return {
            "retry_count": retry_count + 1,
            **write_query({"question": state["question"], "user_profile": state["user_profile"], "retry_count": retry_count + 1})
        }


##################################################################
# 후보 ETF 검색 (결과 검증 포함)
##################################################################

def execute_query(state: State) -> dict:
    """SQL 쿼리 실행하여 후보 ETF 검색 및 결과 검증"""
    execute_query_tool = QuerySQLDatabaseTool(db=db)

    try:
        results = execute_query_tool.invoke(state["query"])

        # 결과가 비어있거나 너무 적은 경우
        if not results or len(results.strip()) < 10:
            # 기본 쿼리로 재시도
            fallback_query = """
            SELECT 종목코드, 종목명, 운용사, 수익률_최근1년, 총보수, 순자산총액
            FROM ETFs
            WHERE 수익률_최근1년 IS NOT NULL
            ORDER BY 순자산총액 DESC
            LIMIT 15
            """
            results = execute_query_tool.invoke(fallback_query)

        return {"candidates": results}

    except Exception as e:
        # 쿼리 실행 오류 시 기본 쿼리 사용
        fallback_query = """
        SELECT 종목코드, 종목명, 운용사, 수익률_최근1년, 총보수, 순자산총액
        FROM ETFs
        WHERE 수익률_최근1년 IS NOT NULL
        ORDER BY 순자산총액 DESC
        LIMIT 15
        """
        results = execute_query_tool.invoke(fallback_query)
        return {"candidates": results}


##################################################################
# ETF 순위 매기기 (개선된 평가 기준)
##################################################################

RANKING_TEMPLATE = """
당신은 한국 ETF 시장 전문가이자 포트폴리오 매니저입니다.
다음 후보 ETF들을 사용자의 투자 프로필에 맞춰 평가하고, 상위 3개 ETF를 선정하여 순위를 매기세요.

## 사용자 투자 프로필
{user_profile}

## 후보 ETF 목록
{candidates}

## 평가 기준 (가중치)

### 1. 수익성 (30%)
- 최근 1년 수익률
- 장기 성과 추이 (가능한 경우)

### 2. 안정성 (25%)
- 순자산총액 (규모가 클수록 안정적)
- 운용사 신뢰도
- 시장 변동성 대응력

### 3. 비용 효율성 (20%)
- 총보수 (낮을수록 좋음)
- 거래 비용

### 4. 프로필 적합성 (25%)
- 위험 성향 일치도
- 투자 기간 적합성
- 선호 섹터 포함 여부
- 제외 섹터 회피 여부
- ESG 선호도 반영

## 위험 성향별 가중치 조정
- Conservative: 안정성 40%, 비용 효율성 30%, 수익성 20%, 프로필 적합성 10%
- Moderate: 각 기준 균등 (25% 씩)
- Aggressive: 수익성 50%, 프로필 적합성 30%, 안정성 10%, 비용 효율성 10%

## 출력 요구사항
1. 정확히 3개의 ETF만 선정하세요.
2. 각 ETF에 대해 0-100점 사이의 종합 점수를 부여하세요.
3. 점수가 높은 순서대로 1위, 2위, 3위를 매기세요.
4. ranking_reason은 최소 3-4문장으로 구체적으로 작성하세요:
   - 이 ETF가 선정된 주요 이유
   - 사용자 프로필과의 적합성
   - 강점과 약점
   - 포트폴리오 내 역할
"""

# ETF Ranking Prompt Template
ranking_prompt = ChatPromptTemplate.from_template(RANKING_TEMPLATE)

# ETF Ranking Output
class ETFRanking(TypedDict):
    """Individual ETF ranking result"""
    rank: Annotated[int, ..., "순위 (1-3)"]
    etf_code: Annotated[str, ..., "ETF 종목코드 (6자리)"]
    etf_name: Annotated[str, ..., "ETF 종목명"]
    score: Annotated[float, ..., "종합 점수 (0-100)"]
    ranking_reason: Annotated[str, ..., "선정 이유 및 평가 근거 (한국어, 최소 3-4문장)"]

class ETFRankingResult(TypedDict):
    """Ranked ETFs with diversity analysis"""
    rankings: List[ETFRanking]


def rank_etfs(state: State) -> dict:
    """Rank ETF candidates with comprehensive evaluation"""
    prompt = ranking_prompt.invoke({
        "user_profile": state["user_profile"],
        "candidates": state["candidates"],
    })

    structured_llm = llm.with_structured_output(ETFRankingResult)
    results = structured_llm.invoke(prompt)

    return {"rankings": results}


##################################################################
# 포트폴리오 다양성 분석 (신규 기능)
##################################################################

DIVERSITY_TEMPLATE = """
선정된 ETF 포트폴리오의 다양성을 분석하고, 분산 투자 관점에서 평가하세요.

## 선정된 ETF
{rankings}

## 분석 항목
1. 섹터 다양성: 다양한 산업 섹터에 분산되어 있는가?
2. 자산 유형: 주식, 채권, 원자재 등 자산 유형이 다양한가?
3. 지역 분산: 국내외 시장 분산이 적절한가?
4. 위험 분산: 서로 다른 위험 특성을 가진 ETF들로 구성되어 있는가?

## 출력
- diversification_score: 다양성 점수 (0-100)
- sector_analysis: 섹터 분산 평가 (한국어)
- risk_analysis: 위험 분산 평가 (한국어)
- recommendations: 개선 제안 (있는 경우, 한국어)
"""

diversity_prompt = ChatPromptTemplate.from_template(DIVERSITY_TEMPLATE)

class DiversityAnalysis(BaseModel):
    """Portfolio diversity analysis"""
    diversification_score: float = Field(description="포트폴리오 다양성 점수 (0-100)")
    sector_analysis: str = Field(description="섹터 분산 평가")
    risk_analysis: str = Field(description="위험 분산 평가")
    recommendations: List[str] = Field(default=[], description="포트폴리오 개선 제안")


def analyze_diversity(rankings: list) -> dict:
    """포트폴리오 다양성 분석"""
    prompt = diversity_prompt.invoke({"rankings": rankings})
    diversity_llm = llm.with_structured_output(DiversityAnalysis)
    result = diversity_llm.invoke(prompt)

    return result.model_dump()


##################################################################
# 추천 설명 생성 (개선된 버전)
##################################################################

EXPLANATION_TEMPLATE = """
당신은 전문 투자 상담사입니다. 선정된 ETF 포트폴리오에 대해 포괄적이고 실용적인 추천 설명을 작성하세요.

## 사용자 투자 프로필
{user_profile}

## 선정된 ETF 순위
{rankings}

## 포트폴리오 다양성 분석
{diversity_analysis}

## 작성 지침

### 1. 투자 전략 개요 (overview)
- 사용자의 투자 목표와 프로필 요약
- 전체 포트폴리오 구성 전략 설명
- 예상되는 기대 효과
- 3-5문장으로 작성

### 2. ETF 추천 상세 (recommendations)
각 ETF에 대해:
- **allocation**: 포트폴리오 내 추천 비중 (3개 ETF의 합이 100%가 되도록)
  * Conservative 성향: 1위 50%, 2위 30%, 3위 20%
  * Moderate 성향: 1위 40%, 2위 35%, 3위 25%
  * Aggressive 성향: 1위 45%, 2위 30%, 3위 25%
- **description**: ETF의 투자 전략과 특징 (3-4문장)
- **key_points**: 주요 투자 포인트 3-4개 (각각 1-2문장)
- **risks**: 투자 위험 요소 2-3개 (각각 1-2문장)

### 3. 투자 시 고려사항 (considerations)
- 시장 상황 모니터링 방법
- 리밸런싱 시기와 방법
- 추가 유의사항
- 최소 4-5개 항목

모든 내용은 한국어로 작성하고, 구체적이고 실용적인 조언을 제공하세요.
"""

explanation_prompt = ChatPromptTemplate.from_template(EXPLANATION_TEMPLATE)


# 추천 설명 출력 스키마
class ETFRecommendation(BaseModel):
    """Individual ETF recommendation details"""
    etf_code: str = Field(..., description="ETF 종목코드 (6자리)")
    etf_name: str = Field(..., description="ETF 종목명")
    allocation: Decimal = Field(..., description="포트폴리오 내 추천 비중 (0-100)")
    description: str = Field(..., description="ETF 설명 및 투자 전략 (3-4문장, 한국어)")
    key_points: List[str] = Field(..., description="주요 투자 포인트 3-4개 (한국어)")
    risks: List[str] = Field(..., description="투자 위험 요소 2-3개 (한국어)")

class RecommendationExplanation(BaseModel):
    """ETF recommendation explanation with markdown formatting"""
    overview: str = Field(..., description="전체 투자 전략 개요 (3-5문장, 한국어)")
    recommendations: List[ETFRecommendation] = Field(..., description="ETF 추천 상세 (3개)")
    considerations: List[str] = Field(..., description="투자 시 고려사항 (4-5개, 한국어)")

    def to_markdown(self) -> str:
        """Convert explanation to markdown format"""
        markdown = [
            "# ETF 포트폴리오 추천",
            "",
            "## 투자 전략 개요",
            self.overview,
            "",
            "## 추천 ETF 포트폴리오",
            ""
        ]

        # 포트폴리오 구성 비율 테이블
        markdown.extend([
            "| 순위 | ETF명 | 종목코드 | 추천 비중 |",
            "|------|-------|----------|-----------|"
        ])

        for idx, rec in enumerate(self.recommendations, 1):
            markdown.append(
                f"| {idx} | {rec.etf_name} | {rec.etf_code} | {rec.allocation}% |"
            )

        # ETF 상세 설명
        markdown.append("\n## ETF 상세 분석\n")

        for idx, rec in enumerate(self.recommendations, 1):
            markdown.extend([
                f"### {idx}. {rec.etf_name} ({rec.etf_code}) - {rec.allocation}%",
                "",
                rec.description,
                "",
                "**주요 투자 포인트**",
                "".join([f"\n- {point}" for point in rec.key_points]),
                "",
                "**투자 위험 요소**",
                "".join([f"\n- {risk}" for risk in rec.risks]),
                ""
            ])

        # 투자 시 고려사항
        markdown.extend([
            "## 투자 시 고려사항",
            "".join([f"\n- {item}" for item in self.considerations]),
            "",
            "---",
            "",
            "*본 추천은 AI 기반 분석 결과이며, 투자 결정 시 추가적인 조사와 전문가 상담을 권장합니다.*"
        ])

        return "\n".join(markdown)


def generate_explanation(state: dict) -> dict:
    """Generate comprehensive ETF recommendation explanation with diversity analysis"""

    # 다양성 분석 수행
    diversity_analysis = analyze_diversity(state["rankings"])

    # 프롬프트 생성
    prompt = explanation_prompt.invoke({
        "rankings": state["rankings"],
        "user_profile": state["user_profile"],
        "diversity_analysis": diversity_analysis
    })

    # 구조화된 출력 생성
    structured_llm = llm.with_structured_output(RecommendationExplanation)
    response = structured_llm.invoke(prompt)

    return {
        "diversity_analysis": diversity_analysis,
        "final_answer": {
            "explanation": response.model_dump(),
            "markdown": response.to_markdown()
        }
    }


##################################################################
# ETF 추천 봇 - LangGraph 워크플로우
##################################################################

# StateGraph 생성
graph_builder = StateGraph(State)

# 노드 추가
graph_builder.add_node("analyze_profile", analyze_profile)
graph_builder.add_node("write_query", write_query)
graph_builder.add_node("execute_query", execute_query)
graph_builder.add_node("rank_etfs", rank_etfs)
graph_builder.add_node("generate_explanation", generate_explanation)

# 엣지 연결 (순차 실행)
graph_builder.add_edge(START, "analyze_profile")
graph_builder.add_edge("analyze_profile", "write_query")
graph_builder.add_edge("write_query", "execute_query")
graph_builder.add_edge("execute_query", "rank_etfs")
graph_builder.add_edge("rank_etfs", "generate_explanation")
graph_builder.add_edge("generate_explanation", END)

# 그래프 컴파일
graph = graph_builder.compile()


##################################################################
# Gradio 인터페이스
##################################################################

def process_message(message: str) -> str:
    """사용자 메시지 처리 및 ETF 추천"""
    try:
        # 입력 검증
        if not message or len(message.strip()) < 10:
            return """
# 입력 오류

질문이 너무 짧습니다. 다음 정보를 포함하여 더 자세히 질문해주세요:
- 투자 목적
- 투자 기간
- 위험 성향
- 월 투자 가능 금액
- 선호/제외 섹터 (선택사항)
"""

        # 그래프 실행
        etf_recommendation = graph.invoke({"question": message})

        # 결과 반환
        return etf_recommendation["final_answer"]["markdown"]

    except Exception as e:
        # 오류 처리
        error_message = str(e)
        return f"""
# 오류가 발생했습니다

죄송합니다. 요청을 처리하는 중에 문제가 발생했습니다.

**오류 내용**: {error_message}

다음 사항을 확인해주세요:
- OpenAI API 키가 올바르게 설정되었는지 확인
- 질문에 투자 관련 정보가 충분히 포함되어 있는지 확인
- 네트워크 연결 상태 확인

다시 시도해주시거나, 질문을 다른 방식으로 작성해주세요.
"""


def answer_invoke(message: str, history: List) -> str:
    """Gradio 인터페이스용 메시지 처리 함수"""
    return process_message(message)


# Gradio ChatInterface 생성
demo = gr.ChatInterface(
    fn=answer_invoke,
    title="AI ETF 추천 어시스턴트",
    description="""
    ## 맞춤형 ETF 포트폴리오 추천 시스템

    투자 성향과 목표에 맞는 최적의 ETF 포트폴리오를 AI가 추천해드립니다.

    ### 질문 시 포함할 정보
    1. **투자 목적**: 노후 대비, 자산 증식, 배당 소득 등
    2. **투자 기간**: 단기(1년 미만), 중기(1-3년), 장기(3년 이상)
    3. **위험 성향**: 안정적, 중간, 공격적
    4. **월 투자 금액**: 투자 가능한 월 금액 (원 단위)
    5. **선호 섹터** (선택): IT, 헬스케어, 배당주, 채권 등
    6. **제외 섹터** (선택): 특정 산업 제외
    7. **ESG 선호** (선택): 친환경, 사회책임 투자 여부

    ### 주요 기능
    - Text2SQL 기반 정밀 ETF 검색
    - 투자 프로필 맞춤형 순위 평가
    - 포트폴리오 다양성 분석
    - 구체적인 투자 비중 제안
    - 위험 요소 및 고려사항 안내
    """,
    examples=[
        """30대 직장인입니다. 월 100만원 정도를 3년 이상 장기 투자하고 싶고, IT와 헬스케어 섹터를 선호합니다.
보수적인 투자를 선호하며, 담배나 무기 관련 기업은 제외하고 싶습니다.""",

        """20대 대학생입니다. 월 50만원 정도를 1년 이상 투자하려고 하는데,
고위험 고수익을 추구하며 환율과 금리 변동에 관심이 있습니다. ESG 투자도 고려하고 싶어요.""",

        """40대 중반입니다. 노후 대비를 위해 월 200만원씩 10년 이상 장기 투자할 계획입니다.
안정적인 배당 수익을 원하며, 국내외 시장에 분산 투자하고 싶습니다.""",

        """미국 시장에 투자하고 싶은데, S&P 500이나 나스닥 관련 ETF를 찾고 있습니다.
월 150만원 정도 중기 투자 예정이고, 적당한 위험은 감수할 수 있습니다."""
    ],
    type="messages",
    theme=gr.themes.Soft(),
    css="""
    .message-wrap {
        max-width: 100% !important;
    }
    """
)

# 앱 실행
if __name__ == "__main__":
    demo.launch(
        server_name="0.0.0.0",  # 허깅페이스 배포를 위해 모든 인터페이스에서 접근 가능하도록 설정
        server_port=7860,
        share=False
    )
