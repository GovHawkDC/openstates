import dateutil.parser
import pytz
import feedparser
import re

from openstates.scrape import Scraper
from openstates.scrape import Event


class MNTownHallScraper(Scraper):
    # bad SSL as of August 2017
    verify = False
    _tz = pytz.timezone("US/Central")

    def scrape(self):
        for party in ["dfl", "gop"]:
            url = f"https://www.house.leg.state.mn.us/rss/townhall{party}.asp"
            yield from self.scrape_rss(url)

    def scrape_rss(self, url):
        rss = feedparser.parse(url)

        for e in rss["entries"]:
            desc = e["description"]

            meta = desc.split("\n")
            datetime = meta[0].strip()
            # they randomly do 5:0 PM a lot
            datetime = datetime.replace(":0 ", ":00 ")
            matches = re.findall(
                r"Meeting Date:\s+(\d+/\d+/\d+).*Meeting Time:\s+(.*)",
                datetime,
                re.MULTILINE | re.IGNORECASE,
            )
            try:
                matches = matches[0]
            except IndexError:
                self.warning(f"Unable to parse datetime {datetime}, skipping")
                continue

            date = matches[0]
            time = matches[1]

            try:
                start = self._tz.localize(dateutil.parser.parse(f"{date} {time}"))
            except ValueError:
                start = self._tz.localize(dateutil.parser.parse(date))

            location = meta[1].replace("-", "").strip()

            # basic strip tags
            description = re.sub("<[^<]+?>", "", e["description"])

            event = Event(
                name=e["title"],
                start_date=start,
                location_name=location,
                classification="townhall-meeting",
                description=description,
            )

            person = re.findall(r"Rep. (.*) town hall", e["title"])
            if person:
                person = person[0]
                event.add_participant(person, type="person", note="host")

            event.add_source(e["link"])

            yield event
