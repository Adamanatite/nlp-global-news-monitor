# User manual 

## Running the program
* In a command prompt, load the pip environment and navigate to "src"
* Ensure both docker containers are running and fully loaded
* * To restart the docker containers, you may need to allocate memory again
* * ```wsl -d docker-desktop```
* * ```sysctl -w vm.max_map_count=262144```
* Run the "controller.py" module in python
* A web interface should (eventually) pop up (you can also set "launch_web_app" to "false" in the config.json file to only launch the scraping system)

# Configuring the program
The **config.json** file provides some variables which can be changed to change how the program operates. These variables are:
* * "min_seconds_per_scrape": The minimum amount of time to wait before scraping from the start again (in seconds)
* * "empty_days_until_stale": The number of days without a new source until a source is considered stale
* * "auto_disable_stale_sources": Whether stale sources will automatically be disabled ("true" or "false")
* * "max_active_crawlers": The maximum number of crawlers which are loaded at the start of the program (from 1 to 9999)
* * "min_article_length": The minimum length of article body which will be sent into the database (in characters)
* * "launch_web_app" Whether or not to launch the web app ("true" or "false"). If false, the scraper system will run in the command line.
