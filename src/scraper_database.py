from mysql.connector import connect, Error

#TODO: Replace variables with input from file
hostname = "localhost"
username = "root"
password = ""
db_name = "news_scraper"

try:
    connection = connect(host = hostname,
                        user = username,
                        password=password)
    c = connection.cursor(buffered=True)
except Error as e:
    print(e)

print("Established connection")

def CreateDB():
    try:
     c.execute(f"CREATE DATABASE IF NOT EXISTS {db_name};")  # Create our DB if it doesn't already exist (RentScraper2 so doesn't mess up working, basic version)
    except Error as e:
        print(e)

    try:
        c.execute(f"""
        CREATE TABLE IF NOT EXISTS {db_name}.sources(
        url VARCHAR(100) PRIMARY KEY,
        name VARCHAR(50),
        country VARCHAR(3),
        language VARCHAR(2) NOT NULL,
        active TINYINT NOT NULL);""") 
    except Error as e:
        print(e)

    try:
        c.execute(f"""
        CREATE TABLE IF NOT EXISTS {db_name}.articles(
        url VARCHAR(700) PRIMARY KEY,
        title VARCHAR(300),
        text VARCHAR(50000),
        publish_date DATETIME DEFAULT CURRENT_TIMESTAMP,
        source VARCHAR(100),
        CONSTRAINT FK_source FOREIGN KEY (source) REFERENCES sources(url) ON DELETE CASCADE);""")
    except Error as e:
        print(e)

def GetCursor():
     return c

def GetDBConnection():
     return connection

#TODO: Write this function so that it can determine the other fields
def add_source(url):
    pass

def add_source(url, name, country, lang, active):
    pass