from django.db import models

# Create your models here.
class UserProfile(models.Model):

    username = models.CharField(max_length=11, verbose_name='用户名', unique=True)
    password = models.CharField(max_length=32, verbose_name='密码')
    email = models.EmailField()
    phone = models.CharField(max_length=11, verbose_name='手机号')
    isActive = models.BooleanField(default=False, verbose_name='是否激活')
    created_time = models.DateTimeField(auto_now_add=True)
    updated_time = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'user_profile'

    def __str__(self):
        return '%s_%s' %(self.username, self.isActive)




class WeiBoUser(models.Model):
    uid = models.OneToOneField(UserProfile,null=True,on_delete=models.SET_NULL)#一对一
    wuid = models.CharField(max_length=50,db_index=True)#索引
    access_token = models.CharField(max_length=100)
    class Meta:
        db_table = 'weibo_user'
    def __str__(self):
        return '%s_%s'%(self.uid,self.wuid)




class account(models.Model):

    user_id = models.IntegerField(max_length=11,verbose_name='用户Id',unique=True)
    name = models.CharField(max_length=11, verbose_name='姓名')
    id_card = models.CharField(max_length=18, verbose_name='身份证号',unique=True)
    bank_id = models.IntegerField(max_length=3, verbose_name='所属银行' )
    bank_no = models.IntegerField(max_length=19, verbose_name='银行卡号')
    addr = models.CharField(max_length=1024, verbose_name='居住地址',default='')
    is_opened = models.IntegerField(max_length=1,verbose_name='是否开户',default=0)
    created_time = models.DateTimeField(auto_now_add=True)
    updated_time = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'account'

    def __str__(self):
        return '%s_%s' %(self.name, self.id_card)





































