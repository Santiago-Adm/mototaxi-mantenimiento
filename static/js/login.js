document.getElementById('login-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const username = document.getElementById('username').value.trim();
    const password = document.getElementById('password').value.trim();

    try {
        console.log("Enviando credenciales a /api/login");
        const response = await fetch('http://localhost:5000/api/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ username, password })
        });

        console.log("Respuesta recibida:", response);

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || 'Error desconocido');
        }

        const data = await response.json();
        alert(data.message);
        window.location.href = '/mostrar-vehiculos';
        
    } catch (error) {
        console.error("Error completo:", error);
        alert('Error: ' + error.message);
    }
});