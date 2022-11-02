import { useParams } from 'react-router-dom'
import axios from "axios"
import React from "react"
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'
import { MapContainer, TileLayer, Popup, Marker, useMap } from 'react-leaflet'

import icon from 'leaflet/dist/images/marker-icon.png';
import iconShadow from 'leaflet/dist/images/marker-shadow.png';

let DefaultIcon = L.icon({
    iconUrl: icon,
    shadowUrl: iconShadow
});

L.Marker.prototype.options.icon = DefaultIcon;



function LandlordTitleRow(props) {
    return (
      <div className="row title-row text-center">
        <div className="col-sm-7">
          <span className="title-label">Landlord</span><br />
          <span className="landlord-name font-handwritten">{props.landlord.name}</span>
        </div>
        <div className="col-sm">
          <span className="title-label">Grade</span><br />
          <span className="font-handwritten grade">{props.landlord.grade}</span>
        </div>        
      </div>
    )
  }


function AliasesBlock(props) {
    if (!props.aliases || props.aliases.length <= 1) {
        return null;
    }
    
    const commaSep = props.aliases.map(item => item.name).join(', ');

    return (
        <div>
        <span className="landlord-attribute">Also Known As: </span> 
          <span className="font-handwritten">
            {commaSep}
          </span>
        </div>
        )

}

function LandlordDetailColumn(props) {
    return (
        <div className="col-sm landlord-info">
          <span className="landlord-attribute">Address: </span>
          <span className="font-handwritten">{props.landlord.address}</span><br/>
          <span className="landlord-attribute">Landlord Size:</span> 
          <span className="font-handwritten">{props.landlord.property_count}</span><br/>
          <AliasesBlock aliases={props.aliases}/>
        </div>
    )
  }


function GradeDetailWidget(props) {
    return (
        <div className="accordion-item">
          <h2 className="accordion-header" id="headingOne">
            <button className="accordion-button collapsed" type="button" data-bs-toggle="collapse" data-bs-target="#collapseOne" aria-expanded="false" aria-controls="collapseOne">
              {props.heading}<span className="font-handwritten grade-value">{props.individual_grade}</span>
            </button>
          </h2>
          <div id="collapseOne" className="accordion-collapse collapse" aria-labelledby="headingOne" data-bs-parent="#accordionExample">
            <div className="accordion-body">
              <p className="mb-0">{props.heading_total}: {props.total} </p>
              <p className="mb-0">{props.heading} Per Property: {props.per_property} </p>
              <p className="mb-0">City Average: {props.city_average} </p>
            </div>
          </div>
        </div>
    )
}

function GradeDetailColumn(props) {
    return (
        <div className="col-sm-5 landlord-grades">
            <div className="accordion" id="accordionExample">
            <GradeDetailWidget heading="Tenant Complaints" heading_total="Total Tenant Complaints" individual_grade={props.landlord.tenant_complaints_count_grade}
            total={props.landlord.tenant_complaints_count} per_property={props.landlord.tenant_complaints_count_per_property} city_average={props.city_average_stats.average_tenant_complaints_count} />
            <GradeDetailWidget heading="Code Violations" heading_total="Total Code Violations" individual_grade={props.landlord.code_violations_count_grade}
            total={props.landlord.code_violations_count} per_property={props.landlord.code_violations_count_per_property} city_average={props.city_average_stats.average_code_violations_count} />
            <GradeDetailWidget heading="Police Incidents" heading_total="Total Police Incidents" individual_grade={props.landlord.police_incidents_count_grade}
            total={props.landlord.police_incidents_count} per_property={props.landlord.police_incidents_count_per_property} city_average={props.city_average_stats.average_police_incidents_count} />
            <GradeDetailWidget heading="Eviction Filings" heading_total="Total Eviction Filings in Q3 2022" individual_grade={props.landlord.eviction_count_grade}
            total={props.landlord.eviction_count} per_property={props.landlord.eviction_count_per_property} city_average={props.city_average_stats.average_eviction_count} />
            </div>
        </div>
    )
  }

function MapMarkers(props) {
    console.log(props.properties);
    const withoutNullLat = props.properties.filter(v => v.latitude !== null);
    return (
      <div>
        {withoutNullLat.map(({latitude, longitude, id, address, code_violations_count, police_incidents_count, tenant_complaints_count}) => (
            <Marker position={[
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
      </div>

    )

}

function MapWidget(props) {
    return (
        <div className="col-sm">
            <MapContainer center={[42.6526, -73.7762]} zoom={13} scrollWheelZoom={false}>
              <TileLayer
                attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
                url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
              />
              <MapMarkers properties={props.properties}/>
            </MapContainer>
      </div>
    )
 
  }


function PropertiesList(props) {
    return (
        <div>
          {props.properties.map(({address, id}) => (
            <li className="list-group-item" key={id}><a href={"/property/" + id}>{address}</a></li>
          ))}
        </div>
    )
}


function PropertyList(props) {
    return (
        <div className="col-sm">
          <h5>Properties Owned By or Associated with {props.landlord.name}:</h5>
          <ul className="list-group">
          <PropertiesList properties={props.properties} />
          </ul>
        </div>
    )
  }

export default function Landlord () {
    let { id } = useParams();

    const [landlord, setLandlord] = React.useState(null)
    const [aliases, setAliases] = React.useState([])
    const [cityAverageStats, setCityAverageStats] = React.useState({})
    const [properties, setProperties] = React.useState([])

    React.useEffect(() => {
        axios.get("/api/landlords/" + id + "/grades").then((response) => {
          setLandlord(response.data);
        });
      }, []);

    React.useEffect(() => {
        axios.get("/api/landlords/" + id + "/aliases").then((response) => {
          setAliases(response.data);
        });
      }, []);

    React.useEffect(() => {
        axios.get("/api/stats").then((response) => {
          setCityAverageStats(response.data);
        });
      }, []);

    React.useEffect(() => {
        axios.get("/api/landlords/" + id + "/properties").then((response) => {
          setProperties(response.data);
        });
      }, []);

    if (!landlord) return null;

    return (
        <div>
         <div className="container font-typewriter">
          <div className="card">
            <div className="card-body">
              <LandlordTitleRow landlord={landlord} />
              <div className="row card-lines">
              <LandlordDetailColumn landlord={landlord} aliases={aliases}/>
              <GradeDetailColumn landlord={landlord} city_average_stats={cityAverageStats}/>
              </div>
              </div>
            </div>
         </div>
         <br/>

        <div className="container font-typewriter">
          <div className="row text-center">
            <PropertyList properties={properties} landlord={landlord} />
            <MapWidget properties={properties} />
          </div>
        </div>
        </div>
    );
}
