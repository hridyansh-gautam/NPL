import React, { useState } from 'react';
import './Register.css';
import axios from 'axios';
import ReCAPTCHA from 'react-google-recaptcha';
axios.defaults.withCredentials = true;

const Register = () => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [captchaToken, setCaptchaToken] = useState(null);

  const handleRegister = async (e) => {
    e.preventDefault();
    const trimmedUsername = username.trim();
    if (!captchaToken) {
      setError('Please complete the CAPTCHA');
      return;
    }
    setLoading(true);
    setError('');
    try {
      const response = await axios.post('http://localhost:5000/register', {
        username: trimmedUsername,
        password,
        captchaToken,
      });
      setLoading(false);
      if (response.status === 201) {
        alert(response.data.message);
        setUsername('');
        setPassword('');
        setCaptchaToken(null);
      } else {
        setError(response.data.message);
      }
    } catch (error) {
      setLoading(false);
      setError('There was an error registering. Please try again.');
      console.error('There was an error registering!', error);
    }
  };

  return (
    <div className="register-container">
      <h2>Register</h2>
      <form onSubmit={handleRegister} className="register-form">
        <div className="form-group">
          <label>Username:</label>
          <input
            type="text"
            value={username}
            onChange={(e) => setUsername(e.target.value.trim())}
            required
          />
        </div>
        <div className="form-group">
          <label>Password:</label>
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
        </div>
        <div className="recaptcha-container">
          <ReCAPTCHA
            sitekey="6LeuV_EpAAAAANQG3iF1uxtOPcPiE_TW7JkTYQ74"
            onChange={(token) => setCaptchaToken(token)}
          />
        </div>
        <button type="submit" className="register-button" disabled={loading}>
          {loading ? 'Registering...' : 'Register'}
        </button>
        {error && <div className="error-message">{error}</div>}
      </form>
    </div>
  );
};

export default Register;