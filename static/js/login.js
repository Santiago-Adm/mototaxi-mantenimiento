document.getElementById('login-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;

    try {
        // Aquí iría la lógica de autenticación (por ejemplo, una llamada a un endpoint /api/login)
        alert('Inicio de sesión en desarrollo. Usuario: ' + username);
        // Redirigir a /mostrar-vehiculos tras autenticación exitosa (a implementar)
        // window.location.href = '/mostrar-vehiculos';
    } catch (error) {
        alert('Error al iniciar sesión: ' + error.message);
    }
});