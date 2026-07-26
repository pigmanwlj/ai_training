from django.contrib import admin

# from myapp.models import budget
# from myapp.models import pr

from import_export.admin import ImportExportModelAdmin
# Register your models here.
from .resource import budgetResource

from django.shortcuts import redirect
from myapp.models import budget, pr, training_platform

#budget模型的管理器(装饰器写法)
@admin.register(budget)
class budgetAdmin(ImportExportModelAdmin):
    #listdisplay设置要显示在列表中的字段（id字段是Django模型的默认主键）
    list_display = ('budgetid','budgetyear','budgetowner','budgetname','budgettype','budgetreminder','budgetplan','approval','budgetmoney','longcontract','countdraw','countdrawmoney')

    #def budgetid_prid(self, obj):
    #    return obj.budgetid.prid
    #budgetid_prid.short_description = 'PR Identity'

    #设置哪些字段可以点击进入编辑界面
    list_display_links = ('budgetyear','budgetowner','budgetname','budgettype','budgetreminder','budgetplan','approval','budgetmoney','longcontract','countdraw','countdrawmoney')

    #list_per_page设置每页显示多少条记录，默认是100条
    list_per_page = 10

    #ordering设置默认排序字段，负号表示降序排序
    ordering = ('budgetid',)  #-id降序

    #list_editable 设置默认可编辑字段
    #list_editable = ['age','sex','classid']

    search_fields = ('budgetid','budgetyear','budgetowner','budgetname')

    resource_class = budgetResource


#pr模型的管理器(装饰器写法)
@admin.register(pr)
class prAdmin(ImportExportModelAdmin):
    #listdisplay设置要显示在列表中的字段（id字段是Django模型的默认主键）
    list_display = ('prid','frombudget','prname','po','contract','contractbegin','contractend','contractmoney','tax','checkaccept','percentage','paymentplan','attachment')

    #设置哪些字段可以点击进入编辑界面
    list_display_links = ('frombudget','prname','po','contract','contractbegin','contractend','contractmoney','tax','checkaccept','percentage','paymentplan','attachment')

    #list_per_page设置每页显示多少条记录，默认是100条
    list_per_page = 10

    #ordering设置默认排序字段，负号表示降序排序
    ordering = ('prid',)  #-id降序

    #list_editable 设置默认可编辑字段
    #list_editable = ['contractmoney','tax']

    search_fields = ('prid','prid','prname')

    #resource_class = prResource


@admin.register(training_platform)
class trainingPlatformAdmin(admin.ModelAdmin):
    def get_model_perms(self, request):
        if request.user.is_staff:
            return {'view': True}
        return {}

    def has_view_permission(self, request, obj=None):
        return request.user.is_staff

    def changelist_view(self, request, extra_context=None):
        return redirect('training_page')

