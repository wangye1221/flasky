from flask import render_template, redirect, request, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from . import auth
from .. import db
from ..models import User
from .forms import LoginForm, RegistrationForm, ChangePasswordForm, PasswordResetForm, PasswordResetRequestForm, ChangeEmailForm
from ..email import send_email


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
        # 生成令牌并发送注册确认邮件
        token = user.generate_confirmation_token()
        send_email(user.email, 'Confirm Your Account', 'auth/email/confirm', user=user, token=token)
        flash('A confirmation email has been sent to you by email.')
        return redirect(url_for('main.index'))
    return render_template('auth/register.html', form=form)

# 用户注册令牌验证
@auth.route('/confirm/<token>')
@login_required
def confirm(token):
    if current_user.confirmed:
        return redirect(url_for('main.index'))
    # 判断令牌有效性
    if current_user.confirm(token):
        db.session.commit()
        flash('You have confirmed your account. Thanks!')
    else:
        flash('The confirmation link is invalid or has expired.')
    return redirect(url_for('main.index'))

# 用户注册生成令牌
@auth.route('/confirm')
@login_required
def resend_confirmation():
    if current_user.confirmed:
        flash("You've confirmed it")
        return redirect(url_for('main.index'))
    token = current_user.generate_confirmation_token()
    send_email(current_user.email, 'Confirm Your Account', 'auth/email/confirm', user=current_user, token=token)
    flash('A new confirmation email has been sent to you by email.')
    return redirect(url_for('main.index'))

# 用户更改密码
@auth.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password() -> 'html':
    form = ChangePasswordForm()
    if form.validate_on_submit():
        # 确认旧密码正确
        if current_user.verify_password(form.old_password.data):
            current_user.password = form.password.data
            db.session.add(current_user)
            db.session.commit()
            flash('您的密码已更新')
            return redirect(url_for('main.index'))
        else:
            flash('请输入正确的旧密码')
    return render_template('auth/change_password.html', form=form)

# 用户重置密码
@auth.route('/reset', methods=['GET', 'POST'])
def password_reset_request() -> 'html':
    if not current_user.is_anonymous:
        return redirect(url_for('main.index'))
    form = PasswordResetRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower()).first()
        if user:
            token = user.generate_reset_token()
            send_email(user.email, 'Reset Your Password', 'auth/email/reset_password', user=user, token=token)
        flash('An email with instructions to reset your password has been sent to you.')
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password.html', form=form)

# 用户重置密码，验证令牌
@auth.route('/reset/<token>', methods=['GET', 'POST'])
def password_reset(token):
    if not current_user.is_anonymous:
        return redirect('main.index')
    form = PasswordResetForm()
    if form.validate_on_submit():
        if User.reset_password(token, form.password.data):
            db.session.commit()
            flash('Your password has been updated.')
            return redirect(url_for('auth.login'))
        else:
            flash('重置失败。')
            return redirect(url_for('main.index'))
    return render_template('auth/reset_password.html', form=form)

# 用户更改email地址
@auth.route('/change_email', methods=['GET', 'POST'])
@login_required
def change_email():
    form = ChangeEmailForm()
    if form.validate_on_submit():
        token = current_user.generate_change_email_token(form.email.data)
        send_email(form.email.data, '更换你的邮箱', 'auth/email/change_email', user=current_user, token=token)
        flash('一封确认邮件已经发送到您的新邮箱中，请及时查收并确认。')
        return redirect(url_for('main.index'))
    return render_template('auth/change_email.html', form=form)

# 用户更改email令牌验证
@auth.route('/change_email/<token>')
@login_required
def change_email_confirm(token):
    # 判断令牌有效性
    if current_user.change_email_confirm(token):
        db.session.commit()
        flash('你的邮箱已经更新成功！')
    else:
        flash('The confirmation link is invalid or has expired.')
    return redirect(url_for('main.index'))

# 拦截所有URL请求，先判断用户邮箱确认状态
@auth.before_app_request
def before_request():
    # 判断用户为登录状态且未确认邮件且请求的URL不在身份验证蓝本和静态文件中
    if current_user.is_authenticated:
        current_user.ping()
        if not current_user.confirmed \
                and request.endpoint \
                and request.blueprint != 'auth' \
                and request.endpoint != 'static':
            return redirect(url_for('auth.unconfirmed'))

@auth.route('/unconfirmed')
def unconfirmed():
    if current_user.is_anonymous or current_user.confirmed:
        return redirect(url_for('main.index'))
    return render_template('auth/unconfirmed.html')
