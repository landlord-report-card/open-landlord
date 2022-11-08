import { useState } from 'react'
import { Link } from "react-router-dom";
import { BrowserRouter, Route, Routes } from 'react-router-dom'
import Container from 'react-bootstrap/Container';
import Search from './components/Search'
import About from './components/About'
import Faq from './components/Faq'
import Top from './components/Top'
import Landlord from './components/Landlord'
import Property from './components/Property'
import Navigationbar from './components/Navigationbar';
import axios from "axios";
import logo from './logo.svg';
import 'bootstrap/dist/css/bootstrap.min.css';
import './App.css';

function App() {

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
          <Route path="/landlord/:id" element={<Landlord />} />
          <Route path="/property/:id" element={<Property />} />
        </Routes>
        </Container>
      </BrowserRouter>
    </>
  );
}

export default App;