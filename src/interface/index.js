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
    moveTable(btn, "disabled-table")
  }
  else {
    btn.classList.remove("toggle-source-btn-disabled")
    btn.classList.remove("accent-btn")
    btn.classList.add("toggle-source-btn-enabled")
    btn.classList.add("disable-btn")
    btn.innerHTML = "Disable"
    //TODO: Check for staleness
    moveTable(btn, "active-table")
  }
  // TODO: Actually toggle source
}

function deleteSource(btn) {
  let row = btn.parentElement.parentElement
  deleteRow(row)
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

// Adapted from https://www.w3schools.com/jsref/met_table_insertrow.asp
function addTableRow(table_id, name, url, lang, no_articles, last, isEnabled) {
  var table = document.getElementById(table_id);
  if (!table){
    addTable(table_id)
    table = document.getElementById(table_id);
  }
  var row = table.insertRow(1);
  var srcCell = row.insertCell(0);
  var langCell = row.insertCell(1);
  var articlesCell = row.insertCell(2);
  var lastCell = row.insertCell(3);
  var disableCell = row.insertCell(4);
  var deleteCell = row.insertCell(5);


  srcCell.innerHTML = `<a href="${url}">${name}</a>`;
  langCell.innerHTML = lang;
  articlesCell.innerHTML = no_articles
  lastCell.innerHTML = last
  lower = name.toLowerCase()
  if (isEnabled){
    disableCell.innerHTML = `<td><button id = "${lower}-toggle" class="action-btn table-btn disable-btn" onclick="toggleSource(this)">Disable</button></td>`
  } else {
    disableCell.innerHTML = `<td><button id = "${lower}-toggle" class="action-btn table-btn accent-btn" onclick="toggleSource(this)">Enable</button></td>`
  }

  deleteCell.innerHTML = `<td><button id = "${lower}-delete" class="action-btn table-btn delete-btn" onclick="deleteSource(this)">Delete</button></td>`
}

function addTable(table_id){
  // Adapted from https://flexiple.com/javascript/javascript-capitalize-first-letter/
  let title = table_id.charAt(0).toUpperCase() + table_id.substring(1, table_id.length - 6)
  tableHTML = `            <h2 class="table-title">${title}</h2>
  <div class="heading-bar"></div>
  <table id="${table_id}" cellspacing="0">
      <tr>
          <th>Source</th>
          <th>Language</th>
          <th>Articles today</th>
          <th>Last article</th>
      </tr>
  </table>`

  let div = document.getElementById(table_id + "-container");
  if(div){
    div.innerHTML = tableHTML
  }

}

function deleteRow(row){
  let table = row.parentElement.parentElement
  row.remove()
  var n = table.rows.length
  if (n === 1){
    table.parentElement.innerHTML = ""
  }
}

function moveTable(btn, to_table){
  let row = btn.parentElement.parentElement;
  var source = row.cells[0].firstChild;

  console.log("BBC News Swahili".toLowerCase().replace(/ /g, "-"))

  addTableRow(to_table, source.innerHTML, source.href, row.cells[1].innerHTML, row.cells[2].innerHTML, row.cells[3].innerHTML, row.cells[4].firstChild.classList.contains("disable-btn"));
  deleteRow(btn.parentElement.parentElement);
}

function goToDashboard(){
  document.getElementById("manage-content").style.display = "none"
  document.getElementById("homepage-content").style.display = "block"
}

function goToManage(){
  document.getElementById("manage-content").style.display = "block"
  document.getElementById("homepage-content").style.display = "none"
}

function toggleAddSource() {
  var box = document.getElementById("toggle-source-box");
  var btn = document.getElementById("add-source-btn")
  if (box.style.display === "block") {
    box.style.display = "none"
    btn.classList.remove("disable-btn")
    btn.classList.add("main-btn")
    btn.innerHTML = "Add source"
  } else {
    box.style.display = "block"
    btn.classList.remove("main-btn")
    btn.classList.add("disable-btn")
    btn.innerHTML = "Cancel"
  }
}

function addSource(){
  toggleAddSource();
  console.log(document.getElementById("language").value)
}