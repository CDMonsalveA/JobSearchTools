"""This script checks for updates on Job Boards, and alerts the user if there are any new job postings."""

import time

import requests

from job_boards.mastercard import MasterCardLastJobPosting
from job_boards.visa import VisaLastJobPosting

LAST_CHANGE_FUNCTIONS = {
    "MasterCard": MasterCardLastJobPosting,
    "Visa": VisaLastJobPosting,
}


def check_for_updates():
    """Check for updates on job boards and alert the user if there are any new job postings."""
    last_change = {}
    for board_name, last_change_function in LAST_CHANGE_FUNCTIONS.items():
        last_change[board_name] = last_change_function()
    while True:
        for board_name, last_change_function in LAST_CHANGE_FUNCTIONS.items():
            new_last_change = last_change_function()
            if new_last_change != last_change[board_name]:
                print(f"New job posting found on {board_name} board! {new_last_change}")
                last_change[board_name] = new_last_change
            else:
                print(f"No new job postings on {board_name} board.")
        time.sleep(3600 / 2)


if __name__ == "__main__":
    check_for_updates()
