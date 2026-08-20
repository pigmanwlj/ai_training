from django.contrib import admin
from django.shortcuts import redirect
from import_export.admin import ImportExportModelAdmin

from .models import PodUsageSession, TrainingContainer, budget, pr, training_platform
from .resource import budgetResource


@admin.register(budget)
class budgetAdmin(ImportExportModelAdmin):
    list_display = (
        "budgetid",
        "budgetyear",
        "budgetowner",
        "budgetname",
        "budgettype",
        "budgetreminder",
        "budgetplan",
        "approval",
        "budgetmoney",
        "longcontract",
        "countdraw",
        "countdrawmoney",
    )

    list_display_links = (
        "budgetyear",
        "budgetowner",
        "budgetname",
        "budgettype",
        "budgetreminder",
        "budgetplan",
        "approval",
        "budgetmoney",
        "longcontract",
        "countdraw",
        "countdrawmoney",
    )

    list_per_page = 10
    ordering = ("budgetid",)
    search_fields = ("budgetid", "budgetyear", "budgetowner", "budgetname")
    resource_class = budgetResource


@admin.register(pr)
class prAdmin(ImportExportModelAdmin):
    list_display = (
        "prid",
        "frombudget",
        "prname",
        "po",
        "contract",
        "contractbegin",
        "contractend",
        "contractmoney",
        "tax",
        "checkaccept",
        "percentage",
        "paymentplan",
        "attachment",
    )

    list_display_links = (
        "frombudget",
        "prname",
        "po",
        "contract",
        "contractbegin",
        "contractend",
        "contractmoney",
        "tax",
        "checkaccept",
        "percentage",
        "paymentplan",
        "attachment",
    )

    list_per_page = 10
    ordering = ("prid",)
    search_fields = ("prid", "prname")


@admin.register(training_platform)
class trainingPlatformAdmin(admin.ModelAdmin):
    list_display = (
        "slot_name",
        "profile",
        "pod_name",
        "owner",
        "status",
        "host_port",
        "allocated_at",
        "started_at",
        "stopped_at",
        "updated_at",
    )
    list_filter = ("profile", "status")
    search_fields = ("slot_name", "pod_name", "owner__username")

    def get_model_perms(self, request):
        if request.user.is_staff:
            return {"view": True}
        return {}

    def has_view_permission(self, request, obj=None):
        return request.user.is_staff

    def changelist_view(self, request, extra_context=None):
        return redirect("training_page")


@admin.register(TrainingContainer)
class TrainingContainerAdmin(admin.ModelAdmin):
    list_display = (
        "slot_name",
        "profile",
        "pod_name",
        "owner",
        "status",
        "host_port",
        "allocated_at",
        "started_at",
        "stopped_at",
        "updated_at",
    )
    list_filter = ("profile", "status")
    search_fields = ("slot_name", "pod_name", "owner__username")
    readonly_fields = ("allocated_at", "started_at", "stopped_at", "updated_at", "token_nonce")


@admin.register(PodUsageSession)
class PodUsageSessionAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "profile",
        "pod_name",
        "container",
        "started_at",
        "stopped_at",
        "created_at",
        "updated_at",
    )
    list_filter = ("profile", "started_at", "stopped_at")
    search_fields = ("user__username", "pod_name", "container__pod_name")
    readonly_fields = ("created_at", "updated_at")

