import { BrowserRouter, Route, Routes } from 'react-router-dom'
import Container from 'react-bootstrap/Container';
import Search from './components/Search'
import About from './components/About'
import Faq from './components/Faq'
import Top from './components/Top'
import TakeAction from './components/TakeAction'
import Landlord from './components/Landlord'
import Property from './components/Property'
import Navigationbar from './components/Navigationbar';
import 'bootstrap/dist/css/bootstrap.min.css';
import './App.css';
import ReactGA from 'react-ga';


function App() {

  ReactGA.initialize('G-WVXYXZ9LGV');
  ReactGA.pageview(window.location.pathname + window.location.search);

  return (
    <>
      <BrowserRouter>
        <Navigationbar />
        <Container>
        <Routes>
          <Route path="/" element={ <Search />}/>
          <Route path="/about" element={ <About />}/>
          <Route path="/faq" element={ <Faq />}/>
          <Route path="/top" element={ <Top />}/>
          <Route path="/action" element={ <TakeAction />}/>
          <Route path="/landlord/:id" element={<Landlord />} />
          <Route path="/property/:id" element={<Property />} />
          <Route path="/top" element={ <Top />}/>
        </Routes>
        </Container>
      </BrowserRouter>
    </>
  );
}

export default App;