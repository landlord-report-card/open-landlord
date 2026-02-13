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
    if (props.property.unsafe_unfit_case_number === null) return null;
    return (
        <Alert variant="danger">
            <Accordion>
              <Accordion.Item className="bg-color-warning" eventKey="0">
                <Accordion.Header><h5 className="warning">Warning about this property!</h5></Accordion.Header>
                <Accordion.Body className="alert-danger">
                  <span className="font-typewriter">
                  <p>This property has been deemed unsafe or unfit for habitability by the City of Albany within the past year.</p>
                  <p>Call the City of Albany Code Department to determine if the unit you're looking at has been deemed unsafe or unfit. <a target="_blank" rel="noreferrer" href="https://www.albanyny.gov/2038/Code-Enforcement#:~:text=Unsafe%2FUnfit%20Orders,gas%2C%20electricity%2C%20or%20heat%20utilities">Learn More</a></p>
                  <p>Violation Number: <a target="_blank" rel="noreferrer" href={"https://albanyny-energovpub.tylerhost.net/Apps/SelfService#/code/" + props.property.unsafe_unfit_case_id}>{props.property.unsafe_unfit_case_number} </a></p>
                  </span>
                </Accordion.Body>
              </Accordion.Item>
            </Accordion>
        </Alert>
        )
}


function PropertyNoROPWarning(props) {
    if (props.property.has_rop) return null;
    return (
        <Alert variant="danger">
            <Accordion>
              <Accordion.Item className="bg-color-warning" eventKey="0">
                <Accordion.Header><h5 className="warning">Are you renting this property?</h5></Accordion.Header>
                <Accordion.Body className="alert-danger">
                  <span className="font-typewriter">
                  <p>This property does not appear to be registered as a rental property with the City of Albany as it does not have an active ROP/Residential Occupancy Permit on file.</p>
                  <p>If it is currently being rented, check Albany's <a target="_blank" rel="noreferrer" href="https://albanyny-energovpub.tylerhost.net/Apps/SelfService#/home">Self Service Portal</a> or call the City of Albany Code Department to determine if the unit you're looking at has an ROP and is safe to be rented. <a target="_blank" rel="noreferrer" href="https://www.albanyny.gov/2037/Residential-Occupancy-Permits">Learn More</a></p>
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
          <span>Owner: </span> &nbsp;<a href={"/landlord/" + props.property.group_id}>{props.property.owner.name}</a><br />
          <span>Has Active Residential Occupancy Permit (ROP): </span>
          {props.property.has_rop ? 'Yes' : 'No'}
          <br />

          {props.property.rop_case_id && (
            <>
              <span>ROP Case: </span>
              <a
                target="_blank"
                rel="noreferrer"
                href={"https://albanyny-energovpub.tylerhost.net/Apps/SelfService#/code/" + props.property.rop_case_id}
              >
                {props.property.rop_case_number}
              </a>
              <br />
            </>
          )}

          {props.property.rop_issue_date && (
            <>
              <span>ROP Issue Date: </span>
              {new Date(props.property.rop_issue_date).toLocaleDateString()}
              <br />
            </>
          )}

          {props.property.expired_rop && (
            <>
              <span>ROP Status: </span>
              <span className="text-danger">
                Expired
              </span>
              <br />
            </>
          )}
          <span>Number of Rental Units: </span>{props.property.unit_count}<br />
          <span>Parcel ID: </span>{props.property.parcel_id}<br />
        </>
    )
  }

function PropertyViolationsTable({ violations }) {
  if (!violations.length) return null;

  return (
    <div className="mt-3"> {/* adds space above the table */}
        <table className="table table-sm table-bordered table-hover">
        <thead className="table-light">
          <tr>
            <th>Case</th>
            <th>Code</th>
            <th>Description</th>
            <th>Status</th>
            <th>Issued</th>
          </tr>
        </thead>
        <tbody>
          {violations.map(v => (
            <tr key={v.code_violation_id}>
              <td>
                <a target="_blank" rel="noreferrer" href={`https://albanyny-energovpub.tylerhost.net/Apps/SelfService#/code/${v.case_id}`}>{v.case_number}</a>
              </td>
              <td>{v.code_number}</td>
              <td>{v.code_description}</td>
              <td className={v.status === "Open" ? "text-danger" : ""}>{v.status}</td>
              <td>{v.issue_date && new Date(v.issue_date).toLocaleDateString()}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}


export default function Property () {
    let { id } = useParams();

    const [property, setProperty] = React.useState(null)
    const [violations, setViolations] = React.useState([])

    React.useEffect(() => {
      axios.get("/api/properties/" + id).then((response) => {
        const propertyResponse = response.data;
        document.title = propertyResponse.address;

        axios.get("/api/landlords/" + response.data.group_id).then((response2) => {
          propertyResponse["owner"] = response2.data;
          setProperty(propertyResponse);
        });

        axios.get("/api/properties/" + id + "/violations").then((v) => {
          // Filter out "* Initial Notice *" and "** Final Notice **"
          const filtered = v.data.filter(violation =>
            violation.code_number !== "* Initial Notice *" &&
            violation.code_number !== "** Final Notice **"
          );
          setViolations(filtered);
        });
      });
    }, [id]);

    if (!property) return null;


return (
    <>
      <PropertyUnsafeUnfitWarning property={property}/>
      <PropertyNoROPWarning property={property}/>
      <Container className="container font-typewriter">
        <Row>
          {/* Property info on the left */}
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

          {/* Map + Code Violations on the right */}
          <Col sm>
            <MapWidget properties={[property]} />
            
            {violations.length > 0 && (
              <div className="mt-3">
                <Card>
                  <Card.Body>
                    <span className="property-label">Code Violations (Past Year)</span>
                    <PropertyViolationsTable violations={violations} />
                  </Card.Body>
                </Card>
              </div>
            )}
          </Col>
        </Row>
      </Container>
    </>
  );
}


