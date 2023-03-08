let is_scraping = true;
let n = 0;
let days_until_stale = 14;

window.onload = function(){
  document.getElementById("kibana-visualisation").style.display="none";
  //update_text(n)
  //TODO: Find out is_scraping here
  eel.get_days_until_stale()(set_days_until_stale)
  eel.get_sources()(populate_tables)

}

function set_days_until_stale(d){
  days_until_stale = d;
}

function populate_tables(scrapers) {
  
  for(i = 0; i < scrapers.length; i++){
    //TODO: Properly decide table
    addTableRow(scrapers[i][0], scrapers[i][1], scrapers[i][2], scrapers[i][3], scrapers[i][4], scrapers[i][5], true)
  }
  update_text(scrapers.length)
}

function get_date_string(date){
  let now = Date.now()
  let then = Date.parse(date)
  if (isNaN(then)){
    return ["Never", true]
  }
  
  let ms_difference = now - then
  // Calculate if source is stale
  let ms_until_stale = days_until_stale * (24 * 60 * 60 * 1000)
  let is_stale = (ms_until_stale < ms_difference)

  // Get date string
  let mins_difference = Math.floor(ms_difference / (1000 * 60))
  if (mins_difference === 0){
    return ["Just now", true]
  }
  if (mins_difference < 60){
    return [mins_difference + " minutes ago", is_stale]
  }
  else if (mins_difference < (60 * 24)){
    return [Math.floor(mins_difference / 60) + " hours ago", is_stale]
  }
  else if (mins_difference < (60 * 24 * 7)){
    return [Math.floor(mins_difference / (60 * 24)) + " days ago", is_stale]
  }
  else if (mins_difference < (60 * 24 * 30)){
    return [Math.floor(mins_difference / (60 * 24 * 7)) + " weeks ago", is_stale]
  }
  else if (mins_difference < (60 * 24 * 365)){
    return [Math.floor(mins_difference / (60 * 24 * 30)) + " months ago", is_stale]
  }
  return [Math.floor(mins_difference / (60 * 24 * 365)) + " years ago", is_stale]
}

function update_text(n){

  sub = document.getElementById("subheading")

  if(is_scraping){
    if (n===1){
      sub.innerHTML = "Scraping 1 source"     
    } else {
      sub.innerHTML = "Scraping " + n + " sources"
    }
  }
  else {
    sub.innerHTML = "Not currently scraping"
  }
}

function update_scraper_button() {
  var b = document.getElementById("toggle-scrape-btn")
  var sub = document.getElementById("subheading")
  if (is_scraping){
    b.innerHTML = "Stop scraping";
    b.classList.remove("main-btn");
    b.classList.add("disable-btn");
  }
  else {
    b.innerHTML = "Start scraping";
    b.classList.remove("disable-btn");
    b.classList.add("main-btn");
  }
  update_text(n);
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
    n = n - 1;
    update_text(n)
  }
  else {
    btn.classList.remove("toggle-source-btn-disabled")
    btn.classList.remove("accent-btn")
    btn.classList.add("toggle-source-btn-enabled")
    btn.classList.add("disable-btn")
    btn.innerHTML = "Disable"
    //TODO: Check for staleness
    moveTable(btn, "active-table")
    n = n + 1;
    update_text(n)
  }
  // TODO: Actually toggle source
}

function deleteSource(btn) {
  let row = btn.parentElement.parentElement
  let table = row.parentElement.parentElement
  console.log(table.id)
  deleteRow(row)
  if(!(table.id === "disabled-table")){
    n = n - 1;
    update_text(n)
  }
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
function addTableRow(source_id, url, name, lang, srcType, last, isEnabled) {

  date_string_data = get_date_string(last)
  console.log()
  date_string = date_string_data[0]
  console.log(date_string)
  is_stale = date_string_data[1]
  let table_id = "active-table"
  if (!(isEnabled)){
    table_id = "disabled-table"
  }
  else if(is_stale){
    table_id="stale-table"
  }

  var table = document.getElementById(table_id);
  if (!table){
    addTable(table_id)
    table = document.getElementById(table_id);
  }
  var row = table.insertRow(1);
  var srcCell = row.insertCell(0);
  var langCell = row.insertCell(1);
  var srcTypeCell = row.insertCell(2);
  var lastCell = row.insertCell(3);
  var disableCell = row.insertCell(4);
  var deleteCell = row.insertCell(5);


  srcCell.innerHTML = `<a href="${url}">${name}</a>`;
  langCell.innerHTML = lang.toUpperCase();
  srcTypeCell.innerHTML = srcType
  lastCell.innerHTML = date_string
  if (isEnabled){
    disableCell.innerHTML = `<td><button id = "${source_id}-toggle" class="action-btn table-btn disable-btn" onclick="toggleSource(this)">Disable</button></td>`
  } else {
    disableCell.innerHTML = `<td><button id = "${source_id}-toggle" class="action-btn table-btn accent-btn" onclick="toggleSource(this)">Enable</button></td>`
  }

  deleteCell.innerHTML = `<td><button id = "${source_id}-delete" class="action-btn table-btn delete-btn" onclick="deleteSource(this)">Delete</button></td>`
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

//TODO: Redo
function moveTable(btn, to_table){
  let row = btn.parentElement.parentElement;
  var source = row.cells[0].firstChild;
  var last_active = row.cells[3].innerHTML;
  console.log(last_active)
  if(to_table === "active-table" && last_active.includes("months")){
    to_table = "stale-table"
  }
  addTableRow(to_table, source.innerHTML, source.href, row.cells[1].innerHTML, row.cells[2].innerHTML, last_active, row.cells[4].firstChild.classList.contains("disable-btn"));
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

  document.getElementById("url").value = ""
  document.getElementById("src-name").value = ""
  document.getElementById("language").value = "Unknown"
  document.getElementById("countries").value = "" 
  document.getElementById("src-type").value = "Unknown" 
  document.getElementById("error-text").style.display = "none"
}

function addSource(){
  let url = document.getElementById("url").value;
  if(!url){
    document.getElementById("error-text").style.display = "block";
    return;
  }
  let srcName = document.getElementById("src-name").value
  if (!srcName){
    srcName = "Unnamed"
  }
  let language = document.getElementById("language").value
  if (!language){
    language = "EN"
  }
  let srcType = document.getElementById("src-type").value.replace("-", " ")

  n = n + 1;
  update_text(n)

  addTableRow("active-table", srcName, url, language, srcType, "--", true)
  toggleAddSource();
}