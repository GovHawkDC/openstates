import datetime
import pytz
import re
import xml.etree.ElementTree as ET 

from openstates.scrape import Bill, Scraper, VoteEvent

class USBillScraper(Scraper):
    # https://www.govinfo.gov/rss/billstatus-batch.xml
    # https://github.com/usgpo/bill-status/blob/master/BILLSTATUS-XML_User_User-Guide.md

    # good sample bill:
    # https://www.govinfo.gov/bulkdata/BILLSTATUS/116/hr/BILLSTATUS-116hr8337.xml

    # custom namespace, see
    # https://docs.python.org/2/library/xml.etree.elementtree.html#parsing-xml-with-namespaces
    ns = {'us': 'http://www.sitemaps.org/schemas/sitemap/0.9'}

    _TZ = pytz.timezone("US/Eastern")

    chambers = {'House': 'lower', 'Joint': 'joint', 'Senate': 'upper'}

    classifications = {
        'HRES':'resolution',
        'HCONRES': 'resolution',
        'HR': 'bill',
        'HJRES': 'resolution',
        'SRES': 'resolution',
        'SJRES': 'resolution',
        'S': 'bill',
        'SCONRES': 'resolution',
    }

    def scrape(self, chambers=None, session=None):
        if not session:
            session = self.latest_session()
            self.info("no session specified, using %s", session)

        sitemap_url = 'https://www.govinfo.gov/sitemap/bulkdata/BILLSTATUS/sitemapindex.xml'
        sitemaps = self.get(sitemap_url).content
        root = ET.fromstring(sitemaps)

        for link in root.findall('us:sitemap/us:loc', self.ns):
            if session in link.text:
                yield from self.parse_bill_list(link.text)

    def parse_bill_list(self, url):
        sitemap = self.get(url).content
        root = ET.fromstring(sitemap)
        for bill_url in root.findall('us:url/us:loc', self.ns):
            yield from self.parse_bill(bill_url.text)

    def parse_bill(self, url):
        xml = self.get(url).content
        xml = ET.fromstring(xml)

        bill_num = self.get_xpath(xml, 'bill/billNumber')
        bill_type = self.get_xpath(xml, 'bill/billType')

        bill_id = '{} {}'.format(bill_type, bill_num)

        chamber_name = self.get_xpath(xml, 'bill/originChamber')
        chamber = self.chambers[chamber_name]

        title = self.get_xpath(xml, 'bill/title')

        classification = self.classifications[bill_type]

        session = self.get_xpath(xml, 'bill/congress')

        bill = Bill(
            bill_id,
            legislative_session=session,
            chamber=chamber,
            title=title,
            classification=classification,
        )

        self.scrape_actions(bill, xml)
        self.scrape_titles(bill, xml)
        self.scrape_sponsors(bill, xml)
        self.scrape_cosponsors(bill, xml)
        self.scrape_versions(bill, xml)

        # https://www.congress.gov/bill/116th-congress/house-bill/1
        xml_url = 'https://www.govinfo.gov/bulkdata/BILLSTATUS/{congress}/{type}/BILLSTATUS-{congress}{type}{num}.xml'
        bill.add_source(
            xml_url.format(
                congress=session,
                type=bill_type.lower(),
                num=bill_num
            )
        )

        cg_url = 'https://congress.gov/bill/{congress}th-congress/{chamber}-{type}/{num}'
        bill.add_source(
            cg_url.format(
                congress=session,
                chamber=chamber_name.lower(),
                type=classification.lower(),
                num=bill_num
            )
        )

        yield bill

    def build_sponsor_name(self, row):
        first_name = self.get_xpath(row, 'firstName')
        middle_name = self.get_xpath(row, 'middleName')
        last_name = self.get_xpath(row, 'lastName')
        return ' '.join(filter(None,[first_name, middle_name, last_name]))

    def classify_action(self, bill, action):
        # https://github.com/usgpo/bill-status/blob/master/BILLSTATUS-XML_User_User-Guide.md
        # see table 3, Action Code Element Possible Values
        pass

    def get_xpath(self, xml, xpath):
        return xml.findall(xpath, self.ns)[0].text

    def scrape_actions(self, bill, xml):
        # list for deduping
        actions = []
        for row in xml.findall('bill/actions/item'):
            action_text = self.get_xpath(row, 'text')
            if action_text not in actions:
                source = self.get_xpath(row, 'sourceSystem/name')
                action_type = self.get_xpath(row, 'type')

                actor = 'lower'
                if 'Senate' in source:
                    actor = 'upper'
                elif 'House' in source:
                    actor = 'lower'
                elif action_type == 'BecameLaw' or action_type == 'President':
                    actor = 'executive'

                if row.findall('actionTime'):
                    action_date = '{} {}'.format(
                        self.get_xpath(row, 'actionDate'),
                        self.get_xpath(row, 'actionTime')
                    )
                    action_date = datetime.datetime.strptime(action_date, '%Y-%m-%d %H:%M:%S')
                else:
                    action_date = datetime.datetime.strptime(
                        self.get_xpath(row, 'actionDate'),
                        '%Y-%m-%d'
                    )
                # chamber will be fun
                action_date = self._TZ.localize(action_date)

                bill.add_action(
                    action_text,
                    action_date,
                    chamber=actor,
                    classification=None
                )
                actions.append(action_text)

    def scrape_cosponsors(self, bill, xml):
        for row in xml.findall('bill/cosponsors/item'):
            if not row.findall('sponsorshipWithdrawnDate'):
                bill.add_sponsorship(
                    self.build_sponsor_name(row), classification="cosponsor", primary=False, entity_type="person"
                )

    def scrape_sponsors(self, bill, xml):
        for row in xml.findall('bill/sponsors/item'):
            if not row.findall('sponsorshipWithdrawnDate'):
                bill.add_sponsorship(
                    self.build_sponsor_name(row), classification="primary", primary=True, entity_type="person"
                )

    def scrape_subjects(self, bill, xml):
        for row in xml.findall('bill/subjects/billSubjects/legislativeSubjects/item'):
            bill.add_subject(self.get_xpath(row, 'name'))

    def scrape_titles(self, bill, xml):
        all_titles = set()
        # add current title to prevent dupes
        all_titles.add(bill.title)

        for alt_title in xml.findall('bill/titles/item'):
            all_titles.add(self.get_xpath(alt_title, 'title'))

        all_titles.remove(bill.title)

        for title in all_titles:
            bill.add_title(title)

    def scrape_versions(self, bill, xml):
        for row in xml.findall('bill/textVersions/item'):
            version_title = self.get_xpath(row, 'type')

            for version in row.findall('formats/item'):
                url = self.get_xpath(version, 'url')
                bill.add_version_link(
                    note = version_title,
                    url = url,
                    media_type = 'text/xml'
                )
                bill.add_version_link(
                    note = version_title,
                    url = url.replace('xml', 'pdf'),
                    media_type = 'application/pdf'
                )
