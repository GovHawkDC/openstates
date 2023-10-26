import json
import lxml

import pytz

from openstates.scrape import Scraper, Event

import datetime as dt
from utils.ghlegistarapibills import GHLegistarAPIBillScraper
from legistar.bills import LegistarBillScraper

class DallasBillScraper(LegistarBillScraper, Scraper):
    TIMEZONE = "US/Central"
    BASE_URL = "http://webapi.legistar.com/v1/cityofdallas"
    BASE_WEB_URL = "https://cityofdallas.legistar.com/"
    LEGISLATION_URL = "https://cityofdallas.legistar.com/Legislation.aspx"

    VOTE_OPTIONS = {'yea' : 'yes',
                    'rising vote' : 'yes',
                    'nay' : 'no',
                    'recused' : 'excused',
                    'yes': 'yes',
                    'no': 'no',
                    'excused': 'excused',
                    'abstain': 'abstain',
                    'aye': 'yes',
                    'present': 'present',
                    'absent': 'absent',
                    'non-voting': 'not voting',
                    'conflict': 'other',
                    }

    BILL_TYPES = {'Ordinance' : 'ordinance',
                'Resolution' : 'resolution',
                'Order' : 'order',
                'Claim' : 'claim',
                'Oath of Office' : None,
                'Communication' : None,
                'Appointment' : 'appointment',
                'Action Item': None,
                'Report' : None,
                'Ceremonial Item': None,
                'Minutes': None,
                'Board/Commission': None,
                'Resolution/Public Hearing': 'resolution',
                'Public Hearing Only': None,
                }

    def scrape(self):
        bills = self.legislation(created_after=dt.datetime(2023, 6, 1))
        for bill in bills:
            print(bill)
        yield []