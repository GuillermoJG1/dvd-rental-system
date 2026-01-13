import sys
import requests
from datetime import datetime
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                              QHBoxLayout, QTabWidget, QPushButton, QLabel, 
                              QComboBox, QTableWidget, QTableWidgetItem, 
                              QMessageBox, QSpinBox, QTextEdit, QGroupBox)
from PyQt6.QtCore import Qt

class DVDRentalApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.api_url = "http://localhost:8000"
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle("Sistema de Renta de DVDs")
        self.setGeometry(100, 100, 1200, 800)
        
        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout principal
        layout = QVBoxLayout()
        central_widget.setLayout(layout)
        
        # Tabs
        tabs = QTabWidget()
        layout.addWidget(tabs)
        
        # Tab 1: Rentar DVDs
        tabs.addTab(self.create_rental_tab(), "Rentar DVD")
        
        # Tab 2: Devolver DVDs
        tabs.addTab(self.create_return_tab(), "Devolver DVD")
        
        # Tab 3: Cancelar Rentas
        tabs.addTab(self.create_cancel_tab(), "Cancelar Renta")
        
        # Tab 4: Reportes
        tabs.addTab(self.create_reports_tab(), "Reportes")
        
    def create_rental_tab(self):
        widget = QWidget()
        layout = QVBoxLayout()
        widget.setLayout(layout)
        
        # Título
        title = QLabel("<h2>Nueva Renta de DVD</h2>")
        layout.addWidget(title)
        
        # Formulario
        form_layout = QVBoxLayout()
        
        # Cliente
        customer_group = QGroupBox("Seleccionar Cliente")
        customer_layout = QVBoxLayout()
        self.customer_combo = QComboBox()
        customer_layout.addWidget(self.customer_combo)
        customer_group.setLayout(customer_layout)
        form_layout.addWidget(customer_group)
        
        # DVD
        dvd_group = QGroupBox("Seleccionar DVD")
        dvd_layout = QVBoxLayout()
        self.dvd_combo = QComboBox()
        dvd_layout.addWidget(self.dvd_combo)
        dvd_group.setLayout(dvd_layout)
        form_layout.addWidget(dvd_group)
        
        # Staff
        staff_group = QGroupBox("Personal que Atiende")
        staff_layout = QVBoxLayout()
        self.staff_combo = QComboBox()
        staff_layout.addWidget(self.staff_combo)
        staff_group.setLayout(staff_layout)
        form_layout.addWidget(staff_group)
        
        # Días de renta
        days_group = QGroupBox("Días de Renta")
        days_layout = QHBoxLayout()
        self.days_spin = QSpinBox()
        self.days_spin.setMinimum(1)
        self.days_spin.setMaximum(30)
        self.days_spin.setValue(7)
        days_layout.addWidget(QLabel("Días:"))
        days_layout.addWidget(self.days_spin)
        days_group.setLayout(days_layout)
        form_layout.addWidget(days_group)
        
        layout.addLayout(form_layout)
        
        # Botones
        button_layout = QHBoxLayout()
        
        refresh_btn = QPushButton("Actualizar Datos")
        refresh_btn.clicked.connect(self.load_rental_data)
        button_layout.addWidget(refresh_btn)
        
        rental_btn = QPushButton("Realizar Renta")
        rental_btn.clicked.connect(self.create_rental)
        rental_btn.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold; padding: 10px;")
        button_layout.addWidget(rental_btn)
        
        layout.addLayout(button_layout)
        
        # Espaciador
        layout.addStretch()
        
        # Cargar datos iniciales
        self.load_rental_data()
        
        return widget
    
    def create_return_tab(self):
        widget = QWidget()
        layout = QVBoxLayout()
        widget.setLayout(layout)
        
        # Título
        title = QLabel("<h2>Devolver DVD</h2>")
        layout.addWidget(title)
        
        # Tabla de rentas activas
        self.active_rentals_table = QTableWidget()
        self.active_rentals_table.setColumnCount(6)
        self.active_rentals_table.setHorizontalHeaderLabels([
            "ID", "Cliente", "DVD", "Fecha Renta", "Fecha Esperada", "Acción"
        ])
        self.active_rentals_table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.active_rentals_table)
        
        # Botón actualizar
        refresh_btn = QPushButton("Actualizar Lista")
        refresh_btn.clicked.connect(self.load_active_rentals)
        layout.addWidget(refresh_btn)
        
        # Cargar datos iniciales
        self.load_active_rentals()
        
        return widget
    
    def create_cancel_tab(self):
        widget = QWidget()
        layout = QVBoxLayout()
        widget.setLayout(layout)
        
        # Título
        title = QLabel("<h2>Cancelar Renta</h2>")
        layout.addWidget(title)
        
        # Tabla de rentas activas para cancelar
        self.cancel_rentals_table = QTableWidget()
        self.cancel_rentals_table.setColumnCount(6)
        self.cancel_rentals_table.setHorizontalHeaderLabels([
            "ID", "Cliente", "DVD", "Fecha Renta", "Monto", "Acción"
        ])
        self.cancel_rentals_table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.cancel_rentals_table)
        
        # Botón actualizar
        refresh_btn = QPushButton("Actualizar Lista")
        refresh_btn.clicked.connect(self.load_cancel_rentals)
        layout.addWidget(refresh_btn)
        
        # Cargar datos iniciales
        self.load_cancel_rentals()
        
        return widget
    
    def create_reports_tab(self):
        widget = QWidget()
        layout = QVBoxLayout()
        widget.setLayout(layout)
        
        # Título
        title = QLabel("<h2>Reportes del Sistema</h2>")
        layout.addWidget(title)
        
        # Botones de reportes
        buttons_layout = QHBoxLayout()
        
        btn1 = QPushButton("Rentas por Cliente")
        btn1.clicked.connect(self.show_customer_rentals_report)
        buttons_layout.addWidget(btn1)
        
        btn2 = QPushButton("DVDs No Devueltos")
        btn2.clicked.connect(self.show_unreturned_report)
        buttons_layout.addWidget(btn2)
        
        btn3 = QPushButton("DVDs Más Rentados")
        btn3.clicked.connect(self.show_most_rented_report)
        buttons_layout.addWidget(btn3)
        
        btn4 = QPushButton("Ganancias por Staff")
        btn4.clicked.connect(self.show_staff_earnings_report)
        buttons_layout.addWidget(btn4)
        
        layout.addLayout(buttons_layout)
        
        # Área de resultados
        self.report_text = QTextEdit()
        self.report_text.setReadOnly(True)
        layout.addWidget(self.report_text)
        
        return widget
    
    # === MÉTODOS DE CARGA DE DATOS ===
    
    def load_rental_data(self):
        try:
            # Cargar clientes
            response = requests.get(f"{self.api_url}/customers")
            if response.status_code == 200:
                customers = response.json()
                self.customer_combo.clear()
                for customer in customers:
                    self.customer_combo.addItem(
                        f"{customer['name']} ({customer['email']})",
                        customer['id']
                    )
            
            # Cargar DVDs
            response = requests.get(f"{self.api_url}/dvds")
            if response.status_code == 200:
                dvds = response.json()
                self.dvd_combo.clear()
                for dvd in dvds:
                    self.dvd_combo.addItem(
                        f"{dvd['title']} - ${dvd['rental_price']} (Disponibles: {dvd['available_copies']})",
                        dvd['id']
                    )
            
            # Cargar Staff
            response = requests.get(f"{self.api_url}/staff")
            if response.status_code == 200:
                staff = response.json()
                self.staff_combo.clear()
                for s in staff:
                    self.staff_combo.addItem(
                        f"{s['name']} ({s['position']})",
                        s['id']
                    )
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al cargar datos: {str(e)}")
    
    def load_active_rentals(self):
        try:
            response = requests.get(f"{self.api_url}/rentals")
            if response.status_code == 200:
                rentals = response.json()
                active_rentals = [r for r in rentals if r['status'] == 'ACTIVE']
                
                self.active_rentals_table.setRowCount(len(active_rentals))
                
                for i, rental in enumerate(active_rentals):
                    # Obtener datos adicionales
                    customer = requests.get(f"{self.api_url}/customers").json()
                    dvd = requests.get(f"{self.api_url}/dvds").json()
                    
                    customer_name = next((c['name'] for c in customer if c['id'] == rental['customer_id']), "N/A")
                    dvd_title = next((d['title'] for d in dvd if d['id'] == rental['dvd_id']), "N/A")
                    
                    self.active_rentals_table.setItem(i, 0, QTableWidgetItem(str(rental['id'])))
                    self.active_rentals_table.setItem(i, 1, QTableWidgetItem(customer_name))
                    self.active_rentals_table.setItem(i, 2, QTableWidgetItem(dvd_title))
                    self.active_rentals_table.setItem(i, 3, QTableWidgetItem(rental['rental_date'][:10]))
                    self.active_rentals_table.setItem(i, 4, QTableWidgetItem(rental['expected_return_date'][:10]))
                    
                    # Botón devolver
                    return_btn = QPushButton("Devolver")
                    return_btn.clicked.connect(lambda checked, rid=rental['id']: self.return_rental(rid))
                    self.active_rentals_table.setCellWidget(i, 5, return_btn)
                    
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al cargar rentas: {str(e)}")
    
    def load_cancel_rentals(self):
        try:
            response = requests.get(f"{self.api_url}/rentals")
            if response.status_code == 200:
                rentals = response.json()
                active_rentals = [r for r in rentals if r['status'] == 'ACTIVE']
                
                self.cancel_rentals_table.setRowCount(len(active_rentals))
                
                for i, rental in enumerate(active_rentals):
                    # Obtener datos adicionales
                    customer = requests.get(f"{self.api_url}/customers").json()
                    dvd = requests.get(f"{self.api_url}/dvds").json()
                    
                    customer_name = next((c['name'] for c in customer if c['id'] == rental['customer_id']), "N/A")
                    dvd_title = next((d['title'] for d in dvd if d['id'] == rental['dvd_id']), "N/A")
                    
                    self.cancel_rentals_table.setItem(i, 0, QTableWidgetItem(str(rental['id'])))
                    self.cancel_rentals_table.setItem(i, 1, QTableWidgetItem(customer_name))
                    self.cancel_rentals_table.setItem(i, 2, QTableWidgetItem(dvd_title))
                    self.cancel_rentals_table.setItem(i, 3, QTableWidgetItem(rental['rental_date'][:10]))
                    self.cancel_rentals_table.setItem(i, 4, QTableWidgetItem(f"${rental['total_amount']:.2f}"))
                    
                    # Botón cancelar
                    cancel_btn = QPushButton("Cancelar")
                    cancel_btn.setStyleSheet("background-color: #f44336; color: white;")
                    cancel_btn.clicked.connect(lambda checked, rid=rental['id']: self.cancel_rental(rid))
                    self.cancel_rentals_table.setCellWidget(i, 5, cancel_btn)
                    
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al cargar rentas: {str(e)}")
    
    # === MÉTODOS DE ACCIONES ===
    
    def create_rental(self):
        try:
            customer_id = self.customer_combo.currentData()
            dvd_id = self.dvd_combo.currentData()
            staff_id = self.staff_combo.currentData()
            days = self.days_spin.value()
            
            if not all([customer_id, dvd_id, staff_id]):
                QMessageBox.warning(self, "Advertencia", "Por favor seleccione todos los campos")
                return
            
            data = {
                "customer_id": customer_id,
                "dvd_id": dvd_id,
                "staff_id": staff_id,
                "days": days
            }
            
            response = requests.post(f"{self.api_url}/rentals", json=data)
            
            if response.status_code == 200:
                rental = response.json()
                QMessageBox.information(
                    self, 
                    "Éxito", 
                    f"Renta creada exitosamente!\n\nID: {rental['id']}\nMonto: ${rental['total_amount']:.2f}\nFecha de devolución: {rental['expected_return_date'][:10]}"
                )
                self.load_rental_data()
            else:
                QMessageBox.critical(self, "Error", f"Error al crear renta: {response.json().get('detail', 'Error desconocido')}")
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error: {str(e)}")
    
    def return_rental(self, rental_id):
        try:
            reply = QMessageBox.question(
                self,
                'Confirmar Devolución',
                f'¿Está seguro de marcar como devuelta la renta #{rental_id}?',
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                response = requests.put(f"{self.api_url}/rentals/{rental_id}/return")
                
                if response.status_code == 200:
                    QMessageBox.information(self, "Éxito", "DVD devuelto exitosamente!")
                    self.load_active_rentals()
                else:
                    QMessageBox.critical(self, "Error", f"Error: {response.json().get('detail', 'Error desconocido')}")
                    
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error: {str(e)}")
    
    def cancel_rental(self, rental_id):
        try:
            reply = QMessageBox.question(
                self,
                'Confirmar Cancelación',
                f'¿Está seguro de cancelar la renta #{rental_id}?\nEsta acción no se puede deshacer.',
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                response = requests.delete(f"{self.api_url}/rentals/{rental_id}")
                
                if response.status_code == 200:
                    QMessageBox.information(self, "Éxito", "Renta cancelada exitosamente!")
                    self.load_cancel_rentals()
                else:
                    QMessageBox.critical(self, "Error", f"Error: {response.json().get('detail', 'Error desconocido')}")
                    
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error: {str(e)}")
    
    # === MÉTODOS DE REPORTES ===
    
    def show_customer_rentals_report(self):
        try:
            response = requests.get(f"{self.api_url}/customers")
            if response.status_code != 200:
                QMessageBox.critical(self, "Error", "No se pudieron cargar los clientes")
                return
            
            customers = response.json()
            
            report = "<h2>Reporte de Rentas por Cliente</h2><hr>"
            
            for customer in customers:
                response = requests.get(f"{self.api_url}/reports/customer/{customer['id']}")
                if response.status_code == 200:
                    data = response.json()
                    report += f"<h3>{data['customer_name']} ({data['customer_email']})</h3>"
                    report += f"<p><b>Total de rentas:</b> {data['total_rentals']}</p>"
                    
                    if data['rentals']:
                        report += "<ul>"
                        for rental in data['rentals']:
                            report += f"<li><b>{rental['dvd_title']}</b> - Fecha: {rental['rental_date'][:10]} - Estado: {rental['status']} - Monto: ${rental['total_amount']:.2f}</li>"
                        report += "</ul>"
                    else:
                        report += "<p><i>No tiene rentas registradas</i></p>"
                    
                    report += "<hr>"
            
            self.report_text.setHtml(report)
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al generar reporte: {str(e)}")
    
    def show_unreturned_report(self):
        try:
            response = requests.get(f"{self.api_url}/reports/unreturned")
            if response.status_code == 200:
                data = response.json()
                
                report = "<h2>DVDs No Devueltos</h2><hr>"
                report += f"<p><b>Total de DVDs sin devolver:</b> {data['total_unreturned']}</p>"
                
                if data['rentals']:
                    report += "<table border='1' cellpadding='5' cellspacing='0' width='100%'>"
                    report += "<tr><th>ID Renta</th><th>DVD</th><th>Cliente</th><th>Fecha Renta</th><th>Fecha Esperada</th><th>Días de Retraso</th></tr>"
                    
                    for rental in data['rentals']:
                        days_late = rental['days_late']
                        color = "red" if days_late > 0 else "green"
                        report += f"<tr>"
                        report += f"<td>{rental['rental_id']}</td>"
                        report += f"<td><b>{rental['dvd_title']}</b></td>"
                        report += f"<td>{rental['customer_name']}</td>"
                        report += f"<td>{rental['rental_date'][:10]}</td>"
                        report += f"<td>{rental['expected_return_date'][:10]}</td>"
                        report += f"<td style='color: {color};'><b>{days_late}</b></td>"
                        report += f"</tr>"
                    
                    report += "</table>"
                else:
                    report += "<p><i>No hay DVDs sin devolver</i></p>"
                
                self.report_text.setHtml(report)
            else:
                QMessageBox.critical(self, "Error", "Error al obtener reporte")
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error: {str(e)}")
    
    def show_most_rented_report(self):
        try:
            response = requests.get(f"{self.api_url}/reports/most-rented")
            if response.status_code == 200:
                data = response.json()
                
                report = "<h2>DVDs Más Rentados</h2><hr>"
                report += f"<p><b>Total de DVDs:</b> {data['total_dvds']}</p>"
                
                if data['dvds']:
                    report += "<table border='1' cellpadding='5' cellspacing='0' width='100%'>"
                    report += "<tr><th>Posición</th><th>DVD</th><th>Género</th><th>Veces Rentado</th></tr>"
                    
                    for i, dvd in enumerate(data['dvds'], 1):
                        report += f"<tr>"
                        report += f"<td><b>{i}</b></td>"
                        report += f"<td>{dvd['title']}</td>"
                        report += f"<td>{dvd['genre']}</td>"
                        report += f"<td><b>{dvd['rental_count']}</b></td>"
                        report += f"</tr>"
                    
                    report += "</table>"
                else:
                    report += "<p><i>No hay datos de rentas</i></p>"
                
                self.report_text.setHtml(report)
            else:
                QMessageBox.critical(self, "Error", "Error al obtener reporte")
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error: {str(e)}")
    
    def show_staff_earnings_report(self):
        try:
            response = requests.get(f"{self.api_url}/reports/staff-earnings")
            if response.status_code == 200:
                data = response.json()
                
                report = "<h2>Ganancias por Miembro del Staff</h2><hr>"
                report += f"<p><b>Total de personal:</b> {data['total_staff']}</p>"
                
                if data['staff']:
                    total_general = sum(s['total_earnings'] for s in data['staff'])
                    
                    report += "<table border='1' cellpadding='5' cellspacing='0' width='100%'>"
                    report += "<tr><th>Nombre</th><th>Posición</th><th>Rentas Realizadas</th><th>Ganancias Totales</th></tr>"
                    
                    for staff in data['staff']:
                        report += f"<tr>"
                        report += f"<td><b>{staff['staff_name']}</b></td>"
                        report += f"<td>{staff['position']}</td>"
                        report += f"<td>{staff['total_rentals']}</td>"
                        report += f"<td><b>${staff['total_earnings']:.2f}</b></td>"
                        report += f"</tr>"
                    
                    report += f"<tr style='background-color: #f0f0f0;'>"
                    report += f"<td colspan='3' align='right'><b>TOTAL GENERAL:</b></td>"
                    report += f"<td><b>${total_general:.2f}</b></td>"
                    report += f"</tr>"
                    
                    report += "</table>"
                else:
                    report += "<p><i>No hay datos de ganancias</i></p>"
                
                self.report_text.setHtml(report)
            else:
                QMessageBox.critical(self, "Error", "Error al obtener reporte")
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error: {str(e)}")

def main():
    app = QApplication(sys.argv)
    window = DVDRentalApp()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()