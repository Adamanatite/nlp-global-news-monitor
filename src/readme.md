# Readme

This folder contains the codebase for the implementation of the system. The file structure is as follows:
* The **classifier** folder contains the code related to the classifier module, which classifies incoming articles
* The **crawlers** folder contains the code related to the crawlers, which ceawl URL's for a list of possible articles
* The **database** folder contains the code for connection to the database, including utility functions to reset and repopulate the database. The **data** folder within it contains data used to repopulate the database and a config for database connection
* The **parsers** folder contains the code for the parser module, which takes incoming article URL's and parses them for detailed information such as headline and publish data
* The **web_interface** folder contains the code for the web interface webpage
* **config.json** contains config information about the program which can be edited
* **controller.py** is the main module, run to start the program
* **kibana_dashboard.ndjson** is used to import the visualisation into a new Kibana instance
* **manual.md** describes how the software is run and modified
* **requirements.txt** is used to store the requirements of the program

## Build instructions

### Requirements
* Python 3.7
* Packages: listed in `requirements.txt` 
* Tested on Windows 10

### Build Steps
* These instructions are for **Windows 10** but should work on any recent Windows version
* Create a new pip environment from 'requirements.txt' in src:
* * ```python -m pip install -r requirements.txt```
* Install pytorch 1.13.0 with CUDA e.g. 
```pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu117```

* Perform either the docker setup or the elastic cloud setup then move to next steps
### Docker setup
* Install [docker desktop](https://www.docker.com/products/docker-desktop/)
* Create docker environment with elasticsearch
* * https://www.elastic.co/guide/en/elasticsearch/reference/current/docker.html
* * Pull the container for version 8.5.0 instead of the one specified in the tutorial
* * e.g. ```docker pull docker.elastic.co/elasticsearch/elasticsearch:8.5.0```
* * ```docker run --name es01 --net elastic -p 9200:9200 -it docker.elastic.co/elasticsearch/elasticsearch:8.6.2```

* * Create a new folder called "cert" in the src/database folder and put the http_ca.crt file in it
* * If running the docker returns an error, it may not have enough memory. You can run the following fix:
* * Run command prompt as an admin and run the following commands:
* * ```wsl -d docker-desktop```
* * ```sysctl -w vm.max_map_count=262144```

* Edit the "db_info.json" file in "database/data"
* * Ensure "connection_type" is "local"
* * Change "local_username" and "local_password" to the admin username and password
* * Ensure the "cert_path" matches the location of the http_ca.crt file (it is a relative path starting from "src/database")

* Using command prompt (with the created pip environment), enter the "src/database" directory and run "load_source_files.py"
* * A list of sources should be initialised in the console

* Create docker environment using Elastic Kibana
* * https://www.elastic.co/guide/en/kibana/current/docker.html
* * Pull the container for version 8.5.0 instead of the one specified in the tutorial
* * e.g. ```docker pull docker.elastic.co/kibana/kibana:8.5.0```
* * ```docker run --name kib-01 --net elastic -p 5601:5601 docker.elastic.co/kibana/kibana:8.5.0```

### Elastic cloud setup
* Create a kibana deployment on version 8.5.3 using the [Elastic cloud](https://www.elastic.co/cloud/)
* Edit the "db_info.json" file in "database/data"
* * Set "connection_type" is "cloud"
* * Change "cloud_username" and "cloud_password" to the admin username and password
* * Change "cloud_id" to the given cloud id, which can be found by clicking the gear next to the deployment on the "deployments" page
* We will now have to change the security settings to allow embedding:
* * Go on the deployments page, select the deployment and click "edit"
* * Go to the Kibana section and click "edit user settings"
* * In the console, paste ```xpack.security.sameSiteCookies: "None"``` and save changes

* On your local device, using command prompt (with the created pip environment), enter the "src/database" directory and run "load_source_files.py"
* * A list of sources should be initialised in the console

### Next steps
* Ensure the two dockers or cloud server is running
* Log into Kibana (default location is localhost:5601 for local machines) using the admin login given

* Import the visualisation data by going to Stack Management -> Saved Objects -> Import and upload the kibana_dashboard.ndjson file in "src"
* * You may need to recreate the data views, ensure all visualisation components load in Dashboards -> Main Dashboard
* * If they do not, go to Discover, and delete any data views which cause errors
* * Recreate the views which cause error
* * "Article view" uses index pattern "articles*" with timestamp field "Published"
* * "Source view" uses index pattern "sources*" with no timestamp field
* * "Full view" uses index pattern "articles,sources*" with no timestamp field
* * Ensure that all visualisation components load without error in the Main Dashboard

* Ensure the default time range is last month
* * Stack Management -> Advanced Settings -> Time Filter defaults
* * Replace "now-15m" to "now-1M"
* * Save changes

* Create a kibana embed for the web interface
* * Go to Dashboard -> Main Dashboard
* * Click Share -> Embed Code
* * Select "Saved object" and uncheck all "Include" boxes
* * Click copy iframe link
* * In the project source code, navigate to "src/web_interface/index.html"
* * Reaplace the URL in line 26 with the copied link
* * (Pasting will paste the entire iframe element, just extract the link, e.g. replace the "src=" section of line 26 with the "src=
 section of the pasted iframe)
* The program should now be fully ready to run

### Test steps
* In a command prompt, load the pip environment and navigate to "src"
* Ensure both docker containers are running and fully loaded
* * To restart the docker containers, you may need to allocate memory again
* * ```wsl -d docker-desktop```
* * ```sysctl -w vm.max_map_count=262144```
* Run the "controller.py" module in python
* A web interface should (eventually) pop up (you can also set "launch_web_app" to "false" in the config.json file to only launch the scraping system)
