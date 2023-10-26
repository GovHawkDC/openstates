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

from .bills import DallasBillScraper

# from .events import A2EventScraper

class Dallas(State):
    division_id = "ocd-division/country:us/state:tx/place:Dallas"
    classification = "legislature"
    name = "Dallas"
    legislature_name = "City Council"
    url = "https://cityofdallas.legistar.com/"
    scrapers = {
        "bills": DallasBillScraper,
        # "events": A2EventScraper,
    }

    org_id = uuid.uuid4()
    org_id = f"ocd-organization/{org_id}"
    metadata = modelState(
        name="Dallas",
        abbr="phx",
        capital="None",
        capital_tz="America/Central",
        fips="48",
        unicameral=True,
        legislature_name="Dallas City Council",
        legislature_organization_id="ocd-organization/8ab77a54-0646-413c-a63a-dc85154282b8",
        executive_name="Executive",
        executive_organization_id="ocd-organization/4c8c2a9c-f33c-476d-bf81-266eb72193f8",
        division_id="ocd-division/country:us/state:az/place:Dallas",
        jurisdiction_id="ocd-division/country:us/state:az/place:Dallas/government",
        url="https://cityofdallas.legistar.com//Calendar.aspx",
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
