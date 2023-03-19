let isScraping = false;
let n = 0;
let daysUntilStale = 14;
let secondsPerUpdate = 60;

// Adapted from https://stackoverflow.com/a/47480429
const delay = s => new Promise(res => setTimeout(res, s * 1000));

window.onload = function(){
  document.getElementById("kibana-visualisation").style.display="none";
  eel.get_days_until_stale()(setDaysUntilStale)
  eel.get_system_status()(updateScraperButton)
  updateTable();
}

async function updateTable(){
  eel.get_js_sources()(populateTables)
  await delay(secondsPerUpdate)
  updateTable();
}

function setDaysUntilStale(d){
  daysUntilStale = d;
}

function populateTables(scrapers) {
  resetTables();
  let noEnabled = 0
  for(i = 0; i < scrapers.length; i++){
    // Increment number of enabled scrapers
    if (scrapers[i][6]){noEnabled += 1;}
    // Add to table
    addTableRow(scrapers[i][0], scrapers[i][1], scrapers[i][2], scrapers[i][3], scrapers[i][4], scrapers[i][5], scrapers[i][6])
  }
  updateText(noEnabled);
  console.log("Refreshed..")
}

function resetTables(){
  let activeTable = document.getElementById("active-table");
  if(activeTable){
    activeTable.parentElement.innerHTML = "";
  }

  let staleTable = document.getElementById("stale-table");
  if(staleTable){
    staleTable.parentElement.innerHTML = "";
  }

  let disabledTable = document.getElementById("disabled-table");
  if(disabledTable){
    disabledTable.parentElement.innerHTML = "";
  }
}

function getDateString(date){
  let now = Date.now()
  let then = Date.parse(date)
  // Return never for default value
  if (then <= 946684800000){
    return ["Never", true]
  }

  let msDifference = now - then
  // Calculate if source is stale
  msUntilStale = Math.floor(daysUntilStale * 24 * 60 * 60 * 1000)
  let is_stale = (msUntilStale < msDifference)

  // Get date string
  let mins_difference = Math.floor(msDifference / (1000 * 60))
  if (mins_difference === 0){
    return ["Just now", is_stale]
  } else if (mins_difference === 1){
    return ["1 minute ago", is_stale]
  }
  // If less than an hour ago
  else if (mins_difference < 60){
    return [mins_difference + " minutes ago", is_stale]
  }
  // If less than a day ago
  let hours_difference = Math.floor(mins_difference / 60)
  if (hours_difference === 1){
    return ["1 hour ago", is_stale]
  } else if (hours_difference < 24){
    return [hours_difference + " hours ago", is_stale]
  }
  // If less than a week ago
  let days_difference = Math.floor(hours_difference / 24)
  if (days_difference === 1){
    return ["Yesterday", is_stale]
  }
  else if (days_difference < 7){
    return [days_difference + " days ago", is_stale]
  }
  // If less than a month ago
  let weeks_difference = Math.floor(days_difference / 7)
  if (weeks_difference === 1){
    return ["Last week", is_stale]
  }
  else if (days_difference < 30){
    return [weeks_difference + " weeks ago", is_stale]
  }
  // If less than a year ago
  let months_difference = Math.floor(days_difference / 30)
  if (months_difference === 1){
    return ["Last month", is_stale]
  }
  else if (days_difference < 365){
    return [months_difference + " months ago", is_stale]
  }
  // If a year agp pr more
  return [Math.floor(days_difference / 365) + " years ago", is_stale]
}

// Get the position to insert the row in, to maintain alphabetical order
function getIndex(table_id, new_string){

  var table = document.getElementById(table_id);

  // Adapted from https://stackoverflow.com/a/3065389
  let index = 0;
  for (var i = 1, row; row = table.rows[i]; i++) {
    if (new_string <= row.cells[0].firstChild.innerHTML){
      return i;
    }
 }
 return table.rows.length;
}

function updateText(noEnabledSources){
  n = noEnabledSources
  sub = document.getElementById("subheading")

  if(isScraping){
    if (n===1){
      sub.innerHTML = "Scraping 1 source"     
    } else {
      sub.innerHTML = "Scraping " + noEnabledSources + " sources"
    }
  }
  else {
    sub.innerHTML = "System is disabled"
  }
}

function updateScraperButton(isSystemScraping) {
  isScraping = isSystemScraping;

  var b = document.getElementById("toggle-scrape-btn")
  var sub = document.getElementById("subheading")
  if (isSystemScraping){
    b.innerHTML = "Stop scraping";
    b.classList.remove("main-btn");
    b.classList.add("disable-btn");
  }
  else {
    b.innerHTML = "Start scraping";
    b.classList.remove("disable-btn");
    b.classList.add("main-btn");
  }
  updateText(n);
}

function toggleSystem() {
  eel.toggle_system()(updateScraperButton)
}

async function toggleSource(btn){
  // Prevent multiple clicks
  if(btn.classList.contains("unlickable")){
    return
  }
  // Get source id
  let source_id = btn.id.substring(0, btn.id.length - 7)
  try {
  // Temporarily update button
  tempUpdateSourceButton(btn)
  // Toggle the source and get success
  let success = await eel.toggle_source(source_id)()
  // Update button
  if(success){
    updateSourceButton(btn);
  } else {
    revertSourceButton(btn);
  }
  // Make button clickable again
  if(btn.classList.contains("unlickable")){
    btn.classList.remove("unclickable")
  }
  } catch(err) {
    // Deal with toggling mid update
    if(!btn){
      toggleSource(document.getElementById(source_id + "-toggle"))
    }
  }
}


