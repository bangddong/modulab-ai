# 허깅페이스 스페이스 배포 가이드

본 문서는 ETF 추천 시스템을 Hugging Face Spaces에 배포하는 방법을 설명합니다.

## 사전 준비

### 1. Hugging Face 계정 생성

1. [Hugging Face](https://huggingface.co/) 접속
2. 회원가입 또는 로그인

### 2. OpenAI API Key 발급

1. [OpenAI Platform](https://platform.openai.com/) 접속
2. API Keys 메뉴에서 새 키 발급
3. 발급된 키를 안전한 곳에 저장

## 배포 절차

### 방법 1: 웹 인터페이스 사용 (권장)

#### Step 1: 새 Space 생성

1. Hugging Face 로그인 후 프로필 메뉴 클릭
2. "New Space" 선택
3. 다음 정보 입력:
   - **Space name**: `etf-recommendation-bot` (또는 원하는 이름)
   - **License**: MIT
   - **Select the Space SDK**: **Gradio** 선택
   - **Hardware**: CPU (basic, free) 선택
   - **Visibility**: Public 또는 Private

#### Step 2: 파일 업로드

생성된 Space에서 "Files" 탭으로 이동하여 다음 파일들을 업로드:

```
필수 파일:
- app.py
- requirements.txt
- etf_database.db
- README.md

선택 파일:
- config.py
- .gitignore
```

업로드 방법:
1. "Add file" > "Upload files" 클릭
2. 파일 드래그 앤 드롭 또는 선택
3. Commit message 입력 (예: "Initial commit")
4. "Commit changes to main" 클릭

#### Step 3: 환경 변수 설정

1. Space의 "Settings" 탭으로 이동
2. "Variables and secrets" 섹션 찾기
3. "New secret" 클릭
4. 다음 정보 입력:
   - **Name**: `OPENAI_API_KEY`
   - **Value**: OpenAI에서 발급받은 API 키
5. "Save" 클릭

#### Step 4: 빌드 확인

1. "App" 탭으로 이동
2. 자동으로 빌드 시작 (수 분 소요)
3. 빌드 로그 확인:
   - 의존성 설치
   - 애플리케이션 시작
4. 빌드 완료 후 Gradio 인터페이스 표시

### 방법 2: Git 사용 (고급)

#### Step 1: Space 생성 (웹 인터페이스)

위의 방법 1과 동일하게 Space 생성

#### Step 2: 로컬에서 클론

```bash
# Hugging Face CLI 설치
pip install huggingface_hub

# 로그인
huggingface-cli login

# Space 클론
git clone https://huggingface.co/spaces/YOUR_USERNAME/etf-recommendation-bot
cd etf-recommendation-bot
```

#### Step 3: 파일 복사 및 푸시

```bash
# 파일 복사
copy ..\hf-etf-bot\* .

# Git 추가 및 커밋
git add .
git commit -m "Initial deployment"
git push
```

#### Step 4: 환경 변수 설정

웹 인터페이스에서 Settings > Variables and secrets 설정

## 배포 확인

### 1. 앱 접속

Space URL: `https://huggingface.co/spaces/YOUR_USERNAME/SPACE_NAME`

### 2. 기능 테스트

다음 테스트 질문 입력:

```
30대 직장인입니다. 월 100만원 정도를 3년 이상 장기 투자하고 싶고,
IT와 헬스케어 섹터를 선호합니다. 보수적인 투자를 선호합니다.
```

### 3. 예상 결과

- 투자 전략 개요
- ETF 추천 테이블 (3개)
- 각 ETF 상세 분석
- 투자 시 고려사항

## 문제 해결

### 빌드 실패

**증상**: Space가 시작되지 않음

**해결 방법**:
1. "Logs" 탭에서 오류 메시지 확인
2. 일반적인 원인:
   - requirements.txt 오류 → 버전 확인
   - 환경 변수 미설정 → OPENAI_API_KEY 확인
   - 파일 누락 → 모든 필수 파일 업로드 확인

### API 키 오류

**증상**: "OPENAI_API_KEY가 설정되지 않았습니다" 오류

**해결 방법**:
1. Settings > Variables and secrets 확인
2. 키 이름이 정확히 `OPENAI_API_KEY`인지 확인
3. Space 재시작 (Settings > Factory reboot)

### 데이터베이스 오류

**증상**: "no such table: ETFs" 오류

**해결 방법**:
1. `etf_database.db` 파일이 업로드되었는지 확인
2. 파일 크기 확인 (약 250KB)
3. 파일 재업로드

### 느린 응답

**증상**: 추천 결과가 나오는 데 오래 걸림

**해결 방법**:
1. 무료 CPU 사용 시 정상 (10-20초)
2. 더 빠른 응답이 필요한 경우:
   - Settings > Hardware > Upgrade 고려
   - 유료 GPU 사용

## 성능 최적화

### 1. 하드웨어 업그레이드

| 하드웨어 | 비용 | 예상 응답 시간 |
|---------|------|---------------|
| CPU basic (free) | 무료 | 10-20초 |
| CPU upgraded | $0.03/hour | 5-10초 |
| GPU T4 small | $0.60/hour | 3-5초 |

### 2. 코드 최적화

app.py에서 다음 설정 조정:

```python
# config.py
DEFAULT_MODEL = "gpt-3.5-turbo"  # 더 빠른 모델 사용
TEMPERATURE = 0.3  # 더 빠른 생성
```

### 3. 캐싱

프로필 분석 결과나 SQL 쿼리 캐싱 (향후 버전)

## Space 관리

### 로그 확인

1. "Logs" 탭에서 실시간 로그 확인
2. 오류 발생 시 스택 트레이스 확인

### Space 재시작

1. Settings 탭
2. "Factory reboot" 클릭
3. 몇 분 대기

### Space 삭제

1. Settings 탭
2. 하단 "Delete this space" 클릭
3. 확인

## 모니터링

### 사용량 확인

1. Space 대시보드에서 확인:
   - 방문자 수
   - API 호출 수
   - 하드웨어 사용률

### 비용 관리

1. 무료 티어 사용 시 비용 없음
2. 유료 하드웨어 사용 시:
   - 사용 시간 모니터링
   - 필요 시 다운그레이드

## 업데이트 방법

### 웹 인터페이스

1. Files 탭
2. 수정할 파일 클릭
3. Edit 클릭
4. 수정 후 Commit

### Git

```bash
# 로컬에서 수정
git add .
git commit -m "Update message"
git push
```

## 추가 기능

### 1. 분석 도구 연동

Google Analytics나 Hugging Face Analytics 연동 가능

### 2. 커스텀 도메인

유료 플랜에서 커스텀 도메인 설정 가능

### 3. 프라이빗 Space

민감한 데이터 사용 시 Private Space 설정

## 참고 자료

- [Hugging Face Spaces 문서](https://huggingface.co/docs/hub/spaces)
- [Gradio 문서](https://gradio.app/docs/)
- [LangChain 문서](https://python.langchain.com/)
- [OpenAI API 문서](https://platform.openai.com/docs/)

## 지원

문제 발생 시:
1. Hugging Face Community Forum
2. GitHub Issues (프로젝트 저장소)
3. 개발자에게 문의

---

**작성일**: 2025년
**업데이트**: 배포 후 지속적으로 업데이트 예정
