from django.db import models

# Create your models here.

class appvpn(models.Model):
    '''自定义appvpn表对应的Model类'''
    #定义属性：默认主键自增id字段可不写
    id = models.AutoField("序号",primary_key = True)
    site = models.CharField("基地",max_length = 16)
    type = models.CharField("类型",max_length = 16,null = True,blank = True)
    average = models.IntegerField("平均值")
    peak = models.IntegerField("峰值")
    max = models.IntegerField("最大并发")
    comment = models.CharField("备注",max_length = 16,null = True,blank = True)

    # 定义默认输出格式
    def __str__(self):
        return "%d:%s:%s:%d:%d:%d:%s"%(self.id,self.site,self.type,self.average,self.peak,self.max,self.comment)

    # 自定义对应的表名，默认表名：myapp_appvpn
    class Meta:
        db_table = "appvpn"
        verbose_name = '浏览基地VPN数据'  
        verbose_name_plural = '基地VPN数据'


class appjump(models.Model):
    '''自定义appvpn表对应的Model类'''
    #定义属性：默认主键自增id字段可不写
    id = models.AutoField("序号",primary_key = True)
    site = models.CharField("基地",max_length = 16)
    type = models.CharField("类型",max_length = 16,null = True,blank = True)
    average = models.IntegerField("平均值")
    peak = models.IntegerField("峰值")
    max = models.IntegerField("最大并发")
    comment = models.CharField("备注",max_length = 16,null = True,blank = True)

    # 定义默认输出格式
    def __str__(self):
        return "%d:%s:%s:%d:%d:%d:%s"%(self.id,self.site,self.type,self.average,self.peak,self.max,self.comment)

    # 自定义对应的表名，默认表名：myapp_appjump
    class Meta:
        db_table = "appjump"
        verbose_name = '浏览基地跳板机数据'  
        verbose_name_plural = '基地跳板机数据'

