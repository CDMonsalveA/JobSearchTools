"""Script to scrape job postings from Mastercard's career page."""

import json
import logging
from typing import NamedTuple

import httpx
import jmespath
import parsel

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
URL = "https://careers.mastercard.com/us/en/bogota-colombia"


class LastJobPosting(NamedTuple):
    title: str
    jobId: str
    postedDate: str
    applyUrl: str


# add headers to the request to make it look like a browser
def MasterCardLastJobPosting():
    """Scrape the last job posting from Mastercard."""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"  # noqa: E501
    }
    # make a request to the URL and get the response
    response = httpx.get(URL, headers=headers)
    # on script phApp.ddo = { ... eagerLoadRefineSearch: { ... data: { ... jobs: { LIST_OF_JOBS } } } }
    selector = parsel.Selector(response.text)
    # get the script tag that contains the job postings data
    script_tag = selector.css("script").re_first(
        r"phApp\.ddo\s*=\s*({.*?});", default=""
    )
    # Decode the JSON data
    data = json.loads(script_tag)
    # Extract the job postings data using JMESPath
    jobs = jmespath.search("eagerLoadRefineSearch.data.jobs", data)
    # Extract the last job posting
    last_job_posting = jobs[0] if jobs else None
    if last_job_posting:
        # Extract the relevant information from the job posting
        title = last_job_posting.get("title")
        jobId = last_job_posting.get("jobId")
        postedDate = last_job_posting.get("postedDate")
        applyUrl = last_job_posting.get("applyUrl")
        # Create a LastJobPosting object
        last_job = LastJobPosting(title, jobId, postedDate, applyUrl)
        # Print the job posting information
        logger.info(f"Last Job Posting on Mastercard: {title}, {jobId}, {postedDate}")
    else:
        print("No job postings found.")

    return last_job
