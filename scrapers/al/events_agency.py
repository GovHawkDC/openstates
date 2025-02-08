import dateutil.parser
import lxml
import pytz

from openstates.scrape import Scraper, Event


class ALAgencyEventScraper(Scraper):
    tz = pytz.timezone("US/Eastern")

    def scrape(self, start_date=None, end_date=None):
        yield from self.scrape_page(0)

    def scrape_page(self, page_num: int, current_page: lxml.html.HtmlElement = None):
        self.info(f"Scraping page {page_num + 1}")
        data = {
            "__EVENTTARGET": f"dgrdTitles$_ctl29$_ctl{page_num}",
            "Agency_TextBox": "",
            "location_Filter_TextBox": "",
            "From_Month_List": "2",
            "From_Day_List": "7",
            "From_Year_List": "2025",
            "To_Month_List": "3",
            "To_Day_List": "7",
            "To_Year_List": "2025",
            "From_Hour_List": "12",
            "From_Minute_List": "00",
            "From_AM_PM_List": "AM",
            "To_Hour_List": "11",
            "To_Minute_List": "59",
            "To_AM_PM_List": "PM",
        }

        url = "https://www.openmeetings.alabama.gov/generalpublic/display_notices.aspx"
        page = self.asp_post(url, data=data, page=current_page)

        for link in page.cssselect("table.ViewNoticesGrid tr td div a"):
            yield from self.scrape_event(link.xpath("@href")[0])

        # if there's a next page link, scrape it
        for link in page.cssselect("tr.ViewNoticesGridPager a"):
            # the post variable is zero indexed
            page_link = int(link.text_content()) - 1
            if page_link == page_num + 1:
                yield from self.scrape_page(page_num + 1, page)

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

    def asp_post(self, url: str, data: dict, page=None):
        # if there's no page object to pull the ASP session vars from, GET one first
        if not page:
            page = self.get(url)
            page = lxml.html.fromstring(page.content)

        (viewstate,) = page.xpath('//input[@id="__VIEWSTATE"]/@value')
        (viewstategenerator,) = page.xpath('//input[@id="__VIEWSTATEGENERATOR"]/@value')
        (eventvalidation,) = page.xpath('//input[@id="__EVENTVALIDATION"]/@value')

        form = {
            "__VIEWSTATE": viewstate,
            "__VIEWSTATEGENERATOR": viewstategenerator,
            "__EVENTVALIDATION": eventvalidation,
            "__EVENTARGUMENT": "",
        }

        data = {**form, **data}
        page = self.post(url, data=data).content
        page = lxml.html.fromstring(page)
        page.make_links_absolute(url)
        return page
