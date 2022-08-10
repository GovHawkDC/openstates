from openstates.scrape import Scraper, Event
import datetime
import pytz
import requests
import lxml.html
import dateutil.parser

class AgendaCenterScraper:
    BASE_URL = ""
    TIMEZONE = ""
    s = requests.Session()

    def session(self, action_date):
        return str(action_date.year)

    def scrape(self, window=3):
        year = datetime.datetime.today().year
        search_url = "{}/Search/".format(self.BASE_URL)
        params = {
            "term": "",
            "CIDs": "all",
            "startDate": "01/01/{}".format(year),
            "endDate": "12/31/{}".format(year),
            "dateRange": "",
            "dateSelector": "",
        }
        headers = {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/79.0.3945.117 Safari/537.36",
            "referer": self.BASE_URL,
            "Sec-Fetch-Mode": "navigate",
        }

        self.info(search_url)

        req = self.s.get(search_url, params=params, headers=headers)
        req.raise_for_status()
        html = req.text

        page = lxml.html.fromstring(html)
        page.make_links_absolute(self.BASE_URL)

        # agencies
        for row in page.xpath('//div[contains(@class, "listing")]'):
            # it's typod as expandCollaspseCategory which seems like something they might fix, hence the OR
            agency_name = row.xpath(
                'h2[contains(@onclick, "expandCollaspseHeader") or contains(@onclick, "expandCollapseHeader") '
                'or contains(@onclick, "expandCollaspseCategory") or contains(@onclick, "expandCollapseCategory")]/text()'
            )[0].strip()
            agency_name = agency_name.replace("Agendas", "").strip()

            print(agency_name)
            # event_date = row.xpath('div[contains(@class, "RowTop")]/div[contains(@class, "RowLink")]/a/text()')[0].strip()
            # event_url = row.xpath('div[contains(@class, "RowTop")]/div[contains(@class, "RowLink")]/a/@href')[0].strip()

            for event_row in row.xpath(".//table/tbody/tr"):
                yield from self.scrape_event_page(agency_name, event_row)

    def scrape_event_page(self, agency_name, row):
        event_location = "Not provided"

        # Jul 18 2019
        event_date_str = row.xpath("string(td/h4/a/strong|td/h4/strong)").strip()

        event_date = dateutil.parser.parse(event_date_str)
        event_date = self.TIMEZONE.localize(event_date)

        description = row.xpath("td/p/text()")[0].strip()

        status = ''
        if event_date > self.TIMEZONE.localize(datetime.datetime.today()):
            status = 'tentative'
        else:
            status = 'passed'

        if 'cancellation' in description.lower() or 'cancelled' in description.lower():
            status = 'cancelled'

        event = Event(
            name=agency_name,
            start_date=event_date,
            description=description,
            location_name=event_location,
            status=status
        )
        event.add_source(self.BASE_URL)

        print(agency_name, event_date, description, event_location, status)

        # participant = "{} {}".format(self.JURIS_NAME, event_group)
        event.add_participant(agency_name, 'organization')

        if row.xpath('td[contains(@class,"videos")]/a'):
            video_url = row.xpath('td[contains(@class,"videos")]/a/@href')[0]
            event.add_media_link(
                'Video',
                video_url,
                'text/html',
                on_duplicate='ignore',
            )

        if row.xpath('td[contains(@class,"minutes")]/a'):
            document_url = row.xpath('td[contains(@class,"minutes")]/a/@href')[0]
            event.add_document(
                'minutes',
                document_url,
                on_duplicate='ignore'
            )      

        if row.xpath('td[contains(@class,"downloads")]/div/a'):
            for media_link in row.xpath('td[contains(@class,"downloads")]/div//ol/li/a'):
                link_name = media_link.xpath('text()')[0].strip()
                link_url = media_link.xpath('@href')[0].strip()
                if 'pdf' in media_link.get('class'):
                    media_type = 'application/pdf'
                elif 'html' in media_link.get('class'):
                    media_type = 'text/html'

                if link_name == 'HTML' or link_name == 'PDF':
                    event.add_document(
                        'Agenda',
                        link_url,
                        on_duplicate='ignore'
                    )
                else:
                    event.add_document(
                        link_name,
                        link_url,
                        on_duplicate='ignore'
                    )
                print(link_name, link_url)

        # # TODO: ones with onlicks are video links

        # for outline_row in page.xpath('//span[@id="ContentPlaceholder1_lblOutline"]/table[@id="MeetingDetail"]/tr'):
        #     item_title = outline_row.xpath('string(td[contains(@class,"Title")])').strip()

        #     if outline_row.xpath('td[contains(@class,"Num")]/text()'):
        #         item_num = outline_row.xpath('td[contains(@class,"Num")]/text()')[0].strip()
        #         item_title = '{} {}'.format(item_num, item_title)
        #         # TODO: Should we add links here as documents? Might overwhelm
        #     event.add_agenda_item(item_title)

        yield event
