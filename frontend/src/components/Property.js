import { useParams } from 'react-router-dom'
import axios from "axios"
import React from "react"
import Card from 'react-bootstrap/Card';
import Col from 'react-bootstrap/Col';
import Container from 'react-bootstrap/Container';
import Row from 'react-bootstrap/Row';
import { MapWidget } from './Maps';


function PropertyInfo(props) {
    return (
        <>
          <span>Current Use: </span> &nbsp;{props.property.current_use}<br />
          <span>Business Entity Type: </span>{props.property.business_entity_type}<br />
          <span>Owner Occupied: </span>{props.property.owner_occupied}<br />
          <span>Parcel ID: </span>{props.property.parcel_id}<br />
          <span>Property Type: </span>{props.property.property_type}<br />
          <span>Tenant Complaints: </span>{props.property.tenant_complaints}<br />
          <span>Code Violations Count: </span>{props.property.code_violations_count}<br />
          <span>Police Incidents Count: </span>{props.property.police_incidents_count}<br />
        </>
    )
  }


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
          <Container className="container font-typewriter">
            <Row>
              <Col sm>
                <Card id="property-card">
                  <Card.Body>
                    <Row className="title-row text-center">
                      <Col sm>
                        <span className="property-label">Property Address</span><br />
                        <span className="property-address font-handwritten">{property.address}</span>
                      </Col>
                    </Row>
                    <div className="card-lines property-info">
                      <PropertyInfo property={property}/>
                    </div>
                  </Card.Body>
                </Card>
              </Col>
              <Col sm>
                 <MapWidget properties={[property]} />
              </Col>
            </Row>
          </Container>
    );
}


