FROM python:3.12-slim

# 작업 디렉토리 생성
WORKDIR /app

# 필요한 시스템 패키지 설치
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Poetry 설치
RUN pip install --no-cache-dir poetry==1.7.1

# Poetry 설정 - 가상환경 생성하지 않음 (Docker 내부이므로 필요 없음)
RUN poetry config virtualenvs.create false

# 의존성 파일 복사 (캐싱 활용을 위해 먼저 복사)
COPY pyproject.toml poetry.lock* ./

# 의존성 설치
RUN poetry install --no-dev --no-interaction --no-ansi

# 소스 코드 복사
COPY . .

# 환경 변수 설정
ENV DOCKER_ENV=1

# 포트 노출
EXPOSE 8000

# 컨테이너 시작 시 실행될 명령
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
