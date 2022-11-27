# Timelog

* A real-time global news monitoring system based on Natural Language Processing (NLP) technology
* Adam Farlie
* 2461352F
* Supervised by Zaiqiao Meng

## Guidance

* This file contains the time log for your project. It will be submitted along with your final dissertation.
* **YOU MUST KEEP THIS UP TO DATE AND UNDER VERSION CONTROL.**
* This timelog should be filled out honestly, regularly (daily) and accurately. It is for *your* benefit.
* Follow the structure provided, grouping time by weeks.  Quantise time to the half hour.

## Week 2

### 28 Sep 2022

* *2 hour* Read project guidance documentation, reached out to supervisor

## Week 3

### 7 Oct 2022

* *1.5 hour* Recapped individual project introduction video and slides
* *0.5 hour* Meeting preparation (brainstorming questions, researching how to make minutes)

## Week 4

### 10 Oct 2022

* *1.5 hour* Setup Zotero, Final meeting preparation
* *0.5 hour* Initial meeting with supervisor
* *0.5 hour* Rewritten minutes into more sorted and easy-to-understand form

### 11 Oct 2022

* *1 hour* Setup GitHub repository and edited template files
* *0.5 hour* Got GitHub student, created and set up wiki, converted first meeting minutes to markdown format

### 14 Oct 2022

* *0.5 hour* Filled in project details and personal details on shared Notion notebook

### 15 Oct 2022

* *2.5 hour* Research on news sources around the world (mostly English for now)

### 16 Oct 2022

* *1.5 hour* Environment setup, installation of libraries, had some trouble with pip and recognising my GPU.

## Week 5

### 17 Oct 2022

* *0.5 hour* Began planning the comparison of different web crawling sources
* *1 hour* Added more newspapers to the list being collected

### 18 Oct 2022

* *2 hour* Added more news sources to document
* *1 hour* Added news sources from the remaining languages to research document
* *0.5 hour* Preparation for next supervisor meeting, updating GitHub
* *1 hour* Second meeting with supervisor, revising minutes and updating shared notes

### 23 Oct 2022
* *1 hour* Preparation for python analysis of current news scrapers

## Week 6

### 24 Oct 2022
* *2.5 hour* Collected news articles to use for testing for every source, updated considerations
* *3 hour* Installed scraping libraries, began writing scripts to perform experiment

### 25 Oct 2022
* *2 hour* More work on experiment, not much progress
* *4.5 hour* Completed timed experiment, updated report
* *1 hour* Meeting preparation, supervisor meeting, cleaning up of minutes

### 26 Oct 2022
* *0.5 hour* Some work on considering individual sources and evaluating scraper performance (closer inspection of metadata)
* *1 hour* Preparation for, attendance of (as a guest) and minutes for BioCaster weekly meeting 

## Week 7

### 31 Oct 2022
* *3.5 hour* Completed report (experiments were very slow), installed mysql and related python packages, setup test database
* *0.5 hour* Created wireframe for scraper dashboard (https://www.figma.com/file/FxrC6tJwUa0Xq3iqChES7B/Scraper-Dashboard?node-id=0%3A1)

### 1 Nov 2022
* *2.5 hour* Planned and set up database schema on mySQL (many errors but finally working)
* *1 hour* Added functions for adding and removing news articles and sources
* *1 hour* Began work on getting newspaper3k to scrape whole websites, unsuccessful. Also planned meeting.
* *1 hour* Customer meeting, research into elastic and refactoring/extending of minutes

### 6 Nov 2022
* *1 hour* Installed Elasticsearch (had some installation problems and had to reset pip environment)

## Week 8

### 7 Nov 2022
* *1.5 hour* Attempted to connect elasticsearch python library to local setup, unsuccessful (HTTPS security errors), planned some visualisations
* *0.5 hour* Update project info
* *3 hour* Set up elasticsearch and kibana on docker without security, adapted mysql code to elasticsearch, kibana doesn't connect yet

### 8 Nov 2022
* *1.5 hour* Robots.txt / legal implications of web scraping research, more testing on newspaper3k full website scraping and other options, meeting prep
* *1 hour* Supervisor meeting, notes cleanup and wiki update

### 10 Nov 2022
* *0.5 hour* Research on possible datasets for multi-label news article classification

### 11 Nov 2022
* *1 hour* Trying to set up elasticsearch and kibana so they work together, some progress

### 13 Nov 2022
* *1 hour* Trying to set up elasticsearch and kibana again, trying new method (secure connection with newest version)

## Week 9

### 14 Nov 2022
* *2 hour* Successfully set up elasticsearch + kibana
* *2 hour* work on automatically scraping web sources for DB, not yet tested
* *1 hour^ testing new scraping system and fixing elasticsearch setup bug

### 15 Nov 2022
* *2.5 hour* Fixed elasticsearch docker memory bug, fixed kibana visualisations and created test visualisation, work and testing on web scraper, research/start on RSS parser
* *1 hour* RSS feed testing and fixes (should work now), 
* *1 hour* Meeting preparation, supervisor meeting and meeting note collation

### 19 Nov 2022
* *2 hour* Getting elasticsearch queries to work and beginning to run scraper on its own
* *0.5 hour* Added own sources to database from files, error at end of file
* *0.5 hour* Testing new main function, getting articles and sources to finally scrape automatically

### 20 Nov 2022
* *1 hour* Work on improving scraper functionality to begin creating scheduler, started running automatically
* *1.5 hour^ Running scraper, researching automatic country, language detection and better scraping methods to avoid duplicates

## Week 10

### 21 Nov 2022
* *2 hour* Work on removing duplicate articles and tracking scraper staleness, needs to be run automatically again
* *1 hour* Fixed issues and began running scraper automatically
* *2 hour* Working on Kibana visualisation and meeting planning, don't know how to replicate BioCaster visualisations

### 22 Nov 2022
* *1 hour* Bug fixes and research on translation and classification transformers
* *2 hour* Learning how to make a fine-tuned BERT model with huggingface, metting planning
* *1 hour* Supervisor meeting and note collation
* *2 hour* Entering countries correctly for RSS and Web scraper data (2 letter ISO code), methods for determining country and name of source, subclassing to remove code duplication in scraper classes

### 23 Nov 2022
* *1.5 hour* Made scraper work with multiple threads
* *1 hour* Bug fixes and investigating random freezing
* *3 hour* Fixed random freezing (by making shared queue non-blocking) and added rate limiter and better duplicate checking

### 26 Nov 2022
* *1 hour* Updated error detection and RSS feed automatic language/name detection