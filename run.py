from final import *
import get_data_HORUS
import get_date_Roostoo
import buy_and_sell_Roostoo

strategy = 'MOM'
position = 0
last_hour = -1

while True:
    if strategy_time() is not None:
        data = get_data_12h(get_data_HORUS.get_price_15m('BTC', strategy_time()[1], strategy_time()[0]))
        data[strategy_time()[0]] = get_date_Roostoo.get_btc_price()
        if strategy_decision_time() == 1:
            strategy = decide_strategy(data)
            print(f'策略选择成功，目前的策略是{strategy}')
        position = run_strategy(data, strategy)
        print(f'交易决策已生成，目前的头寸是{position}')

        if position == 0:
            buy_and_sell_Roostoo.full_btc_sell()
        else:
            buy_and_sell_Roostoo.full_btc_buy()

    current_time = time.localtime()
    current_hour = current_time.tm_hour  # 当前小时（0-23）
    current_min = current_time.tm_min  # 当前分钟（0-59）
    current_sec = current_time.tm_sec  # 当前秒数（0-59）
    if current_min == 0 and current_sec == 0 and current_hour != last_hour:
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 程序正常运行中")
        last_hour = current_hour