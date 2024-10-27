// Proceed.js
import React from 'react';
import { useNavigate } from 'react-router-dom';
import './Proceed.css';

const Proceed = () => {
  const navigate = useNavigate();

  const handleClick = () => {
    navigate(`/analysis`);
  };

  return (
    <button className="proceed-button" onClick={handleClick}>
      Proceed
    </button>
  );
};

export default Proceed;