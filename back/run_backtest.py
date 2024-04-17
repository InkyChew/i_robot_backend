#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
import numpy as np
import math
import os


profit_count, loss_count, total_profit_rate, ROI = 0,0,0,0
principal = 1000000 * 10
cash = principal
portfolio = []
sell_trade_num = None

# In[2]:


##創資料夾
def mkdir(path):
    folder = os.path.exists(path)
    #判斷結果
    if not folder:
        #如果不存在，則建立新目錄
        os.makedirs(path)
        print('-----建立成功-----')
    else:
        #如果目錄已存在，則不建立，提示目錄已存在
        print(path+'目錄已存在')
        
        
## 資料匯出
def OutputCSV(df):
    dir_path = 'Rank'
    csv_name = 'Rank'
    Result = dir_path + '/' + csv_name + '.csv'
    df_SAMPLE = pd.DataFrame.from_dict(df)
    df_SAMPLE.to_csv(Result, index=False)
    print('成功產出'+ Result)
    
    
def insert_df(name, buy_percentage, sell_trade_num, stop_loss, take_profit, profit):
    dir_path = 'Rank'
    csv_name = 'Rank'
    mkdir(dir_path)
    path = dir_path + '/' + csv_name + '.csv'
    try:
        df = pd.read_csv(path)
        temp=pd.DataFrame({'name':name,
                  'buy_percentage':buy_percentage,
                  'sell_trade_num':sell_trade_num,
                  'stop_loss':stop_loss,
                  'take_profit':take_profit,
                  'profit':profit},
                index=[0])
        df=df.append(temp, ignore_index=True)
        OutputCSV(df)
    except OSError:
        df = pd.DataFrame(columns=['name','buy_percentage','sell_trade_num','stop_loss','take_profit','profit'])
        OutputCSV(df)
        df = pd.read_csv(path)
        temp=pd.DataFrame({'name':name,
                  'buy_percentage':buy_percentage,
                  'sell_trade_num':sell_trade_num,
                  'stop_loss':stop_loss,
                  'take_profit':take_profit,
                  'profit':profit},
                index=[0])
        df=df.append(temp, ignore_index=True)
        OutputCSV(df)


# In[3]:


class Trade():
    trade_count = 0
    
    # 建構式
    def __init__(self, price, num):
        Trade.trade_count += 1
        self.price = price #買進價格
        self.num = num #買幾張
        self.total_cost = price*num*1000 #尚未考慮手續費
    
    
    def get_sell_profit(self, sell_price):
        return sell_price*self.num*1000 - self.total_cost
    
    def get_current_profit_pc(self, current_price):
        profit = self.get_sell_profit(current_price)
        profit_pc = profit / self.total_cost
        return profit_pc*100

def buy(buy_price):
    global cash
    cash_ = principal * buy_percentage/100
    if cash < cash_:
        cash_ = cash
    can_buy_num = cash_ // (buy_price*1000)
    if can_buy_num > 0:
        buy_trade = Trade(buy_price,can_buy_num)
        portfolio.append(buy_trade)
        cash -= buy_trade.total_cost #尚未考慮手續費
        print('以 %.1f元，買進 %d 張 2330，現金餘額 %.2f 元' % (buy_price,can_buy_num, cash))
    else:
        print('有買進訊號，但無法購買')


def sell(trade, sell_price):
    global cash, profit_count, loss_count, total_profit_rate
    sell_gain = trade.num*1000*sell_price #尚未考慮手續費
    cash += sell_gain
    profit_loss = trade.get_sell_profit(sell_price)
    profit_rate = trade.get_current_profit_pc(sell_price)
    total_profit_rate += profit_rate

    if profit_loss >= 0:
        profit_count += 1
    else:
        loss_count += 1

    portfolio.remove(trade)
    print('以 %.1f元，賣出 %d 張 2330，利損：%.2f元，現金餘額 %.2f 元'          % (sell_price,trade.num,profit_loss,cash))

def meet_strategy_sell(sell_price):
    if sell_trade_num == 'all':
        for _ in range(len(portfolio)):
            sell(portfolio[0], sell_price)
    else:
        tmp = min(sell_trade_num, len(portfolio))
        for _ in range(tmp):                     
            sell(portfolio[0], sell_price)

def cross_over(col1, col2, idx):
    # col1向上突破col2
    if idx == 0: return False
    return bt_data[col1][idx] > bt_data[col2][idx] and bt_data[col1][idx-1] < bt_data[col2][idx-1]

