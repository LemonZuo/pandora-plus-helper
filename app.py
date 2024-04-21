import json
import os
import string
import secrets
from loguru import logger
from datetime import date, datetime

from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from dotenv import load_dotenv
from flask import Flask
from flask.json.provider import JSONProvider
from flask_apscheduler import APScheduler
from flask_bootstrap import Bootstrap5
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate, upgrade
from flask_moment import Moment

import oai_token
import account
import sys_info
from util.api_response import ApiResponse
from util.share_tools import set_share_token_auth

# 加载当前目录下的 .env 文件
load_dotenv()

DATABASE = 'pandora-plus-helper.db'

app = Flask(__name__, static_folder='frontend/dist', static_url_path='/')
Bootstrap5(app)
Moment().init_app(app)
# 生成随机的secret_key
app.secret_key = secrets.token_hex(16)
jwt = JWTManager(app)


@jwt.unauthorized_loader
def custom_unauthorized_callback(error_string):
    return ApiResponse.unauthorized(error_string, )


@jwt.invalid_token_loader
def custom_invalid_token_callback(error_string):
    return ApiResponse.unauthorized(error_string, )


@jwt.expired_token_loader
def custom_expired_token_callback(error_string, expired_token):
    return ApiResponse.unauthorized(error_string, )


def generate_random_password(length=12):
    if length < 3:
        raise ValueError("Password length must be at least 3 characters to include at least one lowercase, one uppercase, and one digit.")

    # 确保密码中至少包含一个大写字母、一个小写字母和一个数字
    characters = [
        secrets.choice(string.ascii_uppercase),  # 大写字母
        secrets.choice(string.ascii_lowercase),  # 小写字母
        secrets.choice(string.digits)  # 数字
    ]

    # 如果长度大于3，添加其他随机字符来填充密码
    if length > 3:
        all_characters = string.ascii_letters + string.digits
        characters.extend(secrets.choice(all_characters) for _ in range(length - 3))

    # 随机打乱字符顺序以避免可预测性
    secrets.SystemRandom().shuffle(characters)

    # 将字符列表转换为字符串
    random_password = ''.join(characters)
    return random_password


def check_require_config():
    DATA_DIR = os.getenv('DATA_DIR')
    if not DATA_DIR:
        DATA_DIR = "/data"
    ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD')
    if not ADMIN_PASSWORD:
        ADMIN_PASSWORD = generate_random_password(12)
        logger.warning(f"ADMIN_PASSWORD is not set, generate a random password: {ADMIN_PASSWORD}")
    SHARE_TOKEN_AUTH= os.getenv('SHARE_TOKEN_AUTH')
    if not SHARE_TOKEN_AUTH:
        SHARE_TOKEN_AUTH = "https://new.oaifree.com"

    # 设置share_token 认证登录的URL
    set_share_token_auth(SHARE_TOKEN_AUTH)

    app.config.update(
        data_dir=DATA_DIR,
        admin_password=ADMIN_PASSWORD,
        license_id='',
        captcha_enabled=False,
    )


from auth import auth
from model import db

check_require_config()

# scheduler jobstore
app.config['SCHEDULER_JOBSTORES'] = {
    'default': SQLAlchemyJobStore(url='sqlite:///' + os.path.join(app.config['data_dir'], DATABASE))
}
scheduler = APScheduler()
scheduler.init_app(app)
scheduler.start()

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(app.config['data_dir'], DATABASE)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
db.init_app(app)


def include_object(object, name, type_, reflected, compare_to):
    if (
            type_ == "table" and name == "apscheduler_jobs"
    ):
        return False
    else:
        return True


migrate = Migrate(include_object=include_object)
migrate.init_app(app, db)


def format_datetime(value):
    """Format a datetime to a string."""
    if value is None:
        return ""
    return value.strftime('%Y-%m-%d %H:%M:%S')


class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, datetime):
            return o.strftime('%Y-%m-%d %H:%M:%S')
        elif isinstance(o, date):
            return o.strftime('%Y-%m-%d')
        elif hasattr(o, 'keys') and hasattr(o, '__getitem__'):
            return dict(o)
        raise TypeError(f'Object of type {o.__class__.__name__} '
                        f'is not JSON serializable')


class StandardJSONProvider(JSONProvider):
    def dumps(self, obj, **kwargs):
        # 使用自定义的JSON编码器进行序列化
        return json.dumps(obj, cls=JSONEncoder, **kwargs)

    def loads(self, s, **kwargs):
        return json.loads(s, **kwargs)


app.json = StandardJSONProvider(app)


@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):
    return app.send_static_file("index.html")


def create_app():
    app.register_blueprint(auth.auth_bp, url_prefix='/api')
    app.register_blueprint(oai_token.token_bp, url_prefix='/api/token')
    app.register_blueprint(account.account_bp, url_prefix='/api/account')
    app.register_blueprint(sys_info.sys_info_bp, url_prefix='/api/sys_info')
    app.jinja_env.filters['datetime'] = format_datetime
    # 迁移应在应用上下文内进行
    with app.app_context():
        upgrade()
    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
