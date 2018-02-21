# encoding: utf-8
from flask import Flask, request, abort
import json
import random
import LineData
import os
import pymysql
import atexit
import base64
import hashlib
import hmac
import re
from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage, StickerSendMessage
)



banList = ['喵']
app = Flask(__name__)
db = pymysql.connect('localhost', config['dbname'], config['dbpwd'], 'line-bot-meow',charset='utf8')
seesayList = dict()
channel_secret = config['channel_secret']
# 填入你的 message api 資訊
line_bot_api = LineBotApi(config['line_token'])
handler = WebhookHandler(channel_secret)
patternOracle = re.compile("^[\u3105-\u3129\u02CA\u02C7\u02CB\u02D9\u4e00-\u9fa5a-zA-Z0-9]{1,} 抽籤")
patternSeeSay = re.compile("^see[\u3105-\u3129\u02CA\u02C7\u02CB\u02D9\u4e00-\u9fa5a-zA-Z0-9 ]{1,}say[\u3105-\u3129\u02CA\u02C7\u02CB\u02D9\u4e00-\u9fa5a-zA-Z0-9 ]{1,}")
@app.route("/", methods=['POST'])
def index():
    
    body = request.get_data(as_text=True)
    hash = hmac.new(channel_secret.encode('utf-8'), body.encode('utf-8'), hashlib.sha256).digest()
    signature = base64.b64encode(hash)
    # Compare X-Line-Signature request header and the signature
    handler.handle(body, signature.decode())
    cursor = db.cursor()
    # print (request.get_data(as_text=True))
    return " "

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):

    
    if patternOracle.match(event.message.text):
        line_bot_api.reply_message(event.reply_token, oracle(event.message.text))

    elif patternSeeSay.match(event.message.text):
        line_bot_api.reply_message(event.reply_token, getSeeSay(event.message.text))

    else:
        temp = searchSeeSay(event.message.text)
        if temp:
            line_bot_api.reply_message(event.reply_token, temp)

@handler.default()
def default(event):
    print(event)

def oracle(text):
    sqlOracle = "SELECT * FROM oracle ORDER BY RAND() LIMIT 1"
    cursorOracle = db.cursor()
    cursorOracle.execute(sqlOracle)
    resOracle = cursorOracle.fetchone()
    textS = text.split(" ")
    oracleText = "{textS} 中籤\n-------\n{num}\n{content}\n{oracle_explain}".format(textS=textS[0], num=resOracle[1], content=resOracle[2], oracle_explain=resOracle[3])
    return TextMessage(text=oracleText)

def getSeeSay(text):
    if len(text) > 20:
        return TextMessage(text="幹你娘太長了 喵")

    see = text.split('see', 1)
    say = see[1].split('say', 1)
    if say[0] in banList:
        return TextMessage(text="主人說乖貓不能亂學 喵")
    sqlCheck = "SELECT * FROM seesay WHERE `see` = '{see}'".format(see=say[0])
    cursorCheck = db.cursor()
    cursorCheck.execute(sqlCheck)
    res = cursorCheck.fetchone()
    if res:
        sayJson =json.loads(res[2])
        sayJson.append(say[1])
        sql = "UPDATE `seesay` SET `say`='{say}' WHERE `see` = '{see}';".format(see=say[0], say=json.dumps(sayJson, ensure_ascii=False))
        
    else:
        sql = "INSERT INTO `line-bot-meow`.`seesay` (`id`, `see`, `say`, `time`) VALUES (NULL, '{see}', '{say}', CURRENT_TIMESTAMP);".format(see=say[0], say=json.dumps(say[1], ensure_ascii=False))


    cursorCheck.execute(sql)
    db.commit()
            # if say[0] in seesayList:
    #     seesayList[say[0]].append(say[1])
    # else:
    #     seesayList[say[0]]=[]
    #     seesayList[say[0]].append(say[1])

    # update(say[0], seesayList[say[0]])
    # print ('save')

    return TextMessage(text="知道了 喵")

def searchSeeSay(text):
    sqlSearchSeeSay = "SELECT * FROM seesay where `see`='{text}';".format(text=text)
    cursorSearchSeeSay = db.cursor()
    cursorSearchSeeSay.execute(sqlSearchSeeSay)
    res = cursorSearchSeeSay.fetchone()
    if res:
        sayJ = json.loads(res[2])

        return TextMessage(text=sayJ[random.randint(0, len(sayJ)-1)])
    else:
        return None

if __name__ == "__main__":

    # atexit.register(doBeforeExit)
    app.run(debug=True, port=8000)