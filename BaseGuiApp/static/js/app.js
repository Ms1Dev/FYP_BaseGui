

/**
 * 
 *          WEB SOCKET
 * 
 */

$(document).ready(function() {
    disableControls();
    $(".tick").hide();
});


var ping_sent = 0;
var ping_timeout;
const PING_TIMEOUT_MS = 8000;

$("#ping-button").on("click", function(e) {
    $(this).attr('disabled','disabled');
    $("#ping-websocket").val("");
    $("#ping-hc12").val("");
    $("#ping-total").val("");
    ping_sent = Date.now();
    socket.send(JSON.stringify({
        "ping" : ping_sent
    }));

    ping_timeout = setTimeout(pingTimeout, PING_TIMEOUT_MS);
});


function pingTimeout() {
    $("#ping-websocket").val("Timeout");
    $("#ping-hc12").val("Timeout");
    $("#ping-total").val("Timeout");
    $("#ping-button").removeAttr('disabled');
}


function pingReceived(internalTime) {
    clearTimeout([ping_timeout]);
    let webSentWhen = internalTime[0];
    let hc12SentWhen = internalTime[1];
    let hc12RecvWhen = internalTime[2];
    let webRecvWhen = Date.now();
    let websocketDiff = 0;
    let hc12Diff = 0;
    let total = 0;
    if (ping_sent > 0) {
        websocketDiff = Math.trunc(hc12SentWhen - webSentWhen + webRecvWhen - hc12RecvWhen) + " ms";
        hc12Diff = Math.trunc(hc12RecvWhen - hc12SentWhen) + " ms";
        total = (webRecvWhen - webSentWhen) + " ms";
    }

    $("#ping-websocket").val(websocketDiff);
    
    if (internalTime[3]) {
        $("#ping-hc12").val("Timeout");
    }
    else {
        $("#ping-hc12").val(hc12Diff);
    }
    
    $("#ping-total").val(total);
    $("#ping-button").removeAttr('disabled');
    ping_sent = 0;
}


const socket = new WebSocket(
    'ws://' + window.location.host + '/ws/gui/'
    // 'ws://' + "127.0.0.1:8001" + '/ws/gui/'
);

let log_messages = false;

socket.onmessage = function(e) {
    const data = JSON.parse(e.data);
    if (log_messages) {
        console.log(data)
    }
    if (data["ping"]) {
        pingReceived(data["ping"]);
        return;
    }
    dataReceived(data);
};

socket.onclose = function(e) {
    console.error('Socket closed unexpectedly');
};

socket.onopen = function(e) {
    socket.send(JSON.stringify({
        "get_state" : 1
    }));
    enableControls();
}


/**
 * 
 * 
 *      MAP 
 * 
 * 
 */ 

var map = L.map('map').setView([52.926, -1.127], 13);

let tile_loc = 'https://tile.openstreetmap.org/{z}/{x}/{y}.png';
let tile_zoom = 19;

if (!navigator.onLine) {
    tile_loc =  '../static/mapTiles/{z}/{x}/{y}.png';
    tile_zoom = 16;
}

L.tileLayer(tile_loc, {
    maxZoom: tile_zoom,
    attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>'
}).addTo(map);


/**
 * 
 * 
 *      UI UPDATES
 * 
 */


let base_marker = null;
let mobile_marker = null;
let base_marker_no_update = false;

let base_coords_input = $("#base-coordinates");
let base_alt_input = $("#base-altitude");
let base_temperature_input = $("#base-temperature");
let base_bearing = $("#base-bearing");

let mobile_coords_input = $("#mobile-coordinates");
let mobile_alt_diff = $("#mobile-altitude-difference");
let mobile_distance = $("#mobile-distance");
let mobile_temperature_input = $("#mobile-temperature");

let antenna_side_image = $("#antenna-side-image");
let antenna_current_elevation = 0;
let antenna_elevation_value = $("#antenna-elevation-value");

let antenna_top_image = $("#antenna-top-image");
let antenna_current_bearing = 0;
let antenna_azimuth_value = $("#antenna-azimuth-value");

let coordinate_offset = [0.0, 0.0];
let absolute_bearing = false;
let compass_bearing = 0;

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
    if (data["state"]) {
        absolute_bearing = data["state"]["abs_bearing"];
        if (data["state"]["man"]) {
            controlOverride(true);
            $("#manualOverride").prop("checked", true);
        }
    }

    if (data["base_ctrl_coord"]) {
        let lat = data["base_ctrl_coord"][0] + coordinate_offset[0];
        let lon = data["base_ctrl_coord"][1] + coordinate_offset[1];
        if (base_marker == null) {
            base_marker = new L.Marker([lat, lon], {icon: base_marker_icon});
            base_marker.addTo(map);
        }
        else if (!base_marker_no_update) {
            base_marker.setLatLng([lat, lon]);
        }
        if (!jumped_to_location) {
            jumped_to_location = true;
            map.panTo(new L.LatLng(lat, lon));
        }
        base_coords_input.val(lat.toFixed(7) + ", " + lon.toFixed(7));
    }

    if (data["base_gps_pos"]) {
        let altitude = data["base_gps_pos"]["alt"];
        base_alt_input.val(altitude + " m");
    }

    if (data["alt_diff"]) {
        mobile_alt_diff.val(data["alt_diff"].toFixed(2) + " m");
    }

    if (data["distance"]) {
        mobile_distance.val(data["distance"].toFixed(2) + " m");
    }

    if (data["base_temperature"]) {
        base_temperature_input.val(data["base_temperature"]);
    }

    if (data["antenna_azimuth"]) {
        let angle = parseFloat( data["antenna_azimuth"] );
        if (absolute_bearing) {
            angle += compass_bearing;
        }
        move_degrees = angle - antenna_current_bearing;
        antenna_top_image.css("transform", "rotate(" + move_degrees + "deg)");
        antenna_azimuth_value.html("Bearing: " + Math.round(angle) + "°");
    }

    if (data["antenna_elevation"]) {
        move_degrees = data["antenna_elevation"] - antenna_current_elevation;
        antenna_side_image.css("transform", "rotate(" + move_degrees + "deg)");
        antenna_elevation_value.html("Elevation: " + data["antenna_elevation"] + "°");
    }

    if (data["mobile_gps_pos"]) {
        let lat = data["mobile_gps_pos"]["lat"] + coordinate_offset[0];
        let lon = data["mobile_gps_pos"]["lon"] + coordinate_offset[1];
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

    if (data["compass_bearing"]) {
        compass_bearing = data["compass_bearing"][1];
        base_bearing.val(compass_bearing.toFixed(2));
    }

}


