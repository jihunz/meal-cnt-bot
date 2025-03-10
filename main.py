from __future__ import print_function

import base64
import datetime
import json
import os
from email.mime.text import MIMEText

import pytz
import requests
from apscheduler.schedulers.blocking import BlockingScheduler
from google.auth.exceptions import RefreshError
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

CONFIG_FILE = 'config/config.json'


class Meal_count_bot:
    def __init__(self, config_file=CONFIG_FILE):
        self.config_file = config_file
        with open(self.config_file, 'r', encoding='utf-8') as f:
            self.config = json.load(f)
        self.creds = None
        self.meal_exclude_list = []
        self.default_exclude_list = ['김인경', '윤현석', '한혜영', '배건길']
        self.meal_cnt_list = ['장지훈', '김태준', '서대원', '조주형', '김형진', '김대현']
        self.default_meal_cnt = len(self.meal_cnt_list)
        self.now = datetime.datetime.now(pytz.timezone('Asia/Seoul'))

    def get_credentials(self):
        token_path = 'config/token.json'
        creds = None
        if os.path.exists(token_path):
            creds = Credentials.from_authorized_user_file(token_path, self.config['SCOPES'])
        if not creds or not creds.valid:
            try:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                else:
                    raise RefreshError
            except RefreshError:
                if os.path.exists(token_path):
                    os.remove(token_path)
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.config['OAUTH_CRED'],
                    self.config['SCOPES']
                )
                creds = flow.run_local_server(port=0)
                with open(token_path, 'w') as token:
                    token.write(creds.to_json())
        self.creds = creds
        return self.creds

    def send_email(self, result):
        gmail_service = build('gmail', 'v1', credentials=self.creds)
        to = 'hehan@vetec.co.kr'
        sender = 'jhjang@vetec.co.kr'
        formatted_today = self.now.strftime('%Y-%m-%d')
        subject = f'[{formatted_today}] 연구소 식사 인원: {result} 명'
        message_text = ''
        message = MIMEText(message_text)
        message['to'] = to
        message['from'] = sender
        message['subject'] = subject
        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
        try:
            gmail_service.users().messages().send(
                userId='me',
                body={'raw': raw_message}
            ).execute()
            print(f'[{self.now}] 이메일이 성공적으로 전송되었습니다 -> To: {to}')
        except Exception as e:
            print(f'[{self.now}] 이메일 전송 중 오류가 발생했습니다: {e}')

    def get_meal_cnt(self):
        default_meal_cnt = len(self.meal_cnt_list)

        for cal in self.config['CAL_ID_LIST']:
            event_list = self.get_event_list(cal, 1)

            if not event_list:
                print(f'[{self.now}] {cal}에 해당 이벤트가 없습니다.')
                continue

            for event in event_list:
                if 'dateTime' in event['start']:
                    continue

                person_list = [name.strip() for name in event['summary'].split('-')[0].split(',')]
                for name in person_list:
                    if name in self.meal_exclude_list:
                        continue
                    if name not in self.meal_cnt_list:
                        continue
                    self.meal_cnt_list.remove(name)
                    self.meal_exclude_list.append(name)

        result = len(self.meal_cnt_list)
        if result < 0:
            result = 0
        now_kst = datetime.datetime.now(pytz.timezone('Asia/Seoul'))
        print(
            f'[{now_kst}] 연구소 식사 인원 - 포함: {result}{self.meal_cnt_list}, 제외: {len(self.meal_exclude_list)}{self.meal_exclude_list}, 기본 인원수: {default_meal_cnt}')
        return result

    def validate_etc(self):
        for event in self.get_event_list(self.config['BUSINESS_CAL_ID'], 1):
            if '워크샵' in event['summary']:
                print(f'[{self.now}] {event['summary']}')
                return True
        return False

    def print_and_return(self, result, today_info):
        print(f'[{self.now}] 오늘 공휴일 여부: {result}, {today_info}')
        return result

    # 토, 일요일 및 공휴일 판별
    def validate_holiday(self):
        result = False
        today_info = None

        weekday = self.now.weekday()
        if weekday in (5, 6):
            # 토요일(5) 혹은 일요일(6)인 경우
            result = True
            return self.print_and_return(result, '주말')

        formatted_now = self.now.strftime("%Y%m%d")
        curr_year = self.now.strftime("%Y")
        curr_month = self.now.strftime("%m")

        url = 'http://apis.data.go.kr/B090041/openapi/service/SpcdeInfoService/getRestDeInfo'
        params = {
            'serviceKey': 'o9Nl5P8j/q+4yxmDuPD/lUHILUtj804RYh/jJl0KZofUB9mSV/fWhLL1kXyTht+ylHs+cAv/77S7g4kweuVp5A==',
            'pageNo': '1',
            'numOfRows': '100',
            'solYear': curr_year,
            'solMonth': curr_month,
            '_type': 'json'
        }

        response = requests.get(url, params=params)
        if response.status_code != 200:
            return self.print_and_return(result, today_info)

        try:
            res = response.json()
        except Exception as e:
            return self.print_and_return(result, e)

        if len(res['response']['body']['items']) < 1:
            return self.print_and_return(result, today_info)

        data = res['response']['body']['items']['item']
        if isinstance(data, dict):
            data = [data]

        for holiday in data:
            if (formatted_now == str(holiday['locdate'])) and (holiday['isHoliday'] == 'Y'):
                result = True
                today_info = holiday
                break

        return self.print_and_return(result, today_info)

    # 월간회의(금), 월간회의 전날(목) 모두 식사 인원 목록 증가시킴
    def validate_monthly_meeting(self):
        events = self.get_event_list(self.config['BUSINESS_CAL_ID'], 2)
        for event_item in events:
            if '월간회의' in event_item['summary']:
                self.meal_cnt_list.extend(self.default_exclude_list)
                break
        self.default_meal_cnt = len(self.meal_cnt_list)

    def get_event_list(self, cal_id, days):
        service = build('calendar', 'v3', credentials=self.creds)
        start = self.now.replace(hour=0, minute=0, second=0, microsecond=0)
        end = start + datetime.timedelta(days=days)
        events_result = service.events().list(
            calendarId=cal_id,
            timeMin=start.isoformat(),
            timeMax=end.isoformat(),
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        return events_result.get('items', [])

    def job(self):
        self.get_credentials()
        if self.validate_holiday() or self.validate_etc():
            return
        self.validate_monthly_meeting()
        meal_cnt = self.get_meal_cnt()
        self.send_email(meal_cnt)


def create_bot_and_job():
    bot = Meal_count_bot()
    bot.job()


if __name__ == '__main__':
    scheduler = BlockingScheduler(timezone='Asia/Seoul')
    scheduler.add_job(create_bot_and_job, 'cron', day_of_week='mon-fri', hour=9, minute=10)
    print('[ meal_cnt_bot 스케줄러가 시작되었습니다 ]')
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        print('[ meal_cnt_bot 스케줄러가 종료되었습니다 ]')
