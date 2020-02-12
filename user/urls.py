from django.conf.urls import url
from . import views
from .views import AccountView

urlpatterns = [
    #127.0.0.1:8000/v1/users
    url(r'^$', views.user_view),
    #获取验证码
    url(r'/code$',views.code_view),
    url(r'/reset$',views.password_view),
    #http://127.0.0.1:8000/v1/users/activation?code=xxxx
    url(r'^/activation$', views.active_view),
    url(r'^/account$', AccountView.as_view()),
    #地址相关
    #http://127.0.0.1:8000/v1/users/guoxiao7/address
    #get-查询当前用户的所有地址
    #post-给当前用户创建一个地址
    #微薄授权相关
    url(r'^/weibo/authorization$',views.weibo_login),
    #接受前端传来的code，去新浪验证服务器交换access——token
    url(r'^/weibo/users$',views.WeiBoView.as_view()),


]
