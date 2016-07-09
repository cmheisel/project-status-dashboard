""""Appconfig."""
from datetime import datetime

import django_rq

from django.apps import AppConfig


class DashboardConfig(AppConfig):
    """Config for Dashboard app."""

    name = 'dashboard'

    def ready(self):
        """Do this when the app is ready."""
        scheduler = django_rq.get_scheduler('default')
        scheduler.schedule(
            scheduled_time=datetime.utcnow(),
            func='dashboard.jobs.generate_dashboard',
            interval=1 * 60,
            result_ttl=0
        )
        return True
