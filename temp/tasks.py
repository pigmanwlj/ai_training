from celery import shared_task
from django.core.mail import send_mail
from .models import budget

@shared_task
def send_email_notification(notification_id):
    notification = budget.objects.get(id=notification_id)
    send_mail(
        '采购发起提醒邮件',
        notification.budgetname,
        'Grafana_APPCHQ@app.com.cn',
        'wanglingjie@app.com.cn',
        fail_silently=False,
    )

