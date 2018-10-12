# encoding: utf-8
from flask import Flask, request, abort
import json
import random
import LineData
import os
import pymysql
import atexit
from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
)




app = Flask(__name__)
db = pymysql.connect('localhost', 'line-bot-meow', 'meowmeow', 'line-bot-meow',charset='utf8')

seesayList = dict()
# 填入你的 message api 資訊
line_bot_api = LineBotApi('QSlS8X1tnLdligI4WpctOltfHNTJTEC2+HIzxUUO5gDAtK/Ul/QNhDoRCEteyMyucLClq4LxbBWqaHc61UOm0k1YhhXZVBiOSh5MhRLPb8UiC9d0o0MDxz+MX443qzio1Y087zNMmTtaINGAYLEpCgdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('a413c208e8be80c0a4884e6f5e16bd81')

@app.route("/", methods=['POST'])
def index():
    global seesayList
    lineData = LineData.LineData(request.get_data(as_text=True))
    # line_json = json.loads(request.get_data(as_text=True))
    print(lineData.getText())
    if lineData.isType('text'):
        c = db.cursor()
        sql = "INSERT INTO `log`(`id`, `text`, `userid`, `time`) VALUES (NULL, '{text}', '{userId}', CURRENT_TIMESTAMP);".format(text=lineData.getText(), userId=lineData.getUserId())
        # print(sql)
        c.execute(sql)
        db.commit()
        replyMessage = getMessage(lineData)
        if replyMessage:
            print ('reply')
            line_bot_api.reply_message(lineData.getReplyToken(), TextSendMessage(text=replyMessage))
    # print request.get_data(as_text=True)

    # print line_json['events'][0]['message']['text']
    return " "
def getMessage(lineData):
    global seesayList
    if len(lineData.getText()) >= 20:
        return "幹你娘太長了 喵"
    if lineData.isSeeSay():
        see = lineData.getText().split('see', 1)
        say = see[1].split('say', 1)
        if say[0] in seesayList:
            seesayList[say[0]].append(say[1])
        else:
            seesayList[say[0]]=[]
            seesayList[say[0]].append(say[1])

        update(say[0], seesayList[say[0]])
        print ('save')
        return '知道了 喵'

    if lineData.getText() in seesayList:
        print ('match')
        return seesayList[lineData.getText()][random.randint(0,len(seesayList[lineData.getText()])-1)]

def update(key, value):
    cursor1 = db.cursor()
    sql_check = "SELECT * FROM `seesay` WHERE `see` = '{see}'".format(see=key)
    cursor1.execute(sql_check)
    if cursor1.fetchall():
        print('updating')
        sql = "UPDATE `seesay` SET `say`='{say}' WHERE `see` = '{see}';".format(see=key, say=json.dumps(value, ensure_ascii=False))
    else:
        print('inserting')
        sql = "INSERT INTO `line-bot-meow`.`seesay` (`id`, `see`, `say`, `time`) VALUES (NULL, '{see}', '{say}', CURRENT_TIMESTAMP);".format(see=key, say=json.dumps(value, ensure_ascii=False))
    print(sql)
    cursor1.execute(sql)
    db.commit()

def doBeforeExit():
    # global seesayList
    print('exiting')
    cursor1 = db.cursor()
    for key, value in seesayList.items():
        print(key, value)
        print ("saving...")
        sql_check = "SELECT * FROM `seesay` WHERE `see` = '{see}'".format(see=key)
        cursor1.execute(sql_check)
        if cursor1.fetchall():
            print('updating')
            sql = "UPDATE `seesay` SET `say`='{say}' WHERE `see` = '{see}';".format(see=key, say=json.dumps(value, ensure_ascii=False))
        else:
            print('inserting')
            sql = "INSERT INTO `line-bot-meow`.`seesay` (`id`, `see`, `say`, `time`) VALUES (NULL, '{see}', '{say}', CURRENT_TIMESTAMP);".format(see=key, say=json.dumps(value, ensure_ascii=False))
        print(sql)

        cursor1.execute(sql)
        db.commit()

    db.close()


# @app.route("/callback", methods=['POST'])
# def callback():
#     json_line = request.get_json()
#     json_line = json.dumps(json_line)
#     decoded = json.loads(json_line)
#     user = decoded['result'][0]['content']['from']
#     text = decoded['result'][0]['content']['text']
#     #print(json_line)
#     print("使用者：",user)
#     print("內容：",text)
#     return ''





if __name__ == "__main__":

    print('loading...')
    cursor = db.cursor()
    cursor.execute('SELECT * FROM `seesay` WHERE 1')
    res = cursor.fetchall()
    for r in res:
        seesayList[r[1]] = json.loads(r[2])
        
        print(r[1], r[2])
    print('loaded complete')
    # atexit.register(doBeforeExit)
    app.run(debug=True, port=8000)