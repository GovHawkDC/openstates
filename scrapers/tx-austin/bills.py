import json
import lxml

import pytz

from openstates.scrape import Scraper, Event

import datetime as dt
from utils.ghlegistarapibills import GHLegistarAPIBillScraper
from legistar.bills import LegistarBillScraper

class AustinBillScraper(GHLegistarAPIBillScraper, Scraper):
    TIMEZONE = "US/Central"
    BASE_URL = "http://webapi.legistar.com/v1/austintexas"
    BASE_WEB_URL = "https://austintexas.legistar.com/"
    LEGISLATION_URL = "https://austintexas.legistar.com/Legislation.aspx"

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
                'Consent': 'order',
                }
