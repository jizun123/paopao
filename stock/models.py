from django.db import models
from django.db.models import *

# Create your models here.



class stock(models.Model):
    stock_id =  CharField(max_length=6,verbose_name='股票代码',unique=True)
    stock_name =  CharField(max_length=32, verbose_name='股票简称')
    stock_price = DecimalField(max_digits=10,decimal_places=2,verbose_name='股票现价(元)')
    stock_increase = DecimalField(max_digits=10,decimal_places=2,verbose_name='股票涨幅(%)')
    stock_concept =  CharField(max_length=1024, verbose_name='概念解析')
    stock_concept_num = IntegerField(max_length=5,verbose_name='所属概念数量')
    stock_market_value = CharField(max_length=16,verbose_name='市值(亿)')
    stock_industry = CharField(max_length=32, verbose_name='所属行业')

    class Meta():
        db_table = 'stock'

    def __str__(self):

        return '{0}_{1}'.format(self.stock_id,self.stock_name)


class account(models.Model):

    user_id = models.IntegerField(max_length=11,verbose_name='用户Id',unique=True)
    name = models.CharField(max_length=11, verbose_name='姓名')
    id_card = models.CharField(max_length=18, verbose_name='身份证号',unique=True)
    bank_id = models.IntegerField(max_length=3, verbose_name='所属银行' )
    bank_no = models.CharField(max_length=20, verbose_name='银行卡号')
    addr = models.CharField(max_length=1024, verbose_name='居住地址',default='')
    is_opened = models.IntegerField(max_length=1,verbose_name='是否开户',default=0)
    created_time = models.DateTimeField(auto_now_add=True)
    updated_time = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'account'

    def __str__(self):
        return '%s_%s' %(self.name, self.id_card)
