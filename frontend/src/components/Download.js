import React from 'react';
import './Download.css';

const Download = () => {
  return (
    <div className="download-container">
      <h2>View PDF</h2>
      <div className="pdf-container">
        <iframe
          src="https://drive.google.com/file/d/16v2lVsjQ188ZGfXGvk7dSV_VnpEv2NwH/preview"
          title="PDF Viewer"
          width="100%"
          height="500"
        />
      </div>
    </div>
  );
};

export default Download;