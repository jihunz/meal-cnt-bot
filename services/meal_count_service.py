import json
from pathlib import Path

from models.meal_count import MealCountModel
from schemas.meal_count import MealCountResult
from services.email_service import EmailService
from services.event_service import EventService
from utils.auth import get_google_credentials
from utils.date_util import DateUtil


class MealCountService:
    """식사 인원 관리 서비스"""

    def __init__(self, config_file='config/config.json'):
        """서비스 초기화"""
        self.config_file = config_file
        self.credentials = get_google_credentials(config_file)
        self.event_service = EventService(config_file)
        self.email_service = EmailService(self.credentials)
        self.meal_count_model = MealCountModel(config_file)
        self.data_file = Path("data/meal_counts.json")

    def get_saved_meal_count(self):
        """저장된 식사 인원 정보 확인"""
        if not self.data_file.exists():
            return None

        try:
            with open(self.data_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                today = DateUtil.get_now().strftime("%Y-%m-%d")

                if today in data:
                    print(f"[{DateUtil.get_now()}] 저장된 식사 인원 정보를 사용합니다: {data[today]}명")
                    return data[today]

                return None
        except Exception as e:
            print(f"[{DateUtil.get_now()}] 저장된 식사 인원 정보를 불러오는 중 오류가 발생했습니다: {str(e)}")
            return None

    def process_meal_count(self):
        """식사 인원 계산 및 처리"""
        # 미리 저장된 식사 인원이 있는지 확인
        saved_count = self.get_saved_meal_count()
        if saved_count is not None:
            # 저장된 식사 인원 정보가 있으면 그것을 사용
            result = MealCountResult(
                count=saved_count,
                included_people=["수동 입력"],
                excluded_people=["수동 입력"],
                default_count=saved_count
            )
            return result

        # 공휴일, 휴일 확인
        is_holiday, holiday_info = self.event_service.is_holiday()
        if is_holiday:
            print(f'[{DateUtil.get_now()}] 오늘은 공휴일입니다: {holiday_info}')
            return None

        # 워크샵 등 기타 일정 확인
        if self.event_service.check_workshop_event():
            print(f'[{DateUtil.get_now()}] 오늘은 워크샵이 예정되어 있습니다.')
            return None

        # 월간회의 확인
        if self.event_service.check_monthly_meeting():
            print(f'[{DateUtil.get_now()}] 월간회의 일정이 있습니다. 기본 제외 인원도 포함합니다.')
            self.meal_count_model.add_default_excluded_people()

        # 식사 제외 인원 계산
        for cal_id in self.meal_count_model.config['CAL_ID_LIST']:
            events = self.event_service.get_event_list(cal_id)
            self.meal_count_model.exclude_people_from_events(events)

        # 최종 식사 인원 계산
        result = self.meal_count_model.calculate_meal_count()

        # 로그 출력
        print(
            f'[{DateUtil.get_now()}] 연구소 식사 인원 - 포함: {result.count}{result.included_people}, '
            f'제외: {len(result.excluded_people)}{result.excluded_people}, '
            f'기본 인원수: {result.default_count}'
        )

        return result

    def run_meal_count_job(self):
        """식사 인원 계산 작업 실행"""
        meal_count_result = self.process_meal_count()

        if meal_count_result:
            self.email_service.send_email(meal_count_result.count)
            return meal_count_result

        return None
