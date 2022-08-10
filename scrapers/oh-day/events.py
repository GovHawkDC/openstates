import json
import lxml

import pytz

from openstates.scrape import Scraper, Event

import datetime as dt
from dateutil.relativedelta import relativedelta
import dateutil.parser
import cloudscraper


class DaytonEventScraper(Scraper):
    _tz = pytz.timezone("US/Eastern")

    base_url = "https://www.legislature.ohio.gov/schedules/"

    scraper = cloudscraper.create_scraper()

    def scrape(self, start=None, end=None):
        event = Event(
            name="test event",
            start_date=dt.datetime.now(self._tz),
            location_name="the whitehouse",
        )

        event.add_participant("City Council", type="committee", note="host")
        # event.add_document("Agenda", agenda_url, media_type="application/pdf")
        event.add_source('https://www.daytonohio.gov/AgendaCenter/City-Commission-2')

        yield event