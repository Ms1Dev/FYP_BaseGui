


const socket = new WebSocket(
    'ws://' + window.location.host + '/ws/gui/'
    // 'ws://' + "127.0.0.1:8001" + '/ws/gui/'
);

socket.onmessage = function(e) {
    const data = JSON.parse(e.data);
};

socket.onclose = function(e) {
    console.error('Socket closed unexpectedly');
};

socket.onopen = function(e) {
    socket.send(JSON.stringify({"message":"new"}))
}

// document.querySelector('#chat-message-submit').onclick = function(e) {
//     const messageInputDom = document.querySelector('#chat-message-input');
//     const message = messageInputDom.value;
//     socket.send(JSON.stringify({
//         'message': message
//     }));
//     messageInputDom.value = '';
// };



var map = L.map('map').setView([51.505, -0.09], 13);

L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
    attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>'
}).addTo(map);


function azimuthUpdate(value) {
    socket.send(JSON.stringify({
        "azimuth" : value["value"]
    }));
}

function elevationUpdate(value) {
    socket.send(JSON.stringify({
        "elevation" : value["value"]
    }));
}




$("#azimuth-slider").roundSlider({
    radius: 85,
    sliderType: "default",
    value: 0,
    min: 0,
    max: 360,
    startAngle: 90,
    change: "azimuthUpdate"
});



$("#elevation-slider").roundSlider({
    radius: 80,
    circleShape: "custom-quarter",
    sliderType: "min-range",
    showTooltip: false,
    value: 0,
    min: -45,
    max: 45,
    startAngle: 315,
    change: "elevationUpdate"
});