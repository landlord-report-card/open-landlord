import { useParams } from 'react-router-dom'
import axios from "axios"
import React from "react"
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'
import { Accordion } from "react-bootstrap";
import Alert from 'react-bootstrap/Alert';
import Card from 'react-bootstrap/Card';
import Col from 'react-bootstrap/Col';
import Container from 'react-bootstrap/Container';
import Row from 'react-bootstrap/Row';
import { MapWidget } from './Maps';
import icon from 'leaflet/dist/images/marker-icon.png';
import iconShadow from 'leaflet/dist/images/marker-shadow.png';

let DefaultIcon = L.icon({
    iconUrl: icon,
    shadowUrl: iconShadow
});

L.Marker.prototype.options.icon = DefaultIcon;

const SMALL_LANDLORD = {"maxSize": 2, "sizeDetail": "Small (One or two units owned)", "gradeClassName": "green-grade"}
const MEDIUM_LANDLORD = {"maxSize": 5, "sizeDetail": "Medium (Between 3 and 5 units owned)", "gradeClassName": "yellow-grade"}
const LARGE_LANDLORD = {"maxSize": 15, "sizeDetail": "Large (Between 6 and 15 units owned)", "gradeClassName": "red-grade"}
const XLARGE_LANDLORD = {"maxSize": null, "sizeDetail": "Very Large (More than 15 units owned)", "gradeClassName": "red-grade"}


function getLandlordSizeInfo(size, feature) {
    if (size === null) return "No Registered Rental Properties on File"
    if (size > LARGE_LANDLORD["maxSize"]) return XLARGE_LANDLORD[feature];
    if (size > MEDIUM_LANDLORD["maxSize"]) return LARGE_LANDLORD[feature];
    if (size > SMALL_LANDLORD["maxSize"]) return MEDIUM_LANDLORD[feature];
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
        <>
          {props.unsafeUnfit.map(({address, id}) => (
            <li className="list-group-item" key={id}><a href={"/property/" + id}>{address}</a></li>
          ))}
        </>
    )
}

function UnsafeUnfitWarning(props) {
    const unsafe_unfit_list = props.unsafeUnfit;
    if (unsafe_unfit_list.length <= 0) return null;
    return (
        <Alert variant="danger">
            <Accordion>
              <Accordion.Item className="bg-color-warning" eventKey="0">
                <Accordion.Header><h5 className="warning">Warning about this landlord!</h5></Accordion.Header>
                <Accordion.Body>
                  <span className="font-typewriter">
                  <p>This landlord has had one or more properties deemed unsafe or unfit for habitability by the City of Albany within the past year.</p>
                  <p>Call the City of Albany Code Department to determine if the unit you're looking at has been deemed unsafe or unfit. <a target="_blank" href="https://www.albanyny.gov/2038/Code-Enforcement#:~:text=Unsafe%2FUnfit%20Orders,gas%2C%20electricity%2C%20or%20heat%20utilities">Learn More</a></p>
                  <strong>Impacted Properties:</strong>
                  <UnsafeUnfitProperties unsafeUnfit={unsafe_unfit_list} />
                  </span>
                </Accordion.Body>
              </Accordion.Item>
            </Accordion>
        </Alert>
        )
}

function hideGrade(props) {
    if (
        props.landlord.unit_count === null && 
        props.landlord.code_violations_count == 0 && 
        props.landlord.evictions_count == 0
    ) {
        return true
    }
    return false
}


function GradeTitleRow(props) {
    if (hideGrade(props)) {
        return (<span className="landlord-name font-handwritten">N/A</span>)
    }
    return (
        <span className={getColorClassName(props.landlord.grade) + " font-handwritten grade"}>
            {props.landlord.grade}
        </span>
    )
}


function LandlordTitleRow(props) {
    return (
      <Row className="title-row text-center">
        <Col sm={7}>
          <span className="title-label">Landlord</span><br />
          <span className="landlord-name font-handwritten">{props.landlord.name}</span>
        </Col>
        <Col sm>
          <span className="title-label">Grade</span><br />
          <GradeTitleRow landlord={props.landlord}/>
        </Col>        
      </Row>
    )
  }


function AliasesBlock(props) {
    if (!props.aliases || props.aliases.length <= 1) {
        return null;
    }
    
    const commaSep = props.aliases.map(item => item.name).join(', ');

    return (
        <>
            <span className="landlord-attribute">Also Known As: </span> 
            <span className="font-handwritten">{commaSep}</span>
        </>
    )

}

