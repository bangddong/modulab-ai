# 프로젝트 구조

```
hf-etf-bot/
│
├── 핵심 실행 파일
│   ├── app.py                   (27KB)   메인 애플리케이션
│   ├── config.py                (453B)   설정 파일
│   ├── requirements.txt         (175B)   Python 의존성 목록
│   ├── etf_database.db          (252KB)  SQLite DB (930개 ETF)
│   ├── test_db.py               (3.6KB)  DB 검증 스크립트
│   ├── .env.example             (130B)   환경 변수 템플릿
│   └── .gitignore               (333B)   Git 제외 목록
│
├── README.md                    (11KB)   시스템 개요 및 아키텍처
│
└── docs/                                  상세 문서 모음
    ├── 00_START_HERE.md         (9.9KB)  시작 가이드
    ├── SUMMARY.md               (12KB)   프로젝트 전체 요약
    ├── DEPLOYMENT.md            (6.0KB)  허깅페이스 배포 가이드
    ├── USAGE_GUIDE.md           (8.2KB)  상세 사용법 및 FAQ
    ├── CHECKLIST.md             (6.2KB)  배포 전 체크리스트 (98개)
    └── CHANGELOG.md             (3.3KB)  변경 이력
```

## 파일 설명

### 배포 필수 파일 (허깅페이스 스페이스)

| 파일 | 크기 | 필수 | 설명 |
|------|------|------|------|
| app.py | 27KB | ✓ | Gradio 애플리케이션 메인 파일 |
| requirements.txt | 175B | ✓ | Python 패키지 의존성 |
| etf_database.db | 252KB | ✓ | ETF 데이터베이스 |
| README.md | 11KB | ✓ | Space 설명 (자동 표시) |
| .env (환경변수) | - | ✓ | OPENAI_API_KEY 설정 |

### 선택 파일

| 파일 | 용도 |
|------|------|
| config.py | 설정값 중앙 관리 |
| test_db.py | 로컬 DB 검증용 |
| .gitignore | Git 버전 관리용 |

### 문서 파일 (docs/)

배포에 필수는 아니지만 사용자 안내에 유용:

| 문서 | 대상 | 읽는 시간 |
|------|------|----------|
| 00_START_HERE.md | 모든 사용자 | 5분 |
| SUMMARY.md | 개발자/관리자 | 10분 |
| DEPLOYMENT.md | 배포 담당자 | 15분 |
| USAGE_GUIDE.md | 최종 사용자 | 15분 |
| CHECKLIST.md | 배포 담당자 | 10분 |
| CHANGELOG.md | 개발자 | 5분 |

## 읽는 순서

### 빠른 배포 (최소)

```
1. README.md              시스템 개요 파악
2. docs/DEPLOYMENT.md     배포 가이드 따라하기
3. 파일 업로드 및 환경변수 설정
```

예상 소요 시간: 20분

### 완전한 이해 (권장)

```
1. docs/00_START_HERE.md  시작 가이드
2. docs/SUMMARY.md        전체 시스템 이해
3. README.md              아키텍처 확인
4. docs/DEPLOYMENT.md     배포 실행
5. docs/USAGE_GUIDE.md    사용법 학습
```

예상 소요 시간: 50분

## 총 용량

```
전체 크기: 약 340KB
압축 시:   약 280KB
```

매우 가벼워서 GitHub, 허깅페이스 등 어디든 배포 가능

---

**업데이트**: 2025-01-18
**버전**: v2.0.0
