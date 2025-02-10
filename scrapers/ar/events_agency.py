import dateutil.parser
import lxml
import pytz

from openstates.scrape import Scraper, Event


class ARAgencyEventScraper(Scraper):
    tz = pytz.timezone("US/Central")

    def scrape(self):
        yield from self.scrape_listing_page("https://portal.arkansas.gov/events/")

    def scrape_listing_page(self, url):
        page = self.get(url).content
        page = lxml.html.fromstring(page)
        page.make_links_absolute(url)

        for row in page.cssselect("div[data-elementor-type='loop-item'] > a"):
            event_url = row.xpath("@href")[0]

            when = (
                row.xpath(".//div[contains(@data-settings, 'event_date')]")[0]
                .text_content()
                .strip()
            )
            when = dateutil.parser.parse(when).date()

            org = row.cssselect("span.elementor-post-info__terms-list-item")[
                0
            ].text_content()
            title = row.cssselect("h4.elementor-heading-title")[0].text_content()
            # the state parks system includes all its various events for the public
            # e.g. children's necklace making or tree identification
            if org == "Arkansas State Parks":
                self.info(f"Skipping State Parks Event - {title}")
                continue

            title = f"{org} {title}"

            event = Event(
                start_date=when,
                name=title,
                classification="agency_event",
                location_name="See Agenda",
            )

            event.add_source(event_url)

            event.add_participant(org, "agency")
            yield event

        # The next link is broken, so don't just try to follow that.
        next_page = "//span[@aria-current='page']/following-sibling::a[contains(@class,'page-numbers') and not(contains(@class, 'next'))]"
        if page.xpath(next_page):
            yield from self.scrape_listing_page(
                page.xpath(next_page)[0].xpath("@href")[0]
            )
