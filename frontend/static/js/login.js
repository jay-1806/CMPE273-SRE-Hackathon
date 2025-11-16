// Login functionality

const API_BASE = '/api';

document.getElementById('loginForm').addEventListener('submit', async (e) => {
    e.preventDefault();

    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;
    const errorAlert = document.getElementById('errorAlert');
    const loginText = document.getElementById('loginText');
    const loginSpinner = document.getElementById('loginSpinner');

    // Hide error alert
    errorAlert.style.display = 'none';

    // Show loading state
    loginText.style.display = 'none';
    loginSpinner.style.display = 'inline-block';

    try {
        // Create form data
        const formData = new URLSearchParams();
        formData.append('username', username);
        formData.append('password', password);

        const response = await fetch(`${API_BASE}/auth/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: formData
        });

        const data = await response.json();

        if (response.ok) {
            // Store token
            localStorage.setItem('access_token', data.access_token);
            localStorage.setItem('username', username);

            // Redirect to dashboard
            window.location.href = '/';
        } else {
            // Show error
            errorAlert.textContent = data.detail || 'Login failed';
            errorAlert.style.display = 'block';
        }
    } catch (error) {
        errorAlert.textContent = 'Network error. Please try again.';
        errorAlert.style.display = 'block';
        console.error('Login error:', error);
    } finally {
        // Reset loading state
        loginText.style.display = 'inline';
        loginSpinner.style.display = 'none';
    }
});
