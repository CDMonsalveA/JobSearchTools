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
        self, jobs: list[dict[str, Any]], spider_name: str, total_found: int = None
    ) -> bool:
        """
        Send email notification about new job listings.

        Args:
            jobs: List of new job dictionaries.
            spider_name: Name of the spider that found the jobs.
            total_found: Total number of positions found (including duplicates).

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
            html_content = self._generate_html_email(jobs, spider_name, total_found)
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

    def send_spider_failure_alert(self, spider_name: str) -> bool:
        """
        Send alert email when spider finds no job listings.

        Args:
            spider_name: Name of the spider that failed to find jobs.

        Returns:
            True if email was sent successfully, False otherwise.
        """
        if not self.enabled:
            logger.debug("Email notifications disabled, skipping")
            return False

        try:
            # Create message
            msg = MIMEMultipart("alternative")
            msg["Subject"] = f"ALERT: No Jobs Found - {spider_name.upper()}"
            msg["From"] = str(settings.email.from_address)
            msg["To"] = str(settings.email.to_address)

            # Create HTML content
            html_content = self._generate_failure_alert_email(spider_name)
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

            logger.info(f"Spider failure alert sent for {spider_name}")
            return True

        except Exception as e:
            logger.error(f"Failed to send failure alert email: {e}")
            return False

    def _generate_html_email(
        self, jobs: list[dict[str, Any]], spider_name: str, total_found: int = None
    ) -> str:
        """
        Generate HTML-formatted email content.

        Args:
            jobs: List of job dictionaries.
            spider_name: Name of the spider.
            total_found: Total number of positions found (including duplicates).

        Returns:
            HTML string for email body.
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        company = jobs[0].get("company", "Unknown") if jobs else "Unknown"

        # Build the stats message
        new_count = len(jobs)
        if total_found is not None and total_found > 0:
            duplicates = total_found - new_count
            stats_msg = (
                f"<p><strong>{new_count}</strong> new position(s) out of "
                f"<strong>{total_found}</strong> total found "
                f"({duplicates} duplicate(s) skipped)</p>"
            )
        else:
            stats_msg = f"<p><strong>{new_count}</strong> new position(s)</p>"

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
        .stats-info {{
            background-color: #e3f2fd;
            border-left: 4px solid #2196F3;
            padding: 15px;
            margin-bottom: 20px;
            border-radius: 5px;
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
        <p>Company: <strong>{company}</strong></p>
        <p>Spider: {spider_name} | Time: {timestamp}</p>
    </div>
    <div class="stats-info">
        <h3>📊 Search Results</h3>
        {stats_msg}
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

    def _generate_failure_alert_email(self, spider_name: str) -> str:
        """
        Generate HTML-formatted failure alert email.

        Args:
            spider_name: Name of the spider that failed.

        Returns:
            HTML string for email body.
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

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
            background-color: #f44336;
            color: white;
            padding: 20px;
            border-radius: 5px;
            margin-bottom: 20px;
        }}
        .alert-box {{
            background-color: #fff3cd;
            border-left: 4px solid #ff9800;
            padding: 15px;
            margin-bottom: 20px;
            border-radius: 5px;
        }}
        .alert-title {{
            color: #f57c00;
            font-size: 18px;
            font-weight: bold;
            margin-bottom: 10px;
        }}
        .suggestions {{
            background-color: #e8f5e9;
            border-left: 4px solid #4caf50;
            padding: 15px;
            margin-top: 20px;
            border-radius: 5px;
        }}
        ul {{
            margin: 10px 0;
            padding-left: 20px;
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
        <h1>⚠️ Spider Alert: No Jobs Found</h1>
        <p>Spider: <strong>{spider_name}</strong></p>
        <p>Time: {timestamp}</p>
    </div>

    <div class="alert-box">
        <div class="alert-title">⚠️ Potential Issue Detected</div>
        <p>The <strong>{spider_name}</strong> spider completed its run but found
        <strong>0 job listings</strong>.</p>
        <p>This could indicate:</p>
        <ul>
            <li>The website structure has changed</li>
            <li>The career page URL is no longer valid</li>
            <li>The website is temporarily unavailable</li>
            <li>Network connectivity issues</li>
            <li>Anti-scraping measures blocking access</li>
        </ul>
    </div>

    <div class="suggestions">
        <div class="alert-title">🔧 Recommended Actions</div>
        <ul>
            <li>Visit the company's career page manually to verify it's working</li>
            <li>Check the spider logs for error messages</li>
            <li>Review the spider's selectors if the page structure changed</li>
            <li>Verify network connectivity and DNS resolution</li>
            <li>Check if the website requires updated user agents or headers</li>
        </ul>
    </div>

    <div class="footer">
        <p>This is an automated alert from JobSearchTools Health Monitoring.</p>
        <p>To disable alerts or modify settings, update your environment variables.</p>
    </div>
</body>
</html>
"""
        return html


# Global notifier instance
email_notifier = EmailNotifier()
