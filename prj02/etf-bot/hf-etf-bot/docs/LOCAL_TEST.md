# 로컬 테스트 가이드

배포 전 로컬 환경에서 앱을 테스트하는 방법입니다.

## Windows 환경 (현재 환경)

### 1단계: 환경 설정

#### OpenAI API Key 준비
```
https://platform.openai.com/account/api-keys
위 링크에서 API Key 발급
```

#### 가상환경 생성 (권장)
```cmd
# hf-etf-bot 폴더로 이동
cd E:\study\modulab-ai\prj02\etf-bot\hf-etf-bot

# 가상환경 생성
python -m venv venv

# 가상환경 활성화
venv\Scripts\activate

# 활성화 확인 (프롬프트 앞에 (venv) 표시됨)
```

### 2단계: 의존성 설치

```cmd
# requirements.txt 설치
pip install -r requirements.txt

# 설치 확인
pip list
```

예상 설치 패키지:
- gradio 4.44.1
- langchain 0.3.25
- langchain-openai 0.3.21 (자동으로 호환 openai 버전 설치)
- langgraph 0.4.8
- 기타 의존성

### 3단계: 환경 변수 설정

#### 방법 1: .env 파일 사용 (권장)

```cmd
# .env.example을 .env로 복사
copy .env.example .env

# .env 파일을 텍스트 에디터로 열기
notepad .env
```

.env 파일 내용:
```
OPENAI_API_KEY=sk-your-actual-api-key-here
```

발급받은 실제 API Key로 교체 후 저장

#### 방법 2: 환경 변수 직접 설정

```cmd
# 현재 세션에만 적용
set OPENAI_API_KEY=sk-your-actual-api-key-here

# 또는 시스템 환경 변수에 등록
# 제어판 > 시스템 > 고급 시스템 설정 > 환경 변수
```

### 4단계: 데이터베이스 검증 (선택)

```cmd
# DB 테스트 스크립트 실행
python test_db.py
```

예상 출력:
```
============================================================
ETF Database Verification Test
============================================================

✓ Database connected successfully
✓ Total ETFs: 930
✓ Found 14 columns
...
All tests passed successfully!
============================================================
```

### 5단계: 앱 실행

```cmd
# 애플리케이션 시작
python app.py
```

예상 출력:
```
Running on local URL:  http://127.0.0.1:7860

To create a public link, set `share=True` in `launch()`.
```

### 6단계: 브라우저에서 테스트

1. 웹 브라우저 열기
2. 주소창에 입력: `http://127.0.0.1:7860`
3. Gradio 인터페이스 확인

### 7단계: 기능 테스트

#### 테스트 질문 입력

```
30대 직장인입니다. 월 100만원 정도를 3년 이상 장기 투자하고 싶고,
IT와 헬스케어 섹터를 선호합니다. 보수적인 투자를 선호합니다.
```

#### 예상 응답 시간
- 프로필 분석: 2초
- SQL 생성: 3초
- ETF 검색: 1초
- 평가 및 순위: 3초
- 다양성 분석: 2초
- 설명 생성: 3-5초
**총 14-18초**

#### 확인 사항
- [ ] ETF 포트폴리오 추천 제목 표시
- [ ] 투자 전략 개요 출력
- [ ] ETF 추천 테이블 (3개) 표시
- [ ] 각 ETF 상세 분석 표시
- [ ] 투자 시 고려사항 표시
- [ ] 마크다운 형식 정상 렌더링

### 8단계: 종료

```cmd
# Ctrl+C로 서버 중지

# 가상환경 비활성화
deactivate
```

---

## Linux/Mac 환경

### 1단계: 가상환경 생성

```bash
# hf-etf-bot 폴더로 이동
cd /path/to/hf-etf-bot

# 가상환경 생성
python3 -m venv venv

# 가상환경 활성화
source venv/bin/activate
```

### 2단계: 의존성 설치

```bash
pip install -r requirements.txt
```

### 3단계: 환경 변수 설정

```bash
# .env 파일 생성
cp .env.example .env

# 편집기로 열기
nano .env
# 또는
vim .env

# API Key 입력 후 저장
```

### 4단계: 앱 실행

