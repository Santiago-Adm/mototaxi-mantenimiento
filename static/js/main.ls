document.getElementById('vehicle-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const licensePlate = document.getElementById('license_plate').value;
    const ownerName = document.getElementById('owner_name').value;
    const model = document.getElementById('model').value;

    try {
        const response = await fetch('/api/vehicles', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ license_plate: licensePlate, owner_name: ownerName, model })
        });
        if (response.ok) {
            alert('Vehículo agregado exitosamente');
            document.getElementById('vehicle-form').reset();
            loadVehicles();
        } else {
            const error = await response.json();
            alert('Error: ' + error.error);
        }
    } catch (error) {
        alert('Error: ' + error.message);
    }
});

async function loadVehicles() {
    try {
        const response = await fetch('/api/vehicles');
        const vehicles = await response.json();
        const tbody = document.getElementById('vehicles-table-body');
        tbody.innerHTML = '';
        vehicles.forEach(vehicle => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${vehicle.license_plate}</td>
                <td>${vehicle.owner_name}</td>
                <td>${vehicle.model}</td>
            `;
            tbody.appendChild(row);
        });
    } catch (error) {
        alert('Error al cargar vehículos: ' + error.message);
    }
}

// Cargar vehículos al iniciar
loadVehicles();