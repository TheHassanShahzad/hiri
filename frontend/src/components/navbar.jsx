import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import '../styles/navbar.css';

function Navbar() {
  const [isOpen, setIsOpen] = useState(false);

  const toggleMenu = () => {
    setIsOpen(!isOpen);
  };

  return (
    <nav className="navbar">
      <div className="navbar-brand">
        <Link to="/" className="navbar-logo">
          Hiri
        </Link>
        <button className={`hamburger ${isOpen ? 'active' : ''}`} onClick={toggleMenu}>
          <span></span>
          <span></span>
          <span></span>
        </button>
      </div>

      <ul className={`navbar-menu ${isOpen ? 'active' : ''}`}>
        <li>
          <Link to="/" className="navbar-link" onClick={() => setIsOpen(false)}>
            Home
          </Link>
        </li>
        <li>
          <Link to="/live-stream" className="navbar-link" onClick={() => setIsOpen(false)}>
            Live Stream
          </Link>
        </li>
      </ul>
    </nav>
  );
}

export default Navbar;