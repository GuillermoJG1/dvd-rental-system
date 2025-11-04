// Configuración de la API
const API_URL = 'http://localhost:8000';

// ====================================
// FUNCIONES DE NAVEGACIÓN
// ====================================

function showTab(tabName) {
    // Ocultar todos los contenidos
    const contents = document.querySelectorAll('.tab-content');
    contents.forEach(content => content.classList.remove('active'));

    // Desactivar todos los tabs
    const tabs = document.querySelectorAll('.tab');
    tabs.forEach(tab => tab.classList.remove('active'));

    // Activar el tab seleccionado
    document.getElementById(tabName).classList.add('active');
    event.target.classList.add('active');

    // Cargar datos según el tab
    if (tabName === 'catalogo') {
        cargarCatalogo();
    } else if (tabName === 'rentar') {
        cargarDatosRenta();
    } else if (tabName === 'devolver') {
        cargarRentasActivas();
    } else if (tabName === 'reportes') {
        cargarReportes();
    }
}

// ====================================
// FUNCIONES DE RENTAS
// ====================================

async function cargarDatosRenta() {
    try {
        // Cargar clientes
        const clientes = await fetch(`${API_URL}/customers?limit=100`);
        const clientesData = await clientes.json();
        
        const clienteSelect = document.getElementById('cliente');
        clienteSelect.innerHTML = '<option value="">Seleccione un cliente...</option>';
        
        clientesData.forEach(cliente => {
            const option = document.createElement('option');
            option.value = cliente.customer_id;
            option.textContent = `${cliente.first_name} ${cliente.last_name} - ${cliente.email || 'Sin email'}`;
            clienteSelect.appendChild(option);
        });

        // Cargar películas
        const films = await fetch(`${API_URL}/films?limit=100`);
        const filmsData = await films.json();
        
        const dvdSelect = document.getElementById('dvd');
        dvdSelect.innerHTML = '<option value="">Seleccione un DVD...</option>';
        
        for (const film of filmsData) {
            const availability = await fetch(`${API_URL}/films/${film.film_id}/availability`);
            const availData = await availability.json();
            
            const option = document.createElement('option');
            option.value = film.film_id;
            option.textContent = `${film.title} - $${film.rental_rate} (${availData.available_copies} disponibles)`;
            option.disabled = availData.available_copies === 0;
            dvdSelect.appendChild(option);
        }

        // Cargar staff
        const staff = await fetch(`${API_URL}/staff`);
        const staffData = await staff.json();
        
        const staffSelect = document.getElementById('staff');
        staffSelect.innerHTML = '<option value="">Seleccione personal...</option>';
        
        staffData.forEach(s => {
            const option = document.createElement('option');
            option.value = s.staff_id;
            option.textContent = `${s.first_name} ${s.last_name}`;
            staffSelect.appendChild(option);
        });

    } catch (error) {
        console.error('Error al cargar datos:', error);
        mostrarAlerta('⚠️ Error al conectar con el servidor', 'warning');
    }
}

async function rentarDVD() {
    const customer_id = parseInt(document.getElementById('cliente').value);
    const film_id = parseInt(document.getElementById('dvd').value);
    const staff_id = parseInt(document.getElementById('staff').value);
    const days = parseInt(document.getElementById('dias').value);

    // Validar campos
    if (!customer_id || !film_id || !staff_id) {
        mostrarAlerta('⚠️ Por favor complete todos los campos', 'warning');
        return;
    }

    try {
        const response = await fetch(`${API_URL}/rentals`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                customer_id,
                film_id,
                staff_id,
                days
            })
        });

        if (response.ok) {
            const rental = await response.json();
            mostrarAlerta('✅ Renta registrada exitosamente!', 'success');
            limpiarFormulario();
        } else {
            const error = await response.json();
            mostrarAlerta(`❌ Error: ${error.detail}`, 'warning');
        }
    } catch (error) {
        console.error('Error:', error);
        mostrarAlerta('❌ Error al conectar con el servidor', 'warning');
    }
}

function limpiarFormulario() {
    document.getElementById('cliente').value = '';
    document.getElementById('dvd').value = '';
    document.getElementById('staff').value = '';
    document.getElementById('dias').value = '7';
}

// ====================================
// FUNCIONES DE DEVOLUCIÓN
// ====================================

