from flask import render_template, current_app
# 引入邮件库
from flask_mail import Message
from threading import Thread
from . import mail


def send_email(to, subject, template, **kwargs):
    # 实例化邮件内容类，分别传入标题、发件人和收件人
    app = current_app._get_current_object()
    msg = Message(subject=app.config['FLASKY_MAIL_SUBJECT_PREFIX'] + subject, 
    sender=app.config['FLASKY_MAIL_SENDER'], recipients=[to])
    msg.body = render_template(template + '.txt', **kwargs)
    msg.html = render_template(template + '.html', **kwargs)
    # 通过线程异步发送邮件
    thr = Thread(target=send_async_email, args=[app, msg])
    thr.start()
    return thr

# 异步发送邮件
def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)