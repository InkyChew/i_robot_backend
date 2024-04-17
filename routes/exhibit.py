from flask import Flask, Blueprint, jsonify, request

import back.get_rank as gk
from importlib import reload

exhibit = Blueprint("exhibit", __name__)

@exhibit.route("/exhibit/computeProfitRate", methods=["post"])
def computeProfitRate():
  try:
    import back.run_backtest as bt
    name = request.json["name"]
    take_profit = request.json["profit"]
    stop_loss = request.json["loss"]
    buy_pc = request.json["buy"]
    sell_trade_num = request.json["sell"]

    reload(bt)
    total_profit_rate = bt.start_backtest_and_save_record(name, take_profit, stop_loss, buy_pc, sell_trade_num)
    return jsonify({
      "total_profit_rate" : total_profit_rate
    }), 200
  except Exception as e:
    print(e)
    return jsonify({
      "description": "Server Error."
    }), 500

@exhibit.route("/exhibit/rank", methods=["get"])
def rank():
  try:
    return jsonify({
      "exhibit_rank": gk.get_rank()
    }), 200
  except Exception as e:
    print(e)
    return jsonify({
      "description": "Server Error."
    }), 500