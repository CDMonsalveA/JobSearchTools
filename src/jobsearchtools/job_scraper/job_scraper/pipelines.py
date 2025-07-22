# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface


import sqlite3
from pathlib import Path

from jobsearchtools.config.config import config


class SQLiteUniqueJobsPipeline:
    def __init__(self):
        db_config = config.get("db", {})
        db_path = db_config.get("path", "src/jobsearchtools/db/jobsearchtools.db")

        # Robust project root detection: look for pyproject.toml or .git
        def find_project_root(start_path: Path) -> Path:
            for parent in [start_path] + list(start_path.parents):
                if (parent / "pyproject.toml").exists() or (parent / ".git").exists():
                    return parent
            return start_path

        project_root = find_project_root(Path(__file__).resolve())
        abs_db_path = (project_root / db_path).resolve()
        abs_db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(str(abs_db_path))
        self.cursor = self.conn.cursor()
        self._create_table()

    def _create_table(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS jobs (
                job_id TEXT PRIMARY KEY,
                title TEXT,
                company TEXT,
                location TEXT,
                description TEXT,
                salary TEXT,
                url TEXT,
                date_posted TEXT,
                date_extracted TEXT,
                was_opened TEXT
            )
        """)
        self.conn.commit()

    def process_item(self, item, spider):
        job_id = item.get("job_id")
        self.cursor.execute("SELECT 1 FROM jobs WHERE job_id = ?", (job_id,))
        if self.cursor.fetchone():
            # Already seen, skip
            spider.logger.debug(f"Duplicate job skipped: {job_id}")
            return None
        # Insert new job
        self.cursor.execute(
            """
            INSERT INTO jobs (
                job_id, title, company, location, description, salary, url,
                date_posted, date_extracted, was_opened
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                item.get("job_id"),
                item.get("title"),
                item.get("company"),
                item.get("location"),
                item.get("description"),
                item.get("salary"),
                item.get("url"),
                item.get("date_posted"),
                item.get("date_extracted"),
                item.get("was_opened"),
            ),
        )
        self.conn.commit()
        spider.logger.info(f"New job stored: {job_id}")
        return item

    def close_spider(self, spider):
        self.conn.close()
