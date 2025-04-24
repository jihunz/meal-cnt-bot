from fastapi import APIRouter, Depends
from services.scheduler_service import SchedulerService

router = APIRouter(
    prefix="/api/scheduler",
    tags=["scheduler"],
    responses={404: {"description": "Not found"}},
)


def get_scheduler_service():
    """스케줄러 서비스 가져오기"""
    # 싱글톤 패턴으로 구현하기 위해 전역 변수 사용
    if not hasattr(get_scheduler_service, "instance"):
        get_scheduler_service.instance = SchedulerService()
    return get_scheduler_service.instance


@router.post("/start")
async def start_scheduler(scheduler=Depends(get_scheduler_service)):
    """스케줄러 시작"""
    if scheduler.is_scheduler_running():
        return {"message": "스케줄러가 이미 실행 중입니다."}

    scheduler.start()
    return {"message": "스케줄러가 시작되었습니다."}


@router.post("/stop")
async def stop_scheduler(scheduler=Depends(get_scheduler_service)):
    """스케줄러 중지"""
    if not scheduler.is_scheduler_running():
        return {"message": "스케줄러가 이미 중지되었습니다."}

    scheduler.stop()
    return {"message": "스케줄러가 중지되었습니다."}


@router.get("/status")
async def scheduler_status(scheduler=Depends(get_scheduler_service)):
    """스케줄러 상태 확인"""
    status = "실행 중" if scheduler.is_scheduler_running() else "중지됨"
    return {"status": status}
