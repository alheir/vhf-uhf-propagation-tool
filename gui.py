from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QVBoxLayout, QPushButton, QComboBox, QMessageBox
from PyQt6.QtCore import pyqtSlot
import matplotlib.pyplot as plt
import numpy as np
from calculations import calculate_received_power, calculate_electric_field, plot_power_vs_distance

class PropagationCalculator(QWidget):
    def __init__(self):
        super().__init__()

        # Configuración básica de la ventana
        self.setWindowTitle('VHF/UHF Propagation Calculator')
        self.setGeometry(100, 100, 400, 300)

        # Crear layout principal
        layout = QVBoxLayout()

        # Campos de entrada
        self.freq_label = QLabel('Frecuencia (MHz):')
        self.freq_input = QLineEdit()
        layout.addWidget(self.freq_label)
        layout.addWidget(self.freq_input)

        self.power_label = QLabel('Potencia Tx (dBm):')
        self.power_input = QLineEdit()
        layout.addWidget(self.power_label)
        layout.addWidget(self.power_input)

        self.height_tx_label = QLabel('Altura Antena Tx (m):')
        self.height_tx_input = QLineEdit()
        layout.addWidget(self.height_tx_label)
        layout.addWidget(self.height_tx_input)

        self.height_rx_label = QLabel('Altura Antena Rx (m):')
        self.height_rx_input = QLineEdit()
        layout.addWidget(self.height_rx_label)
        layout.addWidget(self.height_rx_input)

        self.distance_label = QLabel('Distancia Tx-Rx (km):')
        self.distance_input = QLineEdit()
        layout.addWidget(self.distance_label)
        layout.addWidget(self.distance_input)

        # Desplegable para el tipo de antena
        self.antenna_type_label = QLabel('Tipo de Antena:')
        self.antenna_type_dropdown = QComboBox()
        self.antenna_type_dropdown.addItems(["Dipolo de media longitud de onda", 
                                             "Monopolo de cuarto de longitud de onda", 
                                             "Isotrópica"])
        layout.addWidget(self.antenna_type_label)
        layout.addWidget(self.antenna_type_dropdown)

        # Botón de cálculo
        self.calculate_button = QPushButton('Calcular')
        self.calculate_button.clicked.connect(self.on_calculate)  # Conectar el botón con el método de cálculo
        layout.addWidget(self.calculate_button)

        # Asignar layout
        self.setLayout(layout)

    @pyqtSlot()
    def on_calculate(self):
        """Método ejecutado cuando se hace clic en el botón 'Calcular'."""
        try:
            # Obtener valores de entrada
            freq = float(self.freq_input.text())
            tx_power = float(self.power_input.text())
            height_tx = float(self.height_tx_input.text())
            height_rx = float(self.height_rx_input.text())
            distance = float(self.distance_input.text()) * 1000  # Convertir de km a metros

            # Realizar cálculos
            received_power = calculate_received_power(freq, tx_power, height_tx, height_rx, distance)
            electric_field = calculate_electric_field(received_power)

            # Mostrar resultados en consola (puedes agregar ventanas emergentes o labels para mostrar en la GUI)
            print(f"Potencia recibida: {received_power:.2f} dBm")
            print(f"Campo eléctrico: {electric_field:.2f} V/m")

            # Generar gráfico de potencia recibida vs distancia (ejemplo)
            distances = np.linspace(1, distance, 100)  # Generar un rango de distancias
            power_values = [calculate_received_power(freq, tx_power, height_tx, height_rx, d) for d in distances]

            plot_power_vs_distance(distances, power_values)

        except ValueError:
            self.show_error_message("Error", "Por favor, ingrese valores numéricos válidos en todos los campos.")

    def show_error_message(self, title, message):
        """Mostrar un mensaje de error si el usuario ingresa datos no válidos."""
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Icon.Warning)
        msg.setWindowTitle(title)
        msg.setText(message)
        msg.exec()