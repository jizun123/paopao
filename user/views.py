import base64
import json
import requests
import random
import time
import jwt
import hashlib
from urllib.parse import urlencode

from django.core.mail import send_mail
from django.db import transaction
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render
from django.views.generic.base import View

from .models import UserProfile, WeiBoUser
from stock.models import account
#获取settings中的配置
from django.conf import settings
from django_redis import get_redis_connection

from ntoken.views import make_token
from .tasks import send_active_email
from tools.logging_check import logging_check
from tools.check_sms import  check_code
from .sms_task import send_sms

#本模块下 响应异常状态码 10101 - 10199

# Create your views here.
@check_code
def user_view(request):
    #/v1/users

    if request.method == 'POST':
        #创建资源
        #前端json串{"uname":"guoxiao","password":"123456","phone":"13488873110","email":"213@qq.com"}
        # request.body
        json_str = request.body
        json_obj = json.loads(json_str)
        username = json_obj.get('uname')
        password = json_obj.get('password')
        phone = json_obj.get('phone')
        email = json_obj.get('email')
        code = json_obj.get('code')
        # 基础校验[数据给没给, 用户名是否可用]
        #TODO 检查不存在情况
        if not username:
            result = {'code':10101, 'error':'Please give me username~'}
            return JsonResponse(result)
        #检查用户名是否可用
        old_users = UserProfile.objects.filter(username=username)
        if old_users:
            #当前用户名已注册
            result = {'code':10102, 'error': 'The username is already registed~'}
            return JsonResponse(result)
        if not code:
            #没有输入code
            return JsonResponse({'code': 20101, 'error': '请输入验证码！'}, json_dumps_params={'ensure_ascii': False})
        #判断验证码是否正确且在有效期内
        if  not request.check_code:
            return JsonResponse({'code': 230201, 'error': '验证码输入错误，请重新发送！'}, json_dumps_params={'ensure_ascii': False})

        import hashlib
        m = hashlib.md5()
        m.update(password.encode())
        #创建用户数据
        try:
            #由于username字段有唯一索引,如果出现并发插入多个相同用户名的情况,mysql会抛错,故此处必须try
            UserProfile.objects.create(username=username,email=email,phone=phone, password=m.hexdigest())
        except Exception as e:
            print('---create user error')
            print(e)
            result = {'code':10103, 'error':'The username is already registed !'}
            return JsonResponse(result)
        #发出 认证激活的 邮件 ?

        #生成随机码
        import random, base64
        random_num = random.randint(1000, 9999)
        random_str = username + '_' + str(random_num)
        #最终链接上的code为
        code_str = base64.urlsafe_b64encode(random_str.encode())
        #随机码存入缓存, 用于激活时,后端进行校验
        r = get_redis_connection('verify_email')
        r.set('verify_email_%s'%(username), random_num)
        active_url = settings.USER_ACTIVE_ADDR+ '?code=%s'%(code_str.decode())
        print('----active_url is ----')
        print(active_url)
        #执行发邮件[同步]
        #send_active_email(email, active_url)
        #发邮件[异步]
        #send_active_email.delay(email, active_url)

        #默认当前用户已登录[签发token-自定义/官方]
        token = make_token(username)
        result = {'code':200, 'username':username, 'data':{'token':token.decode()}}
        return JsonResponse(result)

    elif request.method == 'GET':
        #获取资源
        pass
    #return HttpResponse(json.dumps({'code':200}))
    return JsonResponse({'code':200})






