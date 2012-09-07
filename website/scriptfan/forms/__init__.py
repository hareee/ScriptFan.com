#-*-coding:utf-8-*-
from flask import session
from flask.ext import wtf
from scriptfan.models import (get_user, User, UserInfo, UserOpenID)

class SigninForm(wtf.Form):
    email = wtf.TextField('email', validators=[
        wtf.Required(message=u'请填写电子邮件'), 
        wtf.Email(message=u'无效的电子邮件')])
    password = wtf.PasswordField('password', validators=[
        wtf.Required(message=u'请填写密码'),
        wtf.Length(min=5, max=20, message=u'密应应为5到20位字符')])
    next = wtf.HiddenField('next')
    remember = wtf.BooleanField('remember')
    
    openid_identifier = wtf.HiddenField('openid_identifier')
    openid_provider = wtf.HiddenField('openid_provider')

    def __init__(self, *args, **kargs):
        wtf.Form.__init__(self, *args, **kargs)
        self.user = None

    def validate(self):
        # 验证邮箱是否注册
        if wtf.Form.validate(self):
            user = get_user(email=self.email.data)
            if not user:
                self.email.errors.append(u'该邮箱尚未在本站注册')
            elif not user.check_password(self.password.data):
                self.password.errors.append(u'密码错误')
            else:
                self.user = user

        return len(self.errors) == 0

class SignupForm(wtf.Form):
    email = wtf.TextField('email', validators=[
        wtf.Required(message=u'请填写电子邮件'), 
        wtf.Email(message=u'无效的电子邮件')])
    nickname = wtf.TextField('nickname', validators=[
        wtf.Required(message=u'请填写昵称'),
        wtf.Length(min=2, max=20, message=u'昵称应为2到20字符')])
    password = wtf.PasswordField('password', validators=[
        wtf.Required(message=u'请填写密码'),
        wtf.Length(min=5, max=20, message=u'密码应为5到20位字符')])
    repassword = wtf.PasswordField('repassword', validators=[
        wtf.Required(message=u'请填写确认密码'),
        wtf.EqualTo('password', message=u'两次输入的密码不一致')])
    next = wtf.HiddenField('next')

    def __init__(self, *args, **kargs):
        wtf.Form.__init__(self, *args, **kargs)
        self.user = None

    def validate(self):
        wtf.Form.validate(self)

        # 验证邮箱是否注册
        if not self.email.errors:
            user = get_user(email=self.email.data)
            user and self.email.errors.append(u'该邮箱已被注册')
        
        self.user = User(email=self.email.data, nickname=self.nickname.data, openids=[
            UserOpenID(provider=session['openid_provider'], openid=session['current_openid'])])
        self.user.set_password(self.password.data)
        self.user.info = UserInfo()
        
        return len(self.errors) == 0

class ProfileForm(wtf.Form):
    nickname = wtf.TextField('nickname', validators=[
        wtf.Required(message=u'请填写昵称')])
    slug = wtf.TextField('slug', validators=[
        wtf.Regexp(regex=r'([a-zA-Z0-9_-]{5,24})?', message=u'域名为5到24位，由英文字母、数字或者符号(包括_-)组成')])
    phone = wtf.TextField('phone', validators=[
        wtf.Regexp(regex=r'^(1\d{10})?$', message=u'请输入有效的手机号码')])
    phone_status = wtf.RadioField('phone_status', choices=[
        (0, u'不公开'), (1, u'公开'), (2, u'仅向会员公开')])      
    # photo = db.Column(db.String(255), nullable=True) # 存一张照片，既然有线下的聚会的，总得认得人才行
    motoo = wtf.TextAreaField('motoo', validators=[
        wtf.Length(min=0, max=255, message=u'座右铭最多为255个字符')])
    introduction = wtf.TextAreaField('introduction', validators=[
        wtf.Length(min=0, max=3000, message=u'个人介绍最多为3000个字')])
    
    def __init__(self, *args, **kargs):
        wtf.Form.__init__(self, *args, **kargs)
        self.user = None
