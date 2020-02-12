import jwt
from django.http import JsonResponse
import json
import time
from stock.models import account
from user.models import UserProfile
from django.conf import settings
from django_redis import get_redis_connection

def check_code(func):
    def wrapper(request, *args, **kwargs):
        request.check_code = False
        if request.method == 'POST':
            json_obj = json.loads(request.body)
            phone = json_obj.get('phone')
            code = json_obj.get('code')
            if not phone or not code:
                return JsonResponse({'code': 230202, 'msg': '参数不正确，请核对后重新发送！'},
                                    json_dumps_params={'ensure_ascii': False})
            redis = get_redis_connection('sms')
            val = redis.get(phone)
            if not val:
                return JsonResponse({'code': 230203, 'msg': '验证码输入错误！'}, json_dumps_params={'ensure_ascii': False})
            if val:
                redis_code, time_code = val.decode().split('_')
                time_now = time.time()
                interval = time_now - float(time_code)
                if redis_code != code:
                    return JsonResponse({'code': 230204, 'msg': '验证码输入错误！'}, json_dumps_params={'ensure_ascii': False})
                    # code的有效时间为3分钟。
                if interval > int(settings.SMS_VALID_TIME) * 60:
                    return JsonResponse({'code': 230205, 'msg': '验证码过期，请重新获取！'},
                                        json_dumps_params={'ensure_ascii': False})
                request.check_code = True
        else:
            return JsonResponse({'code': 230201, 'msg': '请求方式错误，请重新发送！'}, json_dumps_params={'ensure_ascii': False})

        return func(request, *args, **kwargs)

    return wrapper
