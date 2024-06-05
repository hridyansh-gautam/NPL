import React, { useState } from 'react';
import './Form.css';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';

axios.defaults.withCredentials = true;


const Form = () => {
  const [formData, setFormData] = useState({
    certificateNo: '',
    date: '',
    recommendedDate: '',
    calibratedFor: '',
    description: '',
    environmentalConditions: '',
    standardsUsed: '',
    traceability: '',
    calibrationProcedure: '',
    calibratedBy: '',
    checkedBy: '',
    inCharge: '',
    issuedBy: ''
  });

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData({
      ...formData,
      [name]: value
    });
  };

  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    try {
      const response = await axios.post('http://localhost:5000/form', {
        body: formData
      });
      if (response.statusText === 'OK') {
        console.log('Form data submitted successfully');
        setFormData({
          certificateNo: '',
          date: '',
          recommendedDate: '',
          calibratedFor: '',
          description: '',
          environmentalConditions: '',
          standardsUsed: '',
          traceability: '',
          calibrationProcedure: '',
          calibratedBy: '',
          checkedBy: '',
          inCharge: '',
          issuedBy: ''
        });
        // window.location.replace('http://localhost:3000/upload');
        navigate('http://localhost:3000/upload');
      } else {
        console.error('Failed to submit form data:', response.statusText);
      }
    } catch (error) {
      console.error('Error submitting form data:', error);
    }
  };

  return (
    <div className="form-container">
      <h2>Calibration Certificate Form</h2>
      <form >
        <label htmlFor="certificateNo">Certificate No.</label>
        <input type="text" id="certificateNo" name="certificateNo" value={formData.certificateNo} onChange={handleChange} required />
        
        <label htmlFor="date">Date</label>
        <input type="date" id="date" name="date" value={formData.date} onChange={handleChange} required />
        
        <label htmlFor="recommendedDate">Recommended Date for the Next Calibration</label>
        <input type="date" id="recommendedDate" name="recommendedDate" value={formData.recommendedDate} onChange={handleChange} required />
        
        <label htmlFor="calibratedFor">Calibrated For</label>
        <input type="text" id="calibratedFor" name="calibratedFor" value={formData.calibratedFor} onChange={handleChange} required />
        
        <label htmlFor="description">Description & Identification of Item under Calibration</label>
        <textarea id="description" name="description" value={formData.description} onChange={handleChange} required />
        
        <label htmlFor="environmentalConditions">Environmental Conditions</label>
        <textarea id="environmentalConditions" name="environmentalConditions" value={formData.environmentalConditions} onChange={handleChange} required />
        
        <label htmlFor="standardsUsed">Standard(s) used (with) Associated uncertainty</label>
        <textarea id="standardsUsed" name="standardsUsed" value={formData.standardsUsed} onChange={handleChange} required />
        
        <label htmlFor="traceability">Traceability of standard(s) used</label>
        <textarea id="traceability" name="traceability" value={formData.traceability} onChange={handleChange} required />
        
        <label htmlFor="calibrationProcedure">Principle/Methodology of calibration & Calibration Procedure number</label>
        <textarea id="calibrationProcedure" name="calibrationProcedure" value={formData.calibrationProcedure} onChange={handleChange} required />

        <label htmlFor="calibratedBy">Calibrated By</label>
        <input type="text" id="calibratedBy" name="calibratedBy" value={formData.calibratedBy} onChange={handleChange} required />
        
        <label htmlFor="checkedBy">Checked By</label>
        <input type="text" id="checkedBy" name="checkedBy" value={formData.checkedBy} onChange={handleChange} required />

        <label htmlFor="inCharge">Scientist-in-charge</label>
        <input type="text" id="inCharge" name="inCharge" value={formData.inCharge} onChange={handleChange} required />

        <label htmlFor="issuedBy">Issued By</label>
        <input type="text" id="issuedBy" name="issuedBy" value={formData.issuedBy} onChange={handleChange} required />

        <button onClick={handleSubmit} className="next-button">Next</button>
      </form>
    </div>
  );
};

export default Form;