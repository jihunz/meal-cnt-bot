import datetime
import pytz
from models.meal_count import MealCountModel
from services.event_service import EventService
from services.email_service import EmailService
from schemas.meal_count import MealCountResult
from utils.auth import get_google_credentials


class MealCountService:
    """식사 인원 관리 서비스"""
    
    def __init__(self, config_file='config/config.json'):
        """서비스 초기화"""
        self.config_file = config_file
        self.credentials = get_google_credentials(config_file)
        self.event_service = EventService(config_file)
        self.email_service = EmailService(self.credentials)
        self.meal_count_model = MealCountModel(config_file)
        self.now = datetime.datetime.now(pytz.timezone('Asia/Seoul'))
    
    def should_skip_meal_count(self):
        """식사 인원 계산을 건너뛰어야 하는지 확인"""
        # EventService의 통합 메소드 사용
        return self.event_service.should_skip_meal_count()
    
    def process_meal_count(self):
        """식사 인원 계산 및 처리"""
        # 이미 계산을 건너뛰어야 하는지 확인
        if self.should_skip_meal_count():
            return None
        
        # 월간회의 확인
        if self.event_service.check_monthly_meeting():
            print(f'[{self.now}] 월간회의 일정이 있습니다. 기본 제외 인원도 포함합니다.')
            self.meal_count_model.add_default_excluded_people()
        
        # 식사 제외 인원 계산
        for cal_id in self.meal_count_model.config['CAL_ID_LIST']:
            events = self.event_service.get_event_list(cal_id)
            self.meal_count_model.exclude_people_from_events(events)
        
        # 최종 식사 인원 계산
        result = self.meal_count_model.calculate_meal_count()
        
        # 로그 출력
        print(
            f'[{self.now}] 연구소 식사 인원 - 포함: {result.count}{result.included_people}, '
            f'제외: {len(result.excluded_people)}{result.excluded_people}, '
            f'기본 인원수: {result.default_count}'
        )
        
        return result
    
    def send_meal_count_email(self, meal_count_result):
        """식사 인원을 이메일로 전송"""
        if not meal_count_result:
            return False, "식사 인원 계산이 수행되지 않았습니다."
        
        # 이제 count 값만 전달
        return self.email_service.send_meal_count_email(meal_count_result.count)
    
    def run_meal_count_job(self):
        """식사 인원 계산 작업 실행"""
        meal_count_result = self.process_meal_count()
        
        if meal_count_result:
            self.send_meal_count_email(meal_count_result)
            return meal_count_result
        
        return None 