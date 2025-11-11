"""
Email notification system for new job listings.

Sends email alerts when new jobs are discovered during spider runs.
Supports HTML-formatted emails with job details and links.
"""

import logging
import smtplib
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Any

from jobsearchtools.config.settings import settings

logger = logging.getLogger(__name__)


class EmailNotifier:
    """
    Email notification service for job listings.

    Sends formatted email alerts with new job information.
    """

    def __init__(self):
        """Initialize the email notifier with settings."""
        self.enabled = settings.email.enabled
        if not self.enabled:
            logger.info("Email notifications are disabled")
            return

        if not settings.email.smtp_password:
            logger.warning(
                "SMTP password not configured. Email notifications will be disabled."
            )
            self.enabled = False

    def send_new_jobs_notification(
        self, jobs: list[dict[str, Any]], spider_name: str
    ) -> bool:
        """
        Send email notification about new job listings.

        Args:
            jobs: List of new job dictionaries.
            spider_name: Name of the spider that found the jobs.

        Returns:
            True if email was sent successfully, False otherwise.
        """
        if not self.enabled:
            logger.debug("Email notifications disabled, skipping")
            return False

        if not jobs:
            logger.debug("No new jobs to notify about")
            return False

        try:
            # Create message
            msg = MIMEMultipart("alternative")
            msg["Subject"] = f"New Job Listings Found - {spider_name.upper()}"
            msg["From"] = str(settings.email.from_address)
            msg["To"] = str(settings.email.to_address)

            # Create HTML content
            html_content = self._generate_html_email(jobs, spider_name)
            html_part = MIMEText(html_content, "html")
            msg.attach(html_part)

            # Send email
            with smtplib.SMTP(
                settings.email.smtp_host, settings.email.smtp_port
            ) as server:
                if settings.email.use_tls:
                    server.starttls()

                server.login(settings.email.smtp_user, settings.email.smtp_password)
                server.sendmail(
                    str(settings.email.from_address),
                    str(settings.email.to_address),
                    msg.as_string(),
                )

            logger.info(
                f"Email notification sent successfully for {len(jobs)} new jobs"
            )
            return True

        except Exception as e:
            logger.error(f"Failed to send email notification: {e}")
            return False

    def _generate_html_email(self, jobs: list[dict[str, Any]], spider_name: str) -> str:
        """
        Generate HTML-formatted email content.

        Args:
            jobs: List of job dictionaries.
            spider_name: Name of the spider.

        Returns:
            HTML string for email body.
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        company = jobs[0].get("company", "Unknown") if jobs else "Unknown"

        html = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{
            font-family: Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
        }}
        .header {{
            background-color: #4CAF50;
            color: white;
            padding: 20px;
            border-radius: 5px;
            margin-bottom: 20px;
        }}
        .job-card {{
            border: 1px solid #ddd;
            border-radius: 5px;
            padding: 15px;
            margin-bottom: 15px;
            background-color: #f9f9f9;
        }}
        .job-title {{
            color: #2196F3;
            font-size: 18px;
            font-weight: bold;
            margin-bottom: 10px;
        }}
        .job-details {{
            margin: 10px 0;
        }}
        .job-label {{
            font-weight: bold;
            color: #555;
        }}
        .apply-button {{
            display: inline-block;
            background-color: #4CAF50;
            color: white;
            padding: 10px 20px;
            text-decoration: none;
            border-radius: 5px;
            margin-top: 10px;
        }}
        .footer {{
            margin-top: 30px;
            padding-top: 20px;
            border-top: 1px solid #ddd;
            color: #777;
            font-size: 12px;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🎯 New Job Listings Found!</h1>
        <p><strong>{len(jobs)}</strong> new position(s) at
        <strong>{company}</strong></p>
        <p>Spider: {spider_name} | Time: {timestamp}</p>
    </div>
"""

        for job in jobs:
            title = job.get("title", "No Title")
            location = job.get("location", "N/A")
            salary = job.get("salary", "Not specified")
            url = job.get("url", "#")
            date_posted = job.get("date_posted", "N/A")

            # Truncate description if too long
            description = job.get("description", "No description available")
            if description and len(description) > 300:
                description = description[:300] + "..."

            html += f"""
    <div class="job-card">
        <div class="job-title">{title}</div>
        <div class="job-details">
            <span class="job-label">📍 Location:</span> {location}<br>
            <span class="job-label">💰 Salary:</span> {salary}<br>
            <span class="job-label">📅 Posted:</span> {date_posted}<br>
        </div>
"""
            if description and description != "No description available":
                html += f"""
        <div class="job-details">
            <span class="job-label">📝 Description:</span><br>
            {description}
        </div>
"""
            html += f"""
        <a href="{url}" class="apply-button">Apply Now →</a>
    </div>
"""

        html += """
    <div class="footer">
        <p>This is an automated notification from JobSearchTools.</p>
        <p>To unsubscribe or modify settings, update your environment variables.</p>
    </div>
</body>
</html>
"""
        return html


# Global notifier instance
email_notifier = EmailNotifier()
