let is_scraping = true

window.onload = function(){
  document.getElementById("kibana-visualisation").style.display="none";
  //TODO: Find out is_scraping here
  //eel.get_no_sources()(update_text)

}

function update_text(n){
    document.getElementById("website-count").innerHTML = "Scraping " + n + " sources."  
}

function update_scraper_button() {
  var b = document.getElementById("toggle-scrape-btn")
  if (is_scraping){
    b.innerHTML = "Stop scraping"
    b.classList.remove("toggle-scrape-btn-disabled")
    b.classList.add("toggle-scrape-btn-enabled")
  }
  else {
    b.innerHTML = "Start scraping"
    b.classList.remove("toggle-scrape-btn-enabled")
    b.classList.add("toggle-scrape-btn-disabled")
  }

}

function toggleScraper() {
  // eel.toggle_scraper()()
  is_scraping = !is_scraping
  update_scraper_button()
}

function toggleVisualisation(){
    var v = document.getElementById("kibana-visualisation")
    var b = document.getElementById("toggle-visualisation-btn")
    if (v.style.display === "none") {
        v.style.display = "block";
        b.innerHTML = "Hide visualisation";
      } else {
        v.style.display = "none";
        b.innerHTML = "Show visualisation";
      }
}