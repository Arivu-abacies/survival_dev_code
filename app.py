from __future__ import print_function
from future.standard_library import install_aliases
install_aliases()

from urllib.parse import urlparse, urlencode
from urllib.request import urlopen, Request
from urllib.error import HTTPError
#
import requests
import json
import os
from xml.etree import cElementTree as ElementTree
from flask import Flask
from flask import request
from flask import make_response
import psycopg2
# Flask app should start in global layout
app = Flask(__name__)

host = "ec2-54-235-109-37.compute-1.amazonaws.com"
dbname = "d1d7bllf3j3sfb"
user = "hdmxhfxqoewzwh"
port = "5432"
password = "dbed93d27d8b33b0a1314e32979e9ff5146867d7888d8681b4920149c5b5b338"

def dbconnect():
    conn = psycopg2.connect(host=host,user=user,password=password,dbname=dbname)
    cursor = conn.cursor()
    return conn,cursor

@app.route('/webhook', methods=['POST'])
def webhook():
    req = request.get_json(silent=True, force=True)
    res = processRequest(req)
    res = json.dumps(res, indent=4)
    r = make_response(res)
    r.headers['Content-Type'] = 'application/json'
    return r

def processRequest(req):
    global rowid    
    global nth 
    global intent
    userval = None
    print(req)   
    cur_intent = req.get("result").get("action") 
    conn,cursor = dbconnect()	
    cursor.execute("select * from survival where category='Fire' order by random() limit 1")
    rows = cursor.fetchone()
    global speech
    try:
        line = rows[2]	
        speech = str(line)+". Want more, Say Yes or No or Main" 			
    except:
        speech =""
            
    if not speech:
        speech = "Sorry i dint get that Options"
    print(speech)    	
    response_data = {
    "data":{
    "google":{
    "userStorage":str({'option' :"fire",'intent':"2",'rowid':"1",'nth':"1"}),
    "resetUserStorage":"True",	
    "expect_user_response":"True",
    "permissions_request":"None"
    },
	"facebook":{
    "userStorage":str({'option' :"fire",'intent':"2",'rowid':"1",'nth':"1"}),
    "resetUserStorage":"True",	
    "expect_user_response":"True",
    "permissions_request":"None"
    }
    },
    "messages":[
    {
    "speech":str(speech),
    "type":0
    },
    {
    "platform":"google",
    "type":"simple_response",
    "displayText":str(speech),
    "textToSpeech":str(speech)
    },
    {
    "platform":"google",
    "type":"suggestion_chips",
    "suggestions":[
    {
    "title":"Read more"
    }
    ]
    }
    ]
    }
    #print(response_data)
    return response_data

def processRequestest(req):
    global rowid    
    global nth 
    global intent
    userval = None
    print(req)
    if req.get("originalRequest"):
        userval = req.get("originalRequest").get("data").get("user").get("userStorage")
    if userval:
        json_acceptable_string = userval.replace("'", "\"")
        userval = json.loads(json_acceptable_string)
    cur_intent1 = req.get("result").get("action")
    cur_intent = req.get("result").get("action")
    print(cur_intent1)
    print(cur_intent)

    if userval and cur_intent == 'readmore':
        intent = userval["intent"]
        nth = userval["nth"]
        rowid = userval["rowid"]
        option = userval['option']
    else:
        nth	= 0
        rowid = 0
        intent = ''

    if cur_intent == 'readmore':
        option = option
    else:	
        list_option = ["fire", "navigation", "foraging", "survivalitems", "basics", "shelter", "firstaid"]
        dict = {'fire': 'Fire', 'navigation': 'Navigation', 'foraging': 'Foraging','basics': 'Basics', 'shelter': 'Shelter', 'survivalitems': 'Survival Items', 'firstaid': 'First Aid'}
        if cur_intent not in list_option:
            return { 
                "speech": "Error in List Option",
                "displayText": "Error in List Option"
                }
        option = dict[cur_intent]
        print(option)
    conn,cursor = dbconnect()
    if cur_intent == 'readmore':	
        cursor.execute("select * from survival where category='"+str(option)+"' and id='"+str(rowid)+"' order by random() limit 1")
    else:
        cursor.execute("select * from survival where category='"+str(option)+"' order by random() limit 1")
    rows = cursor.fetchone()
    global speech
    print(rows[2])
    try:
        line = rows[2]
        n = 300
        splitted = [line[i:i+n] for i in range(0, len(line), n)]
        if not nth:
                nth = 0
                text = splitted[nth]
        else:	
            text = splitted[nth]
        nth = nth + 1				
        if len(splitted) >  nth:	
                speech = str(text)+". Want more, Say Read more"
                rowid = rows[-1]
                #nth = nth + 1	
        else:		
                speech = str(text)+". Want more, Say Yes or No or Main" 			
    except:
        speech =""
            
    if not speech:
        speech = "Sorry i dint get that Options"
    print(speech)    	
    if len(splitted) >	nth:
        response_data = {
        "data":{
        "google":{
        "userStorage":str({'option' :option,'intent':len(splitted),'rowid':rowid,'nth':nth}),
        "resetUserStorage":"True",	
        "expect_user_response":"True",
        "permissions_request":"None"
        }
        },
        "messages":[
        {
        "speech":str(speech),
        "type":0
        },
        {
        "platform":"google",
        "type":"simple_response",
        "displayText":str(speech),
        "textToSpeech":str(speech)
        },
        {
        "platform":"google",
        "type":"suggestion_chips",
        "suggestions":[
        {
        "title":"Read more"
        }
        ]
        }
        ]
        }
    else:
        response_data = {
        "data":{
        "google":{
        "userStorage":str({'option' :option,'intent':len(splitted),'rowid':rowid,'nth':0}),
        "resetUserStorage":"True",	
        "expect_user_response":"True",
        "permissions_request":"None"
        }
        },
        "messages":[
        {
        "speech":str(speech),
        "type":0
        },
        {
        "platform":"google",
        "type":"simple_response",
        "displayText":str(speech),
        "textToSpeech":str(speech)
        },
        {
        "platform":"google",
        "type":"suggestion_chips",
        "suggestions":[
        {
        "title":"Yes"
        },
        {
        "title":"No"
        },
        {
        "title":"Main"
        }
        ]
        }
        ]
        }
    print(response_data)
    return response_data

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))

    print("Starting app on port %d" % port)

    app.run(debug=True, port=port, host='0.0.0.0')
