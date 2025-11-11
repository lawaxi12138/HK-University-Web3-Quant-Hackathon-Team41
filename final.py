import requests
import time
import datetime
import pandas as pd
import numpy as np
import get_data_HORUS

def SMA(data, SMA1=2, SMA2=10):
    data = data.copy()
    data['SMA1'] = data['price'].rolling(SMA1).mean()
    data['SMA2'] = data['price'].rolling(SMA2).mean()
    data['position'] = np.where(data['SMA1'] > data['SMA2'], 1, 0)
    data['returns'] = np.log(data['price'] / data['price'].shift(1))
    data['strategy'] = data['position'].shift(1) * data['returns']
    data['score'] = np.where(data['strategy'] > 0, 1, -1)
    trades = data['position'].diff().fillna(0) != 0
    data.loc[trades, 'strategy'] -= 0.001
    return data.dropna()

def MOM(data, MOM=3):
    data = data.copy()
    data['returns'] = np.log(data['price'] / data['price'].shift(1))
    data['position'] = np.where(data['returns'].rolling(MOM).mean() > 0, 1, 0)
    data['strategy'] = data['position'].shift(1) * data['returns']
    data['score'] = np.where(data['strategy'] > 0, 1, -1)
    trades = data['position'].diff().fillna(0) != 0
    data.loc[trades, 'strategy'] -= 0.001
    return data.dropna()

def MR(data, sma=14):
    data = data.copy()
    data['returns'] = np.log(data['price'] / data['price'].shift(1))
    data['sma'] = data['price'].rolling(sma).mean()
    data['std'] = data['price'].rolling(sma).std()
    data['distance'] = data['price'] - data['sma']
    data['position'] = np.where(data['distance'] > 2 * data['std'], -1, np.nan)
    data['position'] = np.where(data['distance'] < -2 * data['std'], 1, data['position'])
    data['position'] = np.where(data['distance'] * data['distance'].shift(1) < 0, 0, data['position'])
    data['position'] = data['position'].ffill().fillna(0)
    data['strategy'] = data['position'].shift(1) * data['returns']
    data['score'] = np.where(data['strategy'] > 0, 1, -1)
    trades = data['position'].diff().fillna(0) != 0
    data.loc[trades, 'strategy'] -= 0.001
    return data.dropna()

def decide_strategy(data):
    df_SMA = SMA(data)
    score_SMA = ((df_SMA['score'] == 1).sum() - (df_SMA['score'] == -1).sum()) / len(df_SMA)
    df_MOM = MOM(data)
    score_MOM = ((df_MOM['score'] == 1).sum() - (df_MOM['score'] == -1).sum()) / len(df_MOM)
    df_MR = MR(data)
    score_MR = ((df_MR['score'] == 1).sum() - (df_MR['score'] == -1).sum()) / len(df_MR)
    score = [score_SMA, score_MOM, score_MR]
    max_score = max(score)
    if max_score == score_MR:
        return 'MR'
    elif max_score == score_SMA:
        return 'SMA'
    elif max_score == score_MOM:
        return 'MOM'

def run_strategy(data, strategy: str):
    if strategy == 'SMA':
        return SMA(data)['position'].iloc[-1]
    if strategy == 'MOM':
        return MOM(data)['position'].iloc[-1]
    if strategy == 'MR':
        return MR(data)['position'].iloc[-1]

def get_data_12h(data):
    data = data.copy()
    data.reset_index(inplace=True)
    data['datetime'] = pd.to_datetime(data['datetime'])
    data_12h = data[
        (data['datetime'].dt.hour.isin([0, 12])) &
        (data['datetime'].dt.minute == 0)
    ].copy()
    data_12h.set_index('datetime', inplace=True)
    data_12h.sort_index(inplace=True)
    return data_12h

def get_time():
    current_time = datetime.datetime.now()
    formatted_time = current_time.strftime("%Y-%m-%d %H:%M")
    return formatted_time

def strategy_decision_time():
    current_formatted = get_time()
    current_dt = datetime.datetime.strptime(current_formatted, "%Y-%m-%d %H:%M")
    target_hours = 0
    if current_dt.minute == 0 and current_dt.hour in target_hours:
        return True
    else:
        return False

def strategy_time():
    current_formatted = get_time()
    current_dt = datetime.datetime.strptime(current_formatted, "%Y-%m-%d %H:%M")
    target_hours = [0, 12]
    if current_dt.minute == 0 and current_dt.hour in target_hours:
        current = (current_dt + datetime.timedelta(hours=8)).strftime("%Y-%m-%d %H:%M")
        one_week_ago = (current_dt - datetime.timedelta(days=14)).strftime("%Y-%m-%d %H:%M") # 按前一周的表现选取策略
        return current, one_week_ago
    else:
        return None

if __name__ == '__main__':
    df_test = get_data_12h(get_data_HORUS.get_price_15m('BTC', '2025-11-3 08:00', '2025-11-11 00:00'))
    # print(decide_strategy(df_test))
    print(df_test)
    print(get_data_HORUS.get_price_15m('BTC', '2025-11-3 08:00', '2025-11-12 00:00'))
    # print(get_data_HORUS.get_price_15m('BTC', '2025-9-1 08:00', '2025-11-10 23:42'))

    # df_run = get_data_4h(get_data_HORUS.get_price_15m('BTC', '2025-10-1 08:00', '2025-10-9 08:01'))
    # print(run_strategy(df_run, decide_strategy(df_test)))
    # print(strategy_time())


