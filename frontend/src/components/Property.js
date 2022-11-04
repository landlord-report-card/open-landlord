import { useParams } from 'react-router-dom'
import axios from "axios"
import React from "react"
import Card from 'react-bootstrap/Card';
import Col from 'react-bootstrap/Col';
import Container from 'react-bootstrap/Container';
import Row from 'react-bootstrap/Row';
import { Accordion } from "react-bootstrap";
import Alert from 'react-bootstrap/Alert';
import { MapWidget } from './Maps';



function PropertyUnsafeUnfitWarning(props) {
    if (props.property.unsafe_unfit_count <= 0) return null;
    return (
        <Alert variant="danger">
            <Accordion>
              <Accordion.Item className="bg-color-warning" eventKey="0">
                <Accordion.Header><h5 className="warning">Warning about this property!</h5></Accordion.Header>
                <Accordion.Body className="alert-danger">
                  <span className="font-typewriter">
                  <p>This property has been deemed unsafe or unfit for habitability by the City of Albany within the past year.</p>
                  <p>Call the City of Albany Code Department to determine if the unit you're looking at has been deemed unsafe or unfit. <a target="_blank" href="https://www.albanyny.gov/2038/Code-Enforcement#:~:text=Unsafe%2FUnfit%20Orders,gas%2C%20electricity%2C%20or%20heat%20utilities">Learn More</a></p>
                  </span>
                </Accordion.Body>
              </Accordion.Item>
            </Accordion>
        </Alert>
        )
}

function PropertyInfo(props) {
    return (
        <>
          <span>Owner: </span> &nbsp;<a href={"/landlord/" + props.property.owner_id}>{props.property.owner.name}</a><br />
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
          const propertyResponse = response.data;
          document.title = propertyResponse.address;
          axios.get("/api/landlords/" + response.data.owner_id).then((response2) => {
            propertyResponse["owner"] = response2.data
            setProperty(propertyResponse);
          });
        });
      }, []);


    if (!property) return null;


    return (
        <>
          <PropertyUnsafeUnfitWarning property={property}/>
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
        </>
    );
}


