document.addEventListener('DOMContentLoaded', function() {
    const registroForm = document.getElementById('registroForm');

    if (registroForm) {
        registroForm.addEventListener('submit', async function(event) {
            event.preventDefault();

            const formData = {
                username: document.getElementById('username').value,
                password: document.getElementById('password').value,
                email: document.getElementById('email').value,
                vehicle: {
                    last_names: document.getElementById('last_names').value,
                    first_names: document.getElementById('first_names').value,
                    dni: document.getElementById('dni').value,
                    license_plate: document.getElementById('license_plate').value,
                    model: document.getElementById('model').value
                }
            };

            try {
                const response = await fetch('/api/registro', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(formData)
                });

                const data = await response.json();

                if (response.ok) {
                    alert('Registro exitoso. Por favor, inicia sesión.');
                    window.location.href = '/login';
                } else {
                    alert(data.error || 'Error en el registro');
                }
            } catch (error) {
                console.error('Error:', error);
                alert('Error en el registro');
            }
        });
    }

    // Add model selection handling
    const modelButtons = document.querySelectorAll('.model-btn');
    const modelInput = document.getElementById('model');

    modelButtons.forEach(button => {
        button.addEventListener('click', function() {
            // Remove selected class from all buttons
            modelButtons.forEach(btn => btn.classList.remove('selected'));
            // Add selected class to clicked button
            this.classList.add('selected');
            // Update hidden input value
            modelInput.value = this.dataset.model;
        });
    });
});