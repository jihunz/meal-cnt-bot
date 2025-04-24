# 식사 인원 봇

Google Calendar를 사용하여 식사 인원을 자동으로 계산하고 이메일로 전송하는 봇입니다.

## 개발 환경 설정

### 사전 요구사항

- Python 3.12 이상
- [Poetry](https://python-poetry.org/docs/#installation)
- (선택) [pyenv](https://github.com/pyenv/pyenv) - Python 버전 관리

### 설치 방법

1. Poetry 설치 (아직 설치하지 않은 경우)
   ```bash
   # macOS / Linux / WSL
   curl -sSL https://install.python-poetry.org | python3 -
   
   # Windows PowerShell
   Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing | python -
   ```

2. 올바른 Python 버전 설정 (pyenv 사용 시)
   ```bash
   pyenv install 3.12.2
   pyenv local 3.12.2
   ```

3. 의존성 설치
   ```bash
   poetry install
   ```

4. 가상환경 활성화
   ```bash
   poetry shell
   ```

## 실행 방법

### 개발 모드로 실행
```bash
poetry run dev
# 또는
poetry run uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### 프로덕션 모드로 실행
```bash
poetry run start
# 또는
poetry run uvicorn main:app --host 0.0.0.0 --port 8000
```

### Docker로 실행
```bash
docker-compose up -d
```

## API 문서

애플리케이션 실행 후 다음 URL에서 API 문서를 확인할 수 있습니다:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc` 