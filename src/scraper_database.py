from mysql.connector import connect, Error
import json

with open("config.json") as f:
    data = json.load(f)
    db_name = data["db_name"]

try:
    connection = connect(host = data["host"],
                        user = data["username"],
                        password=data["password"])
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
        publish_date DATETIME,
        scrape_date DATETIME DEFAULT CURRENT_TIMESTAMP,
        source VARCHAR(100),
        CONSTRAINT FK_source FOREIGN KEY (source) REFERENCES sources(url) ON DELETE CASCADE);""")
    except Error as e:
        print(e)

    print("Successfully created Database")

def GetCursor():
     return c

def GetDBConnection():
     return connection

#TODO: Write this function so that it can determine the other fields
def AddSource(url):
    pass

def AddSource(url, name, country, lang):
    if(not SourceExists(url)):
        query = "INSERT INTO " + db_name + ".sources (url,name,country,language,active) VALUES(%s,%s,%s,%s,%s)"
        try:
            params = (url, name, country, lang, True)
            c.execute(query, params)
            connection.commit()
        except Error as e:
            print(e)
        return True
    return False

def SourceExists(url):
    query = "SELECT url FROM " + db_name + ".sources WHERE url = %s"
    params = [url]
    c.execute(query, params)
    if(c.fetchall()):
        return True
    return False

def AddArticle(url, title, text, date, source):
    #TODO: Deal with articles which update?
    if(not ArticleExists(url)):
        query = "INSERT INTO " + db_name + ".articles (url,title,text,publish_date,source) VALUES(%s,%s,%s,%s,%s)"
        try:
            params = (url, title, text, date, source)
            c.execute(query, params)
            connection.commit()
        except Error as e:
            print(e)
        return True
    return False

def ArticleExists(url):
    query = "SELECT url FROM " + db_name + ".articles WHERE url = %s"
    params = [url]
    c.execute(query, params)
    if(c.fetchall()):
        return True
    return False