async function cargarRentasActivas() {
    try {
        const response = await fetch(`${API_URL}/reports/unreturned`);
        const data = await response.json();
        
        const tbody = document.getElementById('tabla-devolver');
        tbody.innerHTML = '';

        if (data.rentals && data.rentals.length > 0) {
            data.rentals.forEach(rental => {
                const tr = document.createElement('tr');
                
                const daysLate = rental.days_late;
                const rowClass = daysLate > 0 ? 'style="background-color: #ffebee;"' : '';
                
                tr.innerHTML = `
                    <td>#${rental.rental_id}</td>
                    <td>${rental.customer_name}</td>
                    <td>${rental.film_title}</td>
                    <td>${formatearFecha(rental.rental_date)}</td>
                    <td ${daysLate > 0 ? 'style="color: red; font-weight: bold;"' : ''}>
                        ${formatearFecha(rental.expected_return_date)}
                        ${daysLate > 0 ? `<br><small>(${daysLate} días de retraso)</small>` : ''}
                    </td>
                    <td>
                        <button class="btn" onclick="devolverDVD(${rental.rental_id})">✓ Devolver</button>
                    </td>
                `;
                
                if (daysLate > 0) {
                    tr.style.backgroundColor = '#ffebee';
                }
                
                tbody.appendChild(tr);
            });
        } else {
            tbody.innerHTML = '<tr><td colspan="6" style="text-align: center;">No hay rentas activas</td></tr>';
        }
    } catch (error) {
        console.error('Error:', error);
        mostrarAlerta('⚠️ Error al cargar rentas activas', 'warning');
    }
}

async function devolverDVD(rentalId) {
    const confirmacion = confirm('¿Confirmar devolución del DVD?\n\nEl DVD será marcado como devuelto.');

    if (confirmacion) {
        try {
            const response = await fetch(`${API_URL}/rentals/${rentalId}/return`, {
                method: 'PUT'
            });

            if (response.ok) {
                mostrarAlerta('✅ DVD devuelto exitosamente!', 'success');
                cargarRentasActivas();
            } else {
                const error = await response.json();
                mostrarAlerta(`❌ Error: ${error.detail}`, 'warning');
            }
        } catch (error) {
            console.error('Error:', error);
            mostrarAlerta('❌ Error al conectar con el servidor', 'warning');
        }
    }
}

// ====================================
// FUNCIONES DE CATÁLOGO
// ====================================

async function cargarCatalogo() {
    try {
        const response = await fetch(`${API_URL}/films?limit=100`);
        const films = await response.json();
        
        const grid = document.getElementById('catalogo-grid');
        grid.innerHTML = '';

        for (const film of films) {
            // Obtener disponibilidad de cada película
            const availResponse = await fetch(`${API_URL}/films/${film.film_id}/availability`);
            const availData = await availResponse.json();
            
            const card = document.createElement('div');
            card.className = 'dvd-card';
            
            const statusClass = availData.available_copies > 0 ? 'available' : 'rented';
            const statusText = `${availData.available_copies} de ${availData.total_copies} disponibles`;
            
            card.innerHTML = `
                <div class="dvd-title">${film.title}</div>
                <div class="dvd-info">📅 Año: ${film.release_year || 'N/A'}</div>
                <div class="dvd-info">⏱️ Duración renta: ${film.rental_duration} días</div>
                <div class="price">$${parseFloat(film.rental_rate).toFixed(2)}</div>
                <span class="status ${statusClass}">${statusText}</span>
            `;
            
            grid.appendChild(card);
        }
    } catch (error) {
        console.error('Error:', error);
        mostrarAlerta('⚠️ Error al cargar catálogo', 'warning');
    }
}

// ====================================
// FUNCIONES DE REPORTES
// ====================================

async function cargarReportes() {
    try {
        // Actualizar estadísticas generales
        const rentals = await fetch(`${API_URL}/rentals?limit=1000`);
        const rentalsData = await rentals.json();
        
        const activeRentals = rentalsData.filter(r => r.status === 'ACTIVO').length;
        const totalRentals = rentalsData.length;
        
        // Reporte de ganancias por staff
        const staffEarnings = await fetch(`${API_URL}/reports/staff-earnings`);
        const staffData = await staffEarnings.json();
        
        // Calcular ganancias totales
        const totalEarnings = staffData.staff.reduce((sum, s) => sum + parseFloat(s.total_earnings), 0);
        
        // Actualizar cards de estadísticas
        document.querySelector('.stat-card:nth-child(1) .stat-number').textContent = totalRentals;
        document.querySelector('.stat-card:nth-child(2) .stat-number').textContent = activeRentals;
        document.querySelector('.stat-card:nth-child(3) .stat-number').textContent = `${totalEarnings.toFixed(2)}`;
        
    } catch (error) {
        console.error('Error al cargar reportes:', error);
    }
}

