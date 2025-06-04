async function loadVehicles() {
    try {
        const response = await fetch('/api/vehicles');
        const vehicles = await response.json();
        const container = document.getElementById('vehicles-container');

        if (!container) {
            console.error('Contenedor no encontrado');
            return;
        }

        container.innerHTML = '';
        vehicles.forEach(vehicle => {
            const card = document.createElement('div');
            card.className = 'vehicle-card';
            card.innerHTML = `
                <p><strong>Apellidos:</strong> ${vehicle.last_names}</p>
                <p><strong>Nombres:</strong> ${vehicle.first_names}</p>
                <p><strong>DNI:</strong> ${vehicle.dni}</p>
                <p><strong>Placa:</strong> ${vehicle.license_plate}</p>
                <p><strong>Modelo:</strong> ${vehicle.model}</p>
            `;
            container.appendChild(card);
        });
    } catch (error) {
        console.error('Error:', error);
        alert('Error al cargar los vehículos');
    }
}

// Cargar vehículos al iniciar y añadir botón de actualización
document.addEventListener('DOMContentLoaded', loadVehicles);
document.getElementById('refresh-btn').addEventListener('click', loadVehicles);

async function addVehicle(event) {
    event.preventDefault();
    
    const formData = {
        last_names: document.getElementById('last_names').value,
        first_names: document.getElementById('first_names').value,
        dni: document.getElementById('dni').value,
        license_plate: document.getElementById('license_plate').value,
        model: document.getElementById('model').value
    };

    try {
        const response = await fetch('/api/vehicles', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(formData)
        });

        if (!response.ok) {
            throw new Error('Error al agregar vehículo');
        }

        await loadVehicles(); // Recargar la lista
        document.getElementById('vehicleForm').reset(); // Limpiar formulario
    } catch (error) {
        console.error('Error:', error);
        alert('Error al agregar vehículo: ' + error.message);
    }
}