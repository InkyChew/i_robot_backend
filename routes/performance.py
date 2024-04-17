from flask import Flask, Blueprint, jsonify, request

import back.backtest4start as backtest4start

performance = Blueprint("performance", __name__)

@performance.route("/performance/showInvestInfo", methods=["get"])
def computeProfitRate():
  try:
    result = backtest4start.start_backtest_and_save_record('Jack2',0,0,5.5,1)
    return result, 200
  except Exception as e:
    print(e)
    return jsonify({
      "description": "Server Error."
    }), 500
