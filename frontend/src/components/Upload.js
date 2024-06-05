import React, { useState } from 'react';
import axios from 'axios';
import './Upload.css';

const Upload = () => {
  const [file, setFile] = useState(null);
  const [message, setMessage] = useState('');

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
  };

  const handleFileUpload = async (e) => {
    e.preventDefault();
    if (!file) {
      setMessage('Please select a file to upload');
      return;
    }

    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await axios.post('http://localhost:5000/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });

      if (response.status === 200) {
        setMessage('File uploaded successfully');
        setTimeout(() => {
          window.location.href = 'http://localhost:3000/download';
        }, 2000);
      } else {
        setMessage('Failed to upload file');
      }
    } catch (error) {
      setMessage('Error uploading file: ' + error.message);
    }
  };

  return (
    <div className="upload-container">
      <h2>Upload Excel File</h2>
      <form onSubmit={handleFileUpload} className="upload-form">
        <input type="file" onChange={handleFileChange} required className="file-input" />
        <button type="submit" className="upload-button">Upload</button>
      </form>
      {message && <p className="upload-message">{message}</p>}
    </div>
  );
};

export default Upload;