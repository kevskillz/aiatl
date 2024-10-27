import React, { useState, useEffect } from 'react';
import './Breakdown.css';
import SeaLevelMap from '../mapping/SeaLevelMap';

const Breakdown = ({ coordinates }) => {
  const [geminiResponse, setGeminiResponse] = useState("");
  const [satelliteVideo, setSatelliteVideo] = useState("");
  const [insuranceCost, setInsuranceCost] = useState("");
  const [insurancePercentDiff, setInsurancePercentDiff] = useState("");
  const [sources, setSources] = useState(null);

  // Function to fetch data from the backend API
  useEffect(() => {
    const fetchAnalysisData = async () => {
      try {
        console.log("Lat: " + coordinates.lat);
        console.log("Lng: " + coordinates.lng);
        const response = await fetch('http://127.0.0.1:5000/analysis', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            lat: coordinates.lat || 25.7617,
            lng: coordinates.lng || -80.1918,
          }),
        });

        if (response.ok) {
          const data = await response.json();
          setGeminiResponse(data.geminiResponse);
          setSatelliteVideo(data.satelliteVideo);
          setInsuranceCost(data["insurance cost"]);
          setInsurancePercentDiff(data["insurance percent diff"]);
          setSources(data["sources"]);
          console.log(data['sources']);
        } else {
          console.error("Failed to fetch data");
        }
      } catch (error) {
        console.error("Error fetching data:", error);
      }
    };

    fetchAnalysisData();
  }, [coordinates]);

  // Determine the color class based on the insurance percent difference
  const getPercentDiffClass = (percentDiff) => {
    return percentDiff > 0 ? 'percent-diff-red' : 'percent-diff-green';
  };

  return (
    <div className='breakdown-container'>
      <div className="top-container">
        <div className="breakdown-item gemini-response">
          <h3>Summary & Predictions</h3>
          <p
            dangerouslySetInnerHTML={{
              __html: geminiResponse === ""
                ? "Loading..."
                :
                geminiResponse.replace(/\*\*(.*?)\*\*/g, '<strong><u>$1</u></strong>') // Bold
                  .replace(/__(.*?)__/g, '<u>$1</u>') // Underline
            }}
          />

        </div>

        <div className="breakdown-item gif-container">
          <h3>Hurricane Image</h3>
          {satelliteVideo ? (
            <img
              src={satelliteVideo}
              alt="Hurricane Satellite GIF"
              className="hurricane-gif"
            />
          ) : (
            <p>Retrieving Satellite Data...</p>
          )}
        </div>
      </div>

      <div className="bottom-row">
        <div className="breakdown-item">
          <h3>Recent News Summary</h3>
        </div>
        <div className="breakdown-item">
          <h3>Insurance Information</h3>
          {insuranceCost !== "" ? (
            <div className="insurance-info">
              <p className="insurance-label">Average Annual Cost:</p>
              <p className="insurance-value bold-large">${insuranceCost.toFixed(2)}</p>
              <p className="insurance-label">% Difference National Average:</p>
              <p className={`insurance-value bold-large ${getPercentDiffClass(insurancePercentDiff)}`}>
                {insurancePercentDiff > 0 ? '+' : ''}{insurancePercentDiff.toFixed(2)}%
              </p>
            </div>
          ) : (
            <p>Loading Insurance Data...</p>
          )}
        </div>
        <div className="breakdown-item">
          {/* <h3>Sea Level</h3> */}
          <SeaLevelMap latitude={coordinates.lat} longitude={coordinates.lng} />
        </div>
      </div>
    </div>
  );
};

export default Breakdown;