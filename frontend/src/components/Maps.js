import { MapContainer, TileLayer, Popup, Marker, useMap } from 'react-leaflet'


function MapMarkers(props) {
    const withoutNullLat = props.properties.filter(v => v.latitude !== null);
    return (
      <>
        {withoutNullLat.map(({latitude, longitude, id, address, code_violations_count, police_incidents_count, tenant_complaints_count}) => (
            <Marker key={id} position={[
                latitude, 
                longitude
            ]}
            >
            <Popup>
                <p>{address}</p>
                <p>Code Violations: {code_violations_count}</p>
                <p>Police Incidents: {police_incidents_count}</p>
                <p>Tenant Complaints: {tenant_complaints_count}</p>
            </Popup>
          </Marker>
          ))}
      </>

    )

}

export function MapWidget(props) {
    return (
        <MapContainer center={[42.6526, -73.7762]} zoom={13} scrollWheelZoom={false}>
          <TileLayer
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          />
          <MapMarkers properties={props.properties}/>
        </MapContainer>
    );
  }