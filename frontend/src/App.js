import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Link, Navigate } from 'react-router-dom';
import Register from './components/Register';
import Login from './components/Login';
import Form from './components/Form'; 
import Upload from './components/Upload';
import Download from './components/Download';
import './App.css';

const App = () => {
  const [user, setUser] = useState(null);
  const [formFilled, setFormFilled] = useState(false);
  
  const handleLogout = () => {
    setUser(null);
    setFormFilled(false);
  };

  return (
    <Router>
      <div>
        <div className="navbar">
          {user ? (
            <>
              <span className="navbar-link">Welcome, {user}</span>
              <Link to="/logout" className="navbar-link" onClick={handleLogout}>Logout</Link>
            </>
          ) : (
            <>
              <Link to="/register" className="navbar-link">Register</Link>
              <Link to="/login" className="navbar-link">Login</Link>
            </>
          )}
          <Link to="/form" className="navbar-link">Form</Link>
          <Link to="/upload" className="navbar-link">Upload</Link>
          <Link to="/download" className="navbar-link">Download</Link>
        </div>

        <div className="app-title">
          <h1>Calibration Certificate Generator</h1>
          <img src="logo.png" className="app-logo" alt="logo" />
        </div>

        <Routes>
          <Route path="/register" element={<Register />} />
          <Route path="/login" element={user ? <Navigate to="/form" /> : <Login setUser={setUser} />} />
          <Route path="/form" element={user ? <Form setFormFilled={setFormFilled} /> : <div className="login-message">Please login first.</div>} />
          <Route path="/upload" element={user ? <Upload user={user} formFilled={formFilled} /> : <div className="login-message">Please login first.</div>} />
          <Route path="/download" element={user ? <Download /> : <div className="login-message">Please login first.</div>} />
          <Route path="/logout" element={<Navigate to="/login" />} />
        </Routes>
      </div>
    </Router>
  );
};

export default App;