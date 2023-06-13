import re
import uuid
from utils import url_xpath
from datetime import date
from openstates.scrape import State
from openstates.metadata.models import (
    State as modelState,
    Chamber,
    simple_numbered_districts,
)

from .bills import A2BillScraper

# from .events import A2EventScraper

class AnnArbor(State):
    division_id = "ocd-division/country:us/state:mi/place:ann_arbor"
    classification = "legislature"
    name = "Ann Arbor"
    legislature_name = "City Council"
    url = "https://a2gov.legistar.com/"
    scrapers = {
        "bills": A2BillScraper,
        # "events": A2EventScraper,
    }

    org_id = uuid.uuid4()
    org_id = f"ocd-organization/{org_id}"
    metadata = modelState(
        name="Ann Arbor",
        abbr="mia2",
        capital="None",
        capital_tz="America/Chicago",
        fips="48",
        unicameral=True,
        legislature_name="Ann Arbor City Council",
        legislature_organization_id="ocd-organization/8ab77a54-0646-413c-a63a-dc85154282b7",
        executive_name="Executive",
        executive_organization_id="ocd-organization/4c8c2a9c-f33c-476d-bf81-266eb72193f0",
        division_id="ocd-division/country:us/state:mi/place:ann_arbor",
        jurisdiction_id="ocd-division/country:us/state:mi/place:ann_arbor/government",
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
            "_scraped_name": "2023",
            "classification": "primary",
            "identifier": "2023",
            "name": "2023 Session",
            "start_date": "2023-01-01",
            "end_date": "2023-12-31",
            "active": True,
        },
    ]
    ignored_scraped_sessions = []

    def get_session_list(self):
        return [str(date.today().year)]
