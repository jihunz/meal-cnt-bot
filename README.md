# 식사 인원 관리 시스템

Google Calendar를 사용하여 식사 인원을 자동으로 계산하고 이메일로 전송하는 시스템입니다.
추가로 수동으로 식사 인원을 입력하고 관리할 수 있는 웹 인터페이스를 제공합니다.

## 주요 기능

1. 수동 식사 인원 관리
   - 날짜별 식사 인원 입력 및 저장
   - 캘린더 형식으로 저장된 정보 조회
   - 저장된 정보 수정 및 삭제

2. 자동 식사 인원 계산
   - Google Calendar 일정 기반 식사 인원 자동 계산
   - 계산된 인원 수 이메일 전송

## 시스템 요구사항

- Python 3.12 이상
- 필요한 Python 라이브러리 (requirements.txt 또는 pyproject.toml 참조)

## 설치 및 실행 방법

### Poetry를 사용하는 경우

```bash
# 의존성 설치
poetry install

# 개발 서버 실행
poetry run dev
```

### Pip를 사용하는 경우

```bash
# 가상환경 생성 및 활성화 (선택사항)
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# 또는
.venv\Scripts\activate  # Windows

# 의존성 설치
pip install -r requirements.txt

# 서버 실행
python main.py
```

## 사용 방법

1. 메인 페이지 (http://localhost:8000)
   - 날짜 선택 및 식사 인원 입력
   - 저장 버튼 클릭

2. 상세 페이지 (http://localhost:8000/detail)
   - 캘린더 형식으로 저장된 식사 인원 조회
   - 일정을 클릭하여 식사 인원 수정
   - 일정을 우클릭하여 삭제 메뉴 표시

## API 엔드포인트

- `GET /api/meal-count/all`: 모든 식사 인원 정보 조회
- `GET /api/meal-count/{date}`: 특정 날짜의 식사 인원 정보 조회
- `POST /api/meal-count/save`: 식사 인원 정보 저장
- `PUT /api/meal-count/{date}`: 특정 날짜의 식사 인원 정보 수정
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