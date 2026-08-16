from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

# Create your models here.


class budget(models.Model):
    """自定义budget表对应的Model类"""

    # 定义属性：默认主键自增id字段可不写
    budgetid = models.AutoField("预算序号", primary_key=True)
    budgetyear = models.DecimalField("预算年份", max_digits=4, decimal_places=0)
    budgetowner = models.CharField("负责人", max_length=128, null=True, blank=True)
    budgetname = models.CharField("预算名称", max_length=128)
    CAPEX = "CAPEX"
    OPEX = "OPEX"
    budgettype_choices = ((OPEX, "OPEX"), (CAPEX, "CAPEX"))
    budgettype = models.CharField("预算类型", max_length=6, choices=budgettype_choices, default=OPEX)
    budgetreminder = models.DateField("预算使用提醒日期", null=True, blank=True)
    budgetplan = models.TextField("使用计划", null=True, blank=True, default="暂时无计划")
    approval = models.BooleanField("预算核准", default=False)
    budgetmoney = models.DecimalField("预算金额(未税)", max_digits=16, decimal_places=2, null=True, blank=True, default=0.00)
    longcontract = models.BooleanField("是否长期合同", default=False)
    countdraw = models.BooleanField("是否计提", default=False)
    countdrawmoney = models.DecimalField("计提金额(未税)", max_digits=16, decimal_places=2, null=True, blank=True, default=0.00)
    # pr = models.BooleanField("采购申请")
    # contractbegin = models.DateField("合同起始", null=True, blank=True)
    # contractend = models.DateField("合同终止", null=True, blank=True)
    # checkaccept = models.BooleanField("合同验收")
    # percentage = models.DecimalField(
    #     "验收百分比",
    #     max_digits=5,
    #     decimal_places=2,
    #     null=True,
    #     blank=True,
    #     default=0.00,
    #     validators=[MinValueValidator(0.00), MaxValueValidator(100.00)],
    # )
    # summary = models.CharField("备注", max_length=128, null=True, blank=True)
    # attachment = models.FileField("附件", upload_to="uploads/%Y/%m/%d/", null=True, blank=True)

    # 定义默认输出格式
    def __str__(self):
        return "%d:%d:%s:%s:%s:%s:%d:%d:%d:%d:%d" % (
            self.budgetid,
            self.budgetyear,
            self.budgetowner,
            self.budgetname,
            self.budgettype,
            self.budgetplan,
            self.approval,
            self.budgetmoney,
            self.longcontract,
            self.countdraw,
            self.countdrawmoney,
        )

    # 自定义对应的表名，默认表名：myapp_budget
    class Meta:
        db_table = "budget"
        verbose_name = "浏览预算数据"
        verbose_name_plural = "预算数据"


class pr(models.Model):
    """自定义pr表对应的Model类"""

    # 定义属性：默认主键自增id字段可不写
    prid = models.AutoField("采购序号", primary_key=True)
    frombudget = models.ForeignKey("budget", on_delete=models.CASCADE, db_column="budgetid")
    prname = models.CharField("采购名称", max_length=128, default="")
    po = models.DecimalField("PO号", max_digits=10, decimal_places=0, default=0)
    contract = models.BooleanField("合同完成", default=False)
    contractbegin = models.DateField("合同起始日期", null=True, blank=True)
    contractend = models.DateField("合同终止日期", null=True, blank=True)
    contractmoney = models.DecimalField("本年合同金额(未税)", max_digits=16, decimal_places=2, default=0.00)
    tax = models.DecimalField(
        "税率",
        max_digits=5,
        decimal_places=2,
        default=0.00,
        validators=[MinValueValidator(0.00), MaxValueValidator(100.00)],
    )
    # moneywithtax = models.DecimalField("合同金额(含税)", max_digits=16, decimal_places=2, null=True, blank=True, editable=False)
    checkaccept = models.BooleanField("合同验收", default=False)
    percentage = models.DecimalField(
        "验收比例",
        max_digits=5,
        decimal_places=2,
        default=0.00,
        validators=[MinValueValidator(0.00), MaxValueValidator(100.00)],
    )
    paymentplan = models.TextField("使用计划", null=True, blank=True, default="暂时无计划")
    attachment = models.FileField("合同附件", upload_to="uploads/%Y/%m/%d/", null=True, blank=True)

    # 定义默认输出格式
    def __str__(self):
        return "%d:%s:%s:%d:%d:%s:%s:%d:%d:%d:%d:%s:%s" % (
            self.prid,
            self.frombudget,
            self.prname,
            self.po,
            self.contract,
            self.contractbegin,
            self.contractend,
            self.contractmoney,
            self.tax,
            self.checkaccept,
            self.percentage,
            self.paymentplan,
            self.attachment,
        )

    # 自定义对应的表名，默认表名：myapp_pr
    class Meta:
        db_table = "pr"
        verbose_name = "浏览采购数据"
        verbose_name_plural = "采购数据"


class TrainingContainer(models.Model):
    class Status(models.TextChoices):
        FREE = "free", "Free"
        STARTING = "starting", "Starting"
        RUNNING = "running", "Running"
        STOPPED = "stopped", "Stopped"
        ERROR = "error", "Error"

    class Profile(models.TextChoices):
        A100 = "ollama_a100", "A100"
        H800 = "ollama_h800", "H800"
        RTX5090 = "ollama_rtx5090", "RTX5090"

    slot_name = models.CharField("槽位名", max_length=32, unique=True)
    profile = models.CharField("硬件配置", max_length=32, choices=Profile.choices)
    pod_name = models.CharField("容器名", max_length=128, unique=True)

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="training_containers",
    )
    status = models.CharField("状态", max_length=16, choices=Status.choices, default=Status.FREE)
    host_port = models.PositiveIntegerField("主机端口", null=True, blank=True)
    token_nonce = models.CharField("连接签名随机值", max_length=64, blank=True, default="")
    allocated_at = models.DateTimeField("分配时间", null=True, blank=True)
    started_at = models.DateTimeField("启动时间", null=True, blank=True)
    stopped_at = models.DateTimeField("停止时间", null=True, blank=True)
    updated_at = models.DateTimeField("更新时间", auto_now=True)

    def __str__(self):
        owner_name = self.owner.username if self.owner else "none"
        return f"{self.slot_name}:{self.profile}:{self.pod_name}:{owner_name}:{self.status}"

    class Meta:
        db_table = "training_container"
        verbose_name = "训练容器"
        verbose_name_plural = "训练容器"


class training_platform(TrainingContainer):
    class Meta:
        proxy = True
        verbose_name = "训练平台"
        verbose_name_plural = "训练平台"

