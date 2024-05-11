from datetime import datetime, timedelta

from flask import Blueprint, request
from flask_jwt_extended import jwt_required
from loguru import logger

from model import db, Token, Account
from util.api_response import ApiResponse
from util.pandora_plus_tools import gen_access_token, refresh_by_token, check_subscription_status, refresh_subscription_status

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

    try:
        plus_subscription = check_subscription_status(res.get('access_token'))
    except Exception as e:
        logger.error(e)
        return ApiResponse.error("检查订阅状态失败")

    now = datetime.now()
    expire_at = now + timedelta(seconds=res.get('expires_in'))

    token = Token(
        token_name=token_name,
        plus_subscription=plus_subscription,
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

    try:
        plus_subscription = check_subscription_status(res.get('access_token'))
    except Exception as e:
        logger.error(e)
        return ApiResponse.error("检查订阅状态失败")

    token.token_name = token_name
    token.plus_subscription = plus_subscription
    token.refresh_token = refresh_token
    token.access_token = res.get('access_token')
    token.expire_at = datetime.now() + timedelta(seconds=res.get('expires_in'))
    token.update_time = datetime.now()

    db.session.commit()

    return ApiResponse.success({})


@token_bp.route('/delete', methods=['POST'])
@jwt_required()
def account_delete():
    id = request.json.get('id')
    token = db.session.query(Token).filter_by(id=id).first()
    accounts = db.session.query(Account).filter_by(token_id=id).all()
    if len(accounts) > 0:
        return ApiResponse.error('存在关联账号，请先删除关联账号')
    db.session.delete(token)
    db.session.commit()
    return ApiResponse.success({})


@token_bp.route('/refresh', methods=['POST'])
@jwt_required()
def account_refresh():
    token_id = request.json.get('id')
    token = db.session.query(Token).filter_by(id=token_id).first()

    if not token:
        logger.error('Token不存在')
        return ApiResponse.error('Token不存在')

    try:
        refresh_by_token(token)
    except Exception as e:
        logger.error("刷新失败")
        return ApiResponse.error(str(e))

    try:
        refresh_subscription_status(token_id)
    except Exception as e:
        logger.error("刷新订阅状态失败")
        return ApiResponse.error(str(e))

    return ApiResponse.success('刷新成功')

