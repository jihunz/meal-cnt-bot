import datetime
import pytz


class DateUtil:
    @classmethod
    def get_now(cls):
        return datetime.datetime.now(pytz.timezone('Asia/Seoul'))
