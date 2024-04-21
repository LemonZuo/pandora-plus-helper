from datetime import datetime, timedelta
from model import db, Token, Account
from util.share_tools import gen_share_token
from loguru import logger
from util.request_tools import send_request

# oaifree 获取Access Token
TOKEN_URL = "https://token.oaifree.com/api/auth/refresh"


def refresh_by_token_id(token_id):
    token = db.session.query(Token).filter_by(id=token_id).first()

    if not token:
        raise Exception('Token不存在')

    res = gen_access_token(token.refresh_token)
    if not res:
        raise Exception('刷新失败')

    token.access_token = res.get('access_token')
    token.expire_at = datetime.now() + timedelta(seconds=res.get('expires_in'))
    token.update_time = datetime.now()

    # 刷新关联的share_token
    accounts = db.session.query(Account).filter_by(token_id=token_id).all()
    if not accounts:
        return
    for account in accounts:
        try:
            res = gen_share_token(token.access_token, account.account)
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

