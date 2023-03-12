import re
import json
from datetime import datetime
from database.elasticsearch_database import AddSource, UpdateLastScraped, EnableSource, DisableSource, DeleteSource
from utils.parse_config import ParseBoolean
import os
# Get current directory from project tree
currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)

# Get data from JSON file
with open(str(parentdir) + "/config.json") as f:
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


# Given a country name, returns the ISO 3166-1 alpha-2 country code
def GetCountryByName(country_name):
    # List of recognised countries with ISO code
    countries = {"Afghanistan": "AF",
    "Albania": "AL",
    "Algeria": "DZ",
    "Andorra": "AD",
    "Angola": "AO",
    "Antigua and Barbuda": "AG",
    "Argentina": "AR",
    "Armenia": "AM",
    "Australia": "AU",
    "Austria": "AT",
    "Azerbaijan": "AZ",
    "Bahamas": "BS",
    "Bahrain": "BH",
    "Bangladesh": "BD",
    "Barbados": "BB",
    "Belarus": "BY",
    "Belgium": "BE",
    "Belize": "BZ",
    "Benin": "BJ",
    "Bhutan": "BT",
    "Bolivia": "BO",
    "Bosnia and Herzegovina": "BA",
    "Botswana": "BW",
    "Brazil": "BR",
    "Brunei": "BN",
    "Bulgaria": "BG",
    "Burkina Faso": "BF",
    "Burundi": "BI",
    "Cambodia": "KH",
    "Cameroon": "CM",
    "Canada": "CA",
    "Cape Verde": "CV",
    "Central African Republic": "CF",
    "Chad": "TD",
    "Chile": "CL",
    "China": "CN",
    "Colombia": "CO",
    "Comoros": "KM",
    "Costa Rica": "CR",
    "Croatia": "HR",
    "Cuba": "CU",
    "Cyprus": "CY",
    "Czech Republic": "CZ",
    "Democratic Republic of the Congo": "CD",
    "Denmark": "DK",
    "Djibouti": "DJ",
    "Dominica": "DM",
    "Dominican Republic": "DO",
    "East timor": "TL",
    "Ecuador": "EC",
    "Egypt": "EG",
    "El Salvador": "SV",
    "Equatorial Guinea": "GQ",
    "Eritrea": "ER",
    "Estonia": "EE",
    "Eswatini": "SZ",
    "Ethiopia": "ET",
    "Fiji": "FJ",
    "Finland": "FI",
    "France": "FR",
    "Gabon": "GA",
    "Gambia": "GM",
    "Germany": "DE",
    "Ghana": "GH",
    "Greece": "GR",
    "Grenada": "GD",
    "Guatemala": "GT",
    "Guinea": "GN",
    "Guinea-Bissau": "GW",
    "Guyana": "GY",
    "Haiti": "HT",
    "Honduras": "HN",
    "Hungary": "HU",
    "Iceland": "IS",
    "India": "IN",
    "Indonesia": "ID",
    "Iran": "IR",
    "Iraq": "IQ",
    "Israel": "IL",
    "Italy": "IT",
    "Ivory Coast": "CI",
    "Jamaica": "JM",
    "Japan": "JP",
    "Jordan": "JO",
    "Kazakhstan": "KZ",
    "Kenya": "KE",
    "Kiribati": "KI",
    "Kosovo": "XK",
    "Kuwait": "KW",
    "Kyrgyzstan": "KG",
    "Laos": "LA",
    "Latvia": "LV",
    "Lebanon": "LB",
    "Lesotho": "LS",
    "Liberia": "LR",
    "Libya": "LY",
    "Liechtenstein": "LI",
    "Lithuania": "LT",
    "Luxembourg": "LU",
    "Macedonia": "MK",
    "Madagascar": "MG",
    "Malawi": "MW",
    "Malaysia": "MY",
    "Maldives": "MV",
    "Mali": "ML",
    "Malta": "MT",
    "Marshall Islands": "MH",
    "Mauritania": "MR",
    "Mauritius": "MU",
    "Mexico": "MX",
    "Micronesia": "FM",
    "Moldova": "MD",
    "Monaco": "MC",
    "Mongolia": "MN",
    "Montenegro": "ME",
    "Morocco": "MA",
    "Mozambique": "MZ",
    "Myanmar": "MM",
    "Namibia": "NA",
    "Nauru": "NR",
    "Nepal": "NP",
    "Netherlands": "NL",
    "New Zealand": "NZ",
    "Nicaragua": "NI",
    "Niger": "NE",
    "Nigeria": "NG",
    "North Korea": "KP",
    "Norway": "NO",
    "Oman": "OM",
    "Pakistan": "PK",
    "Palau": "PW",
    "Palestine": "PS",
    "Panama": "PA",
    "Papua New Guinea": "PG",
    "Paraguay": "PY",
    "Peru": "PE",
    "Philippines": "PH",
    "Poland": "PL",
    "Portugal": "PT",
    "Qatar": "QA",
    "Republic of Ireland": "IE",
    "Republic of the Congo": "CG",
    "Romania": "RO",
    "Russia": "RU",
    "Rwanda": "RW",
    "Saint Kitts and Nevis": "KN",
    "Saint Lucia": "LC",
    "Saint Vincent and the Grenadines": "VC",
    "Samoa": "WS",
    "San Marino": "SM",
    "Sao Tome and Principe": "ST",
    "Saudi Arabia": "SA",
    "Senegal": "SN",
    "Serbia": "RS",
    "Seychelles": "SC",
    "Sierra Leone": "SL",
    "Singapore": "SG",
    "Slovakia": "SK",
    "Slovenia": "SI",
    "Solomon Islands": "SB",
    "Somalia": "SO",
    "South Africa": "ZA",
    "South Korea": "KR",
    "South Sudan": "SS",
    "Spain": "ES",
    "Sri Lanka": "LK",
    "Sudan": "SD",
    "Suriname": "SR",
    "Sweden": "SE",
    "Switzerland": "CH",
    "Syria": "SY",
    "Taiwan": "TW",
    "Tajikistan": "TJ",
    "Tanzania": "TZ",
    "Thailand": "TH",
    "Togo": "TG",
    "Tonga": "TO",
    "Trinidad and Tobago": "TT",
    "Tunisia": "TN",
    "Turkey": "TR",
    "Turkmenistan": "TM",
    "Tuvalu": "TV",
    "Uganda": "UG",
    "Ukraine": "UA",
    "United Arab Emirates": "AE",
    "United Kingdom": "GB",
    "United Nations": "UN",
    "United States": "US",
    "Uruguay": "UY",
    "Uzbekistan": "UZ",
    "Vanuatu": "VU",
    "Vatican City": "VA",
    "Venezuela": "VE",
    "Vietnam": "VN",
    "Yemen": "YE",
    "Zambia": "ZM",
    "Zimbabwe": "ZW"}
    for k in countries.keys():
        if country_name.lower() == k.lower():
            return countries[k]
    return "Unknown"

