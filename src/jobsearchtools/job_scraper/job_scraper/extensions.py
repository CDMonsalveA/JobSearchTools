"""
Scrapy extensions for monitoring and notifications.

This module provides extensions that integrate with the Scrapy framework
to add monitoring, health checks, and notification capabilities.
"""

import logging
from datetime import datetime

from scrapy import signals
from scrapy.exceptions import NotConfigured

from jobsearchtools.notifications.email_notifier import email_notifier

logger = logging.getLogger(__name__)


class EmailNotificationExtension:
    """
    Scrapy extension that sends email notifications when new jobs are found.

    Connects to spider signals to send notifications after spider completion.
    """

    def __init__(self, stats):
        """
        Initialize the extension.

        Args:
            stats: Scrapy stats collector instance.
        """
        self.stats = stats
        if not email_notifier.enabled:
            raise NotConfigured("Email notifications are disabled")

    @classmethod
    def from_crawler(cls, crawler):
        """
        Factory method called by Scrapy to create the extension.

        Args:
            crawler: Scrapy crawler instance.

        Returns:
            Instance of EmailNotificationExtension.
        """
        ext = cls(crawler.stats)
        crawler.signals.connect(ext.spider_closed, signal=signals.spider_closed)
        return ext

    def spider_closed(self, spider, reason):
        """
        Called when a spider is closed.

        Sends email notification if new jobs were found or alerts if no jobs found.

        Args:
            spider: The spider instance that closed.
            reason: The reason the spider closed.
        """
        new_jobs = self.stats.get_value("new_jobs", [])
        new_jobs_count = self.stats.get_value("new_jobs_count", 0)
        items_scraped = self.stats.get_value("item_scraped_count", 0)

        logger.info(
            f"Spider {spider.name} closed. Reason: {reason}. "
            f"Total found: {items_scraped}, New jobs: {new_jobs_count}"
        )

        # Send notification if new jobs were found
        if new_jobs:
            success = email_notifier.send_new_jobs_notification(
                new_jobs, spider.name, items_scraped
            )
            if success:
                logger.info(
                    f"Email notification sent for {new_jobs_count} new jobs "
                    f"out of {items_scraped} total found"
                )
            else:
                logger.warning("Failed to send email notification")
        # Send alert if no jobs found (potential spider failure)
        elif reason == "finished" and items_scraped == 0:
            success = email_notifier.send_spider_failure_alert(spider.name)
            if success:
                logger.info(
                    f"Failure alert sent: Spider {spider.name} found no jobs"
                )
            else:
                logger.warning("Failed to send failure alert email")


class SpiderHealthMonitorExtension:
    """
    Scrapy extension that monitors spider health and performance.

    Tracks spider runs, success rates, and item counts for validation.
    """

    def __init__(self, stats):
        """
        Initialize the health monitor.

        Args:
            stats: Scrapy stats collector instance.
        """
        self.stats = stats
        self.start_time = None
        self.spider_name = None

    @classmethod
    def from_crawler(cls, crawler):
        """
        Factory method called by Scrapy to create the extension.

        Args:
            crawler: Scrapy crawler instance.

        Returns:
            Instance of SpiderHealthMonitorExtension.
        """
        ext = cls(crawler.stats)
        crawler.signals.connect(ext.spider_opened, signal=signals.spider_opened)
        crawler.signals.connect(ext.spider_closed, signal=signals.spider_closed)
        crawler.signals.connect(ext.item_scraped, signal=signals.item_scraped)
        return ext

    def spider_opened(self, spider):
        """
        Called when a spider opens.

        Args:
            spider: The spider instance that opened.
        """
        self.start_time = datetime.now()
        self.spider_name = spider.name
        logger.info(f"Spider {spider.name} started at {self.start_time}")

    def spider_closed(self, spider, reason):
        """
        Called when a spider closes.

        Logs performance metrics and validates spider health.

        Args:
            spider: The spider instance that closed.
            reason: The reason the spider closed.
        """
        end_time = datetime.now()
        duration = (
            (end_time - self.start_time).total_seconds() if self.start_time else 0
        )

        items_scraped = self.stats.get_value("item_scraped_count", 0)
        items_saved = self.stats.get_value("new_jobs_count", 0)
        errors = self.stats.get_value("log_count/ERROR", 0)

        logger.info(
            f"Spider {spider.name} finished:\n"
            f"  Duration: {duration:.2f}s\n"
            f"  Items scraped: {items_scraped}\n"
            f"  Items saved: {items_saved}\n"
            f"  Errors: {errors}\n"
            f"  Reason: {reason}"
        )

        # Health check validation
        if reason == "finished" and items_scraped == 0:
            logger.warning(
                f"Health check warning: Spider {spider.name} "
                f"finished but scraped 0 items. "
                f"The website structure may have changed."
            )

        if errors > 0:
            logger.warning(
                f"Health check warning: Spider {spider.name} "
                f"encountered {errors} errors"
            )

    def item_scraped(self, item, spider):
        """
        Called when an item is scraped.

        Args:
            item: The scraped item.
            spider: The spider instance.
        """
        # Could add item validation logic here if needed
        pass
