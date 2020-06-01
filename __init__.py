from __future__ import print_function
import json
import sys
from adapt.intent import IntentBuilder
from adapt.engine import IntentDeterminationEngine
from mycroft.skills.core import MycroftSkill, intent_handler
import pickle
import os.path
from mycroft.util.parse import extract_datetime
from datetime import datetime, timedelta
from adapt.intent import IntentBuilder
from mycroft.skills.core import MycroftSkill, intent_handler
from mycroft.util.log import LOG
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import httplib2
from googleapiclient.discovery import build
from oauth2client.file import Storage
from oauth2client.client import OAuth2WebServerFlow
from oauth2client import tools
UTC_TZ = u'+00:00'
SCOPES = ['https://www.googleapis.com/auth/calendar']


# TODO: Change "Template" to a unique name for your skill
class AffichEventSkill(MycroftSkill):

    # The constructor of the skill, which calls MycroftSkill's constructor
    def __init__(self):
        super(AffichEventSkill, self).__init__(name="AffichEventSkill")

    @property
    def utc_offset(self):
        return timedelta(seconds=self.location['timezone']['offset'] / 1000)

    @intent_handler(IntentBuilder("affichBylocation_intent").require("affich").require("location").build())
    def eventsbylocation(self,message):
        #AUTHORIZE
        creds = None
        # The file token.pickle stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                creds = pickle.load(token)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    '/opt/mycroft/skills/afficheventskill.hanabouzid/client_secret.json', SCOPES)
                creds = flow.run_local_server(port=0)
                # Save the credentials for the next run
            with open('token.pickle', 'wb') as token:
                pickle.dump(creds, token)

        service = build('calendar', 'v3', credentials=creds)

        utt = message.data.get("utterance", None)
        list = utt.split(" in ")
        location =list[1]
        now = datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
        events_result = service.events().list(calendarId='primary', timeMin=now,
                                             singleEvents=True,
                                              orderBy='startTime', q=location).execute()
        events = events_result.get('items', [])
        if not events:
            self.speak_dialog("notEvent")

        for event in events:
            summary=event['summary']
            description=event['description']
            eventstart=event['start']['dateTime']
            eventend = event['end']['dateTime']
            attendee = event['attendees']
            attendees= ",".join(attendee)
            self.speak_dialog("eventbylocation", data={"summary":summary,"description":description,"attendees":attendees,"eventstart":eventstart,"eventend":eventend})

    @intent_handler(IntentBuilder("affichByStartTime_intent").require("affich").require("date").build())
    def eventbystart(self, message):
        # AUTHORIZE
        creds = None
        # The file token.pickle stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                creds = pickle.load(token)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    '/opt/mycroft/skills/afficheventskill.hanabouzid/client_secret.json', SCOPES)
                creds = flow.run_local_server(port=0)
                # Save the credentials for the next run
            with open('token.pickle', 'wb') as token:
                pickle.dump(creds, token)
        service = build('calendar', 'v3', credentials=creds)
        #extraire la date et le titre
        utt = message.data.get("utterance", None)
        list1=utt.split(" start ")
        strtdate=list1[1]
        st = extract_datetime(strtdate)
        st = st[0] - self.utc_offset
        date = st.strftime('%Y-%m-%dT%H:%M:00')
        date += UTC_TZ
        events_result = service.events().list(calendarId='primary', timeMin=date,
                                             singleEvents=True,
                                              orderBy='startTime').execute()
        events = events_result.get('items', [])
        if not events:
            self.speak_dialog("notEvent")

        for event in events:
            summary=event['summary']
            description=event['description']
            location=event['location']
            eventend = event['end']['dateTime']
            attendee = event['attendees']
            attendees= ",".join(attendee)
            self.speak_dialog("eventbystarttime",data={"summary": summary, "description": description, "attendees": attendees,"location": location, "eventend": eventend})

    @intent_handler(IntentBuilder("").require("upcommingevents"))
    def uppcommingevents(self,message):
        # AUTHORIZE
        creds = None
        # The file token.pickle stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                creds = pickle.load(token)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    '/opt/mycroft/skills/afficheventskill.hanabouzid/client_secret.json', SCOPES)
                creds = flow.run_local_server(port=0)
                # Save the credentials for the next run
            with open('token.pickle', 'wb') as token:
                pickle.dump(creds, token)

        service = build('calendar', 'v3', credentials=creds)

        # Call the Calendar API
        now = datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
        print('Getting the upcoming 10 events')
        events_result = service.events().list(calendarId='primary', timeMin=now,
                                              maxResults=20, singleEvents=True,
                                              orderBy='startTime').execute()
        events = events_result.get('items', [])

        if not events:
            print('No upcoming events found.')
            self.speak_dialog("notevent")
        for event in events:
            summary= event['summary']
            eventstart = event['start']['dateTime']
            self.speak_dialog("nextevents", data={"summary": summary,"eventstart":eventstart})



def create_skill():
    return AffichEventSkill()
