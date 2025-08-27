## VSCode 설치

https://code.visualstudio.com/

## uv 설치

https://github.com/astral-sh/uv

### Windows

```java
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

## VS Code 필수 확장 프로그램 설치

1. Python
2. Jupyter

## uv 가상환경 설정

### init

```java
uv init example
```

### 가상환경 생성 및 실행

```java
uv venv
.venv\Scripts\activate // uv venv시 Activate with로 나오는 Command 입력. OS에 따라 다름
```

### 필수 패키지 추가

```java
uv add ipykernel python-dotenv
```

Q. 왜 가상환경을 구성해야 하나요?

A. 패키지별 의존성으로 인해 잦은 충돌이 발생해 실습별 격리를 위해 진행합니다. 만약 실습 중 충돌이 발생한다면 아래와 같은 방법으로 해결할 수 있습니다
```java
.venv 폴더 삭제
uv venv
uv sync (pyproject.toml 내 dependencies를 통해 sync)
```