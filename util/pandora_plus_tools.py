from datetime import datetime, timedelta

import requests
from loguru import logger

from model import db, Token, Account
from util.request_tools import send_request
from util.share_tools import gen_share_token

# oaifree 获取Access Token
TOKEN_URL = "https://token.oaifree.com/api/auth/refresh"
# 订阅检查
SUBSCRIPTION_CHECK_URL = "https://chat.oaifree.com/dad04481-fa3f-494e-b90c-b822128073e5/backend-api/models?history_and_training_disabled=false"


# 发送请求并解析响应以刷新Access Token
def gen_access_token(refresh_token):
    if not refresh_token:
        raise ValueError("Refresh token is empty")

    req_data = {"refresh_token": refresh_token}
    headers = {"Content-Type": "application/x-www-form-urlencoded"}

    res = send_request(TOKEN_URL, req_data, headers)

    access_token = res.get("access_token")
    if not access_token:
        raise Exception("Get access token failed, the access token is empty")

    return res


# 检查订阅状态
def check_subscription_status(access_token):
    if not access_token:
        raise ValueError("Access token is empty")
    headers = {
        "Content-Type": "application/json",
        "Authorization": f'Bearer {access_token}'
    }

    response = requests.get(SUBSCRIPTION_CHECK_URL, None, headers=headers)

    if response.status_code != 200 and response.status_code != 401:
        logger.info(f"check_subscription_status: 1, because of status code {response.status_code}")
        return 1
    elif response.status_code == 401:
        logger.info(f"check_subscription_status: 2, because of status code {response.status_code}")
        return 2

    # 检查返回的json数据
    res = response.json()
    if not res:
        logger.info(f"check_subscription_status: 1, because of empty response body")
        return 1

    # 判断是否存在slug为"gpt-4"的项
    subscribe_plus = any(model['slug'] == 'gpt-4' for model in res['models'])
    if subscribe_plus:
        logger.info(f"check_subscription_status: 3, because of gpt-4 model found in response body")
        return 3
    else:
        logger.info(f"check_subscription_status: 2, because of no gpt-4 model found in response body")
        return 2


# 刷新Access Token
def refresh_by_token(token):
    try:
        res = gen_access_token(token.refresh_token)
    except Exception as e:
        logger.error(e)
        raise Exception("获取Access Token失败")

    token.access_token = res.get('access_token')
    token.expire_at = datetime.now() + timedelta(seconds=res.get('expires_in'))
    token.update_time = datetime.now()
    db.session.commit()

    # 刷新关联的share_token
    accounts = db.session.query(Account).filter_by(token_id=token.id).all()
    if not accounts:
        return
    for account in accounts:
        if account.status == 0:
            continue
        try:
            res = gen_share_token(access_token=token.access_token,
                                  unique_name=account.account,
                                  gpt35_limit=account.gpt35_limit,
                                  gpt4_limit=account.gpt4_limit,
                                  show_conversations=account.show_conversations == 1,
                                  temporary_chat=account.temporary_chat == 1)
            expire_at = datetime.fromtimestamp(res.get('expire_at'))
            # 检查expire_at的类型是否正确
            if not isinstance(expire_at, datetime):
                raise TypeError(f"Expected datetime.datetime, got {type(expire_at)} instead.")

            account.share_token = res.get('token_key')
            account.expire_at = expire_at
            account.update_time = datetime.now()
        except Exception as e:
            logger.error(e)

    db.session.commit()


# 刷新订阅状态
def refresh_subscription_status(token_id):
    token = db.session.query(Token).filter_by(id=token_id).first()
    if not token:
        raise Exception('Token不存在')

    try:
        plus_subscription = check_subscription_status(token.access_token)
    except Exception as e:
        logger.error(e)
        raise Exception('检查订阅状态失败')

    token.plus_subscription = plus_subscription

    db.session.commit()


# 禁用账号
def disable_by_token_id(token_id):
    token = db.session.query(Token).filter_by(id=token_id).first()

    if not token:
        logger.error('Token不存在')

    # 关联的account
    accounts = db.session.query(Account).filter_by(token_id=token_id).all()
    if not accounts:
        return
    now = datetime.now()
    for account in accounts:
        # 如果账号已禁用或者未过期，则跳过
        if account.status == 0 or account.expiration_time > now:
            continue
        try:
            logger.info(f"开始禁用账号: {account.account}")
            res = gen_share_token(access_token=token.access_token,
                                  unique_name=account.account,
                                  expires_in=-1,
                                  gpt35_limit=account.gpt35_limit,
                                  gpt4_limit=account.gpt4_limit,
                                  show_conversations=account.show_conversations == 1,
                                  temporary_chat=account.temporary_chat == 1)
            logger.info(res)
            logger.info(f"禁用账号成功: {account.account}")
        except Exception as e:
            logger.error(f"禁用账号失败: {account.account}", e)
            return

        now = datetime.now()
        account.status = 0
        account.expiration_time = now
        account.expire_at = now
        account.update_time = now
        logger.info(account)
        db.session.commit()

