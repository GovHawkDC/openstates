# encoding=utf-8
from openstates.scrape import State, Organization
from openstates.metadata.models import (
    State as modelState,
    Chamber,
    simple_numbered_districts,
)
import datetime
from .events import LACountyEventScraper


class LACounty(State):
    division_id = "ocd-division/country:us/state:ca/county:los_angeles"
    classification = "legislature"
    name = "LA County"
    url = "https://lacounty.granicus.com/ViewPublisher.php?view_id=1"
    scrapers = {
        "events": LACountyEventScraper,
    }

    def get_organizations(self):
        org = Organization(name="LA County Government", classification="legislature")
        yield org

    legislative_sessions = [
        {
            "_scraped_name": "2024",
            "classification": "primary",
            "identifier": "2024",
            "name": "2024 Session",
            "start_date": "2024-01-01",
            "end_date": "2024-12-31",
            "active": True,
        },
    ]
    ignored_scraped_sessions = []

    def get_session_list(self):
        return [str(datetime.date.today().year)]