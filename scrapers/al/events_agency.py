import dateutil.parser
import lxml
import pytz

from openstates.scrape import Scraper, Event


class ALAgencyEventScraper(Scraper):
    tz = pytz.timezone("US/Eastern")

    def scrape(self):
        url = "https://www.openmeetings.alabama.gov/generalpublic/display_notices.aspx"
        page = self.get(url).content
        page = lxml.html.fromstring(page)
        page.make_links_absolute(url)

        for link in page.cssselect("table.ViewNoticesGrid tr td div a"):
            yield from self.scrape_event(link.xpath("@href")[0])

    def scrape_event(self, url):
        page = self.get(url).content
        page = lxml.html.fromstring(page)
        page.make_links_absolute(url)

        org = page.cssselect("span#name")[0].text_content().strip()

        event_date = page.cssselect("span#meetingdate")[0].text_content().strip()
        event_time = page.cssselect("span#meetingtime")[0].text_content().strip()

        addr1 = page.cssselect("span#meetinglocation")[0].text_content().strip()
        addr2 = page.cssselect("span#cityStateZip")[0].text_content().strip()
        location = f"{addr1} {addr2}"

        when = dateutil.parser.parse(f"{event_date} {event_time}")
        when = self.tz.localize(when)

        desc = page.cssselect("#body1")[0].text_content().strip()

        event = Event(
            start_date=when,
            name=org,
            location_name=location,
            description=desc,
        )

        event.add_source(url)

        event.add_participant(org, "organization")

        yield event
