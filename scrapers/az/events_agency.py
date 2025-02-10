import dateutil.parser
import lxml
import pytz
import re

from openstates.scrape import Scraper, Event
from utils.media import get_media_type


class AZAgencyEventScraper(Scraper):
    tz = pytz.timezone("US/Mountain")

    def scrape(self):
        url = "https://publicmeetings.az.gov/arizona-public-meetings"

        page = self.get(url).content
        page = lxml.html.fromstring(page)
        page.make_links_absolute(url)

        for row in page.cssselect("table.views-table tbody tr"):
            url = row.cssselect("td.views-field-title a")[0].xpath("@href")[0]
            yield from self.scrape_event(url)

    def scrape_event(self, url):
        page = self.get(url).content
        page = lxml.html.fromstring(page)
        page.make_links_absolute(url)

        status = "tentative"

        title = page.cssselect("h1#page-title")[0].text_content()

        org = self.get_row(page, "Public Body")
        when = self.get_row(page, "Date/Time")

        if " to " in when:
            when = re.sub(r"to\s.*", "", when)

        when = dateutil.parser.parse(when)
        when = self.tz.localize(when)
        where = self.get_row(page, "Address:")

        title = f"{org} {title}"

        desc = self.get_row(page, "Body:")

        event = Event(
            start_date=when,
            name=title,
            location_name=where,
            description=desc,
            status=status,
            classification="agency_event",
        )
        event.add_source(url)

        event.add_participant(org, "agency")

        for row in page.cssselect("span.file a"):
            file_url = row.xpath("@href")[0]
            get_media_type
            event.add_document(
                row.text_content(),
                file_url,
                media_type=get_media_type(file_url),
                on_duplicate="ignore",
            )

        yield event

    # get all the text in the div after the label div
    def get_row(self, page: lxml.html.HtmlElement, title: str) -> str:
        return page.xpath(
            f"//div[contains(@class,'field-label') and contains(text(), '{title}')]/following-sibling::div/div"
        )[0].text_content()
