document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('login-form');
    const usernameInput = document.getElementById('username');
    const passwordInput = document.getElementById('password');
    const loginButton = document.getElementById('login-button');
    const errorMessage = document.getElementById('error-message');
  
    form.addEventListener('submit', async (e) => {
      e.preventDefault();
      const username = usernameInput.value.trim();
      const password = passwordInput.value.trim();
      const captchaToken = grecaptcha.getResponse();
  
      if (!captchaToken) {
        errorMessage.textContent = 'Please complete the CAPTCHA';
        return;
      }
  
      loginButton.disabled = true;
      loginButton.textContent = 'Logging in...';
      errorMessage.textContent = '';
  
      try {
        const response = await axios.post('http://localhost:5000/login', {
          username,
          password,
          captchaToken
        });
  
        loginButton.disabled = false;
        loginButton.textContent = 'Login';
  
        if (response.status === 200) {
          alert(response.data.message);
          sessionStorage.setItem('user', response.data.username); 
          window.location.href = 'dashboard';
        } else {
          errorMessage.textContent = response.data.message;
        }
      } catch (error) {
        loginButton.disabled = false;
        loginButton.textContent = 'Login';
        errorMessage.textContent = 'There was an error logging in. Please try again.';
        console.error('There was an error logging in!', error);
      }
    });
  });  