```bash
python app.py
```

나머지는 Windows와 동일

---

## 문제 해결

### 오류 1: ModuleNotFoundError

```
ModuleNotFoundError: No module named 'gradio'
```

**해결**:
```cmd
# 가상환경 활성화 확인
# requirements.txt 재설치
pip install -r requirements.txt
```

### 오류 2: OPENAI_API_KEY 미설정

```
ValueError: OPENAI_API_KEY가 설정되지 않았습니다.
```

**해결**:
```cmd
# .env 파일 확인
type .env  # Windows
cat .env   # Linux/Mac

# API Key가 올바른지 확인
# 파일이 없으면 다시 생성
```

### 오류 3: 데이터베이스 오류

```
sqlite3.OperationalError: no such table: ETFs
```

**해결**:
```cmd
# etf_database.db 파일 존재 확인
dir etf_database.db  # Windows
ls -lh etf_database.db  # Linux/Mac

# 파일이 없으면 원본에서 복사
# 파일 크기 확인 (약 252KB)
```

### 오류 4: 포트 이미 사용 중

```
OSError: [Errno 98] Address already in use
```

**해결**:
```cmd
# 방법 1: 다른 포트 사용
# app.py 마지막 부분 수정:
# demo.launch(server_port=7861)

# 방법 2: 기존 프로세스 종료
# Windows:
netstat -ano | findstr :7860
taskkill /PID <PID번호> /F

# Linux/Mac:
lsof -i :7860
kill <PID번호>
```

### 오류 5: OpenAI API 오류

```
openai.error.AuthenticationError: Incorrect API key provided
```

**해결**:
```cmd
# API Key 확인
# https://platform.openai.com/account/api-keys
# 새 키 발급 또는 기존 키 확인
# .env 파일 업데이트
```

### 오류 6: 의존성 충돌

```
ERROR: pip's dependency resolver does not currently take into account...
```

**해결**:
```cmd
# pip 업그레이드
pip install --upgrade pip

# 가상환경 재생성
deactivate
rmdir /s venv  # Windows
rm -rf venv    # Linux/Mac

python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

pip install -r requirements.txt
```

---

## 성능 체크리스트

### 정상 동작 확인

- [ ] 앱이 7860 포트에서 정상 실행
- [ ] 브라우저에서 인터페이스 로딩
- [ ] 예제 질문 클릭 시 정상 작동
- [ ] 커스텀 질문 입력 시 응답 생성
- [ ] 응답 시간 20초 이내
- [ ] 마크다운 형식 정상 표시
- [ ] 3개 ETF 추천 표시
- [ ] 오류 없이 여러 번 질문 가능

### 배포 전 최종 확인

- [ ] 모든 기능 테스트 통과
- [ ] 오류 메시지 없음
- [ ] API 사용량 확인 (비용)
- [ ] requirements.txt 정확성 확인
- [ ] .env.example 파일 존재 확인
- [ ] README.md 내용 정확성 확인

---

## 다음 단계

### 로컬 테스트 성공 후

1. **허깅페이스 배포**
   ```
   docs/DEPLOYMENT.md 참조
   ```

2. **문제 발견 시**
   ```
   - 코드 수정
   - 로컬에서 재테스트
   - 정상 동작 확인 후 배포
   ```

3. **성능 모니터링**
   ```
   - API 사용량 체크
   - 응답 시간 측정
   - 오류 로그 확인
   ```

---

## 팁

### 개발 모드 실행

app.py 마지막 부분을 다음과 같이 수정하면 자동 리로드:

```python
if __name__ == "__main__":
    demo.launch(
        server_name="127.0.0.1",  # 로컬만 접속
        server_port=7860,
        share=False,
        debug=True  # 디버그 모드 활성화
    )
```

### 공개 URL 생성 (임시 테스트용)

```python
demo.launch(share=True)  # Gradio가 임시 공개 URL 생성
```

약 72시간 유효한 공개 링크 생성됨

### 로그 확인

```cmd
# 상세 로그 출력
python app.py 2>&1 | tee app.log
```

---

**작성일**: 2025-01-18
**버전**: v2.0.0
**환경**: Windows 10/11, Python 3.10+
