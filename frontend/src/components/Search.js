import {
  Table,
  Header,
  HeaderRow,
  HeaderCell,
  Body,
  Row,
  Cell,
} from '@table-library/react-table-library/table';
import React from 'react';
import axios from "axios"



export default function Search() {
    React.useEffect(() => {
        document.title = 'Albany Landlord Report Card';
    });

    const [query, setQuery] = React.useState("") 
    const [results, setResults] = React.useState([])
 

    React.useEffect(() => {
        if (query.length === 0) {
            return
        }
        axios.get("/api/search?query=" + query).then((response) => {
          const addressResults = response.data
          const landlordIds = addressResults.map(a => a.group_id);
          axios.post('/api/landlords/', {"ids": landlordIds}).then((response) => {
              const landlords = response.data
              const mergedData = addressResults;
              mergedData.forEach(function (element) {
                element.landlord = landlords[element.group_id];
              });
              setResults(mergedData)
          });

      });
    }, [query]);

    const data = {
        nodes: results
    };
   
    return (
    <div className="main">
    <h1>Find your landlord</h1>
    <p className="lead">Type in your address or landlord name to find your landlord!</p>
    <input className="form-control me-2" id="search" type="text" autoComplete="off" onChange={event => setQuery(event.target.value)} />
    <br />
    <Table data={data}>
      {(tableList) => (
        <>
            <Header>
              <HeaderRow>
                <HeaderCell>Property Address</HeaderCell>
                <HeaderCell>Owner/Landlord Name</HeaderCell>
                <HeaderCell>Also Known As</HeaderCell>
              </HeaderRow>
            </Header>

              <Body>
                {tableList.map((item) => (
                  <Row key={item.id} item={item}>
                    <Cell>{item.address}</Cell>
                    <Cell><a href={"/landlord/" + item.group_id}>{item.landlord.name}</a></Cell>
                    <Cell>{item.landlord.aliases}</Cell>
                  </Row>
                ))}
              </Body>
        </>
      )}
    </Table>
    </div>
  );

}