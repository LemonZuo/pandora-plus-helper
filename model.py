from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Token(db.Model):
    __tablename__ = 'tb_token'
    id = db.Column(db.Integer, primary_key=True, comment='主键')
    token_name = db.Column(db.Text, nullable=False, comment='token名称')
    refresh_token = db.Column(db.Text, nullable=False, unique=True, comment='刷新token')
    access_token = db.Column(db.Text, nullable=False, comment='访问token')
    expire_at = db.Column(db.DateTime, nullable=False, comment='过期时间')
    create_time = db.Column(db.DateTime, nullable=False, comment='创建时间')
    update_time = db.Column(db.DateTime, nullable=False, comment='更新时间')

    def keys(self):
        return ['id', 'token_name', 'refresh_token', 'access_token', 'expire_at', 'create_time', 'update_time']

    def __getitem__(self, item):
        return getattr(self, item)

    def __repr__(self):
        return '<Token %r>' % self.id


class Account(db.Model):
    __tablename__ = 'tb_account'
    id = db.Column(db.Integer, primary_key=True, comment='主键')
    account = db.Column(db.Text, nullable=False, unique=True, comment='唯一名称')
    password = db.Column(db.Text, nullable=False, unique=True, comment='密码')
    status = db.Column(db.Integer, nullable=False, default=1, comment='状态, 1:正常, 0:禁用')
    token_id = db.Column(db.Integer, nullable=False, comment='token_id')
    share_token = db.Column(db.Text, nullable=False, comment='共享token')
    expire_at = db.Column(db.DateTime, nullable=False, comment='过期时间')
    create_time = db.Column(db.DateTime, nullable=False, comment='创建时间')
    update_time = db.Column(db.DateTime, nullable=False, comment='更新时间')

    def keys(self):
        return ['id', 'account', 'password', 'status', 'token_id', 'share_token', 'expire_at', 'create_time', 'update_time']

    def __getitem__(self, item):
        return getattr(self, item)

    def __repr__(self):
        return '<Token %r>' % self.id
