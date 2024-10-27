import React, { useEffect, useState } from 'react';
import './TopRow.css';

const TopRow = ({ coordinates }) => {
    const [geminiResponse, setGeminiResponse] = useState("");
    const [satelliteVideo, setSatelliteVideo] = useState("");

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
                } else {
                    console.error("Failed to fetch data");
                }
            } catch (error) {
                console.error("Error fetching data:", error);
            }
        };

        fetchAnalysisData();
    }, [coordinates]);

    return (
        <div className="top-container">
            <div className="breakdown-item scrollable">
                <h3>Gemini Response</h3>
                <p>{geminiResponse === "" ? "Loading..." : geminiResponse}</p>
            </div>

            <div className="breakdown-item">
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
    );
};

export default TopRow;