import requests
from loguru import logger


# 发送HTTP请求并处理响应
def send_request(url, data, headers):
    response = requests.post(url, data=data, headers=headers)
    logger.info(f"send_request Response Code: {response.status_code}, Response Body: {response.text}")

    if response.status_code != 200:
        raise Exception(f"Request failed with status code {response.status_code}")

    return response.json()


# 发送HTTP请求返回状态码
def send_request_status(url, data=None, headers=None, method="POST"):
    # 根据方法发送请求
    if method.upper() == "GET":
        response = requests.get(url, params=data, headers=headers)
    elif method.upper() == "POST":
        response = requests.post(url, data=data, headers=headers)
    else:
        # 如果传入的方法不是GET或POST，可以在这里扩展更多的HTTP方法
        logger.error(f"Unsupported method: {method}")
        return None

    # 记录响应状态码
    logger.info(f"send_request_status Response Code: {response.status_code}")

    return response.status_code