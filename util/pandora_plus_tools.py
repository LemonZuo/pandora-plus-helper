import json
from datetime import datetime, timedelta
from model import db, Token, Account
from util.share_tools import gen_share_token
from loguru import logger
from util.request_tools import send_request, send_request_status

# oaifree 获取Access Token
TOKEN_URL = "https://token.oaifree.com/api/auth/refresh"
# 对话URL
CONVERSATION_URL = "https://api.oaifree.com/v1/chat/completions"


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
    req_data = {
        "model": "gpt-3.5-turbo",
        "messages": [
            {
                "role": "user",
                "content": "重复我说的话：我，V，谨庄严宣誓。"
            }
        ],
        "temperature": 0.7
    }

    headers = {
        "Content-Type": "application/json",
        "Authorization": f'Bearer {access_token}'
    }
    subscription_status = send_request_status(CONVERSATION_URL, json.dumps(req_data), headers)
    if not subscription_status:
        raise Exception("Check subscription status failed, the response is empty")

    if subscription_status == 200:
        return 1
    else:
        return 0


# 刷新Access Token
def refresh_by_token_id(token_id):
    token = db.session.query(Token).filter_by(id=token_id).first()

    if not token:
        raise Exception('Token不存在')

    try:
        res = gen_access_token(token.refresh_token)
    except Exception as e:
        logger.error(e)
        raise Exception("获取Access Token失败")

    try:
        plus_subscription = check_subscription_status(res.get('access_token'))
    except Exception as e:
        logger.error(e)
        raise Exception('检查订阅状态失败')

    token.plus_subscription = plus_subscription
    token.access_token = res.get('access_token')
    token.expire_at = datetime.now() + timedelta(seconds=res.get('expires_in'))
    token.update_time = datetime.now()
    db.session.commit()

    # 刷新关联的share_token
    accounts = db.session.query(Account).filter_by(token_id=token_id).all()
    if not accounts:
        return
    for account in accounts:
        try:
            res = gen_share_token(access_token=token.access_token, unique_name=account.account,
                                  gpt35_limit=account.gpt35_limit, gpt4_limit=account.gpt4_limit,
                                  show_conversations=account.show_conversations)
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
