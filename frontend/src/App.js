import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Link, Navigate } from 'react-router-dom';
import Register from './components/Register';
import Login from './components/Login';
import Form from './components/Form'; 
import Upload from './components/Upload';
import Download from './components/Download';
import Home from './components/Home';
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
      <div className="app-container">
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
          <Link to="/" className="navbar-link">Home</Link>
          <Link to="/form" className="navbar-link">Form</Link>
          <Link to="/upload" className="navbar-link">Upload</Link>
          <Link to="/download" className="navbar-link">Download</Link>
        </div>

        <div className="content">
          <Routes>
            <Route path="/" element={<Home />} />  {/* Home component */}
            <Route path="/register" element={<Register />} />
            <Route path="/login" element={user ? <Navigate to="/form" /> : <Login setUser={setUser} />} />
            <Route path="/form" element={user ? <Form setFormFilled={setFormFilled} /> : <div className="login-message">Please login first.</div>} />
            <Route path="/upload" element={user ? (formFilled ? <Upload user={user} formFilled={formFilled} /> : <div className="form-message">Please fill the form first.</div>) : <div className="login-message">Please login first.</div>} />
            <Route path="/download" element={user ? (formFilled ? <Download /> : <div className="form-message">Please fill the form first.</div>) : <div className="login-message">Please login first.</div>} />
            <Route path="/logout" element={<Navigate to="/login" />} />
          </Routes>
        </div>

        <div className="footer">
          <Link to="/about" className="footer-link">About</Link>
          <Link to="/contact" className="footer-link">Contact</Link>
        </div>
      </div>
    </Router>
  );
};

export default App;