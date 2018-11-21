import pytz
import datetime
import lxml.html
from pupa.scrape import Scraper, Event


class GAEventScraper(Scraper):
    tz = pytz.timezone("US/Eastern")

    def scrape(self):
        base_url = 'http://calendar.legis.ga.gov/Calendar/'
        url = "http://calendar.legis.ga.gov/Calendar/?Chamber=Senate"
        page = self.get(url).text
        html = self.get(url).text
        page = lxml.html.fromstring(html)

        # this is an asp.net form so grab our __ variables
        (viewstate, ) = page.xpath('//input[@id="__VIEWSTATE"]/@value')
        (viewstategenerator, ) = page.xpath(
            '//input[@id="__VIEWSTATEGENERATOR"]/@value')
        (eventvalidation, ) = page.xpath(
            '//input[@id="__EVENTVALIDATION"]/@value')
        form = {
            '__EVENTTARGET': 'Calendar1',
            # '__EVENTARGUMENT': 'Select$0',
            '__VIEWSTATE': viewstate,
            '__VIEWSTATEGENERATOR': viewstategenerator,
            '__EVENTVALIDATION': eventvalidation,
        }

        # 'Clicking' (actually a JS form submit) on each sunday gives you
        # that week's events
        sundays = page.xpath('//table[@id="Calendar1"]/tr/td[1]/a/@href')
        for sunday in sundays:
            cal_id = self.extract_vars_from_href(sunday)
            form['__EVENTARGUMENT'] = cal_id
            weekly_html = self.post(url=base_url, data=form, allow_redirects=True).content
            weekly_page = lxml.html.fromstring(weekly_html)
            weekly_page.make_links_absolute(base_url)
            for row in weekly_page.xpath('//div[./div[contains(@class,"cssMeetings")]/div]'):
                day = row.xpath('div[contains(@class, "cssDateLabel")]/text()')[0]
                for meeting_row in row.xpath('div[contains(@class, "cssMeetings")]/div'):
                    time = meeting_row.xpath('span[contains(@class,"cssMeetingTime")][1]/text()')[0]
                    title = meeting_row.xpath('span[contains(@class,"cssMeetingSubject")]/a/text()')[0]
                    link = meeting_row.xpath('span[contains(@class,"cssMeetingSubject")]/a/@href')[0]
                    if meeting_row.xpath('span[contains(@class,"cssMeetingLocation")]/text()'):
                        location = meeting_row.xpath('span[contains(@class,"cssMeetingLocation")]/text()')[0]
                        location = location.strip()
                        location = location.replace(" CAP", ' 206 Washington Street, Atlanta, GA 30334')
                    print(day, time, title, link, location)

                    meeting_page = self.get(link).content
                    meeting_page = lxml.html.fromstring(meeting_page)

                    if 'tbd' in time.lower():
                        meeting_date_str = day
                        date_format = '%A, %B %d, %Y'
                    else:
                        meeting_date_str = '{} {}'.format(day, time)
                        date_format = '%A, %B %d, %Y %I:%M %p'

                    print(meeting_date_str)
                    # Friday, November 16, 2018 8:30 AM
                    meeting_date = datetime.datetime.strptime(meeting_date_str, date_format)
                    meeting_date = self.tz.localize(meeting_date)
                    event = Event(
                        name=title,
                        start_date=meeting_date,
                        location_name=location.strip()
                    )

                    event.add_source(link)

                    # dumb hack to match case insensitive in xpath 1.0
                    # https://stackoverflow.com/questions/8474031/case-insensitive-xpath-contains-possible
                    agenda_link = meeting_page.xpath('//a[contains(translate(text(), "AGENDA", "agenda"), "agenda")]/@href')
                    if agenda_link:
                        print(agenda_link[0])
                        event.add_document(note="Agenda", url=agenda_link[0], media_type="application/pdf")

                    yield event

    def extract_vars_from_href(self, href):
        return href.replace("javascript:__doPostBack('Calendar1','", '').replace("')", '')