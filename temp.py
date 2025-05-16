from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import (
    MessageEvent, TextMessage, PostbackEvent, TextSendMessage, ImagemapSendMessage,
    BaseSize, MessageImagemapAction, URIImagemapAction, ImagemapArea,
    TemplateSendMessage, ButtonsTemplate, DatetimePickerTemplateAction
)
from urllib.parse import parse_qsl
import datetime

app = Flask(__name__)

import os

# 記得替換為你自己的 LINE Channel Access Token 與 Secret
line_bot_api = LineBotApi(os.environ.get('aYFtB6V62sZDw9+JPU2GOJjbmS/YFmcQI93Wb+JutAUs7diGDeDr063W73qU3PMSgb73811wl69FgGLspBZSkF4ZVd+UnfjcLP9VLJgxTaMBzOTxah3Gefx9/FGulwZ2E7BDgSkIzFJOoQVBwk0keAdB04t89/1O/w1cDnyilFU='))
handler = WebhookHandler(os.environ.get('3430c16c558acf00712c4dcdc9e2f7cf'))

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    mtext = event.message.text
    if mtext == '@圖像地圖':
        sendImgmap(event)
    elif mtext == '@選擇日期時間':
        sendDatetime(event)

@handler.add(PostbackEvent)
def handle_postback(event):
    backdata = dict(parse_qsl(event.postback.data))
    if backdata.get('action') == 'sell':
        sendData_sell(event, backdata)

def sendImgmap(event):
    try:
        image_url = 'https://i.imgur.com/Yz2yzve.jpg'
        imgwidth = 1040
        imgheight = 300
        message = ImagemapSendMessage(
            base_url=image_url,
            alt_text="圖像地圖範例",
            base_size=BaseSize(height=imgheight, width=imgwidth),
            actions=[
                MessageImagemapAction(
                    text='你點選了左邊的區塊',
                    area=ImagemapArea(x=0, y=0, width=imgwidth//4, height=imgheight)
                ),
                URIImagemapAction(
                    link_uri='http://www.e-happy.com.tw',
                    area=ImagemapArea(x=imgwidth*3//4, y=0, width=imgwidth//4, height=imgheight)
                ),
            ]
        )
        line_bot_api.reply_message(event.reply_token, message)
    except Exception as e:
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text='發生錯誤：' + str(e)))

def sendDatetime(event):
    try:
        message = TemplateSendMessage(
            alt_text='選擇日期時間',
            template=ButtonsTemplate(
                thumbnail_image_url='https://i.imgur.com/VxVB46z.jpg',
                title='日期時間選擇',
                text='請選擇以下選項：',
                actions=[
                    DatetimePickerTemplateAction(
                        label="選擇日期",
                        data="action=sell&mode=date",
                        mode="date",
                        initial="2025-05-16",
                        min="2025-05-16",
                        max="2026-05-16"
                    ),
                    DatetimePickerTemplateAction(
                        label="選擇時間",
                        data="action=sell&mode=time",
                        mode="time",
                        initial="10:00",
                        min="00:00",
                        max="23:59"
                    ),
                    DatetimePickerTemplateAction(
                        label="選擇日期與時間",
                        data="action=sell&mode=datetime",
                        mode="datetime",
                        initial="2025-05-16T10:00",
                        min="2025-05-16T00:00",
                        max="2026-05-16T23:59"
                    )
                ]
            )
        )
        line_bot_api.reply_message(event.reply_token, message)
    except Exception as e:
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text='發生錯誤：' + str(e)))

def sendData_sell(event, backdata):
    try:
        if backdata.get('mode') == 'date':
            dt = '您選擇的日期是：' + event.postback.params.get('date')
        elif backdata.get('mode') == 'time':
            dt = '您選擇的時間是：' + event.postback.params.get('time')
        elif backdata.get('mode') == 'datetime':
            dt_obj = datetime.datetime.strptime(event.postback.params.get('datetime'), '%Y-%m-%dT%H:%M')
            dt = f"您選擇的日期與時間是：{dt_obj.strftime('%Y-%m-%d %H:%M')}"
        message = TextSendMessage(text=dt)
        line_bot_api.reply_message(event.reply_token, message)
    except Exception as e:
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text='發生錯誤：' + str(e)))

if __name__ == '__main__':
    app.run(debug=True)
