"""This script uses the Spiders from the proyect in src/job_boards_search to
check for updates periodically.

Designed to be run as a cron job or similar scheduler.

It creates a record of the latest job postings and compares them with the
previous ones looking for new ones for each job board.

Then it sends an email with the new job posting links information.
or it opens a web browser with the new job postings.

It uses the Scrapy framework to crawl job boards and extract job postings.
"""

import datetime
import json
import logging
import os
import pathlib
import smtplib
import ssl
import sys
import time
import webbrowser
from multiprocessing import Process, Queue

import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.utils.log import configure_logging
from scrapy.utils.project import get_project_settings

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Set up the path to the project directory
project_dir = os.path.dirname(os.path.abspath(__file__))
project_dir = os.path.join(project_dir, "job_boards_search")
sys.path.append(project_dir)
# Now the project_dir is the path to the job_boards_search directory


def crawl_job_boards(filepath: str) -> None:
    """Crawl all spiders in the project and save the results to a file.

    Args:
        filepath (str): The path to the file where the results will be saved.
            supported format: .jsonl
    """
    delete_old_file(filepath)

    settings = get_project_settings()
    settings.set("SPIDER_MODULES", ["job_boards_search.spiders"])
    settings.set(
        "FEEDS",
        {
            f"{filepath}": {
                "format": "jsonl",
                "overwrite": False,
                "encoding": "utf-8",
            },
        },
    )
    process = CrawlerProcess(settings)
    spiders_names = process.spider_loader.list()
    print(f"Spiders found: {spiders_names}")
    for spider_name in spiders_names:
        process.crawl(spider_name)
    process.start()
    logger.info(f"Crawled job boards and saved results to {filepath}")
    process.stop()


def delete_old_file(filepath: str) -> None:
    """Delete the old file if it exists.

    Args:
        filepath (str): The path to the file to be deleted.
    """
    if os.path.exists(filepath):
        os.remove(filepath)
        logger.info(f"Deleted old file: {filepath}")
    else:
        logger.info(f"File not found, nothing to delete: {filepath}")


if not os.path.exists("old.jsonl"):
    crawl_job_boards("old.jsonl")

print("-------------------------------------------------------------------")
print("Checking for updates...")
print("-------------------------------------------------------------------")
crawl_job_boards("new.jsonl")
# check for differences between old.jsonl and new.jsonl
with (
    open("old.jsonl", "r", encoding="utf-8") as old_file,
    open("new.jsonl", "r", encoding="utf-8") as new_file,
):
    old_data = list(old_file)
    new_data = list(new_file)
jsonl_old = [json.loads(line) for line in old_data]
jsonl_new = [json.loads(line) for line in new_data]

# Compare the two files and find new job postings
new_job_postings = []
for new_job in new_data:
    if new_job not in old_data:
        new_job_postings.append(new_job)

if new_job_postings != []:
    logger.info(f"New job postings found: {len(new_job_postings)}")
    for job in new_job_postings:
        logger.info(f"New job posting: {job}")
        # Open the job posting link in a web browser
        job = json.loads(job)
        if "url" not in job:
            logger.warning("No link found in the job posting.")
            continue
        webbrowser.open(job.get("url"))
else:
    logger.info("No new job postings found.")

# Move new.jsonl to old.jsonl
delete_old_file("old.jsonl")
os.rename("new.jsonl", "old.jsonl")
logger.info("Moved new.jsonl to old.jsonl")


# Solution at https://stackoverflow.com/questions/41495052/scrapy-reactor-not-restartable
# to avoid the reactor already started error
# twisted.internet.error.ReactorNotRestartable
