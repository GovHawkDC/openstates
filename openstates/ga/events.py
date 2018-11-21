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

        # this is an asp form so grab our __VIEWSTATE
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
        # the week's events
        sundays = page.xpath('//table[@id="Calendar1"]/tr/td[1]/a/@href')
        for sunday in sundays:
            cal_id = self.extract_vars_from_href(sunday)
            form['__EVENTARGUMENT'] = cal_id
            weekly_html = self.post(url=base_url, data=form, allow_redirects=True).content
            weekly_page = lxml.html.fromstring(weekly_html)
            weekly_page.make_links_absolute(base_url)
            for row in weekly_page.xpath('//div[./div[contains(@class,"cssMeetings")]/div]'):
                meeting_date = row.xpath('div[contains(@class, "cssDateLabel")]/text()')[0]
                for meeting_row in row.xpath('div[contains(@class, "cssMeetings")]/div'):
                    time = meeting_row.xpath('span[contains(@class,"cssMeetingTime")][1]/text()')[0]
                    title = meeting_row.xpath('span[contains(@class,"cssMeetingSubject")]/a/text()')[0]
                    link = meeting_row.xpath('span[contains(@class,"cssMeetingSubject")]/a/@href')[0]
                    if meeting_row.xpath('span[contains(@class,"cssMeetingLocation")]/text()'):
                        location = meeting_row.xpath('span[contains(@class,"cssMeetingLocation")]/text()')[0]
                    print(meeting_date, time, title, link, location)

                    meeting_page = self.get(meeting_link).content
                    meeting_page = self.

    def extract_vars_from_href(self, href):
        return href.replace("javascript:__doPostBack('Calendar1','", '').replace("')", '')