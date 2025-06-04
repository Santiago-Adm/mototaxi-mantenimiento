document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM fully loaded');
    
    const loginForm = document.getElementById('loginForm');
    console.log('Login form:', loginForm); // Debug log
    
    if (loginForm) {
        loginForm.addEventListener('submit', async function(event) {
            event.preventDefault();
            console.log('Form submitted'); // Debug log

            const formData = {
                username: document.getElementById('username').value,
                password: document.getElementById('password').value
            };

            try {
                const response = await fetch('/api/login', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(formData)
                });

                const data = await response.json();
                console.log('Login response:', data); // Debug log

                if (response.ok) {
                    console.log('Login successful, redirecting...'); // Debug log
                    window.location.href = '/mostrar-vehiculos';
                } else {
                    alert(data.error || 'Usuario o contraseña incorrectos');
                }
            } catch (error) {
                console.error('Error:', error);
                alert('Error en el inicio de sesión');
            }
        });
    } else {
        console.error('Login form not found');
    }
});
