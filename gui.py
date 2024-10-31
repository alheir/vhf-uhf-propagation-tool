from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QVBoxLayout, QPushButton, QComboBox, QMessageBox, QGridLayout
from PyQt6.QtCore import pyqtSlot
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
import numpy as np
from calculations import calculate_received_power, calculate_electric_field, plot_power_vs_distance

class PropagationCalculator(QWidget):
    def __init__(self):
        super().__init__()

        # Configuración básica de la ventana
        self.setWindowTitle('VHF/UHF Propagation Calculator')
        self.setGeometry(100, 100, 800, 500)

        # Crear widgets
        self.frequency_label = QLabel('Frecuencia (MHz):')
        self.frequency_input = QLineEdit()
        self.frequency_input.setText('100')  # Valor por defecto

        self.power_label = QLabel('Potencia (W):')
        self.power_input = QLineEdit()
        self.power_input.setText('10')  # Valor por defecto

        self.tx_height_label = QLabel('Altura de la antena Tx (m):')
        self.tx_height_input = QLineEdit()
        self.tx_height_input.setText('10')  # Valor por defecto

        self.rx_height_label = QLabel('Altura de la antena Rx (m):')
        self.rx_height_input = QLineEdit()
        self.rx_height_input.setText('10')  # Valor por defecto

        self.antenna_type_label = QLabel('Tipo de antena:')
        self.antenna_type_input = QComboBox()
        self.antenna_type_input.addItems(['Dipolo de media longitud de onda', 'Monopolo de cuarto de longitud de onda', 'Isotrópica'])
        self.antenna_type_input.setCurrentIndex(0)  # Valor por defecto

        self.polarization_label = QLabel('Polarización de las antenas:')
        self.polarization_input = QComboBox()
        self.polarization_input.addItems(['Horizontal', 'Vertical'])
        self.polarization_input.setCurrentIndex(0)  # Valor por defecto

        self.earth_radius_factor_label = QLabel('Factor efectivo del radio terrestre:')
        self.earth_radius_factor_input = QLineEdit()
        self.earth_radius_factor_input.setText('1')  # Valor por defecto

        self.terrain_roughness_label = QLabel('Rugosidad del terreno:')
        self.terrain_roughness_input = QLineEdit()
        self.terrain_roughness_input.setText('0.1')  # Valor por defecto

        self.distance_start_label = QLabel('Distancia inicial (km):')
        self.distance_start_input = QLineEdit()
        self.distance_start_input.setText('1')  # Valor por defecto

        self.distance_end_label = QLabel('Distancia final (km):')
        self.distance_end_input = QLineEdit()
        self.distance_end_input.setText('10')  # Valor por defecto

        self.distance_step_label = QLabel('Paso de avance en distancia (km):')
        self.distance_step_input = QLineEdit()
        self.distance_step_input.setText('0.1')  # Valor por defecto

        self.conductivity_label = QLabel('Conductividad del terreno (S/m):')
        self.conductivity_input = QLineEdit()
        self.conductivity_input.setText('0.01')  # Valor por defecto

        self.permittivity_label = QLabel('Permitividad del terreno:')
        self.permittivity_input = QLineEdit()
        self.permittivity_input.setText('15')  # Valor por defecto

        self.calculate_button = QPushButton('Calcular')
        self.calculate_button.clicked.connect(self.calculate)

        self.received_power_label = QLabel('Potencia recibida (dBm):')
        self.electric_field_label = QLabel('Campo eléctrico (V/m):')

        # Crear layout y agregar widgets
        input_layout = QVBoxLayout()
        input_layout.addWidget(self.frequency_label)
        input_layout.addWidget(self.frequency_input)
        input_layout.addWidget(self.power_label)
        input_layout.addWidget(self.power_input)
        input_layout.addWidget(self.tx_height_label)
        input_layout.addWidget(self.tx_height_input)
        input_layout.addWidget(self.rx_height_label)
        input_layout.addWidget(self.rx_height_input)
        input_layout.addWidget(self.antenna_type_label)
        input_layout.addWidget(self.antenna_type_input)
        input_layout.addWidget(self.polarization_label)
        input_layout.addWidget(self.polarization_input)
        input_layout.addWidget(self.earth_radius_factor_label)
        input_layout.addWidget(self.earth_radius_factor_input)
        input_layout.addWidget(self.terrain_roughness_label)
        input_layout.addWidget(self.terrain_roughness_input)
        input_layout.addWidget(self.distance_start_label)
        input_layout.addWidget(self.distance_start_input)
        input_layout.addWidget(self.distance_end_label)
        input_layout.addWidget(self.distance_end_input)
        input_layout.addWidget(self.distance_step_label)
        input_layout.addWidget(self.distance_step_input)
        input_layout.addWidget(self.conductivity_label)
        input_layout.addWidget(self.conductivity_input)
        input_layout.addWidget(self.permittivity_label)
        input_layout.addWidget(self.permittivity_input)
        input_layout.addWidget(self.calculate_button)
        input_layout.addWidget(self.received_power_label)
        input_layout.addWidget(self.electric_field_label)

        # Crear layout principal
        main_layout = QGridLayout()
        main_layout.addLayout(input_layout, 0, 0, 2, 1)  # Ocupa dos filas

        # Crear figuras de Matplotlib
        self.figure1 = plt.figure()
        self.canvas1 = FigureCanvas(self.figure1)
        main_layout.addWidget(self.canvas1, 0, 1)

        self.figure2 = plt.figure()
        self.canvas2 = FigureCanvas(self.figure2)
        main_layout.addWidget(self.canvas2, 0, 2)

        self.figure3 = plt.figure()
        self.canvas3 = FigureCanvas(self.figure3)
        main_layout.addWidget(self.canvas3, 1, 1)

        self.figure4 = plt.figure()
        self.canvas4 = FigureCanvas(self.figure4)
        main_layout.addWidget(self.canvas4, 1, 2)

        self.setLayout(main_layout)

    @pyqtSlot()
    def calculate(self):
        try:
            freq = float(self.frequency_input.text())
            tx_power = float(self.power_input.text())
            height_tx = float(self.tx_height_input.text())
            height_rx = float(self.rx_height_input.text())
            distance_start = float(self.distance_start_input.text()) * 1000  # Convertir de km a metros
            distance_end = float(self.distance_end_input.text()) * 1000  # Convertir de km a metros
            distance_step = float(self.distance_step_input.text()) * 1000  # Convertir de km a metros

            # Realizar cálculos
            received_power = calculate_received_power(freq, tx_power, height_tx, height_rx, distance_end)
            electric_field = calculate_electric_field(received_power)

            # Mostrar resultados en la GUI
            self.received_power_label.setText(f'Potencia recibida (dBm): {received_power:.2f}')
            self.electric_field_label.setText(f'Campo eléctrico (V/m): {electric_field:.2f}')

            # Generar gráficos
            distances = np.arange(distance_start, distance_end, distance_step)
            power_values = [calculate_received_power(freq, tx_power, height_tx, height_rx, d) for d in distances]
            electric_field_values = [calculate_electric_field(p) for p in power_values]

            # Gráfico de potencia recibida vs distancia
            self.figure1.clear()
            ax1 = self.figure1.add_subplot(111)
            ax1.plot(distances / 1000, power_values)  # Convertir de metros a km
            ax1.set_title('Potencia recibida vs Distancia')
            ax1.set_xlabel('Distancia (km)')
            ax1.set_ylabel('Potencia recibida (dBm)')
            self.canvas1.draw()

            # Gráfico de campo eléctrico vs distancia
            self.figure2.clear()
            ax2 = self.figure2.add_subplot(111)
            ax2.plot(distances / 1000, electric_field_values)  # Convertir de metros a km
            ax2.set_title('Campo eléctrico vs Distancia')
            ax2.set_xlabel('Distancia (km)')
            ax2.set_ylabel('Campo eléctrico (V/m)')
            self.canvas2.draw()

            # Gráfico de potencia recibida vs altura de la antena Tx
            heights_tx = np.linspace(1, height_tx, 100)
            power_values_tx = [calculate_received_power(freq, tx_power, h, height_rx, distance_end) for h in heights_tx]
            self.figure3.clear()
            ax3 = self.figure3.add_subplot(111)
            ax3.plot(heights_tx, power_values_tx)
            ax3.set_title('Potencia recibida vs Altura de la antena Tx')
            ax3.set_xlabel('Altura de la antena Tx (m)')
            ax3.set_ylabel('Potencia recibida (dBm)')
            self.canvas3.draw()

            # Gráfico de campo eléctrico vs altura de la antena Tx
            electric_field_values_tx = [calculate_electric_field(p) for p in power_values_tx]
            self.figure4.clear()
            ax4 = self.figure4.add_subplot(111)
            ax4.plot(heights_tx, electric_field_values_tx)
            ax4.set_title('Campo eléctrico vs Altura de la antena Tx')
            ax4.set_xlabel('Altura de la antena Tx (m)')
            ax4.set_ylabel('Campo eléctrico (V/m)')
            self.canvas4.draw()

        except ValueError:
            self.show_error_message("Error", "Por favor, ingrese valores numéricos válidos en todos los campos.")

    def show_error_message(self, title, message):
        QMessageBox.critical(self, title, message)