import json
import lxml

import pytz

from openstates.scrape import Scraper, Event

import datetime as dt
from utils.agendacenter import AgendaCenterScraper


class DaytonEventScraper(AgendaCenterScraper, Scraper):
    TIMEZONE = pytz.timezone("US/Eastern")
    BASE_URL = "https://www.daytonohio.gov/AgendaCenter"
