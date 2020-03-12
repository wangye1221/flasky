from datetime import datetime
from flask import render_template, session, redirect, url_for
from .forms import NameForm
from .. import db
from ..models import User


@main.route('/', methods=['GET', 'POST'])
def index() -> 'html':
    form = NameForm()
    # 验证提交的数据
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.name.data).first()
        if user is None:
            user = User(username=form.name.data)
            db.session.add(user)
            db.session.commit()
            session['known'] = False
            if app.config['FLASKY_ADMIN']:
                send_email(app.config['FLASKY_ADMIN'], 'New User', 'mail/new_user', user=user)
        else:
            session['known'] = True
        session['name'] = form.name.data
        form.name.data = ''
        # 在蓝本中使用端点名需要引用蓝本的名称，'.index'的完整写法为'main.index'。
        # 跨蓝本的重定向必须使用完整的端点名引用方式。
        return redirect(url_for('.index'))
    return render_template('index.html', current_time=datetime.utcnow(), form=form, name=session.get('name'), known=session.get('known', False))