import asyncio
from datetime import datetime
import pytz
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from services.meal_count_service import MealCountService


class SchedulerService:
    """작업 스케줄링을 위한 서비스 클래스"""

    def __init__(self):
        """스케줄러 서비스 초기화"""
        self.scheduler = AsyncIOScheduler(timezone='Asia/Seoul')
        self.meal_count_service = MealCountService()
        self.is_running = False

    def start(self):
        """스케줄러 시작"""
        if self.is_running:
            return

        # 평일(월-금) 오전 9:10에 식사 인원 계산 작업 스케줄링
        self.scheduler.add_job(
            self.run_meal_count_job,
            'cron',
            day_of_week='mon-fri',
            hour=9,
            minute=10
        )

        self.scheduler.start()
        self.is_running = True
        print(f'[{datetime.now(pytz.timezone("Asia/Seoul"))}] meal_cnt_bot 스케줄러가 시작되었습니다')

    def stop(self):
        """스케줄러 중지"""
        if not self.is_running:
            return

        self.scheduler.shutdown()
        self.is_running = False
        print(f'[{datetime.now(pytz.timezone("Asia/Seoul"))}] meal_cnt_bot 스케줄러가 종료되었습니다')

    async def run_meal_count_job(self):
        """식사 인원 계산 작업 실행"""
        # 비동기 환경에서 동기 작업 실행
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, self.meal_count_service.run_meal_count_job)

    def is_scheduler_running(self):
        """스케줄러 실행 상태 확인"""
        return self.is_running