async function cargarReporteMasRentados() {
    try {
        const response = await fetch(`${API_URL}/reports/most-rented?limit=10`);
        const data = await response.json();
        
        const contenedor = document.getElementById('reporte-mas-rentados');
        
        if (data.films && data.films.length > 0) {
            let html = '<table border="1" cellpadding="5" cellspacing="0" width="100%">';
            html += '<tr><th>Posición</th><th>Película</th><th>Año</th><th>Veces Rentado</th></tr>';
            
            data.films.forEach((film, index) => {
                const posicion = index === 0 ? '🥇' : index === 1 ? '🥈' : index === 2 ? '🥉' : (index + 1);
                html += `<tr>
                    <td><b>${posicion}</b></td>
                    <td>${film.title}</td>
                    <td>${film.release_year || 'N/A'}</td>
                    <td><b>${film.rental_count}</b></td>
                </tr>`;
            });
            
            html += '</table>';
            contenedor.innerHTML = html;
        } else {
            contenedor.innerHTML = '<p style="text-align: center; color: #666;">No hay datos disponibles</p>';
        }
    } catch (error) {
        console.error('Error:', error);
        document.getElementById('reporte-mas-rentados').innerHTML = '<p style="color: red;">Error al cargar reporte</p>';
    }
}

async function cargarReporteStaff() {
    try {
        const response = await fetch(`${API_URL}/reports/staff-earnings`);
        const data = await response.json();
        
        const contenedor = document.getElementById('reporte-staff');
        
        if (data.staff && data.staff.length > 0) {
            const totalGeneral = data.staff.reduce((sum, s) => sum + parseFloat(s.total_earnings), 0);
            
            let html = '<table border="1" cellpadding="5" cellspacing="0" width="100%">';
            html += '<tr><th>Personal</th><th>Transacciones</th><th>Ganancias</th></tr>';
            
            data.staff.forEach(staff => {
                html += `<tr>
                    <td><b>${staff.staff_name}</b></td>
                    <td>${staff.total_transactions}</td>
                    <td><b>${staff.total_earnings.toFixed(2)}</b></td>
                </tr>`;
            });
            
            html += `<tr style="background-color: #f0f0f0;">
                <td align="right"><b>TOTAL GENERAL:</b></td>
                <td></td>
                <td><b>${totalGeneral.toFixed(2)}</b></td>
            </tr>`;
            
            html += '</table>';
            contenedor.innerHTML = html;
        } else {
            contenedor.innerHTML = '<p style="text-align: center; color: #666;">No hay datos disponibles</p>';
        }
    } catch (error) {
        console.error('Error:', error);
        document.getElementById('reporte-staff').innerHTML = '<p style="color: red;">Error al cargar reporte</p>';
    }
}

// ====================================
// FUNCIONES AUXILIARES
// ====================================

function mostrarAlerta(mensaje, tipo = 'info') {
    const alerta = document.createElement('div');
    alerta.className = `alert alert-${tipo}`;
    alerta.textContent = mensaje;
    alerta.style.position = 'fixed';
    alerta.style.top = '20px';
    alerta.style.right = '20px';
    alerta.style.zIndex = '9999';
    alerta.style.minWidth = '300px';
    alerta.style.animation = 'slideIn 0.3s ease';
    
    document.body.appendChild(alerta);
    
    setTimeout(() => {
        alerta.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => {
            document.body.removeChild(alerta);
        }, 300);
    }, 3000);
}

function formatearFecha(fecha) {
    const date = new Date(fecha);
    return date.toLocaleDateString('es-MX', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit'
    });
}

// ====================================
// INICIALIZACIÓN
// ====================================

document.addEventListener('DOMContentLoaded', function() {
    console.log('🎬 Sistema de Renta de DVDs - Cargado');
    
    // Cargar datos iniciales
    cargarDatosRenta();
    cargarCatalogo();
    
    // Verificar conexión con backend
    fetch(`${API_URL}/`)
        .then(response => response.json())
        .then(data => {
            console.log('✅ Backend conectado:', data);
        })
        .catch(error => {
            console.error('❌ Error al conectar con backend:', error);
            mostrarAlerta('⚠️ No se pudo conectar con el servidor', 'warning');
        });
});

// Animaciones CSS
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from {
            transform: translateX(100%);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    
    @keyframes slideOut {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(100%);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style);