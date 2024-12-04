from __future__ import print_function
import datetime
import os
import pytz
import re
import base64
import json
from email.mime.text import MIMEText

from google.auth.exceptions import RefreshError
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.oauth2 import service_account

from apscheduler.schedulers.blocking import BlockingScheduler

# 설정 파일 경로
CONFIG_FILE = 'config/config.json'
TOTAL_COMM_HEADCOUNT = 7
EXCLUDE_LIST = ['김인경', '윤현석', '권두진', '김태훈']

# 설정 파일 로드
with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
    config = json.load(f)


def get_credentials():
    creds = None
    token_path = 'token.json'
    # 기존에 저장된 토큰이 있으면 로드
    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, config['SCOPES'])
    # 유효한 자격 증명이 없으면 로그인 흐름 시작
    if not creds or not creds.valid:
        try:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                raise RefreshError
        except RefreshError:
            # 기존의 잘못된 토큰 삭제
            if os.path.exists(token_path):
                os.remove(token_path)
            # 재인증 수행
            cred_ = json.dumps(config['OAUTH_CRED'])
            flow = InstalledAppFlow.from_client_secrets_file(
                config['OAUTH_CRED'], config['SCOPES'])
            creds = flow.run_local_server(port=0)
            # 자격 증명 저장
            with open(token_path, 'w') as token:
                token.write(creds.to_json())
    return creds


def get_credentials_v2():
    credentials = service_account.Credentials.from_service_account_file(
        'config/service_account_key.json',
        scopes=config['SCOPES']
    )

    # 도메인 전체 권한 위임을 위해 사용자 설정
    cred = credentials.with_subject('jhjang@vetec.co.kr')
    return cred


def send_email(result, creds):
    gmail_service = build('gmail', 'v1', credentials=creds)

    to = 'jhjang@vetec.co.kr'
    sender = 'jhjang@vetec.co.kr'
    tz = pytz.timezone('Asia/Seoul')
    today = datetime.datetime.now(tz)
    formatted_today = today.strftime('%Y-%m-%d')
    subject = f'[{formatted_today}] 연구소 식사 인원: {result} 명'
    message_text = ''

    message = MIMEText(message_text)
    message['to'] = to
    message['from'] = sender
    message['subject'] = subject
    raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

    try:
        message = gmail_service.users().messages().send(userId='me', body={'raw': raw_message}).execute()
        print(f'[{today}] 이메일이 성공적으로 전송되었습니다 -> Message Id: {message["id"]}')
    except Exception as e:
        print(f'[{today}] 이메일 전송 중 오류가 발생했습니다: {e}')


def get_meal_cnt(creds):
    num_to_minus = 0

    # API 서비스 생성
    service = build('calendar', 'v3', credentials=creds)

    # 오늘의 시작과 끝 시간 설정
    tz = pytz.timezone('Asia/Seoul')
    today = datetime.datetime.now(tz)
    today_start = today.replace(hour=0, minute=0, second=0, microsecond=0)
    today_end = today_start + datetime.timedelta(days=1)

    # ISO 포맷으로 변환
    time_min = today_start.isoformat()
    time_max = today_end.isoformat()

    # 이벤트 호출
    for cal in config['CAL_ID_LIST']:
        events_result = service.events().list(calendarId=cal, timeMin=time_min,
                                              timeMax=time_max, singleEvents=True,
                                              orderBy='startTime').execute()
        event_list = events_result.get('items', [])
        if not event_list:
            print(f'[{today}] 이벤트가 없습니다.')

        for event in event_list:
            person_list = event['summary'].split('-')[0]

            if is_in_exclude_list(person_list):
                continue
            if 'dateTime' in event['start']:
                continue

            if '외' in person_list:
                number_headcount = int(''.join(re.findall(r'\d+', person_list)))
                num_to_minus += (1 + number_headcount)
            else:
                head_count = len(person_list.split(','))
                num_to_minus += head_count

    result = TOTAL_COMM_HEADCOUNT - num_to_minus
    if result < 0:
        result = 0  # 인원이 음수가 되지 않도록 조정
    print(f'[{today}] 연구소 식사 인원: {result} 명')
    return result


def is_in_exclude_list(person_list):
    names = [name.strip() for name in person_list.split(',')]
    return any(name in EXCLUDE_LIST for name in names)


def job():
    creds = get_credentials()
    meal_cnt = get_meal_cnt(creds)
    send_email(meal_cnt, creds)


if __name__ == '__main__':
    creds = get_credentials()
    meal_cnt = get_meal_cnt(creds)
    send_email(meal_cnt, creds)

    scheduler = BlockingScheduler(timezone='Asia/Seoul')
    scheduler.add_job(job, 'cron', day_of_week='mon-fri', hour=9, minute=10)
    print('[ meal_cnt_bot 스케줄러가 시작되었습니다. Ctrl+C로 종료하세요. ]')
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        print('[ meal_cnt_bot 스케줄러가 종료되었습니다. ]')
