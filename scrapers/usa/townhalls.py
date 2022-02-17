import pytz
import json
import dateutil.parser
import re
import requests

from utils import LXMLMixin
from openstates.scrape import Scraper, Event


class USTownHallScraper(Scraper, LXMLMixin):
    _TZ = pytz.timezone("America/New_York")
    s = requests.Session()

    def scrape(self):
        id_url = 'https://indivisible-data.firebaseio.com/indivisible_public_events.json'

        json = self.get(id_url).json()

        for key, meet in json.items():
            if not ('actionMeetingType' in meet and meet['actionMeetingType'] == 'Town Hall'):
                continue
            
            when = dateutil.parser.parse(f"{meet['starts_at_utc']} UTC")
            what = meet['title']

            address = " ".join([meet['address1'],meet['address2'], meet['city'], meet['state'], meet['zip']])
            
            event = Event(start_date=when, name=what, location_name=address)

            event.add_source(meet['linkToInfo'])
            yield event
        
        if len(json.items()) == 0:
            raise EmptyScrape
