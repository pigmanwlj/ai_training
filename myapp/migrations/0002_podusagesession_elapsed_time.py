from django.db import migrations, models


def backfill_elapsed_time(apps, schema_editor):
    PodUsageSession = apps.get_model("myapp", "PodUsageSession")

    for session in PodUsageSession.objects.filter(
        elapsed_time__isnull=True,
        started_at__isnull=False,
        stopped_at__isnull=False,
    ).iterator():
        session.elapsed_time = session.stopped_at - session.started_at
        session.save(update_fields=["elapsed_time"])


class Migration(migrations.Migration):

    dependencies = [
        ("myapp", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="podusagesession",
            name="elapsed_time",
            field=models.DurationField(blank=True, null=True, verbose_name="耗时"),
        ),
        migrations.RunPython(backfill_elapsed_time, migrations.RunPython.noop),
    ]

