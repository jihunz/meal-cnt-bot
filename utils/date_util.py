import datetime
import pytz


class DateUtil:
    @classmethod
    def get_now(cls):
        return datetime.datetime.now(pytz.timezone('Asia/Seoul'))

    @classmethod
    def get_current_week_dates(cls):
        """현재 주의 월요일부터 금요일까지의 날짜 리스트 반환"""
        now = cls.get_now()
        # 현재 주의 월요일 찾기 (0=월요일, 6=일요일)
        monday = now - datetime.timedelta(days=now.weekday())
        
        weekdays = []
        for i in range(5):  # 월요일부터 금요일까지
            weekdays.append(monday + datetime.timedelta(days=i))
        
        return weekdays
    
    @classmethod
    def get_date_with_timezone(cls, target_date):
        """특정 날짜에 타임존을 적용하여 반환"""
        if isinstance(target_date, datetime.datetime):
            if target_date.tzinfo is None:
                return target_date.replace(tzinfo=pytz.timezone('Asia/Seoul'))
            return target_date
        elif isinstance(target_date, datetime.date):
            return datetime.datetime.combine(target_date, datetime.time()).replace(tzinfo=pytz.timezone('Asia/Seoul'))
        return target_date
