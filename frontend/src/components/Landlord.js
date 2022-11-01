import { useParams } from 'react-router-dom'
import axios from "axios"
import React from "react"


export default function Landlord () {
    let { id } = useParams();

    const [landlord, setLandlord] = React.useState(null)

    React.useEffect(() => {
        axios.get("/api/landlords/" + id).then((response) => {
          setLandlord(response.data);
        });
      }, []);

    if (!landlord) return null;

    return (
        <div>
          <h1>{landlord.name}</h1>
          <p>{landlord.id}</p>
        </div>
    );
}
