""""Appconfig."""
import logging
from datetime import datetime
from django.core.cache import cache

import django_rq

from django.apps import AppConfig

logger = logging.getLogger("dashboard")
INTERVAL = 60 * 5  # Time in seconds between dashboard refresh


class DashboardConfig(AppConfig):
    """Config for Dashboard app."""

    name = 'dashboard'

    def ready(self):
        """Do this when the app is ready."""
        cache_key = 'dashboard.config.jobs_scheduled'
        scheduled = cache.get(cache_key, False)

        if not scheduled:
            logger.info("Scheduling jobs")
            scheduler = django_rq.get_scheduler('default')
            scheduler.schedule(
                scheduled_time=datetime.utcnow(),
                func='dashboard.jobs.generate_dashboard',
                interval=INTERVAL,
                result_ttl=INTERVAL + 30
            )
            cache.set(cache_key, True, INTERVAL)
        return True