def active_view(request):
    #用户激活操作
    if request.method != 'GET':
        result = {'code':10104, 'error': 'Please use GET'}
        return JsonResponse(result)
    code = request.GET.get('code')
    if not code:
        pass

    try:
        code_str = base64.urlsafe_b64decode(code.encode())
        last_code_str = code_str.decode()
        username, rcode = last_code_str.split('_')
    except Exception as e:
        print('---urlb64 decode error')
        print(e)
        result = {'code':10106, 'error':'Your code is wrong'}
        return JsonResponse(result)

    r = get_redis_connection('verify_email')
    old_code = r.get('verify_email_%s'%(username))

    if not old_code:
        result = {'code':10107, 'error': 'Your code is wrong!'}
        return JsonResponse(result)

    if rcode != old_code.decode():
        result = {'code':10108, 'error': 'Your code is wrong!!'}
        return JsonResponse(result)

    try:
       user = UserProfile.objects.get(username=username,isActive=False)
    except Exception as e:
        result = {'code':10109, 'error':'Your is already actived~'}
        return JsonResponse(result)

    user.isActive = True
    user.save()
    #redis缓存中 删除对应数据
    r.delete('verify_email_%s'%(username))

    return JsonResponse({'code':200, 'data':{'message':'激活成功'}})

def get_weibo_login_url():
    #生成微博授权登录页面地址
    #如果需要高级权限，需要再此申明 scope 详情见笔记
    params = {'response_code':'code',
              'client_id':settings.WEIBO_CLIENT_ID,
              'redirect_uri':settings.WEIBO_RETURN_URL}
    login_url = 'https://api.weibo.com/oauth2/authorize?'
    url = login_url + urlencode(params)
    return url
def weibo_login(request):
    url = get_weibo_login_url()
    return JsonResponse({'code':200,'oauth_url':url})

class WeiBoView(View):
    def get(self,request):
        code = request.GET.get('code')
        #向微博服务器发送请求，用code交换token
        result = get_access_token(code)
        print('---exchange token result is---')
        print(result)
        # return JsonResponse({'code':209})
#{'access_token': '2.00x2cMkFq4R5VC8b3b1311a3J6ZZIB', 'remind_in': '157679999', 'expires_in': 157679999, 'uid': '5263382985', 'isRealName': 'true'}
    # 微博表中，是否有这个数据
    # 如果没有数据，第一次访问---》创建WeiboUser数据
    # 有的话，1）绑定注册过【uid】有值--->签发自己的token  ---同普通登录一样，
    # 2） 没有绑定【uid】为空 ---》 给前端返回200code，触发绑定邮箱
        wuid = result.get('uid')
        access_token = result.get('access_token')
        # 查询微博用户表，判断是否是第一次光临
        try:
            weibo_user = WeiBoUser.objects.get(wuid=wuid)
        except Exception as e:
            # 没有数据  -- 该微博账号第一次登录
            WeiBoUser.objects.create(wuid=wuid, access_token=access_token)
            result = {'code': 201, 'uid': wuid}
            return JsonResponse(result)
        else:
            #非第一次登录 WeiboUser有当前wuid对应的数据
            uid = weibo_user.uid
            if uid:
                #之前已经绑定注册过我们网站的用户
                username  = uid.username
                token = make_token(username)
                result = {'code':200,'username':username,'data':{'token':token.decode()}}
                return JsonResponse(result)
            else:
                #之前用当前微博登录过，但是没有完成后续额绑定注册流程
                result = {'code':201,'uid':wuid}
                return JsonResponse(result)

    def post(self,request):
        #绑定注册
        json_str = request.body
        json_obj = json.loads(json_str)
        wuid = json_obj.get('uid')
        email = json_obj.get('email')
        phone = json_obj.get('phone')
        password = json_obj.get('password')
        username = json_obj.get('username')
        #TODO 检查数据是否存在
        import hashlib
        m = hashlib.md5()
        m.update(password.encode())
        password_m = m.hexdigest()
        #创建userProfile 以及绑定WeiBoUser数据
        #有多个数据进行更新插入时，要考虑是否使用事务
        try:
            with transaction.atomic():
            #创建UserProfile用户数据
                user = UserProfile.objects.create(email=email,username=username,
                                                phone=phone,password=password_m)
                weibo_user = WeiBoUser.objects.get(wuid=wuid)
                #绑定外键
                weibo_user.uid = user
                weibo_user.save()
        except Exception as e:
            print(e)
            print('------FOUND foreign key is error, bind user weibouser-------')
            result = {'code':10113,'error':'The username is already existed'}
            return JsonResponse(result)
        #签发token
        token = make_token(user.username)
        #注册流程
        #将前端传递过来的uid，对应的weibo表的外键绑定到新注册的一个用户数据上
        result = {'code':200,'username':username,'data':{'token':token.decode()}}
        return JsonResponse(result)


