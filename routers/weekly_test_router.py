"""
주간 테스트 API 라우터
주간 식사 인원 계산 테스트 관련 API 엔드포인트를 제공합니다.
"""

from fastapi import APIRouter, HTTPException
from services.weekly_test_service import WeeklyTestService
from utils.date_util import DateUtil

router = APIRouter(
    prefix="/api/weekly-test",
    tags=["weekly-test"],
    responses={404: {"description": "Not found"}}
)

# 주간 테스트 서비스 인스턴스
weekly_test_service = WeeklyTestService()


@router.post("/run")
async def run_weekly_test():
    """주간 테스트 실행 - 월요일부터 금요일까지 순차적으로 테스트"""
    try:
        results = weekly_test_service.run_weekly_test()
        return {
            "success": True,
            "message": "주간 테스트가 완료되었습니다.",
            "results": results
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"주간 테스트 실행 중 오류가 발생했습니다: {str(e)}")


@router.get("/summary")
async def get_weekly_summary():
    """현재 주의 식사 인원 요약 정보 조회"""
    try:
        summary = weekly_test_service.get_current_week_summary()
        return {
            "success": True,
            "summary": summary
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"주간 요약 정보 조회 중 오류가 발생했습니다: {str(e)}")


 