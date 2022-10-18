# Global news monitoring system using NLP
This is the repository for my Level 4 Individual project for computing science, "A real-time global news monitoring system based on Natural Language Processing (NLP) technology" Supervised by [Dr. Zaiqiao Meng](https://www.gla.ac.uk/schools/computing/staff/zaiqiaomeng/)

## Table of Contents
* [Motivation](#motivation)
* [Overview](#overview)
* [Build Instructions](#build-instructions)
* [Technologies Used](#technologies-used)

## Motivation
My supervisor has worked on a project called [BioCaster](http://www.biocaster.org/) which uses news articles to identify disease outbreaks across the world. However, the systems available for news sources (RSS subscription feeds) are limited in the news they can provide, only allowing for popular news sources, with limited coverage in many minority languages. I am trying to use web-scraping to design a more flexible system for obtaining news, using NLP to translate different languages into English and filter biomedical articles, to facilitate more accurate and complete identification of disease outbreaks.
## Overview
The project consists of several key features
  * Flexible web-crawlers to be used for different news sources around the world (e.g. in different languages and formats)
  * NLP [huggingface](https://huggingface.co/) pipelines for machine translation and classification (biomedical vs non-biomedical articles)
  * Possible NER/Linking to categorise diseases and link different disease names into one disease object
  * Possible visualisation of data through tools such as [Elastic Kibana](https://www.elastic.co/kibana/)

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
* Ensure TensorFlow CUDA Toolkits are installed e.g.
```conda install -c conda-forge cudatoolkit=11.2 cudnn=8.1.0```
* Create a pip environment from `requirements.txt` in src
* * ```python -m pip install -r requirements.txt```
## Technologies used
* [TensorFlow v2.10](https://github.com/tensorflow/tensorflow/releases/tag/v2.10.0)
* [Huggingface Transformers v4.23.1](https://huggingface.co/transformers)
