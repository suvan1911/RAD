const websocket = new WebSocket("wss://RAD.len1911.repl.co");

const ss = document.getElementById("ss")
const togg =  document.getElementById("toggless")

websocket.addEventListener("message", ({ data }) => {
    var reader = new FileReader();
    reader.readAsDataURL(data);
    reader.onloadend = function () {
      var base64String = reader.result;
      base64String = base64String.replace('application/octet-stream', 'image/png')
      ss.src = base64String;
    }
  });
  
ss.addEventListener('click',(event) => {
    console.log(event)
    const [transX, transY] = translateCords(event.x, event.y, event)
    websocket.send(JSON.stringify({type: "click", x : transX, y : transY}));
});

togg.addEventListener('click',(event) => {
  websocket.send(JSON.stringify({type:"toggle"}))
  setTimeout(()=>{ss.src = ""}, 5000);
  
});

function translateCords(x,y,event) {
    var rect = event.target.getBoundingClientRect();
    return [x - rect.left, y - rect.top]
}

window.addEventListener('keydown', (event) => {
    if (ss.src  != "") {
      websocket.send(JSON.stringify({type: "keydown", key: event.key}));
    }
});

window.addEventListener('keyup', (event) => {
  if (ss.src  != "") {
    websocket.send(JSON.stringify({type: "keyup", key: event.key}));
  }
});