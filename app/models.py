from . import db


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
class User(db.Model):
    # 定义数据库中的表名
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    # unique，列不允许出现重复值
    # index，为列创建索引，提高查询效率
    username = db.Column(db.String(64), unique=True, index=True)
    # 建立外键，值为roles表的id列
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))

    def __repr__(self):
        # 返回具有可读性的字符串表示模型，供测试调试使用，非必须
        return '<User %r>' % self.username