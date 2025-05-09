document.getElementById('vehicle-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const lastNames = document.getElementById('last_names').value;
    const firstNames = document.getElementById('first_names').value;
    const dni = document.getElementById('dni').value;
    const licensePlate = document.getElementById('license_plate').value;
    const model = document.getElementById('model').value;

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
            document.getElementById('vehicle-form').reset();
        } else {
            const error = await response.json();
            alert('Error al agregar el vehículo: ' + error.error);
        }
    } catch (error) {
        alert('Error al agregar el vehículo: ' + error.message);
    }
});