import requests
from loguru import logger


# 发送HTTP请求并处理响应
def send_request(url, data, headers):
    response = requests.post(url, data=data, headers=headers)
    logger.info(f"Response Code: {response.status_code}, Response Body: {response.text}")

    if response.status_code != 200:
        raise Exception(f"Request failed with status code {response.status_code}")

    return response.json()