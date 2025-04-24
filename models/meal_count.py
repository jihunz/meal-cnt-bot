import json
from schemas.meal_count import MealCountResult


class MealCountModel:
    """식사 인원 계산을 위한 모델 클래스"""
    
    def __init__(self, config_file='config/config.json'):
        """식사 인원 모델 초기화"""
        self.config_file = config_file
        with open(self.config_file, 'r', encoding='utf-8') as f:
            self.config = json.load(f)
        
        # 기본 설정
        self.meal_exclude_list = []
        self.default_exclude_list = ['김인경', '윤현석', '한혜영', '배건길']
        self.meal_cnt_list = ['장지훈', '김태준', '서대원', '조주형', '김형진', '김대현']
        self.default_meal_cnt = len(self.meal_cnt_list)
    
    def reset_lists(self):
        """식사 인원 계산을 위한 리스트 초기화"""
        self.meal_exclude_list = []
        self.meal_cnt_list = ['장지훈', '김태준', '서대원', '조주형', '김형진', '김대현']
        self.default_meal_cnt = len(self.meal_cnt_list)
    
    def add_default_excluded_people(self):
        """월간회의 등의 경우 기본 제외 인원도 식사 인원에 포함"""
        self.meal_cnt_list.extend(self.default_exclude_list)
        self.default_meal_cnt = len(self.meal_cnt_list)
    
    def exclude_people_from_events(self, event_list):
        """이벤트에서 식사에서 제외할 인원 계산"""
        for event in event_list:
            if 'dateTime' in event['start']:
                continue
            
            if 'summary' not in event:
                continue
                
            # 이벤트 요약에서 인원 목록 추출
            if '-' in event['summary']:
                person_list = [name.strip() for name in event['summary'].split('-')[0].split(',')]
                
                for name in person_list:
                    if name in self.meal_exclude_list:
                        continue
                    if name not in self.meal_cnt_list:
                        continue
                    self.meal_cnt_list.remove(name)
                    self.meal_exclude_list.append(name)
    
    def calculate_meal_count(self):
        """최종 식사 인원 계산"""
        result = len(self.meal_cnt_list)
        if result < 0:
            result = 0
            
        return MealCountResult(
            count=result,
            included_people=self.meal_cnt_list,
            excluded_people=self.meal_exclude_list,
            default_count=self.default_meal_cnt
        ) 