function LandlordDetailColumn(props) {
    return (
        <Col sm className="landlord-info">
          <span className="landlord-attribute">Address: </span>
          <span className="font-handwritten">{props.landlord.address}</span><br/>
          <span className="landlord-attribute">Landlord Size: </span> 
          <span className={getLandlordSizeClassName(props.landlord.unit_count) + " font-handwritten"}>{getLandlordSize(props.landlord.unit_count)}</span><br/>
          {props.landlord.unit_count != 0 &&
            <><span className="landlord-attribute">Total Rental Unit Count: </span>
            <span className="font-handwritten">{props.landlord.unit_count}</span><br/></>
          }
          <AliasesBlock aliases={props.aliases}/>
        </Col>
    )
  }


function GradeDetailWidget(props) {
    return (
        <Accordion>
          <Accordion.Item eventKey="0">
            <Accordion.Header>{props.heading}<span className={getColorClassName(props.individual_grade) + " font-handwritten grade-value"}>{props.individual_grade}</span></Accordion.Header>
            <Accordion.Body>
              <p className="mb-0">{props.heading_total}: {props.total} </p>
              <p className="mb-0">{props.heading} Per Unit: {Math.round(props.per_unit * 100) / 100} </p>
              <p className="mb-0">City Average Per Unit: {Math.round(props.city_average * 1000) / 1000} </p>
            </Accordion.Body>
          </Accordion.Item>
        </Accordion>
    )
}

function GradeDetailColumn(props) {
    if (hideGrade(props)) {
        return null
    }
    return (
        <Col sm={5} className="landlord-grades">
            <GradeDetailWidget heading="Code Violations" heading_total="Code Violations (Past Year)" individual_grade={props.landlord.code_violations_grade}
            total={props.landlord.code_violations_count} per_unit={props.landlord.code_violations_per_unit} city_average={props.city_average_stats.mean_code_violations_per_unit} />
            <GradeDetailWidget heading="Eviction Filings" heading_total="Eviction Filings (Past Year)" individual_grade={props.landlord.evictions_grade}
            total={props.landlord.evictions_count} per_unit={props.landlord.evictions_per_unit} city_average={props.city_average_stats.mean_evictions_per_unit} />
        </Col>
    )
  }


function PropertiesList(props) {
    return (
        <>
          {props.properties.map(({address, id}) => (
            <li className="list-group-item" key={id}><a href={"/property/" + id}>{address}</a></li>
          ))}
        </>
    )
}


function PropertyList(props) {
    return (
        <Col sm>
          <h5>Properties Owned By or Associated with {props.landlord.name}:</h5>
          <ul className="list-group">
          <PropertiesList properties={props.properties} />
          </ul>
        </Col>
    )
  }

export default function Landlord () {
    let { id } = useParams();

    const [landlord, setLandlord] = React.useState(null)
    const [aliases, setAliases] = React.useState([])
    const [cityAverageStats, setCityAverageStats] = React.useState({})
    const [properties, setProperties] = React.useState([])
    const [unsafeUnfit, setUnsafeUnfit] = React.useState([])
    const [evictions, setEvictions] = React.useState([])

    React.useEffect(() => {
        axios.get("/api/landlords/" + id + "/grades").then((response) => {
          setLandlord(response.data);
          document.title = response.data.name;
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

    React.useEffect(() => {
        axios.get("/api/landlords/" + id + "/evictions").then((response) => {
          setEvictions(response.data);
        });
      }, []);

    if (!landlord) return null;

    return (
        <>
             {<UnsafeUnfitWarning unsafeUnfit={unsafeUnfit} /> }
             <Container className="container font-typewriter">
              <Card className="card">
                <Card.Body className="card-body">
                  <LandlordTitleRow landlord={landlord} />
                  <span className="row card-lines">
                      <LandlordDetailColumn landlord={landlord} aliases={aliases}/>
                      { <GradeDetailColumn landlord={landlord} city_average_stats={cityAverageStats}/> }
                  </span>
                </Card.Body>
              </Card>
             </Container>
             <br/>

            <Container className="container font-typewriter">
              <Row className="row text-center">
                <PropertyList properties={properties} landlord={landlord} />
                <Col sm>
                    <MapWidget properties={properties} />
                </Col>
              </Row>
            </Container>
        </>
    );
}
