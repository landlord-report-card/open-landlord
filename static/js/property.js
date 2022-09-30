var map = L.map('map')
L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
    attribution: '© OpenStreetMap'
}).addTo(map);

var markers = [];

var group = L.featureGroup(markers).addTo(map);

setTimeout(function () {
  map.fitBounds(group.getBounds());
}, 1000);


var marker = L.marker([property_json["latitude"], property_json["longitude"]]);
markers.push(marker)

var group = L.featureGroup(markers).addTo(map);

setTimeout(function () {
  map.fitBounds(group.getBounds());
}, 1000);
