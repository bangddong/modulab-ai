# 배포 전 체크리스트

허깅페이스 스페이스 배포 전 최종 확인 사항

## 1. 파일 확인

### 필수 파일

- [ ] `app.py` (27KB) - 메인 애플리케이션
- [ ] `requirements.txt` (175B) - 의존성 목록
- [ ] `etf_database.db` (252KB) - ETF 데이터베이스
- [ ] `README.md` (11KB) - 프로젝트 설명

### 선택 파일 (권장)

- [ ] `config.py` - 설정 파일
- [ ] `.gitignore` - Git 제외 목록
- [ ] `DEPLOYMENT.md` - 배포 가이드
- [ ] `USAGE_GUIDE.md` - 사용 가이드
- [ ] `CHANGELOG.md` - 변경 이력

## 2. 환경 설정

### OpenAI API Key

- [ ] OpenAI 계정 생성 완료
- [ ] API Key 발급 완료
- [ ] API Key 복사 및 안전하게 보관
- [ ] 사용 한도 확인 (최소 $5 크레딧 권장)

### Hugging Face 계정

- [ ] Hugging Face 계정 생성 완료
- [ ] 로그인 확인
- [ ] Space 생성 권한 확인

## 3. 로컬 테스트 (선택)

### 데이터베이스 검증

```bash
cd hf-etf-bot
python test_db.py
```

- [ ] 데이터베이스 연결 성공
- [ ] 930개 ETF 확인
- [ ] 샘플 데이터 정상 조회

### 코드 구문 검증

```bash
python -m py_compile app.py
python -m py_compile config.py
```

- [ ] app.py 구문 오류 없음
- [ ] config.py 구문 오류 없음

### 의존성 설치 테스트 (선택)

```bash
pip install -r requirements.txt
```

- [ ] 모든 패키지 설치 성공
- [ ] 버전 충돌 없음

## 4. 배포 준비

### Space 설정

- [ ] Space 이름 결정 (예: etf-recommendation-bot)
- [ ] Space 타입: Gradio 선택
- [ ] 하드웨어: CPU basic (무료) 선택
- [ ] 공개 설정: Public 또는 Private 선택

### 파일 업로드 준비

- [ ] 모든 파일을 하나의 폴더에 준비
- [ ] 파일 경로 확인 (상대 경로 사용)
- [ ] 파일 크기 확인 (총 ~1MB)

## 5. 배포 실행

### 웹 인터페이스 방법

- [ ] Hugging Face 로그인
- [ ] "New Space" 클릭
- [ ] Space 정보 입력
- [ ] Space 생성 완료
- [ ] "Files" 탭으로 이동
- [ ] 파일 업로드 (드래그 앤 드롭 또는 선택)
- [ ] Commit message 입력
- [ ] "Commit changes to main" 클릭

### 환경 변수 설정

- [ ] "Settings" 탭으로 이동
- [ ] "Variables and secrets" 섹션 찾기
- [ ] "New secret" 클릭
- [ ] Name: `OPENAI_API_KEY` 입력 (정확히)
- [ ] Value: OpenAI API Key 붙여넣기
- [ ] "Save" 클릭

## 6. 빌드 확인

### 빌드 모니터링

- [ ] "App" 탭으로 이동
- [ ] 빌드 시작 확인
- [ ] "Building" 상태 확인
- [ ] 로그에서 오류 없는지 확인
- [ ] "Running" 상태로 전환 확인

예상 빌드 시간: 3-5분

### 빌드 성공 확인

빌드 로그에서 다음 메시지 확인:

```
Installing dependencies...
✓ gradio
✓ langchain
✓ langchain-openai
...
Running on local URL:  http://0.0.0.0:7860
```

## 7. 기능 테스트

### 기본 기능 테스트

- [ ] Gradio 인터페이스 로딩 확인
- [ ] 예제 질문 클릭 테스트
- [ ] 커스텀 질문 입력 테스트

### 테스트 질문 예시

```
30대 직장인입니다. 월 100만원 정도를 3년 이상 장기 투자하고 싶고,
IT와 헬스케어 섹터를 선호합니다. 보수적인 투자를 선호합니다.
```

