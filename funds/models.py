from django.db import models

# Create your models here.

from django.db import models
from django.db.models import *

# Create your models here.



class funds(models.Model):

    funds_id =  CharField(max_length=6,verbose_name='基金代码',unique=True)
    funds_name =  CharField(max_length=32, verbose_name='基金简称')
    funds_accu = DecimalField(max_digits=10,decimal_places=4,verbose_name='累计净值')
    funds_day_val = DecimalField(max_digits=10,decimal_places=4,verbose_name='日增长值')
    funds_day_rate= DecimalField(max_digits=10,decimal_places=4,verbose_name='日增长率')
    funds_year_rate = DecimalField(max_digits=10,decimal_places=2, verbose_name='申购状态')

    class Meta():
        db_table = 'funds'

    def __str__(self):

        return '{0}_{1}'.format(self.funds_id,self.funds_name)

