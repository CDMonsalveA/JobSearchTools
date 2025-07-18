"""This script uses the Spiders from the proyect in src/job_boards_search to
check for updates periodically.

Designed to be run as a cron job or similar scheduler.

It creates a record of the latest job postings and compares them with the
previous ones looking for new ones for each job board.

Then it sends an email with the new job posting links information.
or it opens a web browser with the new job postings.

It uses the Scrapy framework to crawl job boards and extract job postings.
"""

import json
import logging
import os
import sys
import time
import webbrowser

import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

# logging.basicConfig(
#     level=logging.INFO,
#     format="%(asctime)s - %(levelname)s - %(message)s",
# )
logger = logging.getLogger(__name__)
# logger.setLevel(logging.INFO)
logger.info("Starting the script...")


def count_minutes(time_in_minutes: int = 30) -> None:
    for i in range(time_in_minutes):
        print(
            f"------ Spider has slept for {i} minutes - {time_in_minutes - i} minutes left ------",
            end="\r",
        )
        time.sleep(60)


def setup_directory(__file__):
    project_dir = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.join(project_dir, "job_boards_search")
    sys.path.append(project_dir)


def crawl_job_boards(filepath: str) -> None:
    """Crawl all spiders in the project and save the results to a file.

    Args:
        filepath (str): The path to the file where the results will be saved.
            supported format: .jsonl
    """
    delete_old_file(filepath)

    settings = get_project_settings()
    settings.set("SPIDER_MODULES", ["job_boards_search.spiders"])
    settings.set("NEWSPIDER_MODULE", "job_boards_search.spiders")
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
        print(f"----------- Running spider: {spider_name} -----------------------------------------------------------")
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


########################################################################################################################


# count_minutes(30)
open_all_links = False
setup_directory(__file__)

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
        chrome_path = "C:/Program Files/Google/Chrome/Application/chrome.exe"
        webbrowser.register("chrome", None, webbrowser.BackgroundBrowser(chrome_path))
        webbrowser.get("chrome").open(job.get("url"))
else:
    logger.info("No new job postings found.")

chrome_path = "C:/Program Files/Google/Chrome/Application/chrome.exe"

every_run_list = [
    "https://www.magneto365.com/co/empleos?device=desktop&paginator[page]=1&paginator[pageSize]=20&filters[country_id][0]=47&filters[department_id][0]=779@47&q=&order[field]=publish_date&order[order]=DESC",
    "https://www.linkedin.com/jobs/jam",
    "https://co.indeed.com/?from=gnav-jobseeker-profile--profile-one-frontend",
    "https://torre.ai/search/jobs?q=bestfor%3Acristianmonsalve7",
]
ones_a_day_list = [
    "https://career17.sapsf.com/career?company=atodahoras&career%5fns=job%5flisting%5fsummary&navBarLevel=JOB%5fSEARCH&site=VjItaHJ4VmtnZEVBOWFWWnB1V2tIMmtRZz09&_s.crb=iTzVgD4C72fvRMI6e%2bavYRNLfzk7iGOLh49O0i49n8U%3d",
    "https://agenciapublicadeempleo.sena.edu.co/spe-web/spe/cartelera",
    "https://www.hiring.cafe/",
    "https://remoteandtalent.com/joblist",
    "https://www.weremoto.com/",
    "https://www.workingnomads.com/jobs?location=colombia",
]


links_list = []
for link in every_run_list:
    links_list.append(link)
if open_all_links:
    for link in ones_a_day_list:
        links_list.append(link)
webbrowser.register("chrome", None, webbrowser.BackgroundBrowser(chrome_path))
for link in links_list:
    webbrowser.get("chrome").open(link)
    logger.info(f"Opened link: {link}")
# Move new.jsonl to old.jsonl
delete_old_file("old.jsonl")
os.rename("new.jsonl", "old.jsonl")
logger.info("Moved new.jsonl to old.jsonl")

# cd .\src\job_boards_search\
# python ..\scrapy_check_updates.py