# Given a URL, returns the ISO 3166-1 alpha-2 country code
def GetCountry(url):
    # List of recognised countries ISO codes
    countries = [ "AF", "AL", "DZ", "AD", "AO", "AG", "AR", "AM", "AU", "AT", "AZ", "BS", "BH", "BD", 
    "BB", "BY", "BE", "BZ", "BJ", "BT", "BO", "BA", "BW", "BR", "BN", "BG", "BF", "BI", "CV", "KH", "CM", 
    "CA", "CF", "TD", "CL", "CN", "CO", "KM", "CD", "CG", "CR", "CI", "HR", "CU", "CY", "CZ", "DK", "DJ", 
    "DM", "DO", "EC", "EG", "SV", "GQ", "ER", "EE", "SZ", "ET", "FJ", "FI", "FR", "GA", "GM", "UN", "DE", 
    "GH", "GR", "GD", "GT", "GN", "GW", "GY", "HT", "HN", "HU", "IS", "IN", "ID", "IR", "IQ", "IE", "IL", 
    "IT", "JM", "JP", "JO", "KZ", "KE", "KI", "KP", "KR", "KW", "KG", "LV", "LB", "LS", "LR", "LY", "LI", 
    "LT", "LU", "MK", "MG", "MW", "MY", "MV", "ML", "MT", "MH", "MR", "MU", "MX", "FM", "MD", "MC", "MN", 
    "ME", "MA", "MZ", "MM", "NA", "NR", "NP", "NL", "NZ", "NI", "NE", "NG", "NO", "OM", "PK", "PW", "PS", 
    "PA", "PG", "PY", "PE", "PH", "PL", "PT", "QA", "RO", "RU", "RW", "KN", "LC", "VC", "WS", "SM", "ST", 
    "SA", "SN", "RS", "SC", "TL", "SL", "SG", "SK", "SI", "SB", "SO", "ZA", "SS", "ES", "LK", "SD", "SR", "SE", 
    "CH", "SY", "TW", "TJ", "TH", "TG", "TO", "TT", "TN", "TR", "TM", "TV", "TZ", "UG", "UA", "AE", 
    "GB", "US", "UY", "UZ", "VU", "VE", "VN", "YE", "ZM", "ZW", "XK", "LA", "VA"
    ]
    tld = re.search("\.[a-z]*/", url).group()[1:-1]
    if len(tld) != 2:
        return "Unknown"
    
    #Map UK to GB
    tld = tld.upper().replace("UK","GB")
    if tld in countries:
        return tld
    return "Unknown"

class Scraper:

    def __init__(self, url, name, country=None, lang=None, source_id=None, last_scraped=None, is_active=True):

        self.enabled = is_active

        self.url = url
        self.source_id = source_id
        self.name = name


        self.language = lang

        if country:
            self.country = GetCountryByName(country)
        else:
            self.country=GetCountry(url)
        print(self.country)

        if not source_id:
            self.source_id = AddSource(self.url, self.name, self.country, self.language, self.scrape_type)

        if last_scraped:
            self.last_scrape_time = datetime.strptime(last_scraped, "%Y-%m-%dT%H:%M:%SZ")
        else:
            self.last_scrape_time = datetime(month=1, day=1, year=2000)

        print("Initialised " + self.name + " scraper")


    def UpdateTime(self, publish_date):
        # Update to reflect new source found
        if not publish_date:
            self.last_scrape_time = datetime.now()
        else:
            self.last_scrape_time = publish_date



    def toggle(self):
        self.enabled = not self.enabled
        if self.enabled:
            EnableSource(self.source_id)
        else:
            DisableSource(self.source_id)
    
    def delete(self):
        return DeleteSource(self.source_id)

    def scrape(self):

        if not self.enabled:
            return

        articles = self.GetNewArticles()

        #Update self
        UpdateLastScraped(self.source_id, self.last_scrape_time)

        #Set as stale
        if AUTO_DISABLE_STALE_SOURCES and (datetime.now() - self.last_scrape_time).days > STALE_DAYS:
            self.enabled = False
            print("Disabling " + self.name + str(AUTO_DISABLE_STALE_SOURCES))
            DisableSource(self.source_id)
        return articles

    def GetNewArticles(self):
        return []

