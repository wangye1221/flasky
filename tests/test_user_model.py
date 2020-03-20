import unittest
import time
from app import create_app, db
from app.models import User, AnonymousUser, Role, Permission


class UserModelTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        Role.insert_roles()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_password_setter(self):
        u = User(password='cat')
        self.assertTrue(u.password_hash is not None)

    def test_no_password_getter(self):
        u = User(password='cat')
        with self.assertRaises(AttributeError):
            u.password

    def test_password_verification(self):
        u = User(password='cat')
        self.assertTrue(u.verify_password('cat'))
        self.assertFalse(u.verify_password('dog'))

    def test_password_salts_are_random(self):
        u = User(password='cat')
        u2 = User(password='cat')
        self.assertTrue(u.password_hash != u2.password_hash)

    # 验证令牌有效
    def test_valid_confirmation_token(self):
        u = User(password='cat')
        db.session.add(u)
        db.session.commit()
        token = u.generate_confirmation_token()
        self.assertTrue(u.confirm(token))

    # 验证令牌无效
    def test_invalid_confirmation_token(self):
        u1 = User(password='cat')
        u2 = User(password='dog')
        db.session.add(u1)
        db.session.add(u2)
        db.session.commit()
        token = u1.generate_confirmation_token()
        self.assertFalse(u2.confirm(token))

    # 验证令牌过期
    def test_expired_confirmation_token(self):
        u = User(password='cat')
        db.session.add(u)
        db.session.commit()
        token = u.generate_confirmation_token(1)
        time.sleep(2)
        self.assertFalse(u.confirm(token))

    # 验证重置密码令牌有效性
    def test_valid_reset_token(self):
        u = User(password='cat')
        db.session.add(u)
        db.session.commit()
        token = u.generate_reset_token()
        self.assertTrue(User.reset_password(token, 'dog'))
        self.assertTrue(u.verify_password('dog'))

    # 验证重置密码令牌无效性
    def test_invalid_reset_token(self):
        u = User(password='cat')
        db.session.add(u)
        db.session.commit()
        token = u.generate_reset_token()
        self.assertFalse(User.reset_password(token + 'a', 'horse'))
        self.assertTrue(u.verify_password('cat'))

    # 验证更新邮箱令牌有效性
    def test_valid_change_email_token(self):
        u = User(password='cat')
        db.session.add(u)
        db.session.commit()
        token = u.generate_change_email_token('123@456.com')
        self.assertTrue(u.change_email_confirm(token))

    # 验证更新邮箱令牌无效性
    def test_invalid_change_email_token(self):
        u = User(password='cat')
        db.session.add(u)
        db.session.commit()
        token = u.generate_change_email_token('123@456.com')
        self.assertFalse(u.change_email_confirm(token + 'a'))

    # 验证用户角色权限
    def test_user_role(self):
        u = User(email='test@test.com', password='cat')
        self.assertTrue((u.can(Permission.FOLLOW)))
        self.assertTrue((u.can(Permission.COMMENT)))
        self.assertTrue((u.can(Permission.WRITE)))
        self.assertFalse((u.can(Permission.MODERATE)))
        self.assertFalse((u.can(Permission.ADMIN)))

    # 验证协管员角色权限
    def test_moderate_role(self):
        r = Role.query.filter_by(name='Moderator').first()
        u = User(email='test@test.com', password='cat', role=r)
        self.assertTrue((u.can(Permission.FOLLOW)))
        self.assertTrue((u.can(Permission.COMMENT)))
        self.assertTrue((u.can(Permission.WRITE)))
        self.assertTrue((u.can(Permission.MODERATE)))
        self.assertFalse((u.can(Permission.ADMIN)))

    # 验证管理员角色权限
    def test_admin_role(self):
        r = Role.query.filter_by(name='Administrator').first()
        u = User(email='test@test.com', password='cat', role=r)
        self.assertTrue((u.can(Permission.FOLLOW)))
        self.assertTrue((u.can(Permission.COMMENT)))
        self.assertTrue((u.can(Permission.WRITE)))
        self.assertTrue((u.can(Permission.MODERATE)))
        self.assertTrue((u.can(Permission.ADMIN)))

    # 验证匿名用户角色权限
    def test_anonymous_user(self):
        u = AnonymousUser()
        self.assertFalse((u.can(Permission.FOLLOW)))
        self.assertFalse((u.can(Permission.COMMENT)))
        self.assertFalse((u.can(Permission.WRITE)))
        self.assertFalse((u.can(Permission.MODERATE)))
        self.assertFalse((u.can(Permission.ADMIN)))
