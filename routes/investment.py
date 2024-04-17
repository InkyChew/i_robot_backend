import requests, json
from flask import Flask, Blueprint, jsonify, request
from database import db
from dbms.Models import User, UserInvAct
from dbms.Schemas import UserSchema, UserInvActSchema

investment = Blueprint("investment", __name__)

@investment.route("/investment/postInvAct", methods=["post"])
def postInvAct(): # 將使用者投資資訊存入資料庫
  try:
    uid = request.json["uid"]
    totalAssets = request.json["totalAssets"]
    stopLossPoint = request.json["stopLossPoint"]

    obj_user = UserInvAct.query.filter_by(uid=uid).first()
    userInvAct_schema = UserInvActSchema()
    user = userInvAct_schema.dump(obj_user)
    if not user:
      newUserInvAct = UserInvAct(totalAssets, stopLossPoint, uid)
      db.session.add(newUserInvAct)
      db.session.commit()
      return jsonify({
              "description": "您已成功開始您的第一筆投資"
          }), 200
    else:
      UserInvAct.query.filter_by(uid=uid).update({
        'totalAssets': totalAssets,
        'stopLossPoint': stopLossPoint
      })
      db.session.commit()
      return jsonify({
              "description": "您的投資資訊已更新成功"
          }), 200
  except Exception as e:
    print(e)
    return jsonify({
          "description": "Server Error."
      }), 500
