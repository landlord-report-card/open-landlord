import { useParams } from 'react-router-dom'
import axios from "axios"
import React from "react"
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'
import { Accordion } from "react-bootstrap";
import Alert from 'react-bootstrap/Alert';
import { MapContainer, TileLayer, Popup, Marker, useMap } from 'react-leaflet'

import icon from 'leaflet/dist/images/marker-icon.png';
import iconShadow from 'leaflet/dist/images/marker-shadow.png';

let DefaultIcon = L.icon({
    iconUrl: icon,
    shadowUrl: iconShadow
});

L.Marker.prototype.options.icon = DefaultIcon;

const SMALL_LANDLORD = {"sizeDetail": "Small (One property owned)", "gradeClassName": "green-grade"}
const MEDIUM_LANDLORD = {"sizeDetail": "Medium (Between 1 and 4 properties owned)", "gradeClassName": "yellow-grade"}
const LARGE_LANDLORD = {"sizeDetail": "Large (Between 5 and 10 properties owned)", "gradeClassName": "red-grade"}
const XLARGE_LANDLORD = {"sizeDetail": "Very Large (More than 10 properties owned)", "gradeClassName": "red-grade"}


function getLandlordSizeInfo(size, feature) {
    if (size > 10) return XLARGE_LANDLORD[feature];
    if (size > 4) return LARGE_LANDLORD[feature];
    if (size > 1) return MEDIUM_LANDLORD[feature];
    return SMALL_LANDLORD[feature];
}

function getLandlordSizeClassName(size) {
    return getLandlordSizeInfo(size, "gradeClassName")
}

function getLandlordSize(size) {
    return getLandlordSizeInfo(size, "sizeDetail")
}


function getColorClassName(grade) {
    const baseGrade = grade.charAt(0)
    switch(baseGrade) {
        case "C":
        case "D":
            return "yellow-grade";
        case "F":
            return "red-grade";
        default:
            return "green-grade";
    } 
}


function UnsafeUnfitProperties(props) {
    return (
        <div>
          {props.unsafeUnfit.map(({address, id}) => (
            <li className="list-group-item" key={id}><a href={"/property/" + id}>{address}</a></li>
          ))}
        </div>
    )
}

function UnsafeUnfitWarning(props) {
    const unsafe_unfit_list = props.unsafeUnfit;
    if (unsafe_unfit_list.length <= 0) return null;
    return (
    <div>
    <Alert variant="danger">
    <Accordion>
      <Accordion.Item eventKey="0">
        <Accordion.Header><h5 className="warning">Warning about this landlord!</h5></Accordion.Header>
        <Accordion.Body className="alert-danger">
          <p>This landlord has had one or more properties deemed unsafe or unfit for habitability by the City of Albany within the past year.</p>
          <p>Call the City of Albany Code Department to determine if the unit you're looking at has been deemed unsafe or unfit. <a target="_blank" href="https://www.albanyny.gov/2038/Code-Enforcement#:~:text=Unsafe%2FUnfit%20Orders,gas%2C%20electricity%2C%20or%20heat%20utilities">Learn More</a></p>
          <strong>Impacted Properties:</strong>
          <UnsafeUnfitProperties unsafeUnfit={unsafe_unfit_list} />
        </Accordion.Body>
      </Accordion.Item>
    </Accordion>
    </Alert>
    </div>
        )
}
function LandlordTitleRow(props) {
    return (
      <div className="row title-row text-center">
        <div className="col-sm-7">
          <span className="title-label">Landlord</span><br />
          <span className="landlord-name font-handwritten">{props.landlord.name}</span>
        </div>
        <div className="col-sm">
          <span className="title-label">Grade</span><br />
          <span className={getColorClassName(props.landlord.grade) + " font-handwritten grade"}>{props.landlord.grade}</span>
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
          <span className="landlord-attribute">Landlord Size: </span> 
          <span className={getLandlordSizeClassName(props.landlord.property_count) + " font-handwritten"}>{getLandlordSize(props.landlord.property_count)}</span><br/>
          <AliasesBlock aliases={props.aliases}/>
        </div>
    )
  }


function GradeDetailWidget(props) {
    return (
        <div>
        <Accordion>
          <Accordion.Item eventKey="0">
            <Accordion.Header>{props.heading}<span className={getColorClassName(props.individual_grade) + " font-handwritten grade-value"}>{props.individual_grade}</span></Accordion.Header>
            <Accordion.Body>
              <p className="mb-0">{props.heading_total}: {props.total} </p>
              <p className="mb-0">{props.heading} Per Property: {Math.round(props.per_property * 100) / 100} </p>
              <p className="mb-0">City Average: {Math.round(props.city_average * 100) / 100} </p>
            </Accordion.Body>
          </Accordion.Item>
        </Accordion>
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
    const withoutNullLat = props.properties.filter(v => v.latitude !== null);
    return (
      <div>
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
    const [unsafeUnfit, setUnsafeUnfit] = React.useState([])

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

    React.useEffect(() => {
        axios.get("/api/landlords/" + id + "/unsafe_unfit").then((response) => {
          setUnsafeUnfit(response.data);
        });
      }, []);

    if (!landlord) return null;

    return (
        <div>
         <UnsafeUnfitWarning unsafeUnfit={unsafeUnfit} />
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