def cross_under(col1, col2, idx):
    # col1向上突破col2
    if idx == 0: return False
    return bt_data[col1][idx] < bt_data[col2][idx] and bt_data[col1][idx-1] > bt_data[col2][idx-1]


# In[4]:


def backtest(take_profit, stop_loss, buy_pc, sell_trade_n):
    global buy_percentage, sell_trade_num, ROI
    buy_percentage = buy_pc
    sell_trade_num = sell_trade_n
#     stop_loss = 5  # (%)  不停損 math.inf
#     take_profit = 10 # (%) 不停利 math.inf
    stock_num_2330 = 0
    principal = 1000000 * 10

    # 計算交易策略績效
    Trade.trade_count = 0

    for i in range(len(bt_data)-1):
        close = bt_data['Close'][i]    
        next_close = bt_data['Close'][i+1]
        next_open = bt_data['Open'][i+1]
        rsi6 = bt_data['RSI6'][i]
        uprate_1day = bt_data['predict_1day_uprate'][i]

        ### 先檢查有無 達到停利停損標準的 Trade
        for trade in portfolio:
            if trade.get_current_profit_pc(next_open) <= -stop_loss:
                print('[停損賣出]')
                sell(trade, next_open)
            elif trade.get_current_profit_pc(next_open) >= take_profit:
                print('[停利賣出]')
                sell(trade, next_open)

        ### 買進策略  
        if uprate_1day == 2 and next_open <= close:
            print('(買入)[Model 預測說要漲啦]')
            buy(next_close)

        if cross_over('K_value', 'D_value', i):
            print('(買入)[KD 黃金交叉]')
            buy(next_open)

        if cross_over('MA_5days', 'MA_20days', i):
            print('(買入)[MA 黃金交叉]')
            buy(next_open)

        if rsi6 <= 25:
            print('(買入)[RSI6 <= 25]')
            buy(next_open)


        ### 賣出策略

            #模型預測跌，當沖
        if len(portfolio)>0 and uprate_1day == 0 and next_open >= close:
            print('(當沖)[Model 預測說要跌，隔日開盤買進，收盤賣出]')
            buy(next_open)
            sell(portfolio[-1], next_close)

        if len(portfolio)>0 and cross_under('K_value', 'D_value', i):
            print('(賣出)[KD 死亡交叉]')
            meet_strategy_sell(next_open)

        if len(portfolio)>0 and cross_under('MA_5days', 'MA_20days', i):
            print('(賣出)[MA 死亡交叉]')
            meet_strategy_sell(next_open)

        if len(portfolio)>0 and rsi6 >= 70:
            print('(賣出)[RSI6 >= 70]')
            meet_strategy_sell(next_open)


        print('-'*40)

    print('*'*25, '最後一天，全部平倉', '*'*25)
    last_close = bt_data['Close'][len(bt_data)-1]
    for _ in range(len(portfolio)):
        sell(portfolio[0], last_close)

    ROI = (cash/principal-1)*100
    print('總資產:', cash)
    print('交易次數:', Trade.trade_count)
    print('獲利次數:', profit_count)
    print('虧損次數:', loss_count)
    # print('勝率: %.2f%%' % (profit_count / Trade.trade_count*100))
    # print('總報酬率: %.3f %%' % total_profit_rate)
    # print('平均報酬率: %.3f %%' % (total_profit_rate / Trade.trade_count))


# In[7]:


bt_data = pd.read_csv('backtest_2330_data.csv')

def start_backtest_and_save_record(name, take_profit, stop_loss, buy_pc, sell_trade_num):
    ### buy_pc 0~100
    global profit_count, loss_count, total_profit_rate,ROI
    profit_count, loss_count, total_profit_rate = 0,0,0
    Trade.trade_count = 0
    
    if take_profit == 0:
        # 不停利
        take_profit = math.inf
        
    if stop_loss == 0:
        # 不停損
        stop_loss = math.inf
        
    if sell_trade_num == 0:
        # 符合交易策略，一次全賣
        sell_trade_num = 'all'
    
    backtest(take_profit, stop_loss, buy_pc, sell_trade_num)
    
    insert_df(name, buy_pc, sell_trade_num, stop_loss, take_profit, ROI)
    
    print('每筆交易累加報酬率:', total_profit_rate)
    print('總報酬率:', ROI)
    return ROI

