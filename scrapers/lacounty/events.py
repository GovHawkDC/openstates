import pytz
from openstates.scrape import Scraper, Event
from utils.granicus import GranicusScraper


class LACountyEventScraper(GranicusScraper, Scraper):
    BASE_URL = "https://lacounty.granicus.com/ViewPublisher.php?view_id=1"
    TIMEZONE = pytz.timezone("America/Los_Angeles")