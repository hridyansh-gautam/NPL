document.getElementById('validate-button').addEventListener('click', async function() {
    const checksum = document.getElementById('checksum-input').value;
    if (!checksum) {
      displayValidationResult('Please enter a checksum', 'text-danger');
      return;
    }
  
    try {
      const response = await fetch(`/verify/${checksum}`);
      // const isValid = await response.text();
      console.log(response);
  
      if (response.status == '200') {
        displayValidationResult('Checksum is valid!', 'text-success');
      } else if (response.status == '200'){
        displayValidationResult('Checksum is invalid.', 'text-danger');
      }
    } catch (error) {
      displayValidationResult('An error occurred. Please try again later.', 'text-danger');
    }
  });
  
  function displayValidationResult(message, className) {
    const resultDiv = document.getElementById('validation-result');
    resultDiv.textContent = message;
    resultDiv.className = className;
  }  