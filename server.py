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
from gevent import monkey
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from nltk import tokenize
monkey.patch_all()

from flask import Flask, render_template, session, request
from flask_socketio import SocketIO, emit, join_room

app = Flask(__name__)
app.debug = True
app.config['SECRET_KEY'] = 'nuttertools'
socketio = SocketIO(app)
names=set(names.words())
emaillist=['emptyslot@example.com','emptyslot@example.com','emptyslot@example.com','emptyslot@example.com','emptyslot@example.com','emptyslot@example.com','emptyslot@example.com','emptyslot@example.com','emptyslot@example.com','emptyslot@example.com']
chatnum=[0]
global messageset
messageset=[]
messagestring=[]

@app.route('/')
def chat():
  return render_template('chat.html')

@app.route('/login')
def login():
  return render_template('login.html')

@socketio.on('message', namespace='/chat')
def chat_message(message):
  print("message = ", message)
  emit('message', {'data': message['data']}, broadcast=True)
  messageset.append(message['data']['message'])
 # messagestring[0]+=message['data']['message']
  newemail=message['data']['author']
  if newemail not in emaillist:
      emaillist[chatnum[0]]=newemail
      chatnum[0]+=1
  stop = set(stopwords.words('english'))
  type1=[('today','tonight','tonite',0),('tomorrow','tmr',1)]
  type2a=[('monday','mon',1),('tuesday','tues','tues','tu',2),('wednesday','wed',3),('thursday','thu','thurs','thur',4),('friday','fri',5),('saturday','sat',6),('sunday','sun',7)]
  type2b=[('this',0),('next',7)];
  des_type=[('Project','Project'),('Meeting'),'Interview','Coffee','Dinner','Lunch','Breakfast','Class','Meet','Basketball','Presentation'];
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
      messagestring.append(date[0])
      messagestring.append(date[1])
      messagestring.append(date[2])
  def getdes(l):
      out = 'Meet'
      l = l.strip().split()
      for word in l:
          for key in des_type:
              if word.title() in key:
      			    out = word.title()
      return out

  def find_hours(sentence):
    sentence = sentence.split()
    start_time_hour = -1
    start_time_minute = 0
    actual_time = []
    time = [('1'),('2'),('3'),('4'),('5'),('6'),('7'),('8'),('9'),('10'),('11'),('12')]
    length = len(sentence)
    i = 0
    while i < length:
        if sentence[i] in time:
            start_time_hour = int(sentence[i])
        for hour in time:
            if hour == sentence[i]:
                start_time_hour = int(hour)

            actual_time = sentence[i].split(':')
            if len(actual_time)==2:
                start_time_hour = int(actual_time[0])
                start_time_minute = int(actual_time[1])
        if i!=length-1:
            if start_time_hour!=-1 and (sentence[i+1].lower() == 'pm' or 'afternoon' in sentence):
                if 'afternoon' in sentence:
                    sentence.remove('afternoon')
                if 'tonight' in sentence:
                    sentence.remove('tonight')
                length = length - 1
                start_time_hour += 12

        i = i+1
    return [start_time_hour, start_time_minute]


  message=message['data']['message']
  message=removestop(message, stop)

  #get description
  descrip=getdes(message)

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
  newtime=False
  if type1info!=-1:
      adddays(type1info)
      newtime=True
  else:
      #get information type2
      todayweekday=todaydatec.isoweekday()
      type2info=type2key(message)
      if type2info!=-1:
          adddays(type2info-todayweekday)
          newtime=True

  hourmin=find_hours(message)
  hourminend=[]

  if hourmin[0]==-1:
      hourmin[0]=17
  else:
      adddays(0)
      newtime=True

  if hourmin[0]-5<0:
      hourmin[0]=24-(5-hourmin[0])
      adddays(-1)
  else:
      hourmin[0]-=5

  hourminend.append(hourmin[0]+1)

  if newtime:
      date[0]=messagestring[0]
      date[1]=messagestring[1]
      date[2]=messagestring[2]


  if (date[1]<10):
      if hourmin[0]<10:
          if hourmin[1]<10:
              datestartstr=str(date[0])+'-0'+str(date[1])+'-'+str(date[2])+'T09:00:00-0'+str(hourmin[0])+':0'+str(hourmin[1])
              dateendstr=str(date[0])+'-0'+str(date[1])+'-'+str(date[2])+'T09:00:00-0'+str(hourminend[0])+':0'+str(hourmin[1])
          else:
              datestartstr=str(date[0])+'-0'+str(date[1])+'-'+str(date[2])+'T09:00:00-0'+str(hourmin[0])+':'+str(hourmin[1])
              dateendstr=str(date[0])+'-0'+str(date[1])+'-'+str(date[2])+'T09:00:00-0'+str(hourminend[0])+':'+str(hourmin[1])
      else:
          if hourmin[1]<10:
              datestartstr=str(date[0])+'-0'+str(date[1])+'-'+str(date[2])+'T09:00:00-'+str(hourmin[0])+':0'+str(hourmin[1])
              dateendstr=str(date[0])+'-0'+str(date[1])+'-'+str(date[2])+'T09:00:00-'+str(hourminend[0])+':0'+str(hourmin[1])
          else:
              datestartstr=str(date[0])+'-0'+str(date[1])+'-'+str(date[2])+'T09:00:00-'+str(hourmin[0])+':'+str(hourmin[1])
              dateendstr=str(date[0])+'-0'+str(date[1])+'-'+str(date[2])+'T09:00:00-'+str(hourminend[0])+':'+str(hourmin[1])
  else:
      if hourmin[0]<10:
          if hourmin[1]<10:
              datestartstr=str(date[0])+'-'+str(date[1])+'-'+str(date[2])+'T09:00:00-0'+str(hourmin[0])+':0'+str(hourmin[1])
              dateendstr=str(date[0])+'-'+str(date[1])+'-'+str(date[2])+'T09:00:00-0'+str(hourminend[0])+':0'+str(hourmin[1])
          else:
              datestartstr=str(date[0])+'-'+str(date[1])+'-'+str(date[2])+'T09:00:00-0'+str(hourmin[0])+':'+str(hourmin[1])
              dateendstr=str(date[0])+'-'+str(date[1])+'-'+str(date[2])+'T09:00:00-0'+str(hourminend[0])+':'+str(hourmin[1])
      else:
          if hourmin[1]<10:
              datestartstr=str(date[0])+'-'+str(date[1])+'-'+str(date[2])+'T09:00:00-'+str(hourmin[0])+':0'+str(hourmin[1])
              dateendstr=str(date[0])+'-'+str(date[1])+'-'+str(date[2])+'T09:00:00-'+str(hourminend[0])+':0'+str(hourmin[1])
          else:
              datestartstr=str(date[0])+'-'+str(date[1])+'-'+str(date[2])+'T09:00:00-'+str(hourmin[0])+':'+str(hourmin[1])
              dateendstr=str(date[0])+'-'+str(date[1])+'-'+str(date[2])+'T09:00:00-'+str(hourminend[0])+':'+str(hourmin[1])

  if len(messageset)>2 :
      negn=0
      numanalyzed=0
      for m in messageset[1:]:
          numanalyzed+=1
          lines_list = tokenize.sent_tokenize(m)
          sid = SentimentIntensityAnalyzer()
          ss = sid.polarity_scores(m)
          negn+=ss['neg']
      negn/=numanalyzed

      if negn>=0.2:

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

              now = datetime.datetime.utcnow().isoformat() + 'Z'
              eventsResult = service.events().list(
                  calendarId='primary', timeMin=now, maxResults=1, singleEvents=True,
                  orderBy='startTime').execute()
              events = eventsResult.get('items', [])

              # if not events:
              #     print('No upcoming events found.')
              # for event in events:
              #     start = event['start'].get('dateTime', event['start'].get('date'))
              #     print(start, event['summary'])
              for event in events:
                  service.events().delete(calendarId='primary', eventId=event['id']).execute()

              del messageset[:]


          if __name__ == '__main__':
              main()

  if newtime:
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

          now = datetime.datetime.utcnow().isoformat() + 'Z'
          eventsResult = service.events().list(
              calendarId='primary', timeMin=now, maxResults=10, singleEvents=True,
              orderBy='startTime').execute()
          events = eventsResult.get('items', [])

          # if not events:
          #     print('No upcoming events found.')
          # for event in events:
          #     start = event['start'].get('dateTime', event['start'].get('date'))
          #     print(start, event['summary'])
          if len(messagestring)==3:
              messagestring.append(descrip)
              messagestring.append(descrip+'with'+people)
              event = {
                'summary': descrip,
                'location': '',
                'description':  descrip+' with '+people,
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
                  {'email': emaillist[0]},
                  {'email': emaillist[1]},
                  {'email': emaillist[2]},
                  {'email': emaillist[3]},
                  {'email': emaillist[4]},
                  {'email': emaillist[5]},
                  {'email': emaillist[6]},
                  {'email': emaillist[7]},
                  {'email': emaillist[8]},
                  {'email': emaillist[9]},
                ],
                'reminders': {
                  'useDefault': False,
                  'overrides': [
                    {'method': 'email', 'minutes': 24 * 60},
                    {'method': 'popup', 'minutes': 10},
                  ],
                },
              }

              event = service.events().insert(calendarId='primary',body=event).execute()
          else:
              event = {
                'summary': messagestring[3],
                'location': '',
                'description':  messagestring[4],
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
                  {'email': emaillist[0]},
                  {'email': emaillist[1]},
                  {'email': emaillist[2]},
                  {'email': emaillist[3]},
                  {'email': emaillist[4]},
                  {'email': emaillist[5]},
                  {'email': emaillist[6]},
                  {'email': emaillist[7]},
                  {'email': emaillist[8]},
                  {'email': emaillist[9]},
                ],
                'reminders': {
                  'useDefault': False,
                  'overrides': [
                    {'method': 'email', 'minutes': 24 * 60},
                    {'method': 'popup', 'minutes': 10},
                  ],
                },
              }

              event = service.events().insert(calendarId='primary',body=event).execute()

      if __name__ == '__main__':
          main()

@socketio.on('connect', namespace='/chat')
def test_connect():
  emit('my response', {'data': 'Connected', 'count': 0})

if __name__ == '__main__':
  socketio.run(app,host='0.0.0.0',port=5000)
