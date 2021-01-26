# Importing modules
import re
import nltk
import sqlite3
nltk.download('wordnet')
from nltk.corpus import wordnet
from collections import defaultdict 
import time
import json 
import requests
import time
import urllib
from datetime import date


TOKEN = "1549924791:AAEN3tv6tFtfC9y_9KvuoTNNIyVoKoLP5Ys"
URL = "https://api.telegram.org/bot{}/".format(TOKEN)


from dbutil import DBHelper

db = DBHelper()

nerd_que=[("goal","Hey! I’m Nerd - your budgeting assistant. I’ll help setup budget, weekly targets and keep you on track. Select a goal to begin 🔥\nType option number👇\n1. New Gadget, vacation etc\n2. Investing money3. Building emergency fund\n4. Paying off debt\n5. Just saving"),
 ("income","👍 Awesome! I’ve a few more questions to ask. Note: Answers can’t be edited. To restart setup, type restart\n🤑 Your Income & Pay date?\n👉 Type (eg): 15000, 31\n👉 Income is salary/ allowance/ stipend etc per month"),
 ("invest","🌲 Monthly Investments (SIP etc)\n👉 Enter total amount"),
 ("expances","🧾 Bills you pay every month?\nHome: Rent, Maids, Cook etc\nUtility: Electricity, Water, Phone, Wifi, Gas, TV etc\nEMIs: Loan, Insurance etc\n👉 Enter total amount\n(Don't include investment, credit card bill payment, grocery etc)"),
 ("CC_bills","💳 Credit card(s) Unpaid balance\n👉 Enter total amount, or\n👉 Type N if you don't have cc"),
 ("Ac_balance",["Let's setup budget for current month till your next income.\n💵 Current bank A/C balance?\n👉 Enter Amount",
  "Your income should arrive soon. Let's setup budget then."]),
("m_invest",["Any investment payments to be made before next salary?\n👉 Enter amount",
 "Any fixed expenses to be paid before next salary?\n👉 Enter total amount\n(Don't include investment, credit card bill payment, grocery etc",
 "Lastly, any credit card bills to be paid before next salary?\n👉 Yes? Type Y\n👉 No? Type N"])
]

d = defaultdict(list)
for k, v in nerd_que:
     d[k].append(v)
intent_list=list(d.keys())



def get_url(url):
    response = requests.get(url)
    content = response.content.decode("utf8")
    return content

def date_diff(sd,cd):
  if sd>cd:
    return sd-cd
  else:
    return 31-(cd-sd)

def get_json_from_url(url):
    content = get_url(url)
    js = json.loads(content)
    return js


def get_updates(offset=None):
    url = URL + "getUpdates"
    if offset:
        url += "?offset={}".format(offset)
    js = get_json_from_url(url)
    return js


def get_last_update_id(updates):
    update_ids = []
    for update in updates["result"]:
        update_ids.append(int(update["update_id"]))
    return max(update_ids)

def chat_respose(text,chat_id,lst):

  
  global i
  
  if i==0 or text == "/start" or text=="restart":
        # print the welcoming message
    lst.clear()
    i=0
    intent=intent_list[i]
    db.add_id(x="id",y=chat_id)
    send_message(str(d[intent][0]), chat_id)
    i=i+1
    print(i)

  elif i==2:
    
    try:
      
      db.update_item(x=intent_list[i-1],y=text,z=chat_id)
      pay_date=db.get_items("income",chat_id)[0].split(",")[1]
      intent=intent_list[i]
      print(pay_date)
      send_message(str(d[intent][0]), chat_id)
      i=i+1

    except:

      db.update_item(x=intent_list[i-1],y=text,z=chat_id)
      intent=intent_list[i-1]
      print(intent_list[i-1])
      send_message(str(d[intent][0]), chat_id)
      i=i

  elif i==5:
    
    salary_date=int(db.get_items("income",chat_id)[0].split(",")[1])
    now=int(date.today().day)
    if date_diff(salary_date,now)>4:
      lst.append(text)
      db.update_item(x=intent_list[i-1],y=text,z=chat_id)
      # res[intent_list[i-1]].append(text)
      intent=intent_list[i]
      print(d[intent][0][1])
      send_message(str(d[intent][0][0]), chat_id)
      i=i+1

    else:
      
      db.update_item(x=intent_list[i-1],y=text,z=chat_id)
      # res[intent_list[i-1]].append(text)
      intent=intent_list[i]
      # print(d[intent][0][1])
      send_message(str(d[intent][0][1]), chat_id)
      lst.clear()
      i=0


  elif i>6:
    
    db.update_item(x=intent_list[i-1],y=text,z=chat_id)
    txt="Thank you"
    send_message(str(d["goal"][0]), chat_id)
    db.add_id(x="id",y=chat_id)
    lst.clear()
    i=1
  else:
    if i==3 or i==4:
      lst.append(text)
    print(lst)
    db.update_item(x=intent_list[i-1],y=text,z=chat_id)
    # res[intent_list[i-1]].append(text)
    intent=intent_list[i]
    send_message(str(d[intent][0]), chat_id)
    i=i+1

i=0
# lst=[]
res = defaultdict(list)
ids=100
def echo_all(updates,lst):
    # i=0
    global ids
    for update in updates["result"]:
        text = update["message"]["text"]
        chat_id = update["message"]["chat"]["id"]
        chat_respose(text,chat_id,lst)


def get_last_chat_id_and_text(updates):
    num_updates = len(updates["result"])
    last_update = num_updates - 1
    text = updates["result"][last_update]["message"]["text"]
    chat_id = updates["result"][last_update]["message"]["chat"]["id"]
    return (text, chat_id)


def send_message(text, chat_id):
    text = urllib.parse.quote_plus(text)
    url = URL + "sendMessage?text={}&chat_id={}".format(text, chat_id)
    get_url(url)


def main():
    db.setup()
    last_update_id = None
    lst=[]
    while True:
        updates = get_updates(last_update_id)
        if len(updates["result"]) > 0:
            last_update_id = get_last_update_id(updates) + 1
            print(i)
            echo_all(updates,lst)
        time.sleep(0.5)


if __name__ == '__main__':
    main()