from flask import Flask, render_template
# 引入前端框架 Bootstrap
from flask_bootstrap import Bootstrap
# 引入本地化时间库 Moment
from flask_moment import Moment
from datetime import datetime
# 引入 wtforms表单处理库
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired


app = Flask(__name__)
app.config['SECRET_KEY'] = 'CallMeBigYe'
bootstrap = Bootstrap(app)
moment = Moment(app)

@app.route('/')
def index() -> 'html':
    return render_template('index.html', current_time=datetime.utcnow())

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