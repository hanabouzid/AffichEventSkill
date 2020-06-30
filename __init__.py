from __future__ import print_function
from mycroft.util.parse import extract_datetime
from datetime import datetime, timedelta
from adapt.intent import IntentBuilder
from mycroft.skills.core import MycroftSkill, intent_handler
import httplib2
from googleapiclient.discovery import build
from oauth2client.file import Storage
from oauth2client.client import OAuth2WebServerFlow
from oauth2client import tools
UTC_TZ = u'+00:00'
FLOW = OAuth2WebServerFlow(
    client_id='73558912455-smu6u0uha6c2t56n2sigrp76imm2p35j.apps.googleusercontent.com',
    client_secret='0X_IKOiJbLIU_E5gN3NefNns',
    scope='https://www.googleapis.com/auth/calendar',
    user_agent='Smart assistant box')


# TODO: Change "Template" to a unique name for your skill
class AffichEventSkill(MycroftSkill):

    # The constructor of the skill, which calls MycroftSkill's constructor
    def __init__(self):
        super(AffichEventSkill, self).__init__(name="AffichEventSkill")

    @property
    def utc_offset(self):
        return timedelta(seconds=self.location['timezone']['offset'] / 1000)

    @intent_handler(IntentBuilder("affichByLocation_intent").require('affich').optionally('location').build())
    def eventsbylocation(self,message):
        storage1 = Storage('/opt/mycroft/skills/afficheventskill.hanabouzid/info.dat')
        credentials = storage1.get()
        if credentials is None or credentials.invalid == True:
            credentials = tools.run_flow(FLOW, storage1)
        print(credentials)
        # Create an httplib2.Http object to handle our HTTP requests and
        # authorize it with our good Credentials.
        http = httplib2.Http()
        http = credentials.authorize(http)
        service = build('calendar', 'v3', http=http)

        utt = message.data.get("utterance", None)
        list = utt.split(" of ")
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

            self.speak_dialog("eventbylocation", data={"summary":summary,"description":description,"eventstart":eventstart,"eventend":eventend})
    @intent_handler(IntentBuilder("affichBydate_intent").require('affich').optionally('date').build())
    def eventsbydate(self, message):
        storage1 = Storage('/opt/mycroft/skills/afficheventskill.hanabouzid/info.dat')
        credentials = storage1.get()
        if credentials is None or credentials.invalid == True:
            credentials = tools.run_flow(FLOW, storage1)
        print(credentials)
        # Create an httplib2.Http object to handle our HTTP requests and
        # authorize it with our good Credentials.
        http = httplib2.Http()
        http = credentials.authorize(http)
        service = build('calendar', 'v3', http=http)
        utt = message.data.get("utterance", None)
        list = utt.split(" of ")
        strtdate = list[1]
        st = extract_datetime(strtdate)
        st = st[0] - self.utc_offset
        date = st.strftime('%Y-%m-%dT%H:%M:00')
        date += UTC_TZ
        events_result = service.events().list(calendarId='primary', timeMin=date,
                                              singleEvents=True,
                                              orderBy='startTime').execute()
        events = events_result.get('items', [])
        if not events:
            self.speak_dialog('notevent')

        for event in events:
            summary = event['summary']
            description = event['description']
            eventstart = event['start']['dateTime']
            eventend = event['end']['dateTime']
            self.speak_dialog('eventbystarttime',data={"summary": summary, "description": description, "eventstart": eventstart,"eventend": eventend})

    @intent_handler(IntentBuilder("").require('upcommingEvents'))
    def eventsbydate(self, message):
        storage1 = Storage('/opt/mycroft/skills/afficheventskill.hanabouzid/info.dat')
        credentials = storage1.get()
        if credentials is None or credentials.invalid == True:
            credentials = tools.run_flow(FLOW, storage1)
        print(credentials)
        # Create an httplib2.Http object to handle our HTTP requests and
        # authorize it with our good Credentials.
        http = httplib2.Http()
        http = credentials.authorize(http)
        service = build('calendar', 'v3', http=http)
        now = datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
        events_result = service.events().list(calendarId='primary', timeMin=now,
                                              singleEvents=True,
                                              orderBy='startTime').execute()
        events = events_result.get('items', [])
        if not events:
            self.speak_dialog('notevent')

        for event in events:
            summary = event['summary']
            location = event['location']
            eventstart = event['start']['dateTime']
            eventend = event['end']['dateTime']

            self.speak_dialog('nextevents',data={"summary": summary, "location": location, "eventstart": eventstart,"eventend": eventend})


def create_skill():
    return AffichEventSkill()
