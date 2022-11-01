import { useParams } from 'react-router-dom'
import axios from "axios"
import React from "react"

export default function Property () {
    let { id } = useParams();

    const [property, setProperty] = React.useState(null)

    React.useEffect(() => {
        axios.get("/api/properties/" + id).then((response) => {
          setProperty(response.data);
        });
      }, []);

    if (!property) return null;

    return (
        <div className="main">
          <div className="container font-typewriter">
            <div className="row">
              <div className="col-sm">
                <div className="card" id="property-card">
                  <div className="card-body">
                    <div className="row title-row text-center">
                      <div className="col-sm">
                        <span className="property-label">Property Address</span><br />
                        <span className="property-address font-handwritten">{property.address}</span>
                      </div>
                    </div>
                    <div className="card-lines">
                      <div className="property-info">
                      <span>Current Use: </span> &nbsp;{property.current_use}<br />
                      <span>Business Entity Type: </span>{property.business_entity_type}<br />
                      <span>Owner Occupied: </span>{property.owner_occupied}<br />
                      <span>Parcel ID: </span>{property.parcel_id}<br />
                      <span>Property Type: </span>{property.property_type}<br />
                      <span>Tenant Complaints: </span>{property.tenant_complaints}<br />
                      <span>Code Violations Count: </span>{property.code_violations_count}<br />
                      <span>Police Incidents Count: </span>{property.police_incidents_count}<br />
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
    );
}


