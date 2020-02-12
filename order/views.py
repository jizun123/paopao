import json

from django.http import JsonResponse
from django.shortcuts import render
from django.views import View

from funds.models import funds
from order.models import order
from stock.models import stock
from tools.logging_check import logging_check


class OrderView(View):
    @logging_check
    def get(self, request):
        # 第一步校验参数的合法性
        userid = request.myuser
        if not userid:
            return JsonResponse({'code': 30101, 'error': '请先登录！'}, json_dumps_params={'ensure_ascii': False})
        type = json.loads(request.GET['type'])
        print(type)
        if not type in [1, 0]:
            return JsonResponse({'code': 30101, 'error': '参数不对！'}, json_dumps_params={'ensure_ascii': False})
        data_fin = []
        data_unf = []
        if type == 0:
            order_list = order.objects.filter(fian_type=0,user_id=userid.id)
            for order_obj in order_list:
                if order_obj.order_status == 0:
                    data_unf.append(
                        {'id': order_obj.id, 'code': order_obj.fian_code, 'name': self.get_name(0, order_obj.fian_code),
                         'price': order_obj.fian_price})
                elif order_obj.order_status == 1:
                    data_fin.append(
                        {'id': order_obj.id, 'code': order_obj.fian_code, 'name': self.get_name(0, order_obj.fian_code),
                         'price': order_obj.fian_price})
        elif type == 1:
            order_list = order.objects.filter(fian_type=1,user_id=userid.id)
            for order_obj in order_list:
                code_list = order_obj.fian_code.split(',')
                for code_obj in code_list:
                    if order_obj.order_status == 0:
                        data_unf.append({'id': order_obj.id, 'code': code_obj,'name': self.get_name(1, code_obj), 'price': order_obj.fian_price})
                    elif order_obj.order_status == 1:
                        data_fin.append({'id': order_obj.id, 'code': code_obj,'name': self.get_name(1, code_obj), 'price': order_obj.fian_price})

        else:
            return JsonResponse({'code': 30101, 'error': '参数不对！'}, json_dumps_params={'ensure_ascii': False})

        return JsonResponse({'code': 200, 'data_unf': data_unf, 'data_fin': data_fin},
                            json_dumps_params={'ensure_ascii': False})

    @logging_check
    def post(self, request):
        # 第一步校验参数的合法性
        userid = request.myuser
        if not userid:
            return JsonResponse({'code': 30101, 'error': '请先登录！'}, json_dumps_params={'ensure_ascii': False})
        params = json.loads(request.body.decode())
        print(params)
        try:
            fian_code = params['id']
            fian_price = params['price']
            fian_type = params['type']
            if not params:
                return JsonResponse({'code': 30102, 'error': '参数不正确，请核对！'}, json_dumps_params={'ensure_ascii': False})
        except Exception as e:
            return JsonResponse({'code': 30103, 'error': '参数不正确，请核对！'}, json_dumps_params={'ensure_ascii': False})
        # 第二步,插入订单表
        try:
            order_obj = order.objects.create(user_id=userid.id, fian_code=fian_code, fian_price=fian_price,
                                             fian_type=fian_type, order_status=0)
        except Exception as  e:
            print(e)
            return JsonResponse({'code': 30104, 'error': '创建订单失败，请重新尝试！'}, json_dumps_params={'ensure_ascii': False})
        return JsonResponse({'code': 200, 'data': {'order_id': order_obj.id, 'order_price': order_obj.fian_price}},
                            json_dumps_params={'ensure_ascii': False})

    def get_name(self, type, id):
        name = ''
        try:
            if type == 0:
                print(id)
                funds_obj = funds.objects.get(funds_id=id)
                name = funds_obj.funds_name
            elif type == 1:
                stock_obj = stock.objects.get(stock_id=id)
                name = stock_obj.stock_name
        except Exception as e:
            print(e)
        return name
