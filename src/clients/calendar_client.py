from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
import os
import datetime

SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

class CalendarClient:
    def __init__(self):
        self.service = self.get_calendar_service()

    def get_calendar_service(self):
        creds = None
        if os.path.exists('token.json'):
            creds = Credentials.from_authorized_user_file('config/token.json', SCOPES)
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file('config/credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)
            with open('token.json', 'w') as token:
                token.write(creds.to_json())

        return build('calendar', 'v3', credentials=creds)

    def get_events(self, start_date, end_date):
        start = datetime.datetime.combine(start_date, datetime.time.min).isoformat() + 'Z'
        end = datetime.datetime.combine(end_date, datetime.time.max).isoformat() + 'Z'

        events_result = self.service.events().list(calendarId='primary', timeMin=start,
                                                   timeMax=end, singleEvents=True,
                                                   orderBy='startTime').execute()
        events = events_result.get('items', [])

        meetings = []
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            end = event['end'].get('dateTime', event['end'].get('date'))
            meetings.append({
                'summary': event['summary'],
                'start': start,
                'end': end
            })

        return meetings
