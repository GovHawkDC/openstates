import lxml
import pytz
import re
import demjson3
import dateutil

from openstates.scrape import Scraper, Event


class NEAgencyEventScraper(Scraper):

    tzs = {"CST": "America/Chicago"}
    base_url = "https://www.nebraska.gov/calendar/"

    def scrape(self):
        agency_url = "https://www.nebraska.gov/calendar/index.cgi"

        page = self.get(agency_url).text
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
                print(description)

            e = Event(
                name=row["organization"],
                location_name=row["location"],
                start_date=start,
                end_date=end,
                classification="agency-meeting",
                description=description,
            )

            e.add_participant(row["organization"], "agency")
            e.add_source(url)
            yield (e)
