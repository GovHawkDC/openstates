import pytz
import lxml
import dateutil.parser
import re
import sys
import scrapelib

from openstates.utils import LXMLMixin
from pupa.scrape import Scraper, Event

from .apiclient import ApiClient


class INEventScraper(Scraper, LXMLMixin):
    _TZ = pytz.timezone('US/Eastern')

    def scrape(self, session=None):
        if not session:
            session = self.latest_session()
            self.info('no session specified, using %s', session)

        api_base_url = "https://api.iga.in.gov"
        proxy = {"url": "http://in-proxy.openstates.org"}

        client = ApiClient(self)

        r = client.get("events", session=session)
        all_pages = client.unpaginate(r)
        for row in all_pages:
            event_link = row['link']
            api_link = api_base_url + event_link

            root = '/{}/meetings/'.format(session)
            meeting_id = row['link'].replace(root, '')

            try:
                event_json = client.get("event", session=session, meeting_id=meeting_id)
                print(event_json)
                yield from self.parse_row(session, event_json, meeting_id)
            except scrapelib.HTTPError:
                self.logger.warning('Event {} could not be accessed. Skipping.'.format(meeting_id))
                continue

    def parse_row(self, session, row, meeting_id):
        #  https://api.iga.in.gov/2019/meetings/3c35e29f-2c53-4d5f-a952-70833a2d38b1

        if row['cancelled'] is True:
            return

        if row['starttime'] is not None:
            event_start = '{} {}'.format(row['meetingDate'], row['starttime'])
        else:
            event_start = row['meetingDate']

        end_date = None
        if row['endtime'] is not None:
            event_end = '{} {}'.format(row['meetingDate'], row['endtime'])
            end_date = dateutil.parser.parse(event_end)
            end_date = self._TZ.localize(end_date)


        start_date = dateutil.parser.parse(event_start)
        start_date = self._TZ.localize(start_date)

        location = row['location']

        if location.startswith('Room'):
            location = '200 W. Washington St., Indianapolis, IN 46204, {}'.format(
                location)

        name = row['committee']['name']

        description = ''
        if row['agendanote']:
            description = row['agendanote']

        if end_date is not None:
            event = Event(
                start_date=start_date,
                end_date=end_date,
                name=name,
                location_name=location,
                description=description
            )
        else:
            event = Event(
                start_date=start_date,
                name=name,
                location_name=location,
                description=description
            )

        event.extras['in_id'] = meeting_id

        # http://iga.in.gov/legislative/2019
        # /committees/family_and_children#3c35e29f-2c53-4d5f-a952-70833a2d38b1
        web_url = 'http://iga.in.gov/legislative/{}/committees/{}#{}'
        web_url = web_url.format(
            session,
            self.committee_slug(row['committee']['link']),
            meeting_id
        )
        event.add_source(web_url)

        event.add_participant(
            row['committee']['name'],
            type='committee',
            note='host',
        )

        for agenda_row in row['agenda']:
            desc = agenda_row['bill']['shortDescription']
            agenda_item = event.add_agenda_item(description=desc)
            agenda_item.add_bill(agenda_row['bill']['billName'])

        # for doc_row in row['exhibits']:
        # .. haven't figured out how to get public URLS here yet. Sigh.

        yield event


    '''The Committee Links provided by the api are broken, so transform them

    Returns:
        string -- working committee url slug
    '''
    def committee_slug(self, link):
        tail = link.split('/')[-1]
        tail = tail.replace('committee_','')
        return tail
