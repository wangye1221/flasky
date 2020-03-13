from flask import render_template, redirect, request, url_for, flash
from flask_login import login_user, logout_user, login_required
from . import auth
from ..models import User
from .forms import LoginForm, RegistrationForm


# 用户登录路由
@auth.route('/login', methods=['GET', 'POST'])
def login() -> 'html':
    form = LoginForm()
    # 判断请求是不是POST
    if form.validate_on_submit():
        # 通过email查询数据库内是否有存在用户
        user = User.query.filter_by(email=form.email.data).first()
        # 判断是否返回用户以及密码是否匹配
        if user is not None and user.verify_password(form.password.data):
            login_user(user, form.remember_me.data)
            # 如果用户是从未授权URL重定向至登录页，则将之前的URL保存至next
            next = request.args.get('next')
            if next is None or not next.startswith('/'):
                next = url_for('main.index')
            return redirect(next)
        flash('Invalid username or password.')
    return render_template('auth/login.html', form=form)

# 用户退出路由
@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('main.index'))

# 用户注册路由
@auth.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(email=form.email.data, username=form.username.data, password=form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('You can now login.')
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html', form=form)