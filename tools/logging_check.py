import jwt
from django.http import JsonResponse

from stock.models import account
from user.models import UserProfile
from django.conf import settings

def logging_check(func):
    def wrapper(self, request, *args, **kwargs):
        token = request.META.get('HTTP_AUTHORIZATION')
        if not token:
            return JsonResponse({'code': 40208, 'error': '请先登录!'}, json_dumps_params={'ensure_ascii': False})
        try:
            res = jwt.decode(token, settings.JWT_TOKEN_KEY, algorithms='HS256')
        except Exception as e:
            print(e)
            return JsonResponse({'code': 40208, 'error': '请先登录!'}, json_dumps_params={'ensure_ascii': False})

        username = res['username']
        user = UserProfile.objects.get(username=username)
        #将user 赋值给request,方便视图函数获取当前登录用户
        request.myuser = user

        return func(self, request, *args, **kwargs)
    return wrapper

def account_check(func):
    def wrapper(self, request, *args, **kwargs):
        user = request.myuser
        if not user:
            return JsonResponse({'code': 40208, 'error': '请先登录!'}, json_dumps_params={'ensure_ascii': False})
        try:
            account_obj = account.objects.get(user_id=user.id)
            if not account_obj.is_opened:
                return JsonResponse({'code': 40209, 'error': '请先开户!'},json_dumps_params={'ensure_ascii': False})
        except Exception as e:
            return JsonResponse({'code': 40209, 'error': '请先开户!'}, json_dumps_params={'ensure_ascii': False})
        # 将user 赋值给request,方便视图函数获取当前登录用户
        request.is_open_account = True
        return func(self, request, *args, **kwargs)

    return wrapper





