
var map = L.map('map').setView([42.6496206, -73.7647505], 13);
L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
    attribution: '© OpenStreetMap'
}).addTo(map);



var markers = [];

var group = L.featureGroup(markers).addTo(map);

setTimeout(function () {
  map.fitBounds(group.getBounds());
}, 1000);



for (var i = 0; i < properties_json.length; i++) {
    if (properties_json[i]["latitude"] && properties_json[i]["longitude"]) {
        var marker = L.marker([properties_json[i]["latitude"], properties_json[i]["longitude"]]);
        marker.bindPopup("<a href=\"/property/" + properties_json[i]["id"] + "\">" + properties_json[i]["address"] + "</a>"
            + "</br>" + "Tenant Complaints: " + properties_json[i]["tenant_complaints"]
            + "</br>" + "Code Violations: " + properties_json[i]["code_violations_count"]
            + "</br>" + "Landlord/Tenant Police Incidents: " + properties_json[i]["police_incidents_count"]
            );
        markers.push(marker)
    }
}

var group = L.featureGroup(markers).addTo(map);

setTimeout(function () {
  map.fitBounds(group.getBounds());
}, 1000);
