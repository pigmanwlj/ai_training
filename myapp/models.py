from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

# Create your models here.

class budget(models.Model):
    '''自定义budget表对应的Model类'''
    #定义属性：默认主键自增id字段可不写
    budgetid = models.AutoField("预算序号",primary_key = True)
    budgetyear = models.DecimalField("预算年份",max_digits = 4,decimal_places = 0)
    budgetowner = models.CharField("负责人",max_length = 128,null = True,blank = True)   
    budgetname = models.CharField("预算名称",max_length = 128)
    CAPEX = 'CAPEX'
    OPEX = 'OPEX'
    budgettype_choices = ((OPEX, 'OPEX'),(CAPEX, 'CAPEX'),)
    budgettype = models.CharField("预算类型",max_length = 6,choices = budgettype_choices,default = OPEX)
    budgetreminder = models.DateField("预算使用提醒日期",null = True,blank = True)
    budgetplan = models.TextField("使用计划",null = True,blank = True,default = "暂时无计划")
    approval = models.BooleanField("预算核准",default = False)
    budgetmoney = models.DecimalField("预算金额(未税)",max_digits = 16,decimal_places = 2,null = True,blank = True,default = 0.00)
    longcontract = models.BooleanField("是否长期合同",default = False)
    countdraw = models.BooleanField("是否计提",default = False)
    countdrawmoney = models.DecimalField("计提金额(未税)",max_digits = 16,decimal_places = 2,null = True,blank = True,default = 0.00)
    #pr = models.BooleanField("采购申请")
    #contractbegin = models.DateField("合同起始",null = True,blank = True)
    #contractend = models.DateField("合同终止",null = True,blank = True)
    #checkaccept = models.BooleanField("合同验收")
    #percentage =  models.DecimalField("验收百分比",max_digits = 5,decimal_places = 2,null = True,blank = True,default = 0.00,validators=[MinValueValidator(0.00),MaxValueValidator(100.00)])
    #summary = models.CharField("备注",max_length = 128,null = True,blank = True)
    #attachment = models.FileField("附件",upload_to='uploads/%Y/%m/%d/',null = True,blank = True)

    # 定义默认输出格式
    def __str__(self):
        return "%d:%d:%s:%s:%s:%s:%d:%d:%d:%d:%d"%(self.budgetid,self.budgetyear,self.budgetowner,self.budgetname,self.budgettype,self.budgetplan,self.approval,self.budgetmoney,self.longcontract,self.countdraw,self.countdrawmoney)

    # 自定义对应的表名，默认表名：myapp_budget
    class Meta:
        db_table = "budget"
        verbose_name = '浏览预算数据'
        verbose_name_plural = '预算数据'

#results = budget.objects.filter(budgetid=1)
#results = budget.objects.raw("select * from budget where budget >= 5")


class pr(models.Model):
    '''自定义pr表对应的Model类'''
    #定义属性：默认主键自增id字段可不写
    prid = models.AutoField("采购序号",primary_key = True)
    frombudget = models.ForeignKey('budget',on_delete = models.CASCADE,db_column = 'budgetid')
    prname = models.CharField("采购名称",max_length = 128,default = '')
    po = models.DecimalField("PO号",max_digits = 10,decimal_places = 0,default = 0)
    contract = models.BooleanField("合同完成",default = False)
    contractbegin = models.DateField("合同起始日期",null = True,blank = True)
    contractend = models.DateField("合同终止日期",null = True,blank = True)
    contractmoney = models.DecimalField("本年合同金额(未税)",max_digits = 16,decimal_places = 2,default = 0.00)
    tax = models.DecimalField("税率",max_digits = 5,decimal_places = 2,default = 0.00,validators=[MinValueValidator(0.00),MaxValueValidator(100.00)])
    #moneywithtax = models.DecimalField("合同金额(含税)",max_digits = 16,decimal_places = 2,null = True,blank = True,editable = False)
    checkaccept = models.BooleanField("合同验收",default = False)
    percentage = models.DecimalField("验收比例",max_digits = 5,decimal_places = 2,default = 0.00,validators=[MinValueValidator(0.00),MaxValueValidator(100.00)])
    paymentplan = models.TextField("使用计划",null = True,blank = True,default = "暂时无计划")
    attachment = models.FileField("合同附件",upload_to='uploads/%Y/%m/%d/',null = True,blank = True)

    # 定义默认输出格式
    def __str__(self):
        return "%d:%s:%s:%d:%d:%s:%s:%d:%d:%d:%d:%s:%s"%(self.prid,self.frombudget,self.prname,self.po,self.contract,self.contractbegin,self.contractend,self.contractmoney,self.tax,self.checkaccept,self.percentage,self.paymentplan,self.attachment)

    # 自定义对应的表名，默认表名：myapp_pr
    class Meta:
        db_table = "pr"
        verbose_name = '浏览采购数据'
        verbose_name_plural = '采购数据'


class training_platform(pr):
    class Meta:
        proxy = True
        verbose_name = '训练平台'
        verbose_name_plural = '训练平台'

