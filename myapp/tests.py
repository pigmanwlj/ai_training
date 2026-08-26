from datetime import timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from myapp.models import PodUsageSession, TrainingContainer


User = get_user_model()


class PodUsageReportTests(TestCase):
    def setUp(self):
        self.staff_user = User.objects.create_user(
            username="staff",
            password="testpass123",
            is_staff=True,
        )
        self.client.force_login(self.staff_user)

        self.container = TrainingContainer.objects.create(
            slot_name="slot-1",
            profile=TrainingContainer.Profile.A100,
            pod_name="pod-usage-test",
            status=TrainingContainer.Status.FREE,
            price_per_min=Decimal("2.00"),
        )

    def _create_session(self, username, started_at, minutes=10):
        user = User.objects.create_user(username=username, password="testpass123")
        PodUsageSession.objects.create(
            user=user,
            profile=TrainingContainer.Profile.A100,
            pod_name=f"pod-{username}",
            container=self.container,
            started_at=started_at,
            stopped_at=started_at + timedelta(minutes=minutes),
            elapsed_time=timedelta(minutes=minutes),
        )

    def test_usage_report_paginates_ten_rows_per_page(self):
        base_time = timezone.now() - timedelta(days=1)
        for index in range(11):
            self._create_session(
                username=f"user{index + 1:02d}",
                started_at=base_time + timedelta(minutes=index),
            )

        response = self.client.get(reverse("training_usage_report"))

        self.assertEqual(response.status_code, 200)
        self.assertIn("page_obj", response.context)
        self.assertEqual(response.context["page_obj"].paginator.per_page, 10)
        self.assertEqual(response.context["page_obj"].number, 1)
        self.assertEqual(len(response.context["page_obj"].object_list), 10)
        self.assertContains(response, "Page Up")
        self.assertContains(response, "Page Down")
        self.assertContains(response, "Page 1 of 2")

    def test_usage_report_second_page_shows_remaining_row(self):
        base_time = timezone.now() - timedelta(days=1)
        for index in range(11):
            self._create_session(
                username=f"user{index + 1:02d}",
                started_at=base_time + timedelta(minutes=index),
            )

        response = self.client.get(reverse("training_usage_report"), {"page": 2})

        self.assertEqual(response.status_code, 200)
        self.assertIn("page_obj", response.context)
        self.assertEqual(response.context["page_obj"].number, 2)
        self.assertEqual(response.context["page_obj"].paginator.per_page, 10)
        self.assertEqual(len(response.context["page_obj"].object_list), 1)
        self.assertContains(response, "Page Up")
        self.assertContains(response, "Page Down")
        self.assertContains(response, "Page 2 of 2")

