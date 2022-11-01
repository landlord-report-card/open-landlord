import { useParams } from 'react-router-dom'

export default function Landlord () {
    let { id } = useParams();

    return (
        <div className="main">
            Landlord ID: {id}
        </div>
    );
}