function tempUpdateSourceButton(btn){
  btn.classList.add("unclickable");

  if (btn.classList.contains("disable-btn")) {
    btn.innerHTML = "Disabling..."
  }
  else {
    btn.innerHTML = "Enabling..."
  }
}


function revertSourceButton(btn){
  if (btn.classList.contains("disable-btn")) {
    btn.innerHTML = "Disable"
  }
  else {
    btn.innerHTML = "Enable"
  }
}


function updateSourceButton(btn){
  if (btn.classList.contains("disable-btn")) {
    btn.classList.remove("toggle-source-btn-enabled")
    btn.classList.remove("disable-btn")
    btn.classList.add("toggle-source-btn-disabled")
    btn.classList.add("accent-btn")
    btn.innerHTML = "Enable"
    moveTable(btn, "disabled-table")
    n = n - 1;
    updateText(n)
  }
  else {
    btn.classList.remove("toggle-source-btn-disabled")
    btn.classList.remove("accent-btn")
    btn.classList.add("toggle-source-btn-enabled")
    btn.classList.add("disable-btn")
    btn.innerHTML = "Disable"
    let row = btn.parentElement.parentElement;
    let isStale = row.cells[3].className;
    if(isStale === "true"){
      moveTable(btn, "stale-table")
    }
    else {
      moveTable(btn, "active-table")
    }
    n = n + 1;
    updateText(n)
  }
}


async function deleteSource(btn) {

  btn.innerHTML = "Deleting..."
  let sourceID = btn.id.substring(0, btn.id.length - 7);

  success = await eel.delete_source(sourceID)()
  // In case of refresh
  btn = document.getElementById(sourceID + "-delete")
  let row = btn.parentElement.parentElement
  let table = row.parentElement.parentElement
  
  if(!success) {
    btn.innerHTML = "Delete"
  }
  else {
    deleteRow(row)
    if(!(table.id === "disabled-table")){
      n = n - 1;
      updateText(n)
    }
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
// Adds a row to the table with the information given in the parameters
function addTableRow(source_id, url, name, lang, srcType, last, isEnabled) {

  // Get date string and if source is stale
  date_string_data = getDateString(last)
  date_string = date_string_data[0]
  is_stale = date_string_data[1]

  // Determine correct table
  let table_id = "active-table"
  if (!(isEnabled)){
    table_id = "disabled-table"
  }
  else if(is_stale){
    table_id="stale-table"
  }

  // Default for no language
  if(!lang){
    lang = "--"
  }

  // Get table to add source to, or create it if it doesn't exist
  var table = document.getElementById(table_id);
  if (!table){
    addTable(table_id)
    table = document.getElementById(table_id);
  }
  // Create rows
  var row = table.insertRow(getIndex(table_id, name));
  var srcCell = row.insertCell(0);
  var langCell = row.insertCell(1);
  var srcTypeCell = row.insertCell(2);
  var lastCell = row.insertCell(3);
  var disableCell = row.insertCell(4);
  var deleteCell = row.insertCell(5);

  // Populate rows
  srcCell.innerHTML = `<a href="${url}">${name}</a>`;
  langCell.innerHTML = lang.toUpperCase();
  srcTypeCell.innerHTML = srcType;
  lastCell.innerHTML = date_string;
  lastCell.className = is_stale;

  // Enable / disable and delete buttons
  if (isEnabled){
    disableCell.innerHTML = `<td><button id = "${source_id}-toggle" class="action-btn table-btn disable-btn" onclick="toggleSource(this)">Disable</button></td>`
  } else {
    disableCell.innerHTML = `<td><button id = "${source_id}-toggle" class="action-btn table-btn accent-btn" onclick="toggleSource(this)">Enable</button></td>`
  }
  deleteCell.innerHTML = `<td><button id = "${source_id}-delete" class="action-btn table-btn delete-btn" onclick="deleteSource(this)">Delete</button></td>`
}

function moveTableRow(table_id, source_id, url, name, lang, srcType, date_string, isEnabled, isStale){

  var table = document.getElementById(table_id);
  if (!table){
    addTable(table_id)
    table = document.getElementById(table_id);
  }
  var row = table.insertRow(getIndex(table_id, name));
  var srcCell = row.insertCell(0);
  var langCell = row.insertCell(1);
  var srcTypeCell = row.insertCell(2);
  var lastCell = row.insertCell(3);
  var disableCell = row.insertCell(4);
  var deleteCell = row.insertCell(5);

  srcCell.innerHTML = `<a href="${url}">${name}</a>`;
  langCell.innerHTML = lang.toUpperCase();
  srcTypeCell.innerHTML = srcType;
  lastCell.innerHTML = date_string;
  lastCell.className = isStale;

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

function moveTable(btn, to_table){
  let source_id = btn.id.substring(0, btn.id.length - 7)
  let row = btn.parentElement.parentElement;
  var source = row.cells[0].firstChild;
  let isStale = row.cells[3].className;
  moveTableRow(to_table, source_id, source.href, source.innerHTML, row.cells[1].innerHTML, row.cells[2].innerHTML, row.cells[3].innerHTML, row.cells[4].firstChild.classList.contains("disable-btn"), isStale);
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
  let srcName = document.getElementById("src-name").value
  let language = document.getElementById("language").value
  let country = document.getElementById("countries").value
  let srcType = document.getElementById("src-type").value.replace("-", " ")
  if(!url || !srcName || srcType==="Unknown"){
    document.getElementById("error-text").style.display = "block";
    return;
  }
  eel.add_source(url, srcName, language, country, srcType)(addTableRowPacked)
  n = n + 1;
  updateText(n)
  toggleAddSource();
}

// Unpack data from python
function addTableRowPacked(data) {
  addTableRow(data[0], data[1], data[2], data[3], data[4], data[5], data[6])
}