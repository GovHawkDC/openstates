import lxml
import pytz
import re
import demjson3
import dateutil

from utils.media import get_media_type
from openstates.scrape import Scraper, Event


class NEAgencyEventScraper(Scraper):

    tzs = {"CST": "America/Chicago"}
    base_url = "https://www.nebraska.gov/calendar/"

    def scrape(self):
        agency_url = "https://www.nebraska.gov/calendar/index.cgi"

        post_vars = {
            "activity": "Any",
            "activity_date": 12,
            "agency": "any department",
        }

        page = self.post(agency_url, data=post_vars).text
        matches = re.findall(r"events: ((.|\n)*?)]", page, re.IGNORECASE | re.MULTILINE)
        json_list = f"{matches[0][0]}]".replace("\n", " ")
        # the entries are encoded as a javscript list (not json) in the source page html
        rows = demjson3.decode(json_list)

        for row in rows:
            tz = pytz.timezone(self.tzs[row["timezone"]])
            start = tz.localize(dateutil.parser.parse(row["start"]))
            end = tz.localize(dateutil.parser.parse(row["end"]))
            url = f"{self.base_url}{row['url']}"

            page = self.get(url).content
            page = lxml.html.fromstring(page)

            description = ""
            if page.xpath("//div[small[contains(text(), 'Details')]]"):
                description = page.xpath(
                    "string(//div[small[contains(text(), 'Details')]])"
                ).strip()

            e = Event(
                name=row["organization"],
                location_name=row["location"],
                start_date=start,
                end_date=end,
                classification="agency-meeting",
                description=description,
            )

            if page.xpath("//div[small[contains(text(), 'Meeting Agenda')]]/a"):
                agenda_url = page.xpath(
                    "//div[small[contains(text(), 'Meeting Agenda')]]/a/@href"
                )[0]
                e.add_document(
                    "Agenda",
                    agenda_url,
                    media_type=get_media_type(agenda_url, default="text/html"),
                )

            if page.xpath("//div[small[contains(text(), 'Meeting Materials')]]/a"):
                mats_url = page.xpath(
                    "//div[small[contains(text(), 'Meeting Materials')]]/a/@href"
                )[0]

                if mats_url != "http://":
                    e.add_document(
                        "Meeting Materials",
                        mats_url,
                        media_type=get_media_type(mats_url, default="text/html"),
                        on_duplicate="ignore",
                    )

            e.add_participant(row["organization"], "agency")
            e.add_source(url)
            yield (e)
