from django.core.paginator import Paginator
from django.http import JsonResponse
from django.shortcuts import render
from django.views import View
from django.db.models import Q

from .models import funds

"""
time:2020-01-17
author:JZ
function:获取基金数据(分页)
"""
def get_funds(request):

    print('----get_funds_data------')
    #第一步获取记录的数量
    content = request.GET.get('content',None)
    if content:
        fund_list = funds.objects.filter(Q(funds_id__icontains=content)|Q(funds_name__icontains=content)).order_by("funds_id")
    else:
        fund_list = funds.objects.all().order_by("funds_id")
    data = []
    #第二部获取分页
    page_num = request.GET['page_num']
    if not page_num:
        page_num = 1
    pageinator = Paginator(fund_list,10)
    pages = pageinator.page(page_num)

    for obj in pages:
        data.append({'id':obj.funds_id,'page_no':(int(page_num)-1)*10,'name':obj.funds_name,'accu':obj.funds_accu,'day_val':obj.funds_day_val,'day_rate':obj.funds_day_rate,'year_rate':obj.funds_year_rate})

    return JsonResponse({'code':200,'data':data,'total':len(data)},json_dumps_params={'ensure_ascii':False})



"""
time:2020-01-17
author:JZ
function:获取基金的数量
"""
def get_total(request):

    print('----get_funds------')
    #第一步获取记录的数量
    content = request.GET.get('content',None)
    if content:
        fund_list = funds.objects.filter(Q(funds_id__icontains=content)|Q(funds_name__icontains=content))
    else:
        fund_list = funds.objects.all()
    return JsonResponse({'code':200,'total':len(fund_list)},json_dumps_params={'ensure_ascii':False})