def get_access_token(code):
    #向第三方认证服务器发送code 交换token
    token_url = 'https://api.weibo.com/oauth2/access_token'
    #post 请求
    post_data = {
        'client_id':settings.WEIBO_CLIENT_ID,
        'client_secret':settings.WEIBO_CLIENT_SECRET,
        'grant_type':'authorization_code',
        'redirect_uri':settings.WEIBO_RETURN_URL,
        'code':code
    }
    try:
        res = requests.post(token_url,data=post_data)
    except Exception as e:
        print(e)
        print('--weibo login is wrong--')
        return None

    if res.status_code == 200:
        return json.loads(res.text)
    return None


class AccountView(View):
    @logging_check
    def get(self,request):
        userid = request.myuser
        if not userid:
            return JsonResponse({'code': 20101, 'error': '请先登录！'}, json_dumps_params={'ensure_ascii': False})
        try:
            account_obj = account.objects.get(user_id=userid.id)
            if account_obj:
                return JsonResponse({'code':200,'data':{'name':account_obj.name,'id':account_obj.id_card,'bank_id':account_obj.bank_id,'bank_no':account_obj.bank_no,'addr':account_obj.addr,'is_open':account_obj.is_opened}}, json_dumps_params={'ensure_ascii': False})
        except Exception as e:
            print(e)
            return JsonResponse({'code': 20104, 'error': '该用户未开户。'},json_dumps_params={'ensure_ascii': False})

    @logging_check
    def post(self,request):
        #第一步校验参数的合法性
        userid = request.myuser
        if not userid:
            return JsonResponse({'code': 20101, 'error': '请先登录！'},json_dumps_params={'ensure_ascii':False})
        params = json.loads(request.body.decode())
        print(params)
        try:
            name = params['data']['name']
            id = params['data']['id_card']
            bank_id = params['data']['bank_id']
            bank_no = params['data']['bank_no']
            addr = params['data']['addr']
            if not params:
                return JsonResponse({'code': 20102, 'error': '参数不正确，请核对！'},json_dumps_params={'ensure_ascii':False})
        except Exception as e:
            return JsonResponse({'code': 20103, 'error': '参数不正确，请核对！'},json_dumps_params={'ensure_ascii':False})
        #第二步,插入账户表
        try:
            account_obj = account.objects.filter(user_id=userid.id)
            if account_obj:
                return JsonResponse({'code': 20105, 'error': '该账号已经开户。'},json_dumps_params={'ensure_ascii': False})
            account.objects.create(user_id=userid.id,name=name,id_card=id,bank_id=bank_id,bank_no=bank_no,addr=addr,is_opened=1)
        except Exception as e:
            print(e)
            return JsonResponse({'code':20104,'error':'开户失败,请刷新页面后,重新开户。'},json_dumps_params={'ensure_ascii':False})

        return JsonResponse({'code':2010,'msg':'开户成功'},json_dumps_params={'ensure_ascii':False})

