import re
import json
from datetime import datetime
from elasticsearch_database import AddSource, AddArticle, UpdateLastScraped, DisableSource
from sources.parse_config import ParseBoolean
import time

# Given a URL, returns the ISO 3166-1 alpha-2 country code
def GetCountry(url):
    #List of recognised country domains
    countries = [ "AF", "AL", "DZ", "AD", "AO", "AG", "AR", "AM", "AU", "AT", "AZ", "BS", "BH", "BD", 
    "BB", "BY", "BE", "BZ", "BJ", "BT", "BO", "BA", "BW", "BR", "BN", "BG", "BF", "BI", "CV", "KH", "CM", 
    "CA", "CF", "TD", "CL", "CN", "CO", "KM", "CD", "CG", "CR", "CI", "HR", "CU", "CY", "CZ", "DK", "DJ", 
    "DM", "DO", "EC", "EG", "SV", "GQ", "ER", "EE", "SZ", "ET", "FJ", "FI", "FR", "GA", "GM", "UN", "DE", 
    "GH", "GR", "GD", "GT", "GN", "GW", "GY", "HT", "HN", "HU", "IS", "IN", "ID", "IR", "IQ", "IE", "IL", 
    "IT", "JM", "JP", "JO", "KZ", "KE", "KI", "KP", "KR", "KW", "KG", "LV", "LB", "LS", "LR", "LY", "LI", 
    "LT", "LU", "MK", "MG", "MW", "MY", "MV", "ML", "MT", "MH", "MR", "MU", "MX", "FM", "MD", "MC", "MN", 
    "ME", "MA", "MZ", "MM", "NA", "NR", "NP", "NL", "NZ", "NI", "NE", "NG", "NO", "OM", "PK", "PW", "PS", 
    "PA", "PG", "PY", "PE", "PH", "PL", "PT", "QA", "RO", "RU", "RW", "KN", "LC", "VC", "WS", "SM", "ST", 
    "SA", "SN", "RS", "SC", "SL", "SG", "SK", "SI", "SB", "SO", "ZA", "SS", "ES", "LK", "SD", "SR", "SE", 
    "CH", "SY", "TW", "TJ", "UN", "TH", "UN", "TG", "TO", "TT", "TN", "TR", "TM", "TV", "UG", "UA", "AE", 
    "GB", "US", "UY", "UZ", "VU", "VE", "VN", "YE", "ZM", "ZW"
    ]

    #Map UK to GB
    tld = re.search("\.[a-z]*/", url).group()[1:-1]
    if len(tld) != 2:
        return "Unknown"

    tld = tld.upper().replace("UK","GB")
    if tld in countries:
        return tld
    return "Unknown"

def GetDefaultName(url):
    return re.search("://([a-zA-Z0-9]|\.|-)*/", url).group()[3:-1]

# Get data from JSON file
with open("sources/config.json") as f:
    data = json.load(f)
    try:
        STALE_DAYS = int(data["empty_days_until_stale"])
        FAILURES_UNTIL_DISABLE = int(data["failures_until_disable"])
        AUTO_DISABLE_STALE_SOURCES = ParseBoolean(data["auto_disable_stale_sources"])
    except:
        # Default values
        print("Error in config")
        STALE_DAYS = 7
        FAILURES_UNTIL_DISABLE = 5
        AUTO_DISABLE_STALE_SOURCES = False

class Scraper:

    def __init__(self, url, name, country=None, lang=None, source_id=None, last_scraped=None):

        self.enabled = True
        self.no_consecutive_failures = 0

        self.url = url
        self.source_id = source_id
        
        if name:
            self.name = name
        else:
            self.name=GetDefaultName(self.url)

        #TODO: Determine this parameter from the url
        self.language = lang

        if country:
            self.country = country
        else:
            self.country=GetCountry(url)

        if not source_id:
            self.source_id = AddSource(self.url, self.name, self.country, self.language, self.scrape_type)

        if last_scraped:
            self.last_scrape_time = datetime.strptime(last_scraped, "%Y-%m-%dT%H:%M:%SZ")
        else:
            self.last_scrape_time = datetime(month=1, day=1, year=2000)

        print("Initialised " + self.name + " scraper")


    def AddNewArticle(self, url, title, text, publish_date, update_time=True, skip_verification=False):
        AddArticle(url, title, text, self.country, self.language, publish_date, self.name, self.scrape_type, skip_verification)
        
        if not update_time:
            return

        # Update to reflect new source found
        if not publish_date:
            self.last_scrape_time = datetime.now()
        else:
            self.last_scrape_time = publish_date
    

    def HandleError(self, e):
        #TODO: system for re-enabling (in case of internet error etc)
        self.no_consecutive_failures += 1
        print(self.name + f" error ({self.no_consecutive_failures}): " + str(e))
        if self.no_consecutive_failures > FAILURES_UNTIL_DISABLE:
            self.enabled = False
            DisableSource(self.source_id)

        UpdateLastScraped(self.source_id, self.last_scrape_time)
        # Wait 5 seconds in case we're sending too many requests
        time.sleep(5)


    def scrape(self):

        if not self.enabled:
            return

        self.GetNewArticles()

        #Update self
        UpdateLastScraped(self.source_id, self.last_scrape_time)

        #Set as stale
        if AUTO_DISABLE_STALE_SOURCES and (datetime.now() - self.last_scrape_time).days > STALE_DAYS:
            self.enabled = False
            print("Disabling " + self.name + str(AUTO_DISABLE_STALE_SOURCES))
            DisableSource(self.source_id)

    def GetNewArticles(self):
        pass

