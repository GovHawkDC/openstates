import re
import uuid
from utils import url_xpath
from datetime import date
from openstates.scrape import State
from openstates.metadata.models import State as modelState, Chamber, simple_numbered_districts

# from .bills import KYBillScraper
from .events import DaytonEventScraper


class Dayton(State):
    division_id = "ocd-division/country:us/state:oh/place:dayton"
    classification = "legislature"
    name = "Dayton"
    legislature_name = "Dayton"
    url = "https://www.daytonohio.gov/AgendaCenter/"
    scrapers = {
        "events": DaytonEventScraper,
    }

    org_id = uuid.uuid4()
    org_id = f"ocd-organization/{org_id}"
    metadata = modelState(
        name="Dayton",
        abbr="ohday",
        capital="None",
        capital_tz="America/Chicago",
        fips="48",
        unicameral=True,
        legislature_name="Dayton City Council",
        legislature_organization_id="ocd-organization/8ab77a54-0646-413c-a63a-dc85154282b7",
        executive_name="Executive",
        executive_organization_id="ocd-organization/4c8c2a9c-f33c-476d-bf81-266eb72193f0",
        division_id="ocd-division/country:us/state:oh/city:dayton",
        jurisdiction_id="ocd-jurisdiction/country:us/state:oh/city:dayton/government",
        url="https://www.daytonohio.gov/AgendaCenter/City-Commission-2",
        legislature=Chamber(
            chamber_type="upper",
            name="City Council",
            organization_id=org_id,
            num_seats=31,
            title="Councilmember",
            districts=[]
            # districts=simple_numbered_districts(
            #     "ocd-division/country:us/state:tx", "upper", 31
            # ),
        ),
    )
    legislative_sessions = [
        {
            "_scraped_name": "2022",
            "classification": "primary",
            "identifier": "2022",
            "name": "2022 Session",
            "start_date": "2022-01-01",
            "end_date": "2022-12-31",
            "active": True
        },
    ]
    ignored_scraped_sessions = [
      
    ]

    def get_session_list(self):
        return [str(date.today().year)]
