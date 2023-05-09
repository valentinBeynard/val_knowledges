function initDisplay()
{
  document.getElementById("is_up_flag").innerHTML = "True";
  document.getElementById("up_time_flag").innerHTML = "00:00:00 (hh:mm:ss)";
  document.getElementById("backup_time_flag").innerHTML = "00:00:00 (hh:mm:ss)";
}


function launchMainServer()
{
  var blob = new Blob("launch=1", { type: "text/plain;charset=utf-8" });
  saveAs(blob, "launch_cmd.txt");
}
