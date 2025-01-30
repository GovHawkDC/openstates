import lxml

HI_URL_BASE = "https://data.capitol.hawaii.gov"
SHORT_CODES = f"{HI_URL_BASE}/legislature/committees.aspx?chamber=all"


def get_short_codes(scraper):
    # list_html = scraper.get(SHORT_CODES, verify=False).text
    # list_page = lxml.html.fromstring(list_html)
    # rows = list_page.xpath("//table[contains(@id, 'MainContent_GridView1')]//tr")
    # scraper.short_ids = {"CONF": {"chamber": "joint", "name": "Conference Committee"}}

    # for row in rows:
    #     tds = row.xpath("./td")
    #     short = tds[0].xpath("./a")[0]
    #     clong = tds[1]
    #     chamber = clong.xpath("./span")[0].text_content()
    #     clong = clong.xpath("./a")[0]
    #     short_id = short.text_content().strip()
    #     ctty_name = clong.text_content().strip()
    #     if "house" in chamber.lower():
    #         chamber = "lower"
    #     elif "senate" in chamber.lower():
    #         chamber = "upper"
    #     else:
    #         chamber = "joint"
    #     scraper.short_ids[short_id] = {"chamber": chamber, "name": ctty_name}

    scraper.short_ids = {
        "CONF": {"chamber": "joint", "name": "Conference Committee"},
        "AEN": {"chamber": "upper", "name": "Agriculture and Environment"},
        "AGR": {"chamber": "lower", "name": "Agriculture & Food Systems"},
        "CAA": {"chamber": "lower", "name": "Culture & Arts"},
        "CPC": {"chamber": "lower", "name": "Consumer Protection & Commerce"},
        "CPN": {"chamber": "upper", "name": "Commerce and Consumer Protection"},
        "ECD": {"chamber": "lower", "name": "Economic Development & Technology"},
        "EDN": {"chamber": "lower", "name": "Education"},
        "EDT": {"chamber": "upper", "name": "Economic Development and Tourism"},
        "EDU": {"chamber": "upper", "name": "Education"},
        "EEP": {"chamber": "lower", "name": "Energy & Environmental Protection"},
        "EIG": {"chamber": "upper", "name": "Energy and Intergovernmental Affairs"},
        "FIN": {"chamber": "lower", "name": "Finance"},
        "GVO": {"chamber": "upper", "name": "Government Operations"},
        "HED": {"chamber": "lower", "name": "Higher Education"},
        "HHS": {"chamber": "upper", "name": "Health and Human Services"},
        "HLT": {"chamber": "lower", "name": "Health"},
        "HOU": {"chamber": "upper", "name": "Housing"},
        "HRE": {"chamber": "upper", "name": "Higher Education"},
        "HSG": {"chamber": "lower", "name": "Housing"},
        "HSH": {"chamber": "lower", "name": "Human Services & Homelessness"},
        "HWN": {"chamber": "upper", "name": "Hawaiian Affairs"},
        "JDC": {"chamber": "upper", "name": "Judiciary"},
        "JHA": {"chamber": "lower", "name": "Judiciary & Hawaiian Affairs"},
        "LAB": {"chamber": "lower", "name": "Labor"},
        "LBT": {"chamber": "upper", "name": "Labor and Technology"},
        "LMG": {"chamber": "lower", "name": "Legislative Management"},
        "PBS": {"chamber": "lower", "name": "Public Safety"},
        "PSM": {"chamber": "upper", "name": "Public Safety and Military Affairs"},
        "TCA": {"chamber": "upper", "name": "Transportation and Culture and the Arts"},
        "TOU": {"chamber": "lower", "name": "Tourism"},
        "TRN": {"chamber": "lower", "name": "Transportation"},
        "WAL": {"chamber": "lower", "name": "Water & Land"},
        "WAM": {"chamber": "upper", "name": "Ways and Means"},
        "WTL": {"chamber": "upper", "name": "Water and Land"},
    }

    print(scraper.short_ids)


def make_data_url(url: str) -> str:
    if "www" in url:
        return url.replace("www.", "data.")
    else:
        return url.replace("capitol.", "data.capitol.")
