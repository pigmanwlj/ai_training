from import_export import resources
from import_export.admin import ImportExportModelAdmin
from .models import budget
from .models import pr

class budgetResource(resources.ModelResource):

    class Meta:
        model = budget
        skip_unchanged = True
        report_skipped = True
        import_id_fields = ('budgetyear','budgetname')
        #exclude = ('budgetid')
        fields = ('budgetyear','budgetowner','budgetname','budgettype','budgetreminder','budgetplan','approval','budgetmoney','longcontract','countdraw','countdrawmoney')
        #export_order = ('budgetid','budgetyear','budgetowner','budgetname','budgettype','budgetreminder','budgetplan','approval','budgetmoney','longcontract','countdraw','countdrawmoney')


class prResource(resources.ModelResource):

    class Meta:
        model = pr

