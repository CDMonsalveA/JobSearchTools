# Scrapy project executor for job scraping
import subprocess

from jobsearchtools.config.config import config


class JobScraper:
    def run_subprocess(self):
        """
        Run all spiders as a subprocess.
        """
        # check if inside the project directory
        project_dir = config.get("scrapy", {}).get(
            "project_dir", "src/jobsearchtools/job_scraper"
        )

        spiders_list = config.get("scrapy", {}).get("spiders_list", [])
        if not spiders_list:
            spiders_list = (
                subprocess.check_output(["scrapy", "list"], cwd=project_dir, text=True)  # noqa: S607
                .strip()
                .splitlines()
            )
        print(f"Spiders to run: {spiders_list}")

        for spider in spiders_list:
            print(f"Running spider: {spider}")
            subprocess.run(  # noqa: S603
                ["scrapy", "crawl", spider],  # noqa: S607
                cwd=project_dir,
                check=True,
            )


js = JobScraper()

js.run_subprocess()
