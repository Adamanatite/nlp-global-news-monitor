// eel.get_no_sources()(update_text)

window.onload = function(){document.getElementById("kibana-visualisation").style.display="none";}

function update_text(n){
    document.getElementById("website-count").innerHTML = "Scraping " + n + " sources."  
}

function toggleVisualisation(){
    var v = document.getElementById("kibana-visualisation")
    var b = document.getElementById("toggle-button")
    console.log(v.style.display)
    if (v.style.display === "none") {
        v.style.display = "block";
        b.innerHTML = "Hide visualisation";
      } else {
        v.style.display = "none";
        b.innerHTML = "Show visualisation";
      }
}