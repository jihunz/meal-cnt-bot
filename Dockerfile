# 베이스 이미지로 가벼운 python:3.9-slim 사용
FROM python:3.12-slim

# 작업 디렉토리 생성
WORKDIR /app

# 필요한 시스템 패키지 설치
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# 의존성 파일 복사 (캐싱 활용을 위해 먼저 복사)
COPY requirements.txt .

# pip 업그레이드 및 의존성 설치
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# 소스 코드 복사
COPY . .

# 컨테이너 시작 시 실행될 명령
CMD ["python", "main.py"]
