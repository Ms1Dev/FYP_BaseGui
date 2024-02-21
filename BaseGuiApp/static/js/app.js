

/**
 * 
 *          WEB SOCKET
 * 
 */

const socket = new WebSocket(
    'ws://' + window.location.host + '/ws/gui/'
    // 'ws://' + "127.0.0.1:8001" + '/ws/gui/'
);

socket.onmessage = function(e) {
    const data = JSON.parse(e.data);
    dataReceived(data);
};

socket.onclose = function(e) {
    console.error('Socket closed unexpectedly');
};

socket.onopen = function(e) {
    socket.send(JSON.stringify({"message":"new"}))
}


/**
 * 
 * 
 *      MAP 
 * 
 * 
 */ 

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
    handleSize: "34,10",
    sliderType: "default",
    value: 0,
    animation: false,
    min: 0,
    max: 360,
    startAngle: 90,
    change: "azimuthUpdate"
});


$("#elevation-slider").roundSlider({
    radius: 80,
    handleSize: "34,10",
    circleShape: "custom-quarter",
    sliderType: "min-range",
    animation: false,
    value: 0,
    min: -45,
    max: 45,
    startAngle: 315,
    change: "elevationUpdate"
});


/**
 * 
 * 
 *      UI UPDATES
 * 
 */


var base_marker = null;
var mobile_marker = null;

let base_coords_input = $("#base-coordinates");
let base_temperature_input = $("#base-temperature");

let mobile_coords_input = $("#mobile-coordinates");
let mobile_temperature_input = $("#mobile-temperature");

let antenna_side_image = $("#antenna-side-image");
var antenna_current_elevation = 0;

let antenna_top_image = $("#antenna-top-image");
var antenna_current_bearing = 0;


let jumped_to_location = false;

// Attribution for location icons
//<a href="https://www.flaticon.com/free-icons/outdoor-antenna" title="outdoor antenna icons">Outdoor antenna icons created by Freepik - Flaticon</a>
//<a href="https://www.flaticon.com/free-icons/location" title="location icons">Location icons created by inkubators - Flaticon</a>

var mobile_marker_icon = new L.Icon({
    iconUrl: '../static/images/pin.png',
    iconSize: [50, 50],
    iconAnchor: [25, 45]
  });

var base_marker_icon = new L.Icon({
    iconUrl: '../static/images/outdoor-antenna.png',
    iconSize: [50, 50],
    iconAnchor: [25, 50]
  });

function dataReceived(data) {
    console.log(data);
    if (data["base_gps_pos"]) {
        let lat = data["base_gps_pos"]["lat"];
        let lon = data["base_gps_pos"]["lon"];
        if (base_marker == null) {
            base_marker = new L.Marker([lat, lon], {icon: base_marker_icon});
            base_marker.addTo(map);
        }
        else {
            base_marker.setLatLng([lat, lon]);
        }
        if (!jumped_to_location) {
            jumped_to_location = true;
            map.panTo(new L.LatLng(lat, lon));
        }
        base_coords_input.val(lat + ", " + lon);
    }

    if (data["base_temperature"]) {
        base_temperature_input.val(data["base_temperature"]);
    }

    if (data["antenna_azimuth"]) {
        move_degrees = data["antenna_azimuth"] - antenna_current_bearing;
        antenna_top_image.css("transform", "rotate(" + move_degrees + "deg)");
    }

    if (data["antenna_elevation"]) {
        move_degrees = data["antenna_elevation"] - antenna_current_elevation;
        antenna_side_image.css("transform", "rotate(" + move_degrees + "deg)");
    }

    if (data["mobile_gps_pos"]) {
        let lat = data["mobile_gps_pos"]["lat"];
        let lon = data["mobile_gps_pos"]["lon"];
        if (mobile_marker == null) {
            mobile_marker = new L.Marker([lat, lon], {icon: mobile_marker_icon});
            mobile_marker.addTo(map);
        }
        else {
            mobile_marker.setLatLng([lat, lon]);
        }
        mobile_coords_input.val(lat + ", " + lon);
    }

    if (data["mobile_temperature"]) {
        mobile_temperature_input.val(data["mobile_temperature"]);
    }

}
