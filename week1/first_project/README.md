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