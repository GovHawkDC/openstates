import re
import pytz
import lxml
import dateutil.parser
from openstates.scrape import Scraper, Bill, VoteEvent
from collections import defaultdict

from .common import SESSION_SITE_IDS

tz = pytz.timezone("America/New_York")
SKIP = "~~~SKIP~~~"
ACTION_CLASSIFIERS = (
    ("Enacted, Chapter", "became-law"),
    ("Approved by Governor", "executive-signature"),
    ("Vetoed by Governor", "executive-veto"),
    ("(House|Senate) sustained Governor's veto", "veto-override-failure"),
    (r"\s*Amendment(s)? .+ agreed", "amendment-passage"),
    (r"\s*Amendment(s)? .+ withdrawn", "amendment-withdrawal"),
    (r"\s*Amendment(s)? .+ rejected", "amendment-failure"),
    ("Subject matter referred", "referral-committee"),
    ("Rereferred to", "referral-committee"),
    ("Referred to", "referral-committee"),
    ("Assigned ", "referral-committee"),
    ("Reported from", "committee-passage"),
    ("Read third time and passed", ["passage", "reading-3"]),
    ("Read third time and agreed", ["passage", "reading-3"]),
    ("Passed (Senate|House)", "passage"),
    ("passed (Senate|House)", "passage"),
    ("Read third time and defeated", "failure"),
    ("Presented", "introduction"),
    ("Prefiled and ordered printed", "introduction"),
    ("Read first time", "reading-1"),
    ("Read second time", "reading-2"),
    ("Read third time", "reading-3"),
    ("Senators: ", SKIP),
    ("Delegates: ", SKIP),
    ("Committee substitute printed", "substitution"),
    ("Bill text as passed", SKIP),
    ("Acts of Assembly", SKIP),
)


class VaWebBillScraper(Scraper):

    def scrape(self, session=None):
        if not session:
            session = self.jurisdiction.legislative_sessions[-1]["identifier"]
            self.info("no session specified, using %s", session)

        chamber_types = {
            "H": "lower",
            "S": "upper",
            "G": "executive",
            "C": "legislature",
        }
        session_id = SESSION_SITE_IDS[session]

        first_page = f"https://lis.virginia.gov/cgi-bin/legp604.exe?{session_id}+lst+ALL"

        yield from self.scrape_list_page(session, first_page)

    def scrape_list_page(self, session, url):
        page = self.get(url).content
        page = lxml.html.fromstring(page)
        page.make_links_absolute(url)

        for link in page.xpath('//ul[contains(@class,"linkSect")]/li/a'):
            href = link.xpath("@href")[0]
            print(href)
            if (link.xpath("b[contains(text(), 'More...')]")):
                yield from self.scrape_list_page(session, href)
            else:
                yield from self.scrape_bill_page(session, href)

    def scrape_bill_page(self, session, url):
        page = self.get(url).content
        page = lxml.html.fromstring(page)
        page.make_links_absolute(url)

        # bill_id = url.rpartition("+")[2]

        # print(bill_id)

        toplink = page.xpath("//h3[@class='topLine']/text()")[0].strip()
        parts = re.search(r"(\w+\s+\d+)\s(.*)", toplink)

        bill_id = parts.groups(1)[0].replace("  "," ")
        bill_title = parts.groups(1)[1]

        print(bill_id)
        print(bill_title)    

        bill_type = {"B": "bill", "J": "joint resolution", "R": "resolution"}[
            bill_id[1]
        ]

        description = page.xpath('string(//h4[contains(text(), "SUMMARY AS")]/following-sibling::p)')
        # description = description.replace("\n", " ")
        # print(" ".join(description.split("\n")))
        print(description)
        chamber_types = {
            "H": "lower",
            "S": "upper",
            "G": "executive",
            "C": "legislature",
        }
        chamber = chamber_types[bill_id[0]]
        bill = Bill(
            bill_id,
            session,
            description,
            chamber=chamber,
            classification=bill_type,
        )

        bill.add_source(url)

        for row in page.xpath('//h4[contains(text(), "FULL TEXT")]/following-sibling::ul[contains(@class,"linkSect")][1]/li'):
            version_name = row.xpath('a[1]/text()')[0]
            version_name = version_name.replace('\u00a0', '')
            pdf_url = row.xpath('a[2]/@href')[0]

            print(version_name, pdf_url)

            version_date = re.findall(r"\d+/\d+/\d+", version_name)[1]
            version_date = dateutil.parser.parse(version_date)
            version_date = tz.localize(version_date)

            bill.add_version_link(
                version_name,
                pdf_url,
                date=version_date.strftime("%Y-%m-%d"),
                media_type="application/pdf",
                on_duplicate="ignore"
            )

            if (row.xpath('//b[contains(text(),"impact statement")]')):
                pass

        for row in page.xpath('//h4[contains(text(), "HISTORY")]/following-sibling::ul[contains(@class,"linkSect")][1]/li'):
            bill = self.parse_action(bill, row.xpath('string(.)'))

        yield bill

    def parse_action(self, bill, action):
        chambers = {
            "House": "lower",
            "Senate": "upper",
        }

        action_regex = r"(?P<date>\d+/\d+/\d+)\s+(?P<actor>House|Senate):*\s+(?P<action>.*)"

        matches = re.findall(action_regex, action)
        print(matches)
        action_date, actor, action_text = matches[0]
        print(action_date, actor, action_text)

        actor = chambers[actor]
        action_date = dateutil.parser.parse(action_date)
        action_date = tz.localize(action_date)

        bill.add_action(
            action_text,
            action_date,
            chamber=actor
        )

        return bill

            # bill_url = bill_url_base + f"legp604.exe?{session_id}+sum+{bill_id}"
            # b.add_source(bill_url)

            #         b.add_sponsorship(
            #             bill["patron_name"],
            #             classification="primary",
            #             entity_type="person",
            #             primary=True,
   
            #         b.add_version_link(
            #             version_text,
            #             version_url,
            #             date=version_date,
            #             media_type="text/html",
            #             on_duplicate="ignore",
            #         )

            # yield b
