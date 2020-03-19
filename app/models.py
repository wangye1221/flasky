from . import db, login_manager
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
# 生成令牌字符串库
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app


# 定义数据库表roles模型
class Role(db.Model):
    # 定义数据库中的表名
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    # unique，列不允许出现重复值
    name = db.Column(db.String(64), unique=True)
    # 定义关系，第一个参数定义关系的对端是哪个模型，backref参数定义反向引用
    users = db.relationship('User', backref='role', lazy='dynamic')

    def __repr__(self):
        # 返回具有可读性的字符串表示模型，供测试调试使用，非必须
        return '<Role %r>' % self.name

# 定义数据库表users模型
class User(db.Model, UserMixin):
    # 定义数据库中的表名
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    # unique，列不允许出现重复值
    # index，为列创建索引，提高查询效率
    username = db.Column(db.String(64), unique=True, index=True)
    email = db.Column(db.String(64), unique=True, index=True)
    # 建立外键，值为roles表的id列
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    password_hash = db.Column(db.String(128))
    confirmed = db.Column(db.Boolean, default=False)

    # 装饰器将函数属性化,不允许读取password
    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    # 只写属性
    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    # 比对密码与加密
    def verify_password(self, password) -> bool:
        return check_password_hash(self.password_hash, password)

    # 生成令牌，默认有效期十五分钟
    def generate_confirmation_token(self, expiration=900) -> 'token':
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'confirm': self.id}).decode('utf-8')

    # 验证令牌
    def confirm(self, token) -> bool:
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token.encode('utf-8'))
        except:
            return False
        # 检查令牌中的用户ID与当前登录用户ID是否一致
        if data.get('confirm') != self.id:
            return False
        self.confirmed = True
        db.session.add(self)
        return True

    # 生成重置密码的令牌
    def generate_reset_token(self, expiration=900) -> 'token':
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'reset': self.id}).decode('utf-8')

    # 验证令牌
    @staticmethod
    def reset_password(token, new_password) -> bool:
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token.encode('utf-8'))
        except:
            return False
        user = User.query.get(data.get('reset'))
        if user is None:
            return False
        user.password = new_password
        db.session.add(user)
        return True

    # 生成更换邮箱的令牌
    def generate_change_email_token(self, new_email, expiration=900) -> 'token':
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'change': self.id, 'new_email': new_email}).decode('utf-8')
    
    # 验证令牌
    def change_email_confirm(self, token) -> bool:
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token.encode('utf-8'))
        except:
            return False
        # 检查令牌中的用户ID与当前登录用户ID是否一致
        if data.get('change') != self.id:
            return False
        self.email = data.get('new_email')
        db.session.add(self)
        return True

    def __repr__(self):
        # 返回具有可读性的字符串表示模型，供测试调试使用，非必须
        return '<User %r>' % self.username

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
