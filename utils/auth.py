from __future__ import print_function

import os
import json
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.exceptions import RefreshError


def get_google_credentials(config_file='config/config.json'):
    """Google API 인증 자격증명 획득"""
    with open(config_file, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    token_path = 'config/token.json'
    creds = None
    
    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, config['SCOPES'])
    
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
                config['OAUTH_CRED'],
                config['SCOPES']
            )
            creds = flow.run_local_server(port=0)
            with open(token_path, 'w') as token:
                token.write(creds.to_json())
    
    return creds 