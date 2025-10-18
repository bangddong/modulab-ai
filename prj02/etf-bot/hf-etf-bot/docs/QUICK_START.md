# 빠른 시작 가이드

배포 오류를 수정하고 로컬 테스트를 진행합니다.

## 수정 내역

### 문제: 의존성 충돌
```
ERROR: Cannot install openai==1.59.3
langchain-openai 0.3.21 depends on openai>=1.68.2
```

### 해결: requirements.txt 수정
```diff
- openai==1.59.3
(제거됨 - langchain-openai가 자동으로 호환 버전 설치)
```

## 로컬 테스트 (Windows)

### 빠른 3단계

#### 1. 환경 변수 설정

현재 폴더에 `.env` 파일 생성:

```cmd
cd hf-etf-bot
copy .env.example .env
notepad .env
```

`.env` 파일 내용:
```
OPENAI_API_KEY=sk-your-real-api-key-here
```

실제 OpenAI API Key로 교체 후 저장

#### 2. 의존성 설치

```cmd
pip install -r requirements.txt
```

예상 시간: 2-3분

#### 3. 앱 실행

```cmd
python app.py
```

브라우저에서 열기: http://127.0.0.1:7860

---

## 테스트 질문

```
30대 직장인입니다. 월 100만원 정도를 3년 이상 장기 투자하고 싶고,
IT와 헬스케어 섹터를 선호합니다. 보수적인 투자를 선호합니다.
```

**예상 응답 시간**: 15-20초

---

## 확인 사항

- [ ] 앱이 정상 실행됨
- [ ] 브라우저에서 인터페이스 표시
- [ ] 테스트 질문에 정상 응답
- [ ] ETF 3개 추천 표시
- [ ] 마크다운 형식 정상

---

## 문제 해결

### API Key 오류
```
ValueError: OPENAI_API_KEY가 설정되지 않았습니다.
```

**해결**: `.env` 파일 확인 및 재생성

### 모듈 없음 오류
```
ModuleNotFoundError: No module named 'gradio'
```

**해결**:
```cmd
pip install --upgrade pip
pip install -r requirements.txt
```

### 포트 사용 중
```
Address already in use
```

**해결**:
```cmd
# 다른 포트 사용
python -c "from app import demo; demo.launch(server_port=7861)"
```

---

## 허깅페이스 배포

로컬 테스트 성공 후:

1. Hugging Face Space 생성
2. 파일 업로드:
   - app.py
   - requirements.txt
   - etf_database.db
   - README.md
3. 환경 변수 설정: `OPENAI_API_KEY`
4. 빌드 완료 대기

상세 가이드: `docs/DEPLOYMENT.md`

---

## 참고 문서

- **LOCAL_TEST.md**: 상세 로컬 테스트 가이드
- **docs/DEPLOYMENT.md**: 허깅페이스 배포 가이드
- **docs/USAGE_GUIDE.md**: 사용법 및 FAQ

---

**수정 완료**: 2025-01-18
**이슈**: 의존성 충돌 해결