"""
time:2020-01-26
author:jz
function:生成手机验证码
"""
def code_view(request):
    #生成验证码
    try:
        if request.method == 'POST':
            params = json.loads(request.body)
            username = params.get('username')
            if username:
                try:
                    user = UserProfile.objects.get(username=username)
                    # 将user 赋值给request,方便视图函数获取当前登录用户
                    phone = user.phone
                except Exception as e:
                    print(e)
                    return JsonResponse({'code': 40209, 'msg': '未找到用户名!'}, json_dumps_params={'ensure_ascii': False})
            else:
                phone = params.get('phone',None)
        elif request.method == 'GET':
            token = request.META.get('HTTP_AUTHORIZATION')
            if not token:
                return JsonResponse({'code': 40208, 'msg': '请先登录!'}, json_dumps_params={'ensure_ascii': False})
            try:
                res = jwt.decode(token, settings.JWT_TOKEN_KEY, algorithms='HS256')
            except Exception as e:
                print(e)
                return JsonResponse({'code': 40208, 'msg': '请先登录!'}, json_dumps_params={'ensure_ascii': False})

            username = res['username']
            user = UserProfile.objects.get(username=username)
            # 将user 赋值给request,方便视图函数获取当前登录用户
            phone = user.phone

        if not phone:
            return JsonResponse({'code': 40209, 'error': '未登录或账号存在异常！'}, json_dumps_params={'ensure_ascii': False})
            #获取redis中储存的code
        conn = get_redis_connection('sms')
        val = conn.get(phone)
        print (val)
        code = ''
        #判断是否已经生成code，若生成判断code是否在有效时间内。
        if val:
            redis_code,time_code = val.decode().split('_')
            time_now = time.time()
            interval = time_now-float(time_code)
            print(redis_code)
            print(interval)
            #判断发送间隔是否小于1分钟，小于则不重复发送code。
            if interval<=60:
                return JsonResponse({'code': 30202, 'msg': '获取频繁，请稍后再试。'}, json_dumps_params={'ensure_ascii': False})\
            #code的有效时间为3分钟。
            elif interval<=int(settings.SMS_VALID_TIME)*60:
                send_sms(phone=phone, code=redis_code)
                return JsonResponse({'code': 200, 'msg': '获取成功','phone':phone}, json_dumps_params={'ensure_ascii': False})
        #生成code
        for i in range(4):
            tep = random.randint(0, 9)
            code = code + str(tep)
        print(code)
        #发送短信
        send_sms(phone=phone, code=code)
        #将code存入redis
        conn.set(phone,code+'_'+str(time.time()))
    except Exception as e:
        print (e)
        return JsonResponse({'code': 30101, 'msg': '获取验证码失败，请重新获取'}, json_dumps_params={'ensure_ascii': False})

    return JsonResponse({'code': 200, 'msg': '获取成功','phone':phone}, json_dumps_params={'ensure_ascii': False})


"""
time:2020-01-27
author:jz
function：修改密码
"""
@check_code
def password_view(request):
    if request.method == 'POST':
        try:
            params = json.loads(request.body)
            password = params.get("password",None)
            username = params.get("username",None)
            print(username)
            if not username:
                if not request.check_code:
                    return JsonResponse({'code': 230201, 'msg': '验证码输入错误，请重新发送！'}, json_dumps_params={'ensure_ascii': False})
                token = request.META.get('HTTP_AUTHORIZATION')
                if not token:
                    return JsonResponse({'code': 40208, 'msg': '请先登录!'}, json_dumps_params={'ensure_ascii': False})
                res = jwt.decode(token, settings.JWT_TOKEN_KEY, algorithms='HS256')
                username = res['username']

            user = UserProfile.objects.get(username=username)
            m = hashlib.md5()
            m.update(password.encode())
            user.password = m.hexdigest()
            user.save()
            return JsonResponse({'code': 200, 'msg': '修改成功!'}, json_dumps_params={'ensure_ascii': False})
            # 将user 赋值给request,方便视图函数获取当前登录用户
        except Exception as e:
            print(e)
            return JsonResponse({'code': 40208, 'msg': '未登录或账号存在异常!'}, json_dumps_params={'ensure_ascii': False})
    else:
        return JsonResponse({'code': 20000, 'msg': '请求方式错误!'}, json_dumps_params={'ensure_ascii': False})


