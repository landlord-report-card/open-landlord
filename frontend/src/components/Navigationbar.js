import { Nav, Navbar, NavLink } from "react-bootstrap";
import { Link } from "react-router-dom";


const Navigationbar = () => {
	return (
	    <nav className="navbar navbar-expand-md navbar-light bg-white mb-1s">
	      <a className="navbar-brand d-lg-none d-md-none " href="/">
	        <img src="/static/img/logo.png" alt="Albany Landlord Report Card" height="100" />
	      </a>
	      <button className="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarCollapse" aria-controls="navbarCollapse" aria-expanded="false" aria-label="Toggle navigation">
	        <span className="navbar-toggler-icon"></span>
	      </button>
	      <div className="collapse navbar-collapse" id="navbarCollapse">
	        <ul className="navbar-nav mx-auto align-items-center">
	         <li className="nav-item">
	          <a className="nav-link" href="/">Search</a>
	        </li>
	        <li className="nav-item">
	          <a className="nav-link" href="/about/">About</a>
	        </li>
	        <a className="navbar-brand  d-none d-lg-block d-md-block" href="/">
	          <img src="/static/img/logo.png" alt="Albany Landlord Report Card" height="100" />
	        </a>
	        <li className="nav-item">
	          <a className="nav-link" href="/faq/">FAQ</a>
	        </li>
	        <li className="nav-item">
	          <a className="nav-link" target="_blank" href="https://linktr.ee/utalbany">Resources</a>
	        </li>
	      </ul>
	    </div>
	  </nav>
	);
}

export default Navigationbar;