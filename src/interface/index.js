let is_scraping = true

window.onload = function(){
  document.getElementById("kibana-visualisation").style.display="none";
  //TODO: Find out is_scraping here
  //eel.get_no_sources()(update_text)

}

function update_text(n){

  sub = document.getElementById("subheading")

  if(is_scraping){
    sub.innerHTML = "Scraping " + n + " sources."
  }
  else {
    sub.innerHTML = "Click to enable"
  }
}

function update_scraper_button() {
  var b = document.getElementById("toggle-scrape-btn")
  var sub = document.getElementById("subheading")
  if (is_scraping){
    b.innerHTML = "Stop scraping"
    sub.innerHTML = "Starting up..."
    b.classList.remove("main-btn")
    b.classList.add("disable-btn")
  }
  else {
    b.innerHTML = "Start scraping"
    sub.innerHTML = "Stopping..."
    b.classList.remove("disable-btn")
    b.classList.add("main-btn")
  }

}

function toggleScraper() {
  // When ready, change to make toggle_scraper call update_scraper_button and probably just return new state of scraping
  // eel.toggle_scraper()(update_scraper_button)
  is_scraping = !is_scraping
  // update_text(9)
  update_scraper_button()

  if (is_scraping){
    //eel.start_scraping()(update_text)
  } else {
    //eel.stop_scraping()(update_text)
  }
}

function toggleSource(btn){
  
  if (btn.classList.contains("disable-btn")) {
    btn.classList.remove("toggle-source-btn-enabled")
    btn.classList.remove("disable-btn")
    btn.classList.add("toggle-source-btn-disabled")
    btn.classList.add("accent-btn")
    btn.innerHTML = "Enable"
  }
  else {
    btn.classList.remove("toggle-source-btn-disabled")
    btn.classList.remove("accent-btn")
    btn.classList.add("toggle-source-btn-enabled")
    btn.classList.add("disable-btn")
    btn.innerHTML = "Disable"
  }
  // TODO: Actually toggle source
}

function deleteSource(btn) {
  console.log(btn.parentElement.parentElement.parentElement.parentElement.nodeName)
  let row = btn.parentElement.parentElement
  let table = row.parentElement.parentElement
  row.remove()
  var n = table.rows.length
  if (n === 1){
    table.parentElement.remove()
  }
  console.log(n)
  //var n = 
  //TODO: Actually delete source
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