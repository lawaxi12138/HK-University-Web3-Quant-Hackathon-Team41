import requests
import time
import pandas as pd
import numpy as np

# 配置核心参数
API_KEY = "62ebcce5fbdeec5374f83899bd2b1b9284fde14c5935caabc846c16ab176209b"
BASE_URL = "https://api-horus.com/market/price"

def get_price_1d(asset: str, start_time: str, end_time: str, api_key=API_KEY) -> pd.DataFrame:

    # 时间范围（转换为秒级时间戳）
    start_time = int(time.mktime(time.strptime(start_time, "%Y-%m-%d")))
    end_time = int(time.mktime(time.strptime(end_time, "%Y-%m-%d")))

    # 请求参数
    params = {
        "asset": asset,  # 资产标识
        "interval": "1d",  # 时间间隔：1天（可选1d/1h/15m，此处按日获取）
        "start": start_time,  # 开始时间戳（秒级，含）
        "end": end_time,  # 结束时间戳（秒级，不含）
        "format": "json"  # 返回格式（默认json，可选csv）
    }

    # 请求头（必须携带API密钥）
    headers = {
        "X-API-Key": api_key
    }

    # 发送GET请求
    try:
        response = requests.get(BASE_URL, params=params, headers=headers)
        response.raise_for_status()  # 抛出HTTP请求异常（如401、404等）

        # 解析响应数据
        raw_data = response.json()

        # 转换为DataFrame并处理格式
        df = pd.DataFrame(raw_data)

        # 时间戳转换为日期格式（YYYY-MM-DD），并设为索引
        df["date"] = pd.to_datetime(df["timestamp"], unit="s").dt.strftime("%Y-%m-%d")
        df = df.set_index("date")

        # 筛选目标列并命名（价格单位USD）
        df = df[["price"]]

        # 去除重复索引（若存在）
        df = df.drop_duplicates()

        return df

    except requests.exceptions.RequestException as e:
        print(f"请求失败：{str(e)}")
        if response.status_code == 401:
            print("提示：请检查API密钥是否有效或未填写")

def get_price_15m(asset: str, start_time: str, end_time: str, api_key=API_KEY) -> pd.DataFrame:

    # -------------------------- 关键修改1：时间格式适配15分钟级 --------------------------
    # 原日度只需要日期（%Y-%m-%d），15分钟级需要精确到时分（建议格式：%Y-%m-%d %H:%M）
    # 示例输入：start_time="2025-01-01 00:00", end_time="2025-01-02 00:00"
    start_time = int(time.mktime(time.strptime(start_time, "%Y-%m-%d %H:%M")))
    end_time = int(time.mktime(time.strptime(end_time, "%Y-%m-%d %H:%M")))

    # 请求参数
    params = {
        "asset": asset,  # 资产标识
        # -------------------------- 关键修改2：时间间隔改为15m --------------------------
        "interval": "15m",  # 时间间隔：15分钟（原1d）
        "start": start_time,  # 开始时间戳（秒级，含）
        "end": end_time,  # 结束时间戳（秒级，不含）
        "format": "json"  # 返回格式（默认json，可选csv）
    }

    # 请求头（必须携带API密钥）
    headers = {
        "X-API-Key": api_key
    }

    # 发送GET请求
    try:
        response = requests.get(BASE_URL, params=params, headers=headers)
        response.raise_for_status()  # 抛出HTTP请求异常（如401、404等）

        # 解析响应数据
        raw_data = response.json()

        # 转换为DataFrame并处理格式
        df = pd.DataFrame(raw_data)

        # -------------------------- 关键修改3：时间格式保留时分秒 --------------------------
        # 15分钟级需要保留「年月日 时分」（如2025-01-01 00:15），而非仅日期
        df["datetime"] = pd.to_datetime(df["timestamp"], unit="s").dt.strftime("%Y-%m-%d %H:%M")
        df = df.set_index("datetime")  # 用精确时间作为索引

        # 筛选目标列并命名（价格单位USD）
        df = df[["price"]]

        # 去除重复索引（15分钟级可能出现重复数据，保留第一条）
        df = df.drop_duplicates(keep="first")

        return df

    except requests.exceptions.RequestException as e:
        print(f"请求失败：{str(e)}")
        # 避免response未定义时报错（添加判断）
        if 'response' in locals() and response.status_code == 401:
            print("提示：请检查API密钥是否有效或未填写")
        return pd.DataFrame()  # 异常时返回空DataFrame，避免后续报错




if __name__ == '__main__':
    df = get_price_15m("BTC", "2025-09-01", "2025-11-01")
    print(df)

    # 15分钟级数据：需要传入精确到时分的时间（示例：2025年1月1日0点到1月1日1点）
    df = get_price_15m(
        asset="BTC",
        start_time="2025-01-01 00:00",
        end_time="2025-01-01 01:00"
    )
    print("15分钟级价格数据：")
    print(df.head(10))