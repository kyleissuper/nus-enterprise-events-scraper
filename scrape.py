from settings import CALENDAR_ID

from pytz import timezone
from bs4 import BeautifulSoup
import argparse
import datetime
import httplib2
import json
import os
import re
import requests

from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage


# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/calendar-python.json
SCOPES = 'https://www.googleapis.com/auth/calendar'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Google Calendar API'

flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()


def get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'calendar-python.json')

    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else: # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials

def singapore_time_string(year, month, day, hour, minute):
    d = datetime.datetime(year, month, day, hour, minute)
    l = timezone('Singapore').localize(d)
    return l.isoformat()

def parse_date_string(date_string):
    months = {
        "January": 1,
        "February": 2,
        "March": 3,
        "April": 4,
        "May": 5,
        "June": 6,
        "July": 7,
        "August": 8,
        "September": 9,
        "October": 10,
        "November": 11,
        "December": 12
    }
    d = {}
    date_parts = date_string.split(" ")[1:]
    d["day"] = int(date_parts[0])
    d["month"] = months[date_parts[1]]
    d["year"] = int(date_parts[2])
    return d

def parse_time_string(time_string):
    t = []
    time_parts = time_string.split(" - ")
    for time_part in time_parts:
        hour = int(time_part[:2])
        if time_part[6:] == "PM":
            hour += 12
        minute = int(time_part[3:5])
        t.append({"hour": hour, "minute": minute})
    return t


if __name__ == "__main__":

    # Ready Gcal
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('calendar', 'v3', http=http)

    base_url = "http://enterprise.nus.edu.sg"

    # Get latest events
    r = requests.get(base_url + "/event")
    soup = BeautifulSoup(r.text, "html.parser")
    parsed_events = []
    for event in soup.find_all("a", class_="item"):
        parsed_events.append({
            "title": event.find("h4").string,
            "link": event["href"]
        })
    for event in parsed_events:
        r = requests.get(base_url + event["link"])
        s = BeautifulSoup(r.text, "html.parser")
        date_string = s.find("h4", string="Date").find_next("p").string
        print date_string
        print parse_date_string(date_string)
        time_string = s.find("h4", string="Time").find_next("p").string
        print time_string
        print parse_time_string(time_string)
        break



    #eventsResult = service.events().list(
    #    calendarId=CALENDAR_ID,
    #    q="Rahhh"
    #    ).execute()
    #events = eventsResult.get('items', [])
    #if not events:
    #    print "No events"
    #    #inserted = service.events().insert(
    #    #    calendarId=CALENDAR_ID,
    #    #    body={
    #    #        "summary": "New event",
    #    #        "description": "Url to event",
    #    #        "start": {
    #    #            "dateTime":  singapore_time_string(2017, 10, 26, 12, 0)
    #    #        },
    #    #        "end": {
    #    #            "dateTime":  singapore_time_string(2017, 10, 26, 13, 0)
    #    #        }
    #    #    }
    #    #    ).execute()
    #else:
    #    for event in events:
    #        start = event['start'].get('dateTime', event['start'].get('date'))
    #        print(start, event['summary'])
