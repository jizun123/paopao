import json

from django.http import JsonResponse
from django.shortcuts import render
from django.conf import settings
from stock.models import stock
from tools.logging_check import logging_check,account_check

# Create your views here.
from django.views import View
from django_redis import get_redis_connection

"""
time:2020-01-11
author:JZ
function:自选模块(增,删,查)
"""
class cartsView(View):
    @logging_check
    def get(self,request):
        userid = request.myuser
        if not userid:
            return  JsonResponse({'code':10102,'error':'请先登录！'},json_dumps_params={'ensure_ascii': False})
        user_key = 'carts_{0}'.format(userid)
        data = []
        conn = get_redis_connection('carts')
        key_list = conn.hkeys(user_key)
        #hash_list = conn.hgetall(user_key)
        for key in key_list:
            stock_id = key.decode()
            count = conn.hget(user_key,stock_id).decode()
            stock_obj = stock.objects.get(stock_id=stock_id)
            if not stock_obj:
                continue
            stock_name = stock_obj.stock_name
            stock_price = stock_obj.stock_price
            data.append({'stock_id':stock_id,'stock_count':count,'stock_name':stock_name,'stock_price':stock_price})

        return JsonResponse({'code': 200, 'data':data,'count':len(data)}, json_dumps_params={'ensure_ascii': False})

    @logging_check
    @account_check
    def post(self,request):
        #第一步，需要判断当前用户是否已经登录,如果登录的话就返回用户名
        userid = request.myuser
        if not userid:
            return JsonResponse({'code': 10102, 'error': '请先登录！'},json_dumps_params={'ensure_ascii': False})
        if not request.is_open_account:
            return JsonResponse({'code': 40209, 'error': '请先开户!'},json_dumps_params={'ensure_ascii': False})
        user_key = 'carts_{0}'.format(userid)
        params = json.loads(request.body.decode())
        try:
            data = params['data']
            if not data:
                return JsonResponse({'code':10102,'error':'参数不正确，请核对！'},json_dumps_params={'ensure_ascii': False})
        except Exception as e:
            return JsonResponse({'code':10102,'error':'参数不正确，请核对！'},json_dumps_params={'ensure_ascii': False})
        conn = get_redis_connection('carts')

        #遍历，判断股票是否已经添加。
        for cart in data:
            if conn.hexists(user_key,cart):
                count = conn.hget(user_key,cart)
                conn.hset(user_key,cart,int(count.decode())+1)
            else:
                conn.hset(user_key, cart,1)

        return JsonResponse({'code': 200, 'msg': '添加成功！'}, json_dumps_params={'ensure_ascii': False})

    @logging_check
    def delete(self,request):
        # 第一步，需要判断当前用户是否已经登录,如果登录的话就返回用户名
        userid = request.myuser
        if not userid:
            return JsonResponse({'code': 10102, 'error': '请先登录！'},json_dumps_params={'ensure_ascii': False})
        user_key = 'carts_{0}'.format(userid)
        params = json.loads(request.body.decode())
        try:
            data = params['data']
            if not data:
                return JsonResponse({'code': 10102, 'error': '参数不正确，请核对！'},json_dumps_params={'ensure_ascii': False})
        except Exception as e:
            return JsonResponse({'code': 10102, 'error': '参数不正确，请核对！'},json_dumps_params={'ensure_ascii': False})
        conn = get_redis_connection('carts')
        for cart in data:
            stock_id = cart
            if conn.hexists(user_key,stock_id):
                conn.hdel(user_key,stock_id)
        return JsonResponse({'code': 200, 'msg': '删除成功！'},json_dumps_params={'ensure_ascii': False})


"""
time:2020-01-12
author:JZ
function:保存自选模块中股票的信息
"""
@logging_check
def save_carts(request):

    if request.method == 'POST':
        # 第一步，需要判断当前用户是否已经登录,如果登录的话就返回用户名
        userid = request.myuser
        if not userid:
            return JsonResponse({'code': 10102, 'error': '请先登录！'},json_dumps_params={'ensure_ascii': False})
        user_key = 'carts_{0}'.format(userid)
        params = json.loads(request.body.decode())
        try:
            data = params['data']
            if not data:
                return JsonResponse({'code': 10102, 'error': '参数不正确，请核对！'},json_dumps_params={'ensure_ascii': False})
        except Exception as e:
            return JsonResponse({'code': 10102, 'error': '参数不正确，请核对！'},json_dumps_params={'ensure_ascii': False})
        conn = get_redis_connection('carts')
        for cart in data:
            stock_id  = cart.id
            stock_count = cart.count
            if conn.hexists(user_key,stock_id):
                conn.hset(user_key,stock_id,stock_count)

        return JsonResponse({'code': 200, 'msg': '保存成功！'}, json_dumps_params={'ensure_ascii': False})


