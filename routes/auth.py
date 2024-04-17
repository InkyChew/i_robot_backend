import requests, json, configparser
import jwt, datetime
from flask import Flask, Blueprint, url_for, session
from flask import jsonify, request
from flask import render_template, redirect
from flask_jwt_extended import jwt_required, create_access_token, get_jwt_identity, get_raw_jwt

from database import db
from dbms.Models import User
from dbms.Schemas import UserSchema

auth = Blueprint("auth", __name__)

config = configparser.ConfigParser()
config.read('config.ini')
client_id = config.get('line-login', 'client_id')
client_secret = config.get('line-login', 'client_secret')
redirect_uri = "http://localhost:8080/investment"

@auth.route("/auth/line/login_url", methods=["GET"])
def getLineLoginURL():
  loginURL = ("https://access.line.me/oauth2/v2.1/authorize?response_type=code"
        "&client_id=1654259982"
        "&redirect_uri=http://localhost:8080/investment"
        "&state=12313154"
        "&bot_prompt=aggressive"
        "&scope=profile%20openid%20email")

  return jsonify({
            "LineloginURL": loginURL
          }), 200

@auth.route("/auth/line/<code>", methods=["POST"])
def postCodeToLine(code):
  if code:
    try:
      headers = {
        "Content-Type": "application/x-www-form-urlencoded"
      }
      body = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": redirect_uri,
        "client_id": client_id,
        "client_secret": client_secret
      }
      lineAPI = "https://api.line.me/oauth2/v2.1/token"
      # 取得id_token解碼得到user的line資訊
      res = requests.post(lineAPI, headers=headers, data=body).json()
      if res:
        access_token = res.get("access_token")
        decoded_id_token = jwt.decode(res.get("id_token"),
                                client_secret,
                                audience=client_id,
                                issuer="https://access.line.me",
                                algorithms=["HS256"])
        lineId = decoded_id_token.get("sub")
        # user是否已存在db
        obj_user = User.query.filter_by(lineId=lineId).first()
        user_schema = UserSchema()
        user = user_schema.dump(obj_user)

        if not user:
          # user 不存在，存入db
          email = decoded_id_token.get("email") # email允許=null
          name = decoded_id_token.get("name")
          picture = decoded_id_token.get("picture")
          newUser = User(email, None, name, picture, lineId)
          db.session.add(newUser)
          db.session.flush()
          db.session.commit()
          return jsonify({
              "access_token": access_token,
              "uid": newUser.uid,
              "description": "Line first login success."
          }), 200
        else:
          return jsonify({
              "access_token": access_token,
              "uid": user["uid"]
          }), 200
      else:
        return jsonify({
            "description": "Can't get line user"
        }), 404
    except Exception as e:
      print(e)
      return jsonify({
            "description": "Server Error."
        }), 500
  else:
    return jsonify({
        "description": "Can't get code."
    }), 400

@auth.route("/auth/regist", methods=["POST"])
def postNewUser():
  try:
    email = request.json["email"]
    password = request.json["password"]
    name = request.json["name"]

    obj_user = User.query.filter_by(email=email).first()
    user_schema = UserSchema()
    user = user_schema.dump(obj_user)
    if not user:
      newUser = User(email, password, name, None, None)
      db.session.add(newUser)
      db.session.commit()
      return jsonify({
              "description": "Regist success.",
              "name": name
          }), 200
    else:
      return jsonify({
              "description": "Email is already exist.",
              "name": name
          }), 401
  except Exception as e:
    print(e)
    return jsonify({
          "description": "Server Error."
      }), 500

@auth.route("/auth/login", methods=["POST"])
def login():
  try:
    u_email = request.json["email"]
    u_pwd = request.json["password"]
    obj_user = User.query.filter_by(email=u_email).first()
    user_schema = UserSchema()
    user = user_schema.dump(obj_user)
    if not user:
      return jsonify({
          "description": "Email invalid."
      }), 401
    elif user["password"] != u_pwd:
      return jsonify({
          "description": "Password is wrong."
      }), 401
    else:
      expires = datetime.timedelta(days = 90)
      access_token = create_access_token(
        identity={"uid": user["uid"], "email":  user["email"]},
        expires_delta = expires)
      return jsonify({
          "status": 200,
          "access_token": access_token,
          "uid": user["uid"],
          "description": "Login success."
      }), 200
  except Exception as e:
    print(e)
    return jsonify({
          "description": "Server Error."
      }), 500

@auth.route("/auth/getUserInfo/<uid>", methods=["GET"])
def getUserInfo(uid):
  try:
    obj_user = User.query.filter_by(uid=uid).first()
    user_schema = UserSchema()
    user = user_schema.dump(obj_user)
    if not user:
      print(Exception)
    else:
      userInfo = {
        "name": user["name"],
        "picture": user["picture"]}
      return jsonify({
                "data": userInfo
              }), 200
  except Exception as e:
    print(e)
    return jsonify({
          "description": "Server Error."
      }), 500