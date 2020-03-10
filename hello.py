from flask import Flask, render_template, session, redirect, url_for, flash
# 引入前端框架 Bootstrap
from flask_bootstrap import Bootstrap
# 引入本地化时间库 Moment
from flask_moment import Moment
from datetime import datetime
# 引入 wtforms表单处理库
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
import os
# 引入sqlalchemy ORM
from flask_sqlalchemy import SQLAlchemy


basedir = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__)
# session的密钥
app.config['SECRET_KEY'] = 'CallMeBigYe'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'data.sqlite')
# 关闭追踪对象的修改
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
bootstrap = Bootstrap(app)
moment = Moment(app)
db = SQLAlchemy(app)

@app.route('/', methods=['GET', 'POST'])
def index() -> 'html':
    # 实例化NameForm表单类
    form = NameForm()
    # 验证提交的数据
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.name.data).first()
        if user is None:
            user = User(username=form.name.data)
            db.session.add(user)
            db.session.commit()
            session['known'] = False
        else:
            session['known'] = True
        session['name'] = form.name.data
        form.name.data = ''
        return redirect(url_for('index'))
    return render_template('index.html', current_time=datetime.utcnow(), form=form, name=session.get('name'), known=session.get('known', False))

@app.route('/user/<name>')
def user(name:str) -> 'html':
    return render_template('user.html', name=name)

# 定义错误页面
@app.errorhandler(404)
def page_not_found(e) -> 'html':
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e) -> 'html':
    return render_template('500.html'), 500

# 定义表单类
class NameForm(FlaskForm):
    # StringField类表示属性为 type="text"的 HTML<input>元素，DataRequired()函数确保提交字段不为空
    name = StringField('What is your name?', validators=[DataRequired()])
    # SubmitField类表示属性为 type="submit"的 HTML<input>元素
    submit = SubmitField('Submit')

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