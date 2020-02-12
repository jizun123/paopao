from django.db import models

# Create your models here.

from django.db import models
from django.db.models import *

# Create your models here.

class order(models.Model):

    user_id = IntegerField(max_length=11,verbose_name='用户Id')
    fian_code = CharField(max_length=1042,verbose_name='股票或基金的代码')
    fian_price = FloatField(max_length=11,verbose_name='订单支付的钱')
    fian_type = IntegerField(max_length=1, verbose_name='基金或股票的类型',default=0)
    order_status = IntegerField(max_length=1,verbose_name='订单的状态')
    created_time = models.DateTimeField(auto_now_add=True)
    updated_time = models.DateTimeField(auto_now=True)

    class Meta():
        db_table = 'order'

    def __str__(self):

        return '{0}_{1}'.format(self.funds_id,self.funds_name)

