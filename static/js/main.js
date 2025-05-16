document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('vehicle-form');
    if (!form) {
        console.error('Formulario no encontrado');
        return;
    }

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        const lastNames = document.getElementById('last_names').value.trim();
        const firstNames = document.getElementById('first_names').value.trim();
        const dni = document.getElementById('dni').value.trim();
        const licensePlate = document.getElementById('license_plate').value.trim();
        const model = document.getElementById('model').value.trim();

        if (!lastNames || !firstNames || !dni || !licensePlate || !model) {
            alert('Por favor, completa todos los campos.');
            return;
        }

        try {
            const response = await fetch('/api/vehicles', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ 
                    last_names: lastNames, 
                    first_names: firstNames, 
                    dni: dni, 
                    license_plate: licensePlate, 
                    model: model 
                })
            });
            if (response.ok) {
                alert('Vehículo agregado exitosamente');
                form.reset();
            } else {
                const error = await response.json();
                alert('Error al agregar el vehículo: ' + error.error);
            }
        } catch (error) {
            console.error('Error en fetch:', error);
            alert('Error al agregar el vehículo: ' + error.message);
        }
    });
});