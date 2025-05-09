import datetime
import json
import requests
from googleapiclient.discovery import build
from utils.auth import get_google_credentials
from utils.date_util import DateUtil

class EventService:
    """이벤트 및 날짜 관련 기능을 통합적으로 제공하는 서비스 클래스"""

    def __init__(self, config_file='config/config.json'):
        """이벤트 서비스 초기화"""
        self.config_file = config_file
        with open(self.config_file, 'r', encoding='utf-8') as f:
            self.config = json.load(f)
        self.creds = get_google_credentials(config_file)
        self.calendar_service = build('calendar', 'v3', credentials=self.creds)
        self.holiday_api_key = 'o9Nl5P8j/q+4yxmDuPD/lUHILUtj804RYh/jJl0KZofUB9mSV/fWhLL1kXyTht+ylHs+cAv/77S7g4kweuVp5A=='

    # Calendar 관련 메소드
    def get_event_list(self, cal_id, days=1):
        """특정 기간 내의 캘린더 이벤트 목록 가져오기"""
        start = DateUtil.get_now().replace(hour=0, minute=0, second=0, microsecond=0)
        end = start + datetime.timedelta(days=days)

        events_result = self.calendar_service.events().list(
            calendarId=cal_id,
            timeMin=start.isoformat(),
            timeMax=end.isoformat(),
            singleEvents=True,
            orderBy='startTime'
        ).execute()

        return events_result.get('items', [])

    def check_workshop_event(self):
        """워크샵 일정 확인"""
        for event in self.get_event_list(self.config['BUSINESS_CAL_ID'], 1):
            if '워크샵' in event['summary']:
                return True
        return False

    def check_monthly_meeting(self):
        """월간회의 일정 확인"""
        events = self.get_event_list(self.config['BUSINESS_CAL_ID'], 2)
        for event_item in events:
            if '월간회의' in event_item['summary']:
                return True
        return False

    # Holiday 관련 메소드
    def is_holiday(self):
        """현재 날짜가 휴일(주말 또는 공휴일)인지 확인"""
        # 주말 확인 (토요일=5, 일요일=6)

        weekday = DateUtil.get_now().weekday()
        if weekday in (5, 6):
            return True, '주말'

        # 공휴일 확인
        return self._check_public_holiday()

    def _check_public_holiday(self):
        """공공 API를 통해 공휴일 확인"""
        formatted_now = DateUtil.get_now().strftime("%Y%m%d")
        curr_year = DateUtil.get_now().strftime("%Y")
        curr_month = DateUtil.get_now().strftime("%m")

        url = 'http://apis.data.go.kr/B090041/openapi/service/SpcdeInfoService/getRestDeInfo'
        params = {
            'serviceKey': self.holiday_api_key,
            'pageNo': '1',
            'numOfRows': '100',
            'solYear': curr_year,
            'solMonth': curr_month,
            '_type': 'json'
        }

        try:
            response = requests.get(url, params=params)
            if response.status_code != 200:
                return False, None

            res = response.json()

            if res['response']['body']['totalCount'] == 0:
                return False, None

            data = res['response']['body']['items']['item']
            if isinstance(data, dict):
                data = [data]

            for holiday in data:
                if (formatted_now == str(holiday['locdate'])) and (holiday['isHoliday'] == 'Y'):
                    return True, holiday

            return False, None

        except Exception as e:
            return False, str(e)
