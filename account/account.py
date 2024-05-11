import json
from datetime import datetime, timedelta

from flask import Blueprint, request
from flask_jwt_extended import jwt_required
from loguru import logger

from model import db, Token, Account
from util import share_tools
from util.api_response import ApiResponse
from util.share_tools import gen_share_token

account_bp = Blueprint('account_bp', __name__)


def account2share(accounts):
    shares = []
    for account in accounts:
        _share_list = json.loads(account.share_list)
        for share in _share_list:
            share['email'] = account.email
            share['account_id'] = account.id
            shares.append(share)
    return shares


@account_bp.route('/list')
@jwt_required()
def share_list():
    accounts = db.session.query(Token).all()
    return ApiResponse.success(account2share(accounts))


@account_bp.route('/search', methods=['POST'])
@jwt_required()
def search():
    # 根据tokenId
    token_id = request.json.get('token_id')
    if token_id:
        accounts = db.session.query(Account).filter_by(token_id=token_id).all()
    else:
        accounts = db.session.query(Account).all()

    return ApiResponse.success(accounts)


@account_bp.route('/add', methods=['POST'])
@jwt_required()
def share_add():
    token_id = request.json.get('token_id')
    account = request.json.get('account')
    password = request.json.get('password')
    expiration_time = datetime.strptime(request.json.get('expiration_time'), '%Y-%m-%d %H:%M:%S')
    gpt35_limit = request.json.get('gpt35_limit')
    gpt4_limit = request.json.get('gpt4_limit')
    show_conversations = request.json.get('show_conversations')
    temporary_chat = request.json.get('temporary_chat')

    token = db.session.query(Token).filter_by(id=token_id).first()

    if token:
        if not token.access_token:
            return ApiResponse.error('请先登录账号')
        else:
            try:
                res = gen_share_token(access_token=token.access_token,
                                      unique_name=account,
                                      gpt35_limit=gpt35_limit,
                                      gpt4_limit=gpt4_limit,
                                      show_conversations=show_conversations == 1,
                                      temporary_chat=temporary_chat == 1)
                logger.info(res)
            except Exception as e:
                logger.error(e)
                return ApiResponse.error('生成分享用户失败')
            expire_at=datetime.fromtimestamp(res.get('expire_at'))
            # 检查expire_at的类型是否正确
            if not isinstance(expire_at, datetime):
                raise TypeError(f"Expected datetime.datetime, got {type(expire_at)} instead.")

            now = datetime.now()
            account_entity = Account(
                account=account,
                password=password,
                status=1,
                expiration_time=expiration_time,
                token_id=token_id,
                share_token=res.get('token_key'),
                expire_at=expire_at,
                create_time=now,
                update_time=now,
                gpt35_limit=gpt35_limit,
                gpt4_limit=gpt4_limit,
                show_conversations=show_conversations,
                temporary_chat=temporary_chat
            )
            logger.info(account_entity)
            db.session.add(account_entity)
            db.session.commit()
            return ApiResponse.success({})
    else:
        return ApiResponse.error('令牌不存在')


@account_bp.route('/delete', methods=['POST'])
@jwt_required()
def share_delete():
    id = request.json.get('id')
    account = db.session.query(Account).filter_by(id=id).first()
    if not account:
        return ApiResponse.error('账号不存在')
    token = db.session.query(Token).filter_by(id=account.token_id).first()
    if not token:
        return ApiResponse.error('令牌不存在')
    if not token.access_token:
        return ApiResponse.error('请先登录账号')
    else:
        try:
            res = gen_share_token(access_token=token.access_token,
                                  unique_name=account.account,
                                  expires_in=-1)
            logger.info(res)
        except Exception as e:
            logger.error(e)
            return ApiResponse.error('删除分享用户失败')
    db.session.delete(account)
    db.session.commit()
    return ApiResponse.success({})


@account_bp.route('/update', methods=['POST'])
@jwt_required()
def share_update():
    id = request.json.get('id')
    token_id = request.json.get('token_id')
    account = request.json.get('account')
    password = request.json.get('password')
    expiration_time = datetime.strptime(request.json.get('expiration_time'), '%Y-%m-%d %H:%M:%S')
    gpt35_limit = request.json.get('gpt35_limit')
    gpt4_limit = request.json.get('gpt4_limit')
    show_conversations = request.json.get('show_conversations')
    temporary_chat = request.json.get('temporary_chat')

    account_entity = db.session.query(Account).filter_by(id=id).first()
    if not account_entity:
        return ApiResponse.error('账号不存在')

    token = db.session.query(Token).filter_by(id=token_id).first()
    if not token:
        return ApiResponse.error('令牌不存在')

    if not token.access_token:
        return ApiResponse.error('请先登录账号')
    else:
        try:
            res = gen_share_token(access_token=token.access_token,
                                  unique_name=account,
                                  gpt35_limit=gpt35_limit,
                                  gpt4_limit=gpt4_limit,
                                  show_conversations=show_conversations == 1,
                                  temporary_chat=temporary_chat == 1)
            logger.info(res)
        except Exception as e:
            logger.error(e)
            return ApiResponse.error('生成分享用户失败')
        expire_at=datetime.fromtimestamp(res.get('expire_at'))
        # 检查expire_at的类型是否正确
        if not isinstance(expire_at, datetime):
            raise TypeError(f"Expected datetime.datetime, got {type(expire_at)} instead.")

        account_entity.token_id = token_id
        account_entity.account = account
        account_entity.password = password
        account_entity.expiration_time = expiration_time
        account_entity.share_token = res.get('token_key')
        account_entity.gpt35_limit = gpt35_limit
        account_entity.gpt4_limit = gpt4_limit
        account_entity.show_conversations = show_conversations
        account_entity.expire_at = expire_at
        account_entity.update_time = datetime.now()
        logger.info(account_entity)
        db.session.commit()
        return ApiResponse.success({})


@account_bp.route('/statistic', methods=['POST'])
@jwt_required()
def share_info():
    token_id = request.json.get('token_id')
    token = db.session.query(Token).filter_by(id=token_id).first()

    if token.access_token is None:
        return ApiResponse.error('请先登录账号')
    accounts = db.session.query(Account).filter_by(token_id=token_id, status=1).all()
    unique_names = list(map(lambda x: x['account'], accounts))
    info_list = {}
    for account in accounts:
        try:
            info = share_tools.get_share_token_info(account.share_token, token.access_token)
        except Exception as e:
            logger.error(e)
            return ApiResponse.error('获取分享用户信息失败, 请检查access_token是否有效')
        info_list[account.account] = info

    models = []
    # 取出所有的model

    for k, v in info_list.items():
        if 'usage' not in v:
            raise Exception('获取分享用户信息失败, 请检查access_token是否有效')
        if 'range' in v['usage']:
            # 删除range键值对
            del v['usage']['range']
        for k1, v1 in v['usage'].items():
            if k1 not in models:
                models.append(k1)

    series = []
    # 组装series
    for model in models:
        data = []
        # 保持顺序一致
        for u_name in unique_names:
            if u_name in info_list and model in info_list[u_name]['usage']:
                data.append(info_list[u_name]['usage'][model])
            else:
                data.append(0)
        s = {
            'name': model,
            'data': data,
        }
        series.append(s)

    return ApiResponse.success({
        "categories": unique_names,
        "series": series
    })


@account_bp.route('/disable', methods=['POST'])
@jwt_required()
def disable_account():
    id = request.json.get('id')

    account = db.session.query(Account).filter_by(id=id).first()
    if not account:
        return ApiResponse.error('账号不存在')

    token = db.session.query(Token).filter_by(id=account.token_id).first()
    if not token:
        return ApiResponse.error('令牌不存在')

    if not token.access_token:
        return ApiResponse.error('请先登录账号')
    else:
        try:
            res = gen_share_token(access_token=token.access_token,
                                  unique_name=account.account,
                                  expires_in=-1,
                                  gpt35_limit=account.gpt35_limit,
                                  gpt4_limit=account.gpt4_limit,
                                  show_conversations=account.show_conversations == 1,
                                  temporary_chat=account.temporary_chat == 1)
            logger.info(res)
        except Exception as e:
            logger.error(e)
            return ApiResponse.error('生成分享用户失败')

        now = datetime.now()
        account.status = 0
        account.expiration_time = now
        account.expire_at = now
        account.update_time = now
        logger.info(account)
        db.session.commit()
        return ApiResponse.success({})


@account_bp.route('/enable', methods=['POST'])
@jwt_required()
def enable_account():
    id = request.json.get('id')

    account = db.session.query(Account).filter_by(id=id).first()
    if not account:
        return ApiResponse.error('账号不存在')

    token = db.session.query(Token).filter_by(id=account.token_id).first()
    if not token:
        return ApiResponse.error('令牌不存在')

    if not token.access_token:
        return ApiResponse.error('请先登录账号')
    else:
        try:
            res = gen_share_token(access_token=token.access_token,
                                  unique_name=account.account,
                                  gpt35_limit=account.gpt35_limit,
                                  gpt4_limit=account.gpt4_limit,
                                  show_conversations=account.show_conversations == 1,
                                  temporary_chat=account.temporary_chat == 1)
            logger.info(res)
        except Exception as e:
            logger.error(e)
            return ApiResponse.error('生成分享用户失败')
        expire_at=datetime.fromtimestamp(res.get('expire_at'))
        # 检查expire_at的类型是否正确
        if not isinstance(expire_at, datetime):
            raise TypeError(f"Expected datetime.datetime, got {type(expire_at)} instead.")

        now = datetime.now()
        account.share_token = res.get('token_key')
        account.status = 1
        account.expiration_time = now + timedelta(days=30)
        account.expire_at = expire_at
        account.update_time = now
        logger.info(account)
        db.session.commit()
        return ApiResponse.success({})
