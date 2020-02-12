"""paopao URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin
from . import views

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    #http://127.0.0.1:8000/v1/users
    url(r'^v1/users', include('user.urls')),
    url(r'^v1/tokens', include('ntoken.urls')),
    # 理财模块-股票
    url(r'^v1/financing/stock', include('stock.urls')),
    # 支付模块
    url(r'^v1/payment', include('payment.urls')),
    # 自选模块
    url(r'^v1/carts', include('carts.urls')),
    # 基金模块
    url(r'^v1/financing/funds', include('funds.urls')),
    # 订单模块
    url(r'^v1/financing/order', include('order.urls')),

]