function disableControls() {
    $("#options-menu button").attr('disabled', 'disabled');
    $("#manualOverride").attr('disabled', 'disabled');
    $("#outbound-message-send").find("button").attr('disabled', 'disabled');
    $("#ping-button").attr('disabled', 'disabled');
}


function enableControls() {
    $("#options-menu button").removeAttr('disabled');
    $("#manualOverride").removeAttr('disabled');
    $("#outbound-message-send").find("button").removeAttr('disabled');
    $("#ping-button").removeAttr('disabled');
}


/**
 * 
 * 
 *     Controls
 * 
 * 
 */

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
    radius: 60,
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


$("#manualOverride").change(function() {
    controlOverride($(this).is(":checked"));
});

function controlOverride (isManual) {  
    if (isManual) {
        socket.send(JSON.stringify({
            "antenna_ctrl" : "man"
        }));
        $("#azimuth-slider-wrapper").show(500);
        $("#elevation-slider-wrapper").show(500);
        $("label[for='manualOverride']").html("Manual");
    }
    else {
        socket.send(JSON.stringify({
            "antenna_ctrl" : "auto"
        }));
        $("#azimuth-slider-wrapper").hide(500);
        $("#elevation-slider-wrapper").hide(500);
        $("label[for='manualOverride']").html("Auto");
    }
}



$("#log-messages").on("click", function() {
    log_messages = !log_messages;
    $(this).find(".tick").toggle();
});


$("#anonymise-pos").on("click", function(e) {
    let _lat = Math.random() * 20;
    let _lon = Math.random() * 20;

    if (coordinate_offset[0] == 0 && coordinate_offset[1] == 0) {
        coordinate_offset[0] = _lat;
        coordinate_offset[1] = _lon;
        $(this).find(".tick").show();
    }
    else {
        coordinate_offset[0] = 0;
        coordinate_offset[1] = 0;
        $(this).find(".tick").hide();
    }
});


$("#calibrate-altitude").on("click", function() {
    socket.send(JSON.stringify({
        "cal" : true
    }));
});


$("#home-antenna").on("click", function() {
    socket.send(JSON.stringify({
        "antenna_home" : true
    }));
});


$("#base-pos-mode-avg").on("click", function() {
    socket.send(JSON.stringify({
        "antenna_pos" : {
            "mode" : "avg"
        }
    }));
    if (base_marker) {
        base_marker.dragging.disable();
    }
    base_marker_no_update = false; 
});


$("#base-pos-mode-live").on("click", function() {
    socket.send(JSON.stringify({
        "antenna_pos" : {
            "mode" : "live"
        }
    }));
    if (base_marker) {
        base_marker.dragging.disable();
    }
    base_marker_no_update = false; 
});


$("#base-pos-mode-lock").on("click", function() {
    socket.send(JSON.stringify({
        "antenna_pos" : {
            "mode" : "fixed"
        }
    }));
    if (base_marker) {
        base_marker.dragging.disable();
    }
    base_marker_no_update = false; 
});


$("#base-pos-mode-man").on("click", function() {
    socket.send(JSON.stringify({
        "antenna_pos" : {
            "mode" : "fixed"
        }
    }));

    if (!base_marker) {
        base_marker = new L.Marker([map.lat, map.lon], {icon: base_marker_icon});
        base_marker.addTo(map);
    }

    base_marker.dragging.enable();
        base_marker.on("dragend", function(event) {
        let latlng = event.target.getLatLng();
        socket.send(JSON.stringify({
            "antenna_pos" : {
                "mode" : "fixed",
                "pos" : [latlng["lat"], latlng["lng"]]
            }
        }));
    });
    base_marker_no_update = true;    
    
});


$("#calibrate-compass").on("click", function() {
    socket.send(JSON.stringify({
        "compass" : "calibrate"
    }));
});


$("#validate-compass").on("click", function() {
    socket.send(JSON.stringify({
        "compass" : "validate"
    }));
});


$("#bearing-absolute").on("click", function() {
    socket.send(JSON.stringify({
        "bearing_absolute" : true 
    }));
});


$("#bearing-relative").on("click", function() {
    socket.send(JSON.stringify({
        "bearing_absolute" : false 
    }));
});


$("#outbound-message-send").submit(function(e) {
    e.preventDefault();
    let textarea = $("#outbound-message");
    let message = textarea.val();
    textarea.val("");
    socket.send(JSON.stringify({
        "transmit" : message
    }));
});


