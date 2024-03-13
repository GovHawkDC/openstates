from openstates.scrape import Scraper, Event
import datetime
import pytz
import requests
import re
import lxml.html
import dateutil.parser
from lxml import etree

class GranicusScraper():
    BASE_URL = ""
    TIMEZONE = ""
    s = requests.Session()

    def session(self, action_date):
        return str(action_date.year)

    def scrape(self, window=30):
        page = lxml.html.fromstring(requests.get(self.BASE_URL).content)
        page.make_links_absolute(self.BASE_URL)
        self.info(self.BASE_URL)
        yield from self.scrape_upcoming(page)

        yield from self.scrape_past(page, window)

    def handle_date(self, date_col):
        if isinstance(date_col, str):
            print(date_col)
            event_date = dateutil.parser.parse(date_col)
            return self.TIMEZONE.localize(event_date)

        if date_col.xpath('span'):
            event_date = date_col.xpath('span[1]/text()')[0].strip()
            event_date = datetime.datetime.utcfromtimestamp(int(event_date))
        else:
            event_date = date_col.text_content().strip()

            if event_date.lower() == "in progress":
                event_date = datetime.datetime.now().replace(second=0, microsecond=0, minute=0)
            else:
                event_date = dateutil.parser.parse(event_date)

        event_date = self.TIMEZONE.localize(event_date)
        return event_date


    def scrape_upcoming(self, page):
        # table#upcoming is regular
        # div#upcoming/table.listingTable struct is alexandria VA
        for row in page.xpath('//table[contains(@id,"upcoming")]/tbody/tr|//div[contains(@id,"upcoming")]/table[contains(@class,"listingTable")]/tbody/tr'):
            if 'currently there are no upcoming events' in row.text_content().lower():
                return

            event_name = row.xpath('td[contains(@headers,"EventName") or contains(@headers,"Name")]')[0].text_content().strip()
            # inside the date td is a display:none span w/ the unixtime.
            date_col =  row.xpath('td[contains(@headers,"Date")]')[0]
            event_date = self.handle_date(date_col)

            event = Event(name=event_name,
                        start_date=event_date,
                        # description=description,
                        location_name="See Agenda",
                        )

            if row.xpath('.//a[contains(text(), "Agenda")]'):
                agenda_url = row.xpath('.//a[contains(text(), "Agenda")]/@href')[0]
                event.add_document('Agenda', agenda_url)

            base_xpath = './/a[contains(@href, "MinutesViewer")]'
            if row.xpath(base_xpath):
                agenda_url = row.xpath(f'{base_xpath}/@href')[0]
                agenda_text = row.xpath(f'string({base_xpath})')
                event.add_document(agenda_text, agenda_url)

            base_xpath = './/option[contains(@value, "MinutesViewer")]'
            if row.xpath(base_xpath):
                agenda_url = row.xpath(f'{base_xpath}/@value')[0]
                agenda_text = row.xpath(f'string({base_xpath})')
                event.add_document(agenda_text, agenda_url)

            if row.xpath('.//a[text() = "Video"]'):
                item_url = row.xpath('.//a[text() = "Video"]/@href')[0]
                event.add_media_link("Video", item_url, "text/html")

            if row.xpath('.//a[text() = "MP4 Video"]'):
                item_url = row.xpath('.//a[text() = "MP4 Video")]/@href')[0]
                event.add_media_link("Video", item_url, "video/mp4")

            if row.xpath('.//a[text() = "MP3 Audio"]'):
                item_url = row.xpath('.//a[text() = "MP3 Audio")]/@href')[0]
                event.add_media_link("Audio", item_url, "audio/mpeg")

            event.add_source(self.BASE_URL)

            yield event
    
    def scrape_past(self, page, window):
        for row in page.xpath('//table[contains(@id,"archive") or contains(@class,"archive")]/tbody/tr|//div[contains(@id,"archive")]/table/tr'):

            if "Please check back at a later date" in row.text_content():
                continue

            event_name = row.xpath('string(td[contains(@headers,"Name")])').strip()

            if event_name == '':
                event_name = row.xpath("string(td[1])").strip()

            if row.xpath('td[contains(@headers,"Date")]'):
                date_col = row.xpath('td[contains(@headers,"Date")]')[0]
            else:
                date_col = row.xpath('string(td[2])')
            event_date = self.handle_date(date_col)

            if event_name == '':
                self.warning(f"Skipping blank event name on {event_date}")
                continue

            event = Event(name=event_name,
                        start_date=event_date,
                        # description=description,
                        location_name="TBD",
                        )

            if row.xpath('.//a[contains(text(), "Agenda")]'):
                url = row.xpath('.//a[contains(text(), "Agenda")]/@href')[0]
                event.add_document('Agenda', url)

            if row.xpath('.//a[contains(text(), "Minutes")]'):
                url = row.xpath('.//a[contains(text(), "Minutes")]/@href')[0]
                event.add_document('Minutes', url)

            if row.xpath('.//a[contains(text(), "MP4")]'):
                url = row.xpath('.//a[contains(text(), "MP4")]/@href')[0]
                event.add_media_link("Video", url, 'video/mp4')


            base_xpath = './/a[contains(@href, "MinutesViewer")]'
            if row.xpath(base_xpath):
                agenda_url = row.xpath(f'{base_xpath}/@href')[0]
                agenda_text = row.xpath(f'string({base_xpath})')
                event.add_document(agenda_text, agenda_url)

            base_xpath = './/option[contains(@value, "MinutesViewer")]'
            if row.xpath(base_xpath):
                for item in row.xpath(base_xpath):
                    agenda_url = item.xpath('@value')[0]
                    if agenda_url[0:4] != 'http':
                        agenda_url = f"https:{agenda_url}"
                    agenda_text = item.xpath('string(.)')
                    event.add_document(agenda_text, agenda_url)

            if row.xpath('.//a[text() = "Video"]'):
                item_url = row.xpath('.//a[text() = "Video"]/@href')[0]
                event.add_media_link("Video", item_url, "text/html")


            if row.xpath('.//a[contains(text(), "MP3")]'):
                item_url = row.xpath('.//a[contains(text(), "MP3")]/@href')[0]
                event.add_media_link("Audio", item_url, "audio/mpeg")


            # TODO: Video and extracting that link from the js popup

            event.add_source(self.BASE_URL)

            yield event