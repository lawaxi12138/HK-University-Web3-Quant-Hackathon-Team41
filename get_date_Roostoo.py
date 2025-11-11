import requests
import time

BASE_URL = "https://mock-api.roostoo.com"

def get_btc_price():
    # 生成 13 位毫秒时间戳
    timestamp = int(time.time() * 1000)
    params = {
        "timestamp": timestamp,
        "pair": "BTC/USD"  # 指定比特币对美元的交易对
    }
    try:
        response = requests.get(f"{BASE_URL}/v3/ticker", params=params)
        response.raise_for_status()  # 检查请求是否成功
        data = response.json()
        if data.get("Success"):
            # 提取最新价格（LastPrice）
            btc_data = data["Data"].get("BTC/USD")
            if btc_data:
                return btc_data["LastPrice"]
            else:
                return "未找到 BTC/USD 数据"
        else:
            return f"请求失败：{data.get('ErrMsg')}"
    except Exception as e:
        return f"错误：{str(e)}"

if __name__ == '__main__':
    # 调用函数获取价格
    print(f"当前 BTC 价格：{get_btc_price()} USD")