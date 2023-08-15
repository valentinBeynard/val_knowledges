function initDisplay()
{
  document.getElementById("is_up_flag").innerHTML = "True";
  document.getElementById("up_time_flag").innerHTML = "00:00:00 (hh:mm:ss)";
  document.getElementById("backup_time_flag").innerHTML = "00:00:00 (hh:mm:ss)";
}

// Add parameters with their values automaticly
function formatParams( params ){
  return "?" + Object
        .keys(params)
        .map(function(key){
          return key+"="+encodeURIComponent(params[key])
        })
        .join("&")
}

function launchMainServer()
{
  var xml_rq = new XMLHttpRequest();

  xml_rq.open("GET", "myapp?rq=start&key=123456");
  xml_rq.send();

  document.getElementById("is_up_flag").innerHTML = "Test";
}
