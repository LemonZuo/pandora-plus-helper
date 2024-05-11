from datetime import datetime, timedelta
from threading import Lock

from loguru import logger

from model import db, Token
from util.pandora_plus_tools import refresh_by_token, refresh_subscription_status, disable_by_token_id

# 全局锁
refresh_lock = Lock()
disable_lock = Lock()


def refresh_all_token():
    if refresh_lock.acquire(blocking=False):
        try:
            logger.info('开始刷新token')

            from app import scheduler
            with scheduler.app.app_context():
                tokens = db.session.query(Token).all()
                logger.info(f'共有{len(tokens)}个token')

                # 刷新token
                for token in tokens:
                    # 检查 rt 是否存在
                    if not token.refresh_token:
                        logger.error(f'{token.token_name} 不存在refresh_token')
                        continue
                    # 判断at是否需要刷新
                    if token.expire_at - datetime.now() > timedelta(hours=1):
                        logger.info(f'{token.token_name} 无需刷新')
                        # 刷新订阅状态
                        try:
                            refresh_subscription_status(token.id)
                        except Exception as e:
                            logger.error("刷新订阅状态失败", e)
                        continue
                    else:
                        logger.info(f'{token.token_name} 执行刷新')
                        # 刷新订阅状态
                        try:
                            refresh_subscription_status(token.id)
                        except Exception as e:
                            logger.error("刷新订阅状态失败", e)
                        # 刷新token
                        try:
                            refresh_by_token(token)
                        except Exception as e:
                            logger.error("刷新token失败", e)

                logger.info('定时刷新结束')
        finally:
            refresh_lock.release()
    else:
        logger.info('上一次任务还未执行完，跳过本次执行')


def disable_all_account():
    if disable_lock.acquire(blocking=False):
        try:
            logger.info('开始禁用账号')
            from app import scheduler
            with scheduler.app.app_context():
                tokens = db.session.query(Token).all()
                logger.info(f'共有{len(tokens)}个token')

                # 刷新token
                for token in tokens:
                    try:
                        disable_by_token_id(token.id)
                    except Exception as e:
                        logger.error("禁用账号失败", e)
                logger.info('定时禁用结束')
        finally:
            disable_lock.release()
    else:
        logger.info('上一次任务还未执行完，跳过本次执行')
