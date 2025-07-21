import scrapy


class MastercardSpider(scrapy.Spider):
    name = "mastercard"
    allowed_domains = ["careers.mastercard.com"]
    start_urls = ["https://careers.mastercard.com/us/en/bogota-colombia"]

    def parse(self, response):
        import json
        from datetime import datetime

        from ...items import JobScraperItem

        self.logger.info(f"Parsing {response.url}")

        # Extract embedded JSON from phApp.ddo variable in <script> tag
        script_text = response.css("script").re_first(
            r"phApp\.ddo\s*=\s*({.*?});", default=None
        )
        if script_text:
            try:
                data = json.loads(script_text)
                jobs = data
                # Try to find jobs in the most likely path
                for path in [
                    ["eagerLoadRefineSearch", "data", "jobs"],
                    ["refineSearch", "data", "jobs"],
                ]:
                    d = data
                    for key in path:
                        d = d.get(key) if d else None
                    if d:
                        jobs = d
                        break
                for job in jobs:
                    self.logger.info(f"Found job: {job}")
                    item = JobScraperItem()
                    item["job_id"] = job.get("jobId")
                    item["title"] = job.get("title")
                    item["company"] = "Mastercard"
                    item["location"] = job.get("city")
                    item["salary"] = job.get("salary")
                    item["url"] = job.get("applyUrl")
                    item["date_posted"] = job.get("dateCreated")
                    item["date_extracted"] = datetime.utcnow().isoformat()
                    item["was_opened"] = None
                    # Build detail page URL
                    job_id = job.get("jobId")
                    slug = (
                        job.get("title", "")
                        .replace(" ", "-")
                        .replace(",", "")
                        .replace("/", "-")
                    )
                    detail_url = (
                        f"https://careers.mastercard.com/us/en/job/{job_id}/{slug}"
                        if job_id and slug
                        else None
                    )
                    self.logger.info(f"Detail URL: {detail_url}")
                    if detail_url:
                        yield response.follow(
                            detail_url, self.parse_detail, cb_kwargs={"item": item}
                        )
                    else:
                        yield item
            except Exception as e:
                self.logger.warning(f"Failed to parse job JSON: {e}")
        else:
            self.logger.info("No embedded job JSON found in script tags.")

        # Use <link rel="next"> for pagination
        next_page = response.xpath('//link[@rel="next"]/@href').get()
        self.logger.info(f"Next page URL (from <link rel='next'>): {next_page}")
        if next_page:
            yield response.follow(next_page, self.parse)

    def parse_detail(self, response, item):
        # Try to extract the job description from the detail page
        desc = response.css(
            "div.job-description, section.job-description, "
            "div[data-test='job-description']"
        ).get()
        if not desc:
            # fallback: get the largest text block
            paragraphs = response.css("div *::text, section *::text").getall()
            desc = "\n".join([p.strip() for p in paragraphs if len(p.strip()) > 100])
        item["description"] = desc.strip() if desc else None
        yield item
