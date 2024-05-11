import datetime

import requests
from flask import request, current_app, Blueprint, Flask, jsonify
from flask_jwt_extended import create_access_token
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from loguru import logger

from model import db, Account
from util.api_response import ApiResponse
from util.share_tools import share_token_login

auth_bp = Blueprint("auth", __name__)
app = Flask(__name__)
limiter = Limiter(
    app,
    key_func=get_remote_address,  # 使用客户端IP作为限流的键
    default_limits=["50 per day", "25 per hour"]
)


def validate_hcaptcha_response(token):
    secret_key = current_app.config['captcha_secret_key']
    verify_url = "https://api.hcaptcha.com/siteverify"
    payload = {
        'secret': secret_key,
        'response': token
    }
    r = requests.post(verify_url, data=payload)
    result = r.json()
    return result['success']


# 自定义429错误响应
@auth_bp.errorhandler(429)
def ratelimit_handler(e):
    return jsonify({"status": 429, "message": "request too frequently, please wait!!!"}), 429


# 使用Jwt登录
@auth_bp.route('/auth', methods=['POST'])
@limiter.limit("5 per minute")
def auth():
    password = request.json.get('password')
    token = request.json.get('token')
    type = request.json.get('type')
    if current_app.config['captcha_enabled'] and not validate_hcaptcha_response(token):
        return ApiResponse.error('Captcha is failed', 401)

    if type == 1:
        account = db.session.query(Account).filter_by(password=password, status=1).first()
        if not account:
            # 账号不存在
            return ApiResponse.error('login failed！', 401)
        else:
            res = share_token_login(account.share_token)
            login_url = res.get('login_url')
            if not login_url:
                logger.error('login failed！, login_url is None')
                return ApiResponse.error('login failed！', 401)
            return ApiResponse.success(data={'type': 1, 'access_token': None, 'user': None, 'login_url': login_url})
    elif type == 2:
        admin_password = current_app.config['admin_password']
        if password == admin_password:
            user = {
                'id': 1,
                'username': 'admin',
                'email': 'admin@uasm.com',
                'role': ADMIN_ROLE,
                'status': 1,
                'permissions': PERMISSION_LIST,
            }
            access_token = create_access_token(identity='admin', expires_delta=datetime.timedelta(days=3))
            return ApiResponse.success(data={'type': 2, 'access_token': access_token, 'user': user, 'login_url': None})
        else:
            return ApiResponse.error('login failed！', 401)

DASHBOARD_PERMISSION = {
    'id': '9710971640510357',
    'parentId': '',
    'label': 'sys.menu.analysis',
    'name': 'Analysis',
    'type': 1,
    'route': 'home',
    'icon': 'ic-analysis',
    'order': 1,
    'component': '/dashboard/analysis/index.tsx',
}

TOKEN_PERMISSION = {
    'id': '9100714781927721',
    'parentId': '',
    'label': 'sys.menu.token',
    'name': 'Token',
    'icon': 'ph:key',
    'type': 0,
    'route': 'token',
    'order': 2,
    'children': [
        {
            'id': '84269992294009655',
            'parentId': '9100714781927721',
            'label': 'sys.menu.token-management',
            'name': 'Token',
            'type': 1,
            'route': 'token',
            'component': '/token/token/index.tsx',
        },
        {
            'id': '84269992294009656',
            'parentId': '9100714781927721',
            'hide': False,
            'label': 'sys.menu.account-management',
            'name': 'Account',
            'type': 1,
            'route': 'account',
            'component': '/token/account/index.tsx',
        }
    ],
}

PERMISSION_LIST = [
    DASHBOARD_PERMISSION,
    TOKEN_PERMISSION,
]

ADMIN_ROLE = {
    'id': '4281707933534332',
    'name': 'Admin',
    'label': 'Admin',
    'status': 1,
    'order': 1,
    'desc': 'Super Admin',
    'permission': PERMISSION_LIST,
}
