import './App.css';
import SearchAddress from './mapping/Mapping';
import Proceed from './analysis/Proceed';
import Analysis from './analysis/Analysis';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import React, { useState } from 'react';

function App() {
  const [coordinates, setCoordinates] = useState({ lat: null, lng: null });
  const [address, setAddress] = useState("");
  const [zipCode, setZipCode] = useState("");

  const [coordRecent, setRecent] = useState(false); // coordinates: True -> coordinates  else Address

  return (
    <Router>
      <div className='Main'>
        <Routes>
          <Route path="/" element={
            <div>
              <div className='main-upper'>
                <SearchAddress setCoordinates={setCoordinates} setAddressParent={setAddress} setRecent={setRecent} setZipCode={setZipCode}/>
              </div>
              
              <div className='main-lower'>
                {!coordRecent ? (
                  <div className='data'>
                    <p className='data-txt'>Selected Address: {address}</p>
                    <p className='data-txt'>Zip Code: {zipCode}</p>
                  </div>
                ) : (
                  <div className='data'>
                    <p className='data-txt'>Selected Latitude: {Math.round(coordinates.lat * 100) / 100}</p>
                    <p className='data-txt'>Selected Longitude: {Math.round(coordinates.lng * 100) / 100}</p>
                  </div>)
                
                }
                <Proceed className='button' /> {/* Pass coordinates here */}
              </div>
            </div>
          } />
          
          <Route path="/analysis" element={<Analysis coordinates={coordinates} address={address} />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;