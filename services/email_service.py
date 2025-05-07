import base64
import datetime
from email.mime.text import MIMEText
import pytz
from googleapiclient.discovery import build

from utils.date_util import DateUtil


class EmailService:
    """이메일 전송을 위한 서비스 클래스"""

    # 클래스 변수로 선언
    to = 'hehan@vetec.co.kr'
    sender = 'jhjang@vetec.co.kr'
    subject_template = '[{date}] 연구소 식사 인원: {count} 명'

    def __init__(self, credentials):
        """이메일 서비스 초기화"""
        self.creds = credentials
        self.service = build('gmail', 'v1', credentials=self.creds)

    def send_email(self, count):
        """식사 인원 정보를 이메일로 전송"""
        formatted_today = DateUtil.get_now().strftime('%Y-%m-%d')
        subject = self.subject_template.format(date=formatted_today, count=count)

        message = MIMEText('')
        message['to'] = self.to
        message['from'] = self.sender
        message['subject'] = subject

        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

        try:
            self.service.users().messages().send(
                userId='me',
                body={'raw': raw_message}
            ).execute()

            print(f'[{DateUtil.get_now()}] 이메일이 성공적으로 전송되었습니다 -> To: {self.to}')
            return True, None

        except Exception as e:
            error_msg = f'[{DateUtil.get_now()}] 이메일 전송 중 오류가 발생했습니다: {e}'
            print(error_msg)
            return False, error_msg
