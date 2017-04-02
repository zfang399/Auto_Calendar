from __future__ import print_function
import httplib2
import os

from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage

import datetime

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

import datetime
import numpy as np
import codecs
from nltk.corpus import stopwords
import logging, gensim, bz2
from nltk.tag import pos_tag
from nltk.corpus import names
from collections import defaultdict

stop = set(stopwords.words('english'))
names=set(names.words())
type1=[('today','tonight','tonite',0),('tomorrow','tmr',1)]
type2a=[('monday','mon',1),('tuesday','tues','tues','tu',2),('wednesday','wed',3),('thursday','thu','thurs','thur',4),('friday','fri',5),('saturday','sat',6),('sunday','sun',7)]
type2b=[('this',0),('next',7)];
type3=[]
days_dic=[0,31,0,31,30,31,30,31,31,30,31,30,31]

def removestop(l,s):
	out = """"""
	l = l.strip().split()
	for word in l:
		if word not in s:
			out += word + ' '
	return out.strip()

def getperson(l):
    out = """"""
    l = l.strip().split()
    for word in l:
		if word in names:
			out += word + ' '
    return out.strip()

def gettime(l):
    out = -1
    l = l.strip().split()
    for word in l:
		if word in names:
			out += word + ' '
    return out.strip()

def getdate(l):
    out=[]
    l = l.strip().split()
    l=l[0].split('-')
    for word in l:
        out.append(int(word))

    return out

def leapyr(n):
    isleap=False
    if n%4==0 and n%100!=0:
        if n%400==0:
            isleap=True
    elif n%4!=0:
        isleap=False
    if isleap:
        days_dic[2]=29
    else:
        days_dic[2]=28


def type1key(l):
    out =-1
    l = l.strip().split()
    for word in l:
        for key in type1:
            if word in key:
			    out = key[-1]
    return out

def type2key(l):
    out = -1
    l = l.strip().split()
    for word in l:
        for key in type2a:
            if word.lower() in key:
			    out = key[-1]
    for word in l:
        for key in type2b:
            if word.lower() in key:
                out += key[-1]
    return out

def adddays(n):
    while date[2]+n > days_dic[date[1]]:
        n=n-(days_dic[date[1]]-date[2])
        date[2]=0
        if date[1]==12:
            date[1]=1
            date[0]+=1
        else:
            date[1]+=1
    date[2]+=n

message="Meet James and Andy blah blah on Eric blah blah next fri"
message=removestop(message, stop)

# get name of the people
people=getperson(message)
peoplelist=people.split()
#print people

# get the time of the event
# get today's date first
todaydate= str(datetime.datetime.now())
todaydatec=datetime.datetime.now()
date=getdate(todaydate)
leapyr(date[1])
#get information type1
type1info=type1key(message)
if type1info!=-1:
    adddays(type1info)
else:
    #get information type2
    todayweekday=todaydatec.isoweekday()
    type2info=type2key(message)
    if type2info!=-1:
        adddays(type2info-todayweekday)

if (date[1]<10):
    datestartstr=str(date[0])+'-0'+str(date[1])+'-'+str(date[2])+'T09:00:00-05:00'
    dateendstr=str(date[0])+'-0'+str(date[1])+'-'+str(date[2])+'T09:00:00-06:00'
else:
    datestartstr=str(date[0])+'-'+str(date[1])+'-'+str(date[2])+'T09:00:00-10:00'
    dateendstr=str(date[0])+'-'+str(date[1])+'-'+str(date[2])+'T09:00:00-11:00'

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/calendar-python-quickstart.json
SCOPES = 'https://www.googleapis.com/auth/calendar'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Google Calendar API Python Quickstart'


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
                                   'calendar-python-quickstart.json')

    store = Storage(credential_path)
    credentials = store.get()
    if False:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else: # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials

def main():
    """Shows basic usage of the Google Calendar API.

    Creates a Google Calendar API service object and outputs a list of the next
    10 events on the user's calendar.
    """
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('calendar', 'v3', http=http)

    now = datetime.datetime.utcnow().isoformat() + 'Z' # 'Z' indicates UTC time
    print('Getting the upcoming 10 events')
    eventsResult = service.events().list(
        calendarId='primary', timeMin=now, maxResults=10, singleEvents=True,
        orderBy='startTime').execute()
    events = eventsResult.get('items', [])

    # if not events:
    #     print('No upcoming events found.')
    # for event in events:
    #     start = event['start'].get('dateTime', event['start'].get('date'))
    #     print(start, event['summary'])

    event = {
      'summary': 'Meeting',
      'location': '800 Howard St., San Francisco, CA 94103',
      'description': 'Meet with '+people,
      'start': {
        'dateTime': datestartstr,
        'timeZone': 'America/Chicago',
      },
      'end': {
        'dateTime': dateendstr,
        'timeZone': 'America/Chicago',
      },
      'recurrence': [
        'RRULE:FREQ=DAILY;COUNT=1'
      ],
      'attendees': [
        {'email': 'lpage@example.com'},
        {'email': 'sbrin@example.com'},
      ],
      'reminders': {
        'useDefault': False,
        'overrides': [
          {'method': 'email', 'minutes': 24 * 60},
          {'method': 'popup', 'minutes': 10},
        ],
      },
    }

    event = service.events().insert(calendarId='primary', body=event).execute()

if __name__ == '__main__':
    main()
