# Global news monitoring system using NLP
This is the repository for my Level 4 Individual project for computing science, "A real-time global news monitoring system based on Natural Language Processing (NLP) technology" Supervised by [Dr. Zaiqiao Meng](https://www.gla.ac.uk/schools/computing/staff/zaiqiaomeng/)

## Table of Contents
* [Motivation](#motivation)
* [Overview](#overview)
* [Build Instructions](#build-instructions)
* [Running the Program](#running-the-program)
* [Technologies Used](#main-technologies-used)

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

## Main Technologies used
* [Elasticsearch](https://www.elastic.co/elasticsearch/) v8.5.0
* [Elastic Kibana](https://www.elastic.co/kibana/) v8.5.0
### Main Libraries
* [Newspaper3k](https://github.com/codelucas/newspaper) v0.2.8
* [feedparser](https://pypi.org/project/feedparser/) v6.0.10
* [elasticsearch](https://elasticsearch-py.readthedocs.io/en/v8.4.3/) v8.4.3
* [Huggingface Transformers](https://huggingface.co/transformers) v4.23.1
* [Pytorch](https://pytorch.org/blog/PyTorch-1.13-release/) v1.13.0
* [langdetect](https://pypi.org/project/langdetect/) v1.0.9
* [Eel](https://github.com/python-eel/Eel/releases/tag/v0.15.1) v0.15.1
