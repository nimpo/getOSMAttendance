#!/usr/bin/env python3
#
# Copyright 2024 Mike Jones, <dr.mike.jones@gmail.com>
# AKA Grey Wolf <mike.jones@mansouthscouts.org>
# AKA Akela <mike.jones@mansouthscouts.org>
# [23rd Manchester (Birch with Fallowfield)]
# Scout Membership number: 12114313
#
# This program is free software: you can redistribute it and/or modify it 
# under the terms of the GNU General Public License as published by 
# the Free Software Foundation, either version 3 of the License, 
# or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, 
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. 
# See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along 
# with this program. If not, see <https://www.gnu.org/licenses/>.
#
######################
# Before you go any further, get an API key here: https://www.onlinescoutmanager.co.uk/main.php
# Expand "Settings" (bottom of left pane)
# Select "My Account Details"
# From the new menu on the left in the main pane select "Develpoer Tools"
# Click Create Application button (top right)
# This will give you a client_id and client_secret: keep these secret; keep these safe
# Put this in a separate file perhaps called credentials.py <<EOF >.env
# OSM_API_KEY=<put value here>
# OSM_API_SECRET=<put secret here>
# OSM_API_RETURL=<put OAuth2 Callback URI here>
#EOF

#import credentials.py

import os
from dotenv import load_dotenv
import requests
from oauthlib.oauth2 import WebApplicationClient
import uuid
import json
from urllib.parse import urlparse,parse_qs
import itertools
import csv
from datetime import date, datetime, timedelta
import time
import webbrowser

# Get secrets from .env
load_dotenv()
client_id = os.getenv("OSM_API_KEY")
client_secret = os.getenv("OSM_API_SECRET")
redirectURL = os.getenv("OSM_API_RETURL")

# These variables and decorator to stop exceeding rate limited http requests (no limit to start with)
HTTPWaitUntil = datetime.now()
RateLimit = 99999
RateLimitLeft = 99999
RateLimitTTL = 0
RateLimitBlockedState = False

from functools import wraps
def decoraterequest(f):
  @wraps(f)
  def wrapper(*args, **kwargs):
    # Load global rate variables
    global HTTPWaitUntil, RateLimit, RateLimitLeft, RateLimitTTL, RateLimitBlockedState
    # Do something before
    while datetime.now() < HTTPWaitUntil:
      print("Waiting for rate limit to clear")
      time.sleep(5)
    r = f(*args, **kwargs)
    if 'X-RateLimit-Limit' in r.headers:
      RateLimit=r.headers['X-RateLimit-Limit']
    if 'X-RateLimit-Remaining' in r.headers:
      RateLimitLeft=r.headers['X-RateLimit-Remaining']
    if 'X-RateLimit-Reset' in r.headers:
      RateLimitTTL=r.headers['X-RateLimit-Reset']
    if 'X-Blocked' in r.headers:
      RateLimitBlockedState=r.headers['X-Blocked']
    if r.status_code == 429:
      if "Retry-After" in r.headers:
        HTTPWaitUntil = datetime.now()  + timedelta(seconds = r.headers['Retry-After'])
    elif r.status_code != 200:
      print("Something went wrong accessing URL", args[0])
      quit()
    return r
  return wrapper

requests.post=decoraterequest(requests.post)
requests.get=decoraterequest(requests.get)

#######################
# Prep OAuth2 initiator

client = WebApplicationClient(client_id)
authorization_url = 'https://www.onlinescoutmanager.co.uk/oauth/authorize'
token_url = 'https://www.onlinescoutmanager.co.uk/oauth/token'
state=str(uuid.uuid4())

url = client.prepare_request_uri(
  authorization_url,
  redirect_uri = redirectURL,
  scope = ['section:attendance:read'],
  state = state
)

#########################################
# Open System Browser and initiate OAuth2

print("Opening Browser for login")

webbrowser.open(url, new=1, autoraise=True)

returl = input("Enter full redirect URL that yout browser was sent to: ")
while not ("code=" in returl and redirectURL+"?" in returl and "state="+state in returl):
  print("No, it should look something like: "+redirectURL+"?code=0123456789abcdef...&state="+state)
  returl = input("Enter full redirect URL here:")

###############################
# Parse URL to get access token

purl=urlparse(returl)
query=parse_qs(purl.query)
code=query["code"][0]

###############################
# prep the OAuth2 token request

data = client.prepare_request_body(
  code = code,
  redirect_uri = redirectURL,
  client_id = client_id,
  client_secret = client_secret
)

# This header is required
headers = {'Content-type': 'application/x-www-form-urlencoded'}

##################
# Fire request off

response = requests.post(token_url, data=data, headers=headers)

#################################
# Pull access token from response

jtok=json.loads("{}")
if response.status_code==200:
  jtok=json.loads(response.text)
  access=jtok['access_token']
  refresh=jtok['refresh_token']

############################################
# Set bearer header for subsequent API calls

header = {'Authorization': 'Bearer {}'.format(access)}

#############################################################################
# Get OSM startup infos (contains info about what sections/groups you can see

response = requests.get('https://www.onlinescoutmanager.co.uk/ext/generic/startup/?action=getData', headers=header)

#####################again status

# Gets the lump of json in the startup var setting exercise.
b=json.loads(response.text.split("var data_holder = ")[1])

# Build a section dict
sectionid=dict()
sectiontype=dict()
for a in b["globals"]["roles"]:
  fullname=a['groupname']+": "+a['sectionname']
  sectionid[fullname]=a['sectionid']
  sectiontype[fullname]=a['section']

####################################
# Simple Menu for sections and dates

sectiondict = {str(index): element for index, element in enumerate(sorted(sectionid.keys()))}
for i in sorted(sectiondict.keys()):
  print (i,sectiondict[i])

while True:
  get=input("Space separated list of sections to include: ")
  got=get.split()
  test=True
  for i in got:
    if i in sectiondict:
      print(i, "selected:", sectiondict[i])
    else:
      print(i, "Invalid choice")
      test=False
  if test:
    break

while True:
  notbeforein=input("First Date (not before YYYY-MM-DD): ").strip()
  try:
      notbefore=date.fromisoformat(notbeforein)
      break
  except ValueError:
      print("Date Not Valid; Try again!")
      continue

while True:
  notafterin=input("Last Date (not after YYYY-MM-DD [default: today]): ").strip()
  if notafterin == "":
    notafter=date.today()
    print("Using Today's date",notafter)
    break
  try:
    notafter=date.fromisoformat(notafterin)
    break
  except ValueError:
    print("Date Not Valid; Try again!")
    continue

########## 
# Todo: Show user and get them to check menu choices before continuing

pass

##################
# Get the relevant URLs for terms in the date range and sections chosen

terms={}
for i in got:
  mysection=sectiondict[i]
  for a in b["globals"]["terms"]:
    for termchunk in b["globals"]["terms"][a]:
      if 'sectionid' in termchunk:
        if termchunk['sectionid'] == sectionid[mysection]:
          term=termchunk['name']
          termid=termchunk['termid']
          start=date.fromisoformat(termchunk['startdate'])
          end=date.fromisoformat(termchunk['enddate'])
          if end < notbefore: #cant
#            print("term out of (range older)", termchunk['startdate'], termchunk['enddate'])
            pass
          elif start > notafter:
#            print("term out of (range newer)", termchunk['startdate'], termchunk['enddate'])
            pass
          else:
            terms[i+": "+sectionid[mysection]+"; "+term]="https://www.onlinescoutmanager.co.uk/ext/members/attendance/?action=get&sectionid="+sectionid[mysection]+"&termid="+termid+"&section="+sectiontype[mysection]+"&nototal=true"

#####################################
# Go and get attendance data from OSM

meetings={} # should probably use a set here
names={}

for termurl in terms: # Loop over section specific terms we know about
  response = requests.get(terms[termurl], headers=header)  # Request term data
  att=json.loads(response.text)
  for item in att['items']:           # dict()s per individual in this term containing name, meeting attendance, and some other data
    namekey=item['firstname']+" "+item['lastname']+" ("+str(item['scoutid'])+")"
    sectionstart=item['startdate']
    ss=date.fromisoformat(sectionstart)
#    sectionend=item['enddate'] # Can be a data string or None #!!!! can be weird depending on moving on choices; probably to do with unclear last term to show in values
#    try:
#      se=date.fromisoformat(sectionend)
#    except TypeError:
#      se=date.today()
    se=date.today()
    if not ( namekey in names ):
      names[namekey]=dict()            # Add name with dict to index so it can be filled if not already defined
    for meeting in att["meetings"]:    # Loop over meetings in this term
      md=date.fromisoformat(meeting)
      if md >= notbefore and md <= notafter: # Process meetings which fall within user's requested range (from menu)
        meetings[meeting]=1
        if md >= ss and md <= se:           # Process meetings for this member which fall within their membership of this section
          if meeting in item:
            if item[meeting] == 'Yes':
              names[namekey][meeting]=1
            else:
              names[namekey][meeting]=0
          else:
              names[namekey][meeting]=0  # sometimes value is not set (depending on who did register set to 0 if within date & section membership params)

################## Consider making names section specific or adding col for each section entry per person?

# Write to CSV
##############
with open("output.csv", "w") as f:  # Should give user a way to choose location
  w = csv.DictWriter(f, fieldnames=["name"]+sorted(meetings.keys()) )
  w.writeheader()
  for person in sorted(names.keys()):
    row = {'name': person}
    row.update(names[person])
    w.writerow(row)

