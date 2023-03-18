import os
import re
import json
from datetime import datetime, timezone
from database.database_connector import add_source, update_last_scraped, enable_source, disable_source, delete_source, get_article_from_url


# Get current directory from project tree
currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)


# Given a country name, returns the ISO 3166-1 alpha-2 country code
def get_country_by_name(country_name):
    """
    Attempts to get the country code from the given country name

    :param country_name: The country name
    :returns: The country code of the origin country, if it can be mined.
    Otherwise it returns Unknown
    """

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
def get_country(url):
    """
    Attempts to get the country code from the URL

    :param url: The source URL
    :returns: The country code of the URLs origin country, if it can be mined.
    Otherwise it returns Unknown
    """

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


class Crawler:
    """
    Abstract class for crawling a given URL to provide a list of URLs periodically
    """
    def __init__(self, url, name, country=None, lang=None, source_id=None, last_scraped=None, is_active=True, days_until_stale=14, auto_disable_stale = False):
        """
        Initialises parameters, attempting to guess country if it is not specified.
        If not given a source ID, it will create the source object in the database 
        and use its new ID
        """
        # Update parameters
        self.enabled = is_active
        self.url = url
        self.source_id = source_id
        self.name = name
        self.language = lang.upper()
        self.days_until_stale = days_until_stale
        self.auto_disable_stale = auto_disable_stale

        # Create source if it does not exist, and attempt to retrieve country name
        if not source_id:
            if country:
                if len(country) == 2:
                    self.country = country
                else:
                    self.country = get_country_by_name(country)
            else:
                self.country = get_country(url)

            self.source_id = add_source(self.url, self.name, self.country, 
                                        self.language, self.source_type)
        else:
            self.source_id = source_id
            self.country = country

        # Set last scrape time
        if last_scraped:
            self.last_scrape_time = datetime.strptime(last_scraped, "%Y-%m-%dT%H:%M:%SZ").astimezone(timezone.utc)
        else:
            self.last_scrape_time = datetime(month=1, day=1, year=2000).astimezone(timezone.utc)

        # Confirmation message
        print("Initialised " + self.name + " crawler")


    def set_last_scrape_time(self, time):
        """
        Updates the last scrape time of the crawler and updates the database.
        Sets the crawler to stale if it has not found new articles in a set amount of time.
        """
        # Update last scrape time and commit to DB
        time = time.astimezone(timezone.utc)
        if time > self.last_scrape_time:
            self.last_scrape_time = time
            print(self.source_id)
            update_last_scraped(self.source_id, time)

        # Toggle source if it is stale (and this is specified in the config)
        days_since_last_update = (datetime.now().astimezone(timezone.utc) - self.last_scrape_time).days
        if self.auto_disable_stale and days_since_last_update > self.days_until_stale:
            self.toggle()


    def toggle(self):
        """
        Sets the crawler to enabled or disabled (the opposite of its previous state)
        and updates the database
        """
        self.enabled = not self.enabled
        if self.enabled:
            enable_source(self.source_id)
        else:
            disable_source(self.source_id)


    def delete(self):
        """
        Deletes this crawler and updates the dataset
        """
        return delete_source(self.source_id)


    def crawl(self):
        """
        Crawls for URLs from the given source URL, using the concrete implementation
        """

        if not self.enabled:
            return []
        
        print("Crawling " + self.name)

        # Get new articles (from concrete implementation)
        urls = self.get_new_articles()
        articles = []

        # Add all new URLs to list for parsing
        for url in urls:
            if get_article_from_url(url):
                continue
            article = {
                "url": url,
                "language": self.language,
                "country": self.country,
                "source": self.name,
                "source_type": self.source_type,
                "crawler": self
            }
            articles.append(article)
        return articles


    def get_new_articles(self):
        """
        To be overriden in subclasses by a method which 
        gets a list of new articles from the source URL
        """ 
        return []

