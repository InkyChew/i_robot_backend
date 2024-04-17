import json, configparser, os
from flask import Flask, request, abort
from database import db, ma
from flask_cors import CORS
from routes.auth import auth
from routes.lineBot import lineBot
from routes.investment import investment
from routes.exhibit import exhibit
from routes.performance import performance
from flask_jwt_extended import JWTManager
from linebot import LineBotApi, WebhookHandler, SignatureValidator
from linebot.models import MessageEvent, TextMessage, TextSendMessage
from linebot.exceptions import InvalidSignatureError

app = Flask(__name__)
config = configparser.ConfigParser()
config.read('config.ini')

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root@127.0.0.1/stockai'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root@localhost/stockai'

app.register_blueprint(auth)
app.register_blueprint(lineBot)
app.register_blueprint(investment)
app.register_blueprint(exhibit)
app.register_blueprint(performance)

# Setup the Flask-JWT-Extended extension
app.config['JWT_SECRET_KEY'] = config.get('JWT', 'JWT_secret_key')
app.config['JWT_BLACKLIST_ENABLED'] = True
app.config['JWT_BLACKLIST_TOKEN_CHECKS'] = ['access']
jwt = JWTManager(app)

db.init_app(app)
ma.init_app(app)

line_bot_api = LineBotApi(config.get('line-bot', 'channel_access_token'))
handler = WebhookHandler(config.get('line-bot', 'channel_secret'))

@app.route('/')
def index():
  db.create_all()
  return 'Hello World'

@app.route("/callback", methods=['POST'])
def callback():
  signature = request.headers['X-Line-Signature']
  print("sig", signature)
  body = request.get_data(as_text=True)
  app.logger.info("Request body: " + body)

  print(body)
  try:
    handler.handle(body, signature)
  except Exception as e:
    print(e)
    abort(400)
  return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
  message = TextSendMessage(text=event.message.text)
  print(event.message.text)
  line_bot_api.reply_message(event.reply_token, message)

# @handler.add(PostbackEvent)
# def handle_postback(event):
#     if event.postback.data == 'ping':
#         line_bot_api.reply_message(
#             event.reply_token, TextSendMessage(text='pong'))
#     elif event.postback.data == 'datetime_postback':
#         line_bot_api.reply_message(
#             event.reply_token, TextSendMessage(text=event.postback.params['datetime']))
#     elif event.postback.data == 'date_postback':
#         line_bot_api.reply_message(
#             event.reply_token, TextSendMessage(text=event.postback.params['date']))

if __name__ == "__main__":
  CORS(app)
  # port = int(os.environ.get('PORT', 5000))
  # app.run(host='0.0.0.0', port=port)
  app.run(host="localhost", port=8888)
  # app.run(host="192.168.43.19", port=8888)