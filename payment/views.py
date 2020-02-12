import copy
import json

#from alipay import AliPay
from django.http import JsonResponse, HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from order.models import order
# Create your views here.

from django.views import View
from django.conf  import settings

app_private_key_string = open(settings.ALIPAY_KEY_FILES + 'app_private_key.pem').read()
alipay_public_key_string = open(settings.ALIPAY_KEY_FILES+'alipay_public_key.pem').read()


"""
time:2020-01-10
author:JZ
function:此视图类用来进行支付宝支付的跳转
"""
class JumpView(View):

    def post(self,request):
        #第一步，应该判断是否登录和是否已经开户，目前没办法做，暂定。(用装饰器)
        #第二步，接收参数，验证参数的有效性
        params = json.loads(request.body)
        try:
            trade_no = params['trade_no']
            amount_price = float(params['amount_price'])
            return_url = params['return_url']
        except Exception as e:
             result ={'code':10101,'error':'参数有误,请核对后重新发送。'}
             return result

         #这里需要校验订单号是不是正确的，需要从订单表里核对暂时不核对。
         #第三步，创建AliPay对象。
        alipay = AliPay(
             appid=settings.ALIPAY_APP_ID,
             app_notify_url=None,
             app_private_key_string=app_private_key_string,
             alipay_public_key_string=alipay_public_key_string,
             sign_type='RSA2',
             debug=True
         )
        order_string = alipay.api_alipay_trade_page_pay(
             out_trade_no=trade_no,
             total_amount=amount_price,
             subject='泡泡金融',
             # 这个参数是get请求
             return_url=settings.LOCAL_URL+'v1/payment/result',
             # 这个参数是post请求
             notify_url=settings.LOCAL_URL+'v1/payment/result',
         )  # 网站页面支付
        pay_url = "https://openapi.alipaydev.com/gateway.do?" + order_string
        return JsonResponse({'code': 200, 'pay_url': pay_url}, json_dumps_params={'ensure_ascii': False})




"""
time:2020-01-11
author:JZ
function:此视图类用来接收支付宝支付结果。
"""
class ResultView(View):

    def get_verify(self, data):
        # 支付宝传回 基础信息 + sign(除了签名以外的数据 +签名)
        pass
        # r_data = copy.deepcopy(data)
        # sign = r_data.pop('sign')
        # alipay = AliPay(
        #     appid=settings.ALIPAY_APP_ID,
        #     app_notify_url=None,
        #     app_private_key_string=app_private_key_string,
        #     alipay_public_key_string=alipay_public_key_string,
        #     sign_type='RSA2',
        #     debug=True
        # )
        # #校验信息
        # is_verify = alipay.verify(r_data, sign)
        # return r_data, is_verify, alipay

    #post方法接收支付宝异步回调,指的是notify_url,这个地方主要是作为参数通知商家。
    def post(self, request):
        pass
        # print('我正在执行post！')
        # # 1.获取参数字典,验签结果,alipay对象
        # request_data = {k: request.POST[k] for k in request.GET.keys()}
        # success_dict, ali_verify, alipay = self.get_verify(request_data)
        # # 2.根据验证结果进行业务处理
        # if ali_verify is True:
        #     trade_status = success_dict.get('trade_status', None)
        #     if trade_status == "TRADE_SUCCESS":
        #         print('更改订单状态')
        #         order_id = success_dict.get('out_trade_no', None)
        #         try:
        #             order_obj = order.objects.get(order_id=order_id)
        #             order_obj.order_status=1
        #             order_obj.save()
        #         except Exception as e:
        #             print(e)
        #             print('更新订单状态发生错误,订单号为:'+order_id)
        #         # 通过trade_no去订单表里查询订单的状态,暂时不做。
        #         return HttpResponse("success")
        # else:
        #     return HttpResponse("error")


    #get方式接收支付宝的同步跳转,指的是return_url，这个主要是用户方起作用。
    def get(self, request):
        pass
        # #获取所有的key和value
        # request_data = {k: request.GET[k] for k in request.GET.keys()}
        # #校验签名是否正确
        # success_dict, ali_verify, alipay = self.get_verify(request_data)
        # # 订单状态：暂定，目前还没有订单接口。
        # type=-1
        # url=''
        # if ali_verify is True:
        #     order_id = success_dict.get('out_trade_no', None)
        #     try:
        #         order_obj = order.objects.get(id=order_id)
        #         order_obj.order_status = 1
        #         order_obj.save()
        #         type = order_obj.fian_type
        #     except Exception as e:
        #         print(e)
        #         print('更新订单状态发生错误,订单号为:' + order_id)
        #     # 主动查询
        # else:
        #     print('-----非法访问-------')
        #
        # if type==-1:
        #     url = settings.LOCAL_URL+'static/templates/index.html'
        # elif type==0:
        #     url = settings.LOCAL_URL+'static/templates/order_funds.html'
        # elif type==1:
        #     url = settings.LOCAL_URL+'static/templates/order_stocks.html'
        # return HttpResponseRedirect(url)