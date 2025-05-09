async function loadVehicles() {
    try {
        const response = await fetch('/api/vehicles');
        const vehicles = await response.json();
        const container = document.getElementById('vehicles-container');
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
        alert('Error al cargar los vehículos: ' + error.message);
    }
}

// Cargar vehículos al iniciar y añadir botón de actualización
document.addEventListener('DOMContentLoaded', loadVehicles);
document.getElementById('refresh-btn').addEventListener('click', loadVehicles);