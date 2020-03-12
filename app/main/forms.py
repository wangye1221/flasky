# 引入 wtforms表单处理库
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired


# 定义表单类
class NameForm(FlaskForm):
    # StringField类表示属性为 type="text"的 HTML<input>元素，DataRequired()函数确保提交字段不为空
    name = StringField('What is your name?', validators=[DataRequired()])
    # SubmitField类表示属性为 type="submit"的 HTML<input>元素
    submit = SubmitField('Submit')