import os
import uvicorn
import json
from fastapi import FastAPI, Request, Depends, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from routers import scheduler_router, meal_count_router
from services.meal_count_service import MealCountService
from schemas.meal_count import MealCountResult

# 설정 파일 로드
with open("config/config.json", "r") as f:
    config = json.load(f)

# FastAPI 애플리케이션 생성
app = FastAPI(
    title="VETEC 연구소 식사 인원 관리",
    description="Google Calendar를 사용하여 식사 인원을 자동으로 계산하고 이메일로 전송하는 API",
    version="1.0.0"
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 라우터 등록
app.include_router(scheduler_router.router)
app.include_router(meal_count_router.router)

# 정적 파일 및 템플릿 설정
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

@app.get("/")
async def root(request: Request):
    """통합 메인 페이지"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/detail")
async def detail(request: Request):
    """상세 페이지 (레거시 지원)"""
    return templates.TemplateResponse("detail.html", {"request": request})

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """전역 예외 처리"""
    return JSONResponse(
        status_code=500,
        content={"message": f"서버 오류가 발생했습니다: {str(exc)}"}
    )


def start_scheduler():
    """애플리케이션 시작 시 스케줄러 시작"""
    from services.scheduler_service import SchedulerService
    scheduler = SchedulerService()
    scheduler.start()


# 애플리케이션 시작 시 스케줄러 시작
@app.on_event("startup")
async def startup_event():
    """애플리케이션 시작 이벤트"""
    # 스케줄러 시작
    start_scheduler()


# 애플리케이션 종료 시 스케줄러 종료
@app.on_event("shutdown")
async def shutdown_event():
    """애플리케이션 종료 이벤트"""
    # 스케줄러 종료
    from routers.scheduler_router import get_scheduler_service
    scheduler = get_scheduler_service()
    scheduler.stop()


if __name__ == "__main__":
    # 실행 환경에 따라 호스트 결정
    host = "0.0.0.0"
    port = int(config["port"])

    print(f"🚀 식사 인원 봇 API 서버가 시작됩니다: http://{host}:{port}")
    uvicorn.run("main:app", host=host, port=port, reload=True)
