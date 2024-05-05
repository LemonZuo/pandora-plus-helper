from datetime import datetime, timedelta
from flask import Blueprint, request
from flask_jwt_extended import jwt_required
from loguru import logger
from model import db, Token, Account
from util.api_response import ApiResponse
from util.pandora_plus_tools import gen_access_token, refresh_by_token_id, check_subscription_status, refresh_subscription_status

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
    try:
        refresh_by_token_id(token_id)
    except Exception as e:
        logger.error("刷新失败")
        return ApiResponse.error(str(e))

    try:
        refresh_subscription_status(token_id)
    except Exception as e:
        logger.error("刷新订阅状态失败")
        return ApiResponse.error(str(e))

    return ApiResponse.success('刷新成功')


def refresh_all_user():
    logger.info('开始定时刷新')

    from app import scheduler
    flag = False
    with scheduler.app.app_context():
        tokens = db.session.query(Token).all()
        logger.info(f'共有{len(tokens)}个token')

        for token in tokens:
            # 刷新token
            try:
                # 检查 rt 是否存在
                if not token.refresh_token:
                    logger.error(f'{token.token_name} 不存在refresh_token')
                    continue
                # 判断at是否过期
                if token.expire_at > datetime.now():
                    logger.info(f'{token.token_name} 未过期')
                    # 刷新订阅状态
                    try:
                        refresh_subscription_status(token.id)
                    except Exception as e:
                        logger.error("刷新订阅状态失败", e)
                    continue
                else:
                    flag = True
                    # 刷新订阅状态
                    try:
                        refresh_subscription_status(token.id)
                    except Exception as e:
                        logger.error("刷新订阅状态失败", e)
            except Exception as e:
                logger.error("刷新token失败", e)
        if flag:
            logger.info('刷新成功')

        logger.info('定时刷新结束')


@token_bp.route('/start', methods=['post'])
@jwt_required()
def refresh_task():
    from app import scheduler
    scheduler.add_job(func=refresh_all_user, trigger='cron', minute='0', id='token_job', replace_existing=True)
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