### 예상 결과 확인

- [ ] 10-20초 내 응답 생성
- [ ] 투자 전략 개요 표시
- [ ] ETF 추천 테이블 (3개) 표시
- [ ] 각 ETF 상세 분석 표시
- [ ] 투자 시 고려사항 표시
- [ ] 마크다운 포맷 정상 렌더링

## 8. 오류 해결

### 빌드 실패 시

- [ ] "Logs" 탭에서 오류 메시지 확인
- [ ] requirements.txt 버전 확인
- [ ] 파일 누락 여부 확인
- [ ] Space 재시작 시도 (Settings > Factory reboot)

### API 키 오류 시

```
오류: "OPENAI_API_KEY가 설정되지 않았습니다"
```

- [ ] Settings > Variables and secrets 확인
- [ ] 키 이름이 정확히 `OPENAI_API_KEY`인지 확인
- [ ] 키 값이 올바른지 확인
- [ ] Space 재시작

### 데이터베이스 오류 시

```
오류: "no such table: ETFs"
```

- [ ] `etf_database.db` 파일 업로드 확인
- [ ] 파일 크기 확인 (약 252KB)
- [ ] 파일 재업로드

## 9. 최적화 (선택)

### 성능 개선

- [ ] 응답 시간 측정 (10-20초 정상)
- [ ] 필요 시 하드웨어 업그레이드 고려
- [ ] 모델 변경 고려 (gpt-3.5-turbo로 변경 시 더 빠름)

### 사용자 경험

- [ ] 예제 질문 추가/수정
- [ ] 설명 텍스트 커스터마이징
- [ ] 테마 변경 (선택)

## 10. 문서화

### 사용자 안내

- [ ] README.md 확인
- [ ] USAGE_GUIDE.md 링크 공유
- [ ] 예제 질문 준비

### 유지보수

- [ ] CHANGELOG.md 업데이트 계획
- [ ] 버전 관리 계획
- [ ] 백업 계획

## 11. 공유 및 홍보 (선택)

### Space 공유

- [ ] Space URL 복사
- [ ] 소셜 미디어 공유
- [ ] 관련 커뮤니티에 소개

### 피드백 수집

- [ ] 사용자 피드백 수집 방법 결정
- [ ] 이슈 트래커 설정
- [ ] 개선 사항 리스트 작성

## 12. 최종 확인

### 전체 점검

- [ ] 모든 필수 파일 업로드 완료
- [ ] 환경 변수 설정 완료
- [ ] 빌드 성공 확인
- [ ] 기능 테스트 통과
- [ ] 오류 없음 확인

### 준비 완료

- [ ] Space URL 저장
- [ ] API 사용량 모니터링 설정
- [ ] 정기 점검 일정 수립

---

## 체크리스트 요약

```
파일 확인:        [ ] 10개 항목
환경 설정:        [ ] 7개 항목
로컬 테스트:      [ ] 7개 항목
배포 준비:        [ ] 8개 항목
배포 실행:        [ ] 12개 항목
빌드 확인:        [ ] 9개 항목
기능 테스트:      [ ] 12개 항목
오류 해결:        [ ] 10개 항목
최적화:           [ ] 5개 항목
문서화:           [ ] 6개 항목
공유 및 홍보:     [ ] 5개 항목
최종 확인:        [ ] 7개 항목

총 항목 수:       98개
```

## 배포 완료 후

축하합니다! ETF 추천 시스템이 성공적으로 배포되었습니다.

### 다음 단계

1. 정기적으로 모니터링
2. 사용자 피드백 수집
3. 지속적인 개선
4. 문서 업데이트

### 문제 발생 시

- DEPLOYMENT.md 참조
- USAGE_GUIDE.md FAQ 섹션 확인
- Hugging Face Community Forum 질문
- GitHub Issues (프로젝트가 있는 경우)

---

**작성일**: 2025-01-18
**버전**: v2.0.0
**난이도**: 초급~중급
**예상 소요 시간**: 10-15분
