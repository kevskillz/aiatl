import React, { useEffect, useState } from 'react';
import { GoogleMap, Circle, InfoWindow } from '@react-google-maps/api';
import Breakdown from '../breakdown/Breakdown';
import './Analysis.css'; // Import your CSS file

const Analysis = ({ coordinates, address }) => {
  const [hurricanes, setHurricanes] = useState({});
  const [selectedHurricane, setSelectedHurricane] = useState(null);

  useEffect(() => {
    const fetchHurricaneData = async () => {
      try {
        const response = await fetch('http://127.0.0.1:5000/find_hurricanes', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            lat: coordinates.lat || 27,
            lng: coordinates.lng || -80,
          }),
        });

        

        if (!response.ok) {
          throw new Error('Network response was not ok');
        }

        // console.log(response2)

        const data = await response.json();
        setHurricanes(data);
      } catch (error) {
        console.error('Error fetching hurricane data:', error);
      }
    };

    fetchHurricaneData();
  }, [coordinates]);

  const mapContainerStyle = {
    width: '30vw',
    height: '30vw',
  };

  const center = {
    lat: coordinates.lat || 27,
    lng: coordinates.lng || -80,
  };

  return (
    <div className="analysis-container">
      <div className="outer-flex">
        <h2 className="map-header">Hurricane Paths in Your Area</h2>

        <div className="map-container">
          <GoogleMap
            mapContainerStyle={mapContainerStyle}
            center={center}
            zoom={8}
          >
            {Object.entries(hurricanes).map(([id, data]) =>
              data.points.map((point, index) => (
                <Circle
                  key={`${id}-${index}`}
                  center={{ lat: point.lat, lng: point.lng }}
                  radius={point.r * 100}
                  options={{
                    fillColor: data.color,
                    strokeColor: "#61dafb",
                    fillOpacity: 0.7,
                    strokeWeight: 1,
                  }}
                  onClick={() => setSelectedHurricane({ name: data.name, speed: point.speed, position: { lat: point.lat, lng: point.lng } })}
                />
              ))
            )}
            {/* Display InfoWindow if a hurricane is selected */}
            {selectedHurricane && (
              <InfoWindow
                position={selectedHurricane.position}
                onCloseClick={() => setSelectedHurricane(null)} // Clear selected hurricane when InfoWindow is closed
              >
                <div className="info-window"> {/* Apply the new class here */}
                  <h3>{selectedHurricane.name}</h3>
                  <p>Speed: {Math.round(selectedHurricane.speed * 115.078) / 100} mph</p>
                </div>
              </InfoWindow>
            )}
          </GoogleMap>
        </div>
      </div>
      <div className="breakdown-container">
        <Breakdown coordinates={coordinates} />
      </div>
    </div>
  );
};

export default Analysis;