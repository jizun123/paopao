from django.core.paginator import Paginator
from django.http import JsonResponse
from django.shortcuts import render
from django.views import View

from django.db.models import Q
from .models import stock

# Create your views here.

"""
time:2020-01-09
author:JZ
function:获取股票数据(分页)
"""
def get_stocks(request):

    print('----get_stock_data------')
    #第一步获取记录的数量

    content = request.GET.get('content', None)
    if content:
        stocks = stock.objects.filter(Q(stock_id__icontains=content) | Q(stock_name__icontains=content)).order_by(
            "stock_id")
    else:
        stocks = stock.objects.all().order_by("stock_id")

    data = []
    #第二部获取分页
    page_num = request.GET['page_num']
    if not page_num:
        page_num = 1
    pageinator = Paginator(stocks,10)
    pages = pageinator.page(page_num)

    for obj in pages:
        data.append({'id':obj.stock_id,'page_no':(int(page_num)-1)*10,'name':obj.stock_name,'price':obj.stock_price,'incre':obj.stock_increase,'concept':obj.stock_concept,'concept_num':obj.stock_concept_num,'value':obj.stock_market_value,'industry':obj.stock_industry})

    return JsonResponse({'code':200,'data':data,'total':len(data)},json_dumps_params={'ensure_ascii':False})



"""
time:2020-01-09
author:JZ
function:获取股票的数量
"""
def get_total(request):

    print('----get_stock------')
    #第一步获取记录的数量
    content = request.GET.get('content', None)
    if content:
        stocks = stock.objects.filter(Q(stock_id__icontains=content) | Q(stock_name__icontains=content))
    else:
        stocks = stock.objects.all()
    return JsonResponse({'code':200,'total':len(stocks)},json_dumps_params={'ensure_ascii':False})



