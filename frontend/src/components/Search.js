export default function Search () {
    return (
    <div className="main">
    <h1>Find your landlord</h1>
        <p className="lead">Type in your address or landlord name to find your landlord!</p>

        <form className="d-flex ui-autocomplete-input" role="textbox" method="post" autoComplete="off" aria-autocomplete="list" aria-haspopup="true">
            <input className="form-control me-2" id="tags" name="search" type="text"/>
            <button className="btn btn-outline-danger" type="submit">Search</button>
        </form>
    <br />

    <table className="table">
      <thead>
        <tr>
          <th scope="col">Property Address</th>
          <th scope="col">Owner/Landlord Name</th>
        </tr>
      </thead>
      <tbody>
      </tbody>
    </table>
    </div>
    );
}
