from legistar.bills import LegistarBillScraper, LegistarAPIBillScraper
from openstates.scrape import Scraper, Bill, VoteEvent
import datetime


class GHLegistarAPIBillScraper(LegistarAPIBillScraper, Scraper):
    def session(self, action_date):
        return str(action_date.year)

    def sponsorships(self, matter_id):
        for i, sponsor in enumerate(self.sponsors(matter_id)):
            sponsorship = {}
            if i == 0:
                sponsorship["primary"] = True
                sponsorship["classification"] = "Primary"
            else:
                sponsorship["primary"] = False
                sponsorship["classification"] = "Regular"

            sponsor_name = sponsor["MatterSponsorName"].strip()

            if sponsor_name.startswith(("City Clerk",)):
                sponsorship["name"] = "Office of the City Clerk"
                sponsorship["entity_type"] = "organization"
            else:
                sponsorship["name"] = sponsor_name
                sponsorship["entity_type"] = "person"

            if not sponsor_name.startswith(
                ("Misc. Transmittal", "No Sponsor", "Dept./Agency")
            ):
                yield sponsorship

    def actions(self, matter_id):
        old_action = None
        actions = self.history(matter_id)

        for action in actions:
            action_date = action["MatterHistoryActionDate"]
            action_description = action["MatterHistoryActionName"]
            responsible_org = action["MatterHistoryActionBodyName"]

            action_date = self.toTime(action_date).date()

            responsible_person = None
            # if responsible_org == 'City Council' :
            #     responsible_org = 'Chicago City Council'
            # elif responsible_org == 'Office of the Mayor':
            #     responsible_org = 'City of Chicago'
            #     if action_date < datetime.date(2011, 5, 16):
            #         responsible_person = 'Daley, Richard M.'
            #     else:
            #         responsible_person = 'Emanuel, Rahm'

            bill_action = {
                "description": action_description,
                "date": action_date,
                "organization": {"name": responsible_org},
                #    'classification' : ACTION[action_description]['ocd'], # TODO: action classifier somehow
                "classification": None,
                "responsible person": responsible_person,
            }
            if bill_action != old_action:
                old_action = bill_action
            else:
                continue

            if (
                action["MatterHistoryEventId"] is not None
                and action["MatterHistoryRollCallFlag"] is not None
                and action["MatterHistoryPassedFlag"] is not None
            ):

                bool_result = action["MatterHistoryPassedFlag"]
                result = "pass" if bool_result else "fail"

                # Votes that are not roll calls, i.e., voice votes, sometimes
                # include "votes" that omit the vote option (yea, nay, etc.).
                # Capture that a vote occurred, but skip recording the
                # null votes, as they break the scraper.

                action_text = action["MatterHistoryActionText"] or ""

                if "voice vote" in action_text.lower():
                    # while there should not be individual votes
                    # for voice votes, sometimes there are.
                    #
                    # http://webapi.legistar.com/v1/chicago/eventitems/163705/votes
                    # http://webapi.legistar.com/v1/chicago/matters/26788/histories

                    self.info(
                        "Skipping votes for history {0} of matter ID {1}".format(
                            action["MatterHistoryId"], matter_id
                        )
                    )
                    votes = (result, [])
                else:
                    votes = (result, self.votes(action["MatterHistoryId"]))
            else:
                votes = (None, [])

            yield bill_action, votes

    def matters(self, since_datetime=None):
        # scrape from oldest to newest. This makes resuming big
        # scraping jobs easier because upon a scrape failure we can
        # import everything scraped and then scrape everything newer
        # then the last bill we scraped
        params = {"$orderby": "MatterLastModifiedUtc"}

        if since_datetime:
            since_iso = since_datetime.replace(microsecond=0).isoformat()

            update_fields = (
                "MatterLastModifiedUtc",
                "MatterIntroDate",
                "MatterPassedDate",
                "MatterDate1",
                "MatterDate2",
                # 'MatterEXDate1', # can't use all 17 search
                # terms, this one always
                # seems to be not set
                "MatterEXDate2",
                "MatterEXDate3",
                "MatterEXDate4",
                "MatterEXDate5",
                "MatterEXDate6",
                "MatterEXDate7",
                "MatterEXDate8",
                "MatterEXDate9",
                "MatterEXDate10",
                "MatterEnactmentDate",
                "MatterAgendaDate",
            )

            since_fmt = "{field} gt datetime'{since_datetime}'"
            since_filter = " or ".join(
                since_fmt.format(field=field, since_datetime=since_iso)
                for field in update_fields
            )

            ## HACK
            ## For some reason the larger filter wasnt' working
            ## but this slimmed down version does
            # since_filter = "MatterLastModifiedUtc gt datetime'2022-08-07T20:34:12'"
            since_filter = f"MatterLastModifiedUtc gt datetime'{since_iso}'"
            self.info(f"Since filter {since_filter}")

            params["$filter"] = since_filter

        matters_url = self.BASE_URL + "/matters"

        for matter in self.pages(matters_url, params=params, item_key="MatterId"):
            try:
                legistar_url = self.legislation_detail_url(matter["MatterId"])

            except scrapelib.HTTPError as e:
                if e.response.status_code > 403:
                    raise

                url = matters_url + "/{}".format(matter["MatterId"])
                self.warning("Bill could not be found in web interface: {}".format(url))
                if not self.scrape_restricted:
                    continue

            else:
                matter["legistar_url"] = legistar_url

            yield matter

    def scrape(self, window=3):
        n_days_ago = datetime.datetime.utcnow() - datetime.timedelta(float(window))
        for matter in self.matters(n_days_ago):
            self.info(n_days_ago)
            matter_id = matter["MatterId"]

            date = matter["MatterIntroDate"]
            title = matter["MatterTitle"]
            identifier = matter["MatterFile"]

            # If a bill has a duplicate action item that's causing the entire scrape
            # to fail, add it to the `problem_bills` array to skip it.
            # For the time being...nothing to skip!

            problem_bills = ["Or2011-189"]

            if identifier in problem_bills:
                continue

            if not all((date, title, identifier)):
                continue

            bill_session = self.session(self.toTime(date))
            # TODO: if it's not in .. maybe just throw a warning?
            # nice to blow up for now while deving
            if matter["MatterTypeName"] in self.BILL_TYPES:
                bill_type = self.BILL_TYPES[matter["MatterTypeName"]]
            else:
                self.warning("Unknown bill type: {}".format(matter["MatterTypeName"]))
                bill_type = None

            if identifier.startswith("S"):
                alternate_identifiers = [identifier]
                identifier = identifier[1:]
            else:
                alternate_identifiers = []

            bill = Bill(
                identifier=identifier,
                legislative_session=bill_session,
                title=title,
                classification=bill_type,
            )

            legistar_web = matter["legistar_url"]

            legistar_api = "{}/matters/{}".format(self.BASE_URL, matter_id)

            bill.add_source(legistar_web, note="web")
            bill.add_source(legistar_api, note="api")

            for identifier in alternate_identifiers:
                bill.add_identifier(identifier)

            for action, vote in self.actions(matter_id):
                responsible_person = action.pop("responsible person")
                act = bill.add_action(**action)

                if responsible_person:
                    act.add_related_entity(
                        responsible_person,
                        "person",
                    )

                if action["description"] == "Referred":
                    body_name = matter["MatterBodyName"]
                    if body_name != "City Council":
                        act.add_related_entity(body_name, "organization")

                result, votes = vote
                if result:
                    vote_event = VoteEvent(
                        legislative_session=bill.legislative_session,
                        motion_text=action["description"],
                        organization=action["organization"],
                        classification=None,
                        start_date=action["date"],
                        result=result,
                        bill=bill,
                    )

                    vote_event.add_source(legistar_web)
                    vote_event.add_source(legistar_api + "/histories")

                    for vote in votes:
                        vote_value = vote["VoteValueName"]
                        if vote_value is None:
                            continue
                        raw_option = vote_value.lower()
                        if raw_option not in self.VOTE_OPTIONS:
                            self.warning(f"{raw_option} missing from VOTE_OPTIONS")
                        clean_option = self.VOTE_OPTIONS.get(raw_option, "other")
                        vote_event.vote(clean_option, vote["VotePersonName"].strip())

                    yield vote_event

            for sponsorship in self.sponsorships(matter_id):
                bill.add_sponsorship(**sponsorship)

            for topic in self.topics(matter_id):
                bill.add_subject(topic["MatterIndexName"].strip())

            for attachment in self.attachments(matter_id):
                if attachment["MatterAttachmentName"]:
                    bill.add_version_link(
                        attachment["MatterAttachmentName"],
                        attachment["MatterAttachmentHyperlink"],
                        media_type="application/pdf",
                    )

            bill.extras = {"local_classification": matter["MatterTypeName"]}

            text = self.text(matter_id)

            if text:
                if text["MatterTextPlain"]:
                    bill.extras["plain_text"] = text["MatterTextPlain"]

            yield bill
