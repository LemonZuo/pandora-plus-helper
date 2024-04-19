import requests
import json
from flask import current_app

# 官方接口地址
AUTH0_TOKEN_URL = "https://auth0.openai.com/oauth/token"

# 始皇代理接口地址
MIRROR_TOKEN_URL = "https://token.oaifree.com/api/auth/refresh"

# 是否使用代理
USE_MIRROR = True

SHARE_TOKEN_URL = "https://chat.oaifree.com/token/register"
SHARE_TOKEN_AUTH = ''
SHARE_TOKEN_AUTH_URL = ''


def set_share_token_auth(share_token_auth):
    global SHARE_TOKEN_AUTH, SHARE_TOKEN_AUTH_URL  # 声明这些变量为全局变量
    SHARE_TOKEN_AUTH = share_token_auth
    SHARE_TOKEN_AUTH_URL = f"{SHARE_TOKEN_AUTH}/api/auth/oauth_token"  # 更新URL


# 发送HTTP请求并处理响应
def send_request(url, data, headers):
    response = requests.post(url, data=data, headers=headers)
    print(f"Status Code: {response.status_code}")
    print(f"Response Body: {response.text}")

    if response.status_code != 200:
        raise Exception(f"Request failed with status code {response.status_code}")

    return response.json()


# 通过官方接口刷新Token
def refresh_token_using_auth0(refresh_token):
    req_data = {
        "grant_type": "refresh_token",
        "client_id": "pdlLIX2Y72MIl2rhLhTE9VV9bN905kBh",
        "refresh_token": refresh_token,
        "redirect_uri": "com.openai.chat://auth0.openai.com/ios/com.openai.chat/callback"
    }
    headers = {"Content-Type": "application/json"}
    return send_request(AUTH0_TOKEN_URL, json.dumps(req_data), headers)


# 通过镜像接口刷新Token
def refresh_token_using_mirror(refresh_token):
    req_data = {"refresh_token": refresh_token}
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    return send_request(MIRROR_TOKEN_URL, req_data, headers)


# 发送请求并解析响应以刷新Access Token
def gen_access_token(refresh_token):
    if not refresh_token:
        raise ValueError("Refresh token is empty")

    if USE_MIRROR:
        res = refresh_token_using_mirror(refresh_token)
    else:
        res = refresh_token_using_auth0(refresh_token)

    access_token = res.get("access_token")
    if not access_token:
        raise Exception("Get access token failed, the access token is empty")

    return res


# 生成share_token
def gen_share_token(access_token, unique_name):
    req_data = {
        "unique_name": unique_name,
        "access_token": access_token,
        "expires_in": 0,
        "site_limit": "",
        "gpt35_limit": "-1",
        "gpt4_limit": "-1",
        "show_conversations": False,
        "reset_limit": True,
    }
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    share_token = send_request(SHARE_TOKEN_URL, req_data, headers)
    if not share_token:
        raise Exception("Get share token failed, the share token is empty")
    return share_token


def share_token_login(share_token):
    req_data = {
        "share_token": share_token,
    }
    headers = {"Content-Type": "application/json", "Origin": SHARE_TOKEN_AUTH}
    res = send_request(SHARE_TOKEN_AUTH_URL, json.dumps(req_data), headers)
    if not res:
        raise Exception("Login with share token failed, the response is empty")
    return res

