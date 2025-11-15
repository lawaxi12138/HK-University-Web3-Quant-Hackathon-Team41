import requests
import time
import hmac
import hashlib

API_KEY = "x3K8tL1wP5bT2oN9gY4mH6kV7fR1lS5nC0aJ8uM4eD2pI7yW3qX0zB9jN6vF0s"
SECRET = "V2bN0mQwE5rT7yUiP1oA3sDdF6gJ8hKlZ4xC9vBnM0qW2eRtY7uI5oPaS3dF1gHj"
BASE_URL = "https://mock-api.roostoo.com"


def generate_signature(params):
    """生成请求签名"""
    query_string = '&'.join([f"{k}={params[k]}" for k in sorted(params.keys())])
    return hmac.new(
        SECRET.encode('utf-8'),
        query_string.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()


def get_btc_balance():
    """获取比特币可用余额"""
    payload = {"timestamp": int(time.time()) * 1000}
    headers = {
        "RST-API-KEY": API_KEY,
        "MSG-SIGNATURE": generate_signature(payload)
    }

    try:
        response = requests.get(
            f"{BASE_URL}/v3/balance",
            params=payload,
            headers=headers
        )
        response.raise_for_status()
        data = response.json()
        if data.get("Success"):
            return data["SpotWallet"].get("BTC", {}).get("Free", 0.0)
        return 0.0
    except Exception as e:
        print(f"获取比特币余额失败: {e}")
        return 0.0


def get_usd_balance():
    """获取美元可用余额"""
    payload = {"timestamp": int(time.time()) * 1000}
    headers = {
        "RST-API-KEY": API_KEY,
        "MSG-SIGNATURE": generate_signature(payload)
    }

    try:
        response = requests.get(
            f"{BASE_URL}/v3/balance",
            params=payload,
            headers=headers
        )
        response.raise_for_status()
        data = response.json()
        if data.get("Success"):
            return data["SpotWallet"].get("USD", {}).get("Free", 0.0)
        return 0.0
    except Exception as e:
        print(f"获取美元余额失败: {e}")
        return 0.0


def get_btc_price():
    """获取当前比特币最新价格"""
    payload = {"timestamp": int(time.time()) * 1000, "pair": "BTC/USD"}
    try:
        response = requests.get(
            f"{BASE_URL}/v3/ticker",
            params=payload
        )
        response.raise_for_status()
        data = response.json()
        if data.get("Success"):
            return data["Data"]["BTC/USD"]["LastPrice"]
        return 0.0
    except Exception as e:
        print(f"获取比特币价格失败: {e}")
        return 0.0


def full_btc_buy():
    """全仓买入比特币（使用所有可用美元）"""
    # 获取可用美元余额
    usd_balance = get_usd_balance()
    if usd_balance <= 0:
        print("没有可用美元余额用于购买")
        return

    # 获取当前比特币价格
    btc_price = get_btc_price()
    if btc_price <= 0:
        print("无法获取有效比特币价格")
        return

    # 计算可购买数量（扣除少量手续费预留）
    quantity = (usd_balance * 0.999) / btc_price  # 预留0.1%作为手续费缓冲

    # 下单
    payload = {
        "timestamp": int(time.time()) * 1000,
        "pair": "BTC/USD",
        "side": "BUY",
        "quantity": quantity,
        "type": "MARKET"
    }

    headers = {
        "RST-API-KEY": API_KEY,
        "MSG-SIGNATURE": generate_signature(payload),
        "Content-Type": "application/x-www-form-urlencoded"
    }

    try:
        response = requests.post(
            f"{BASE_URL}/v3/place_order",
            data=payload,
            headers=headers
        )
        print(f"全仓买入响应: {response.status_code} {response.text}")
        return response.json()
    except Exception as e:
        print(f"全仓买入失败: {e}")
        return None


def full_btc_sell():
    """全仓卖出所有比特币"""
    # 获取可用比特币余额
    btc_balance = get_btc_balance()
    if btc_balance <= 0:
        print("没有可用比特币用于卖出")
        return

    # 下单
    payload = {
        "timestamp": int(time.time()) * 1000,
        "pair": "BTC/USD",
        "side": "SELL",
        "quantity": btc_balance,
        "type": "MARKET"
    }

    headers = {
        "RST-API-KEY": API_KEY,
        "MSG-SIGNATURE": generate_signature(payload),
        "Content-Type": "application/x-www-form-urlencoded"
    }

    try:
        response = requests.post(
            f"{BASE_URL}/v3/place_order",
            data=payload,
            headers=headers
        )
        print(f"全仓卖出响应: {response.status_code} {response.text}")
        return response.json()
    except Exception as e:
        print(f"全仓卖出失败: {e}")
        return None


# 使用示例
if __name__ == "__main__":
    full_btc_buy()