from utils import url_xpath
from openstates.scrape import State
from .bills import NMBillScraper
from .votes import NMVoteScraper
from .events import NMEventScraper


class NewMexico(State):
    scrapers = {
        "bills": NMBillScraper,
        "events": NMEventScraper,
        "votes": NMVoteScraper,
    }
    legislative_sessions = [
        {
            "_scraped_name": "2011 Regular",
            "identifier": "2011",
            "name": "2011 Regular Session",
            "start_date": "2011-01-18",
            "end_date": "2011-03-19",
        },
        {
            "_scraped_name": "2011 1st Special",
            "identifier": "2011S",
            "name": "2011 Special Session",
            "start_date": "2011-09-15",
            "end_date": "2011-09-23",
        },
        {
            "_scraped_name": "2012 Regular",
            "identifier": "2012",
            "name": "2012 Regular Session",
            "start_date": "2012-01-17",
            "end_date": "2012-02-16",
        },
        {
            "_scraped_name": "2013 Regular",
            "identifier": "2013",
            "name": "2013 Regular Session",
            "start_date": "2013-01-15",
            "end_date": "2013-03-16",
        },
        {
            "_scraped_name": "2014 Regular",
            "identifier": "2014",
            "name": "2014 Regular Session",
            "start_date": "2014-01-21",
            "end_date": "2014-02-20",
        },
        {
            "_scraped_name": "2015 Regular",
            "identifier": "2015",
            "name": "2015 Regular Session",
            "start_date": "2015-01-20",
            "end_date": "2015-03-21",
        },
        {
            "_scraped_name": "2015 1st Special",
            "identifier": "2015S",
            "name": "2015 Special Session",
            "start_date": "2015-06-08",
            "end_date": "2015-06-08",
        },
        {
            "_scraped_name": "2016 Regular",
            "classification": "primary",
            "identifier": "2016",
            "name": "2016 Regular Session",
            "start_date": "2016-01-19",
            "end_date": "2016-02-18",
        },
        {
            "_scraped_name": "2016 2nd Special",
            "classification": "special",
            "identifier": "2016S",
            "name": "2016 2nd Special Session",
            "start_date": "2016-09-30",
            "end_date": "2016-10-01",
        },
        {
            "_scraped_name": "2017 Regular",
            "classification": "primary",
            "identifier": "2017",
            "name": "2017 Regular Session",
            "start_date": "2016-01-17",
            "end_date": "2017-03-18",
        },
        {
            "_scraped_name": "2017 1st Special",
            "classification": "special",
            "identifier": "2017S",
            "name": "2017 Special Session",
            "start_date": "2017-05-24",
            "end_date": "2017-05-30",
        },
        {
            "_scraped_name": "2018 Regular",
            "classification": "primary",
            "identifier": "2018",
            "name": "2018 Regular Session",
            "start_date": "2018-01-15",
            "end_date": "2018-03-16",
        },
        {
            "_scraped_name": "2019 Regular",
            "classification": "primary",
            "identifier": "2019",
            "name": "2019 Regular Session",
            "start_date": "2019-01-15",
            "end_date": "2019-03-16",
        },
        {
            "_scraped_name": "2020 Regular",
            "classification": "primary",
            "identifier": "2020",
            "name": "2020 Regular Session",
            "start_date": "2020-01-21",
            "end_date": "2020-02-20",
        },
        {
            "_scraped_name": "2020 1st Special",
            "classification": "special",
            "identifier": "2020S",
            "name": "2020 Special Session",
            "start_date": "2020-06-18",
            "end_date": "2020-06-22",
        },
        {
            "_scraped_name": "2020 2nd Special",
            "classification": "special",
            "identifier": "2020S2",
            "name": "2020 Second Special Session",
            "start_date": "2020-11-24",
            "end_date": "2020-11-24",
        },
        {
            "_scraped_name": "2021 Special",
            "classification": "special",
            "identifier": "2021S",
            "name": "2021 Special Session",
            "start_date": "2021-03-30",
            "end_date": "2021-03-31",
        },
        {
            "_scraped_name": "2021 Regular",
            "classification": "primary",
            "identifier": "2021",
            "name": "2021 Regular Session",
            "start_date": "2021-01-19",
            "end_date": "2021-03-20",
            "active": False,
        },
        {
            "_scraped_name": "2021 2nd Special",
            "classification": "special",
            "identifier": "2021S2",
            "name": "2021 Second Special Session",
            "start_date": "2021-12-06",
            "end_date": "2021-12-17",
            "active": False,
        },
        {
            "_scraped_name": "2022 Regular",
            "classification": "primary",
            "identifier": "2022",
            "name": "2022 Regular Session",
            "start_date": "2022-01-18",
            "end_date": "2022-02-17",
            "active": False,
        },
        {
            "_scraped_name": "2022 3rd Special",
            "classification": "special",
            "identifier": "2022S3",
            "name": "2022 Third Special Session",
            "start_date": "2022-04-05",
            "end_date": "2022-04-05",
            "active": False,
        },
        {
            "_scraped_name": "2023 Regular",
            "classification": "primary",
            "identifier": "2023",
            "name": "2023 Regular Session",
            "start_date": "2023-01-17",
            "end_date": "2023-03-18",
            "active": False,
        },
        {
            "_scraped_name": "2024 Regular",
            "classification": "primary",
            "identifier": "2024",
            "name": "2024 Regular Session",
            "start_date": "2024-01-16",
            "end_date": "2024-02-15",
            "active": False,
        },
        {
            "_scraped_name": "2024 1st Special",
            "classification": "primary",
            "identifier": "2024S1",
            "name": "2024 First Special Session",
            "start_date": "2024-07-18",
            # TODO: Correct start date
            "end_date": "2024-07-26",
            "active": True,
        },
    ]
    ignored_scraped_sessions = [
        "2010 2nd Special",
        "2010 Regular",
        "2009 1st Special",
        "2009 Regular",
        "2008 2nd Special",
        "2008 Regular",
        "2007 1st Special",
        "2007 Regular",
        "2006 Regular",
        "2005 1st Special",
        "2005 Regular",
        "2004 Regular",
        "2003 1st Special",
        "2003 Regular",
        "2002 Extraordinary",
        "2002 Regular",
        "2001 2nd Special",
        "2001 1st Special",
        "2001 Regular",
        "2000 2nd Special",
        "2000 Regular",
        "1999 1st Special",
        "1999 Regular",
        "1998 1st Special",
        "1998 Regular",
        "1997 Regular",
        "1996 1st Special",
        "1996 Regular",
    ]

    def get_session_list(self):
        return url_xpath(
            "http://www.nmlegis.gov/",
            '//select[@name="ctl00$MainContent$ddlSessions"]' "/option/text()",
        )
