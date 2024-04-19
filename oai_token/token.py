from datetime import datetime, timedelta

from flask import Blueprint, request
from flask_jwt_extended import jwt_required
from loguru import logger

from model import db, Token
from util.api_response import ApiResponse
from util.pandora_plus_tools import gen_access_token
from util.pandora_plus_token_tools import refresh_by_token_id

token_bp = Blueprint('token_bp', __name__)


@jwt_required()
@token_bp.route('/list')
def account_list():
    accounts = db.session.query(Token).all()
    return ApiResponse.success(accounts)


@token_bp.route('/search', methods=['POST'])
@jwt_required()
def account_search():
    token_name = request.json.get('token_name') if request.json.get('token_name') else ''
    tokens = db.session.query(Token).filter(Token.token_name.like(f'%{token_name}%')).all()
    return ApiResponse.success(tokens)


@token_bp.route('/add', methods=['POST'])
@jwt_required()
def account_add():
    refresh_token = request.json.get('refresh_token')
    token_name = request.json.get('token_name')
    try:
        res = gen_access_token(refresh_token)
    except Exception as e:
        logger.error(e)
        return ApiResponse.error("获取Access Token失败")

    now = datetime.now()
    expire_at = now + timedelta(seconds=res.get('expires_in'))

    token = Token(
        token_name=token_name,
        refresh_token=refresh_token,
        access_token=res.get('access_token'),
        expire_at=expire_at,
        create_time=now,
        update_time=now
    )

    logger.info(token)

    db.session.add(token)
    db.session.commit()

    return ApiResponse.success({})


@token_bp.route('/update', methods=['POST'])
@jwt_required()
def account_update():
    token_id = request.json.get('id')
    refresh_token = request.json.get('refresh_token')
    token_name = request.json.get('token_name')

    token = db.session.query(Token).filter_by(id=token_id).first()

    try:
        res = gen_access_token(refresh_token)
    except Exception as e:
        logger.error(e)
        return ApiResponse.error("获取Access Token失败")

    token.token_name = token_name
    token.refresh_token = refresh_token
    token.access_token = res.get('access_token')
    token.expire_at = datetime.now() + timedelta(seconds=res.get('expires_in'))
    token.update_time = datetime.now()

    db.session.commit()

    return ApiResponse.success({})


@token_bp.route('/delete', methods=['POST'])
@jwt_required()
def account_delete():
    token_id = request.json.get('id')
    token = db.session.query(Token).filter_by(id=token_id).first()
    db.session.delete(token)
    db.session.commit()
    return ApiResponse.success({})


@token_bp.route('/refresh', methods=['POST'])
@jwt_required()
def account_refresh():
    token_id = request.json.get('id')
    try:
        refresh_by_token_id(token_id)
    except Exception as e:
        return ApiResponse.error(str(e))

    return ApiResponse.success('刷新成功')


def refresh_all_user():
    from app import scheduler
    flag = False
    with scheduler.app.app_context():
        tokens = db.session.query(Token).all()

        for token in tokens:
            try:
                # 检查 rt 是否存在
                if not token.refresh_token:
                    continue
                # 判断at是否过期
                if token.expire_at > datetime.now():
                    continue
                flag = True
                refresh_by_token_id(token.id)
            except Exception as e:
                logger.error(e)
        if flag:
            logger.info('刷新成功')


@token_bp.route('/start', methods=['post'])
@jwt_required()
def refresh_task():
    from app import scheduler
    scheduler.add_job(func=refresh_all_user, trigger='interval', minutes=1, id='token_job')
    if not scheduler.running:
        scheduler.start()
    return ApiResponse.success('定时刷新已开启')


@token_bp.route('/stop', methods=['post'])
@jwt_required()
def kill_refresh_task():
    from app import scheduler
    scheduler.remove_job(id='token_job')
    return ApiResponse.success('定时刷新已关闭')


@token_bp.route('/task_status')
@jwt_required()
def refresh_status():
    from app import scheduler
    if scheduler.running and scheduler.get_job(id='token_job'):
        return ApiResponse.success({'status': True})
    else:
        return ApiResponse.success({'status': False})
