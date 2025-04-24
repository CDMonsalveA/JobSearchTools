"""Script that executes the scrapy_check_updates.py script to crawl job boards
every 30 minutes and check for updates."""

import os
import time
import subprocess
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("scheduler.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)
# Check if the virtual environment is activated
if os.name == 'nt':
    # Windows
    venv_path = os.path.join(os.getcwd(), "venv", "Scripts", "activate")
else:
    # Unix/Linux
    venv_path = os.path.join(os.getcwd(), "venv", "bin", "activate")


# Execute the script every 30 minutes
def execute_script(script_path: str, interval: int = 1800) -> None:
    """Execute the script at the specified interval."""
    while True:
        try:
            # Activate the virtual environment on windows
            subprocess.run(["venv\\Scripts\\activate"], shell=True)
            # Execute the script
            subprocess.run(["python", script_path], check=True)
            logging.info(f"Executed {script_path} successfully.")
        except subprocess.CalledProcessError as e:
            logging.error(f"Error executing {script_path}: {e}")
        time.sleep(interval)
#print current path
logger.info(f"Current working directory: {os.getcwd()}")
