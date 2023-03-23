# Global news monitoring system using NLP
This is the repository for my Level 4 Individual project for computing science, "A real-time global news monitoring system based on Natural Language Processing (NLP) technology" Supervised by [Dr. Zaiqiao Meng](https://www.gla.ac.uk/schools/computing/staff/zaiqiaomeng/)

## Table of Contents
* [Motivation](#motivation)
* [Overview](#overview)
* [Build Instructions](#build-instructions)
* [Running the Program](#running-the-program)
* [Technologies Used](#technologies-used)

## Motivation
Diseases can travel rapidly between areas and cause widespread harm before they can be detected and contained. Traditional methods of surveillance such as testing parients in a lab to identify patterns can be slow, taking days for experiment results to be obtained. Digital disease surveillance systems can use online data to provide quick alerts for diseases which can be used tp notify citizens and inform government policy.
My supervisor has worked on a project called [BioCaster](http://www.biocaster.org/) which uses news articles to identify disease outbreaks across the world. However, the systems available for news sources (RSS subscription feeds) are limited in the news they can provide, only allowing for popular news sources, with limited coverage in many minority languages. I am trying to use web-scraping to design a more flexible system for obtaining news, using NLP to translate different languages into English and filter biomedical articles, to facilitate more accurate and complete identification of disease outbreaks.
## Overview
The project consists of several key features:
  * A web crawling system built on [Newspaper3k](https://github.com/codelucas/newspaper) and [feedparser](https://pypi.org/project/feedparser/) to scrape news website and RSS data.
  * A webpage parsing system built on [Newspaper3k](https://github.com/codelucas/newspaper) to obtain article information from webpage HTML.
  * NLP [huggingface](https://huggingface.co/) pipelines for multilingual news article classification
  * An [Elasticsearch](https://www.elastic.co/elasticsearch/) database to store results of web crawling 
  * Real-time visualisation of data through [Elastic Kibana](https://www.elastic.co/kibana/)
  * An interactive web interface for controlling the scraping system and viewing visualisations

The languages being considered for this project are:
* English
* French
* Spanish
* Chinese
* Russian
* Portuguese
* Indonesian
* Swahili
* Korean
* Arabic

## Build Instructions
* These instructions are for **Windows 10** but should work on any recent Windows version
* Create a new pip environment from 'requirements.txt' in src:
* * ```python -m pip install -r requirements.txt```
* Install pytorch 1.13.0 with CUDA e.g. 
```pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu117```

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

* Ensure the two docker environments are running (and give them enough time, probably around 2 minutes, to load)

* Log into Kibana (default location is localhost:5601) using the admin login given

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

## Running the program
* In a command prompt, load the pip environment and navigate to "src"
* Ensure both docker containers are running and fully loaded
* * To restart the docker containers, you may need to allocate memory again
* * ```wsl -d docker-desktop```
* * ```sysctl -w vm.max_map_count=262144```
* Run the "controller.py" module in python
* A web interface should (eventually) pop up (you can also set "launch_web_app" to "false" in the config.json file to only launch the scraping system)

## Technologies used
* [Newspaper3k](https://github.com/codelucas/newspaper) v0.2.8
* [TensorFlow](https://github.com/tensorflow/tensorflow/releases/tag/v2.10.0) v2.10
* [Huggingface Transformers](https://huggingface.co/transformers) v4.23.1
* [Elasticsearch](https://www.elastic.co/elasticsearch/) v8.5.0
* [Elastic Kibana](https://www.elastic.co/kibana/) v8.5.0
