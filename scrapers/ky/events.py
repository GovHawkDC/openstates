import datetime
import os
import re
import json
import lxml

import pytz

from openstates.scrape import Scraper, Event
from openstates.utils import convert_pdf

import datetime as dt
from dateutil.relativedelta import relativedelta
import dateutil.parser


class KYEventScraper(Scraper):
    _tz = pytz.timezone("US/Eastern")

    def scrape(self):
        url = "https://apps.legislature.ky.gov/legislativecalendar"

        page = self.get(url).content
        page = lxml.html.fromstring(page)

        for time_row in page.xpath('//div[contains(@class,"TimeAndLocation")]'):
            date = (
                time_row.xpath(
                    'preceding-sibling::div[contains(@class,"DateHeading")][1]'
                )[0]
                .text_content()
                .strip()
            )

            status = "tentative"

            if time_row.xpath('div[contains(@class,"Cancelled")]'):
                status = "cancelled"

            row_text = time_row.text_content()
            row_text = row_text.replace("Noon", "PM")
            # upon recess (of House|Senate)
            row_text = re.sub("Upon Recess(\sof\s)?(House|Senate)?", "", row_text)
            parts = re.split(',|AM|PM', row_text)
            time = parts[0].strip()
            location = " ".join(x.replace(u'\xa0','').strip() for x in parts[1:])

            when = f"{date} {time}"
            when = dateutil.parser.parse(when)
            when = self._tz.localize(when)

            if not time_row.xpath(
                'following-sibling::div[contains(@class,"CommitteeName")][1]/a'
            ):
                continue

            com_name = (
                time_row.xpath(
                    'following-sibling::div[contains(@class,"CommitteeName")][1]/a'
                )[0]
                .text_content()
                .strip()
            )

            event = Event(
                name=com_name,
                start_date=when,
                classification="committee-meeting",
                location_name=location,
                status=status,
            )

            agenda_row = time_row.xpath(
                'following-sibling::div[contains(@class,"Agenda")][1]'
            )[0]
            agenda_text = agenda_row.text_content().strip()

            agenda = event.add_agenda_item(agenda_text)

            for bill_link in agenda_row.xpath('.//a[contains(@href,"/record/")]'):
                agenda.add_bill(bill_link.text_content().strip())

            event.add_source(url)

            yield event
