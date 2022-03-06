var socket;
function init(){
  var host = "ws://localhost:11456/";
  try{
    socket = new WebSocket(host);
    socket.onopen = function(msg){ 
      log("Start WebSocket connection");
    }
    socket.onmessage = function(msg){
      log(msg.data);
    }
    socket.onclose   = function(msg){
      log("Connection Lose");
    }
    socket.onerror   = function(msg){
      console.log("Error");
    }
  }catch(ex){
    log(ex);
  }

}
function send(){
  var txt,msg;
  txt = $("termip");
  msg = txt.value;
  msg = msg.split('❯ ')[1]
  console.log("message is", msg)
  if(!msg){
    log("Message can not be empty");
    return;
  }
  txt.value="❯ ";
  txt.focus();
  try{ 
    log(msg);
    socket.send(msg);
  }catch(ex){
    log(ex);
  }
}

window.onbeforeunload=function(){
  try{
    socket.send('quit');
    socket.close();
    socket=null;
  }catch(ex){
    log(ex);
  }
}

function $(id){
  return document.getElementById(id);
}

function log(msg){
  $("termop").innerHTML+=msg+"<br>"+ "❯ <img src=\"data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAUAAAAFCAYAAACNbyblAAAAHElEQVQI12P4//8/w38GIAXDIBKE0DHxgljNBAAO9TXL0Y4OHwAAAABJRU5ErkJggg==\" />";
  $('termop').scrollTop = $('termop').scrollHeight;
}

function onkey(event){
  switch(event.keyCode){
    case 13:
      send();
    case 8:
      if (($("termip").value).length <= 2){
        event.preventDefault();
      }
    case 37:
      if ($("termip").selectionStart <= 2 || $("termip").selectionEnd <= 2){
        event.preventDefault();
      }
}
}
function cursorpos() {
  if ($("termip").selectionStart <= 2 || $("termip").selectionEnd <= 2){
    $("termip").setSelectionRange(2, 2);
  }
}
function inp(){
  if (($("termip").value).slice(0, 2) != '❯ '){
    $("termip").value="❯ ";
  }
}
