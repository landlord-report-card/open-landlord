import { useState } from 'react'
import { Link } from "react-router-dom";
import { BrowserRouter, Route, Routes } from 'react-router-dom'
import Search from './components/Search'
import About from './components/About'
import Faq from './components/Faq'
import Landlord from './components/Landlord'
import Property from './components/Property'
import Navigationbar from './components/Navigationbar';
import axios from "axios";
import logo from './logo.svg';
import 'bootstrap/dist/css/bootstrap.min.css';
import './App.css';

function App() {

  return (
    <div>
      <Navigationbar /> 
      <Routes>
        <Route path="/" element={ <Search />}/>
        <Route path="/about" element={ <About />}/>
        <Route path="/faq" element={ <Faq />}/>
        <Route path="/landlord/:id" element={<Landlord />} />
        <Route path="/property/:id" element={<Property />} />
      </Routes>
    </div>
  );
}

export default App;