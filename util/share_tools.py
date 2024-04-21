import requests
import json
from loguru import logger
from util.request_tools import send_request

SHARE_TOKEN_URL = "https://chat.oaifree.com/token/register"
SHARE_TOKEN_AUTH = None
SHARE_TOKEN_AUTH_URL = None


def set_share_token_auth(share_token_auth):
    global SHARE_TOKEN_AUTH, SHARE_TOKEN_AUTH_URL
    SHARE_TOKEN_AUTH = share_token_auth
    SHARE_TOKEN_AUTH_URL = f"{SHARE_TOKEN_AUTH}/api/auth/oauth_token"


# 获取share_token
def gen_share_token(access_token, unique_name, expires_in=0, show_conversations=False, show_userinfo=True,
                    reset_limit=True):
    req_data = {
        "unique_name": unique_name,
        "access_token": access_token,
        "expires_in": expires_in,
        "site_limit": "",
        "gpt35_limit": "-1",
        "gpt4_limit": "-1",
        "show_conversations": show_conversations,
        "show_userinfo": show_userinfo,
        "reset_limit": reset_limit,
    }
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    share_token = send_request(SHARE_TOKEN_URL, req_data, headers)
    if not share_token:
        raise Exception("Get share token failed, the share token is empty")
    return share_token


# 获取share_token的信息
# 若access_token 不为空，则返回的信息中包含share_token的详细用量信息
def get_share_token_info(share_token, access_token=None):
    headers = {}
    if access_token:
        headers = {
            'Authorization': f'Bearer {access_token}'
        }
    url = f'https://chat.oaifree.com/token/info/{share_token}'
    response = requests.request("GET", url, headers=headers, data={})
    logger.info("获取share_token信息结果：{}", response.json())
    return response.json()


# 使用share_token登录
def share_token_login(share_token):
    req_data = {
        "share_token": share_token,
    }
    headers = {"Content-Type": "application/json", "Origin": SHARE_TOKEN_AUTH}
    res = send_request(SHARE_TOKEN_AUTH_URL, json.dumps(req_data), headers)
    if not res:
        raise Exception("Login with share token failed, the response is empty")
    return res
