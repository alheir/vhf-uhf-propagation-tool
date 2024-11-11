from PyQt6.QtWidgets import QWidget, QLabel, QLineEdit, QVBoxLayout, QPushButton, QComboBox, QMessageBox, QGridLayout, QTableWidget, QTableWidgetItem, QCheckBox
from PyQt6.QtCore import pyqtSlot
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
import numpy as np
from calculations import PropagationCalculator

class PropagationCalculatorGUI(QWidget):
    def __init__(self):
        super().__init__()

        # Configuración básica de la ventana
        self.setWindowTitle('VHF/UHF Propagation Calculator')
        self.setGeometry(100, 100, 1000, 700)

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
        self.antenna_type_input.addItems(
            ['Dipolo de media longitud de onda', 'Monopolo de cuarto de longitud de onda', 'Isotrópica'])
        self.antenna_type_input.setCurrentIndex(0)  # Valor por defecto

        self.polarization_label = QLabel('Polarización de las antenas:')
        self.polarization_input = QComboBox()
        self.polarization_input.addItems(['Horizontal', 'Vertical'])
        self.polarization_input.setCurrentIndex(0)  # Valor por defecto

        self.earth_radius_factor_label = QLabel(
            'Factor efectivo del radio terrestre:')
        self.earth_radius_factor_input = QLineEdit()
        self.earth_radius_factor_input.setText('1.3333')  # Valor por defecto

        self.terrain_roughness_label = QLabel('Rugosidad del terreno:')
        self.terrain_roughness_input = QLineEdit()
        self.terrain_roughness_input.setText('0.1')  # Valor por defecto

        self.distance_start_label = QLabel('Distancia inicial Tx (km):')
        self.distance_start_input = QLineEdit()
        self.distance_start_input.setText('0')  # Valor por defecto

        self.distance_end_label = QLabel('Distancia final Rx (km):')
        self.distance_end_input = QLineEdit()
        self.distance_end_input.setText('10')  # Valor por defecto

        self.distance_step_label = QLabel('Paso de avance en distancia (km):')
        self.distance_step_input = QLineEdit()
        self.distance_step_input.setText('1')  # Valor por defecto

        self.conductivity_label = QLabel('Conductividad del terreno (S/m):')
        self.conductivity_input = QLineEdit()
        self.conductivity_input.setText('0.01')  # Valor por defecto

        self.permittivity_label = QLabel('Permitividad relativa del terreno:')
        self.permittivity_input = QLineEdit()
        self.permittivity_input.setText('1')  # Valor por defecto
        
        self.height_step_label = QLabel('Paso de avance en altura (m):')
        self.height_step_input = QLineEdit()
        self.height_step_input.setText('1')  # Valor por defecto

        self.height_vary_label = QLabel('Antena a variar en altura:')
        self.height_vary_input = QComboBox()
        self.height_vary_input.addItems(['Tx', 'Rx'])
        self.height_vary_input.setCurrentIndex(0)  # Valor por defecto
        
        self.scatter_checkbox = QCheckBox('Mostrar puntos en los gráficos')
        self.scatter_checkbox.setChecked(True)  # Valor por defecto

        self.power_unit_label = QLabel('Unidad de potencia:')
        self.power_unit_input = QComboBox()
        self.power_unit_input.addItems(['W', 'dBm'])
        self.power_unit_input.setCurrentIndex(0)  # Valor por defecto

        self.calculate_button = QPushButton('Calcular')
        self.calculate_button.clicked.connect(self.calculate)

        self.received_power_label = QLabel('Potencia recibida (W):')
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
        input_layout.addWidget(self.height_step_label)
        input_layout.addWidget(self.height_step_input)
        input_layout.addWidget(self.height_vary_label)
        input_layout.addWidget(self.height_vary_input)
        input_layout.addWidget(self.scatter_checkbox)
        input_layout.addWidget(self.power_unit_label)
        input_layout.addWidget(self.power_unit_input)
        input_layout.addWidget(self.calculate_button)
        input_layout.addWidget(self.received_power_label)
        input_layout.addWidget(self.electric_field_label)

        # Crear layout principal
        main_layout = QGridLayout()
        main_layout.addLayout(input_layout, 0, 0, 2, 1)  # Ocupa dos filas

        # Ajustar el ancho de las columnas
        main_layout.setColumnStretch(0, 1)  # Columna de inputs
        main_layout.setColumnStretch(1, 3)  # Columna de gráficos
        main_layout.setColumnStretch(2, 3)  # Columna de gráficos

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
        
        self.figure5 = plt.figure()
        self.canvas5 = FigureCanvas(self.figure5)
        main_layout.addWidget(self.canvas5, 2, 1, 1, 2)  # Ocupa dos columnas

        # Crear tablas
        self.table1 = QTableWidget()
        main_layout.addWidget(self.table1, 3, 1)

        self.table2 = QTableWidget()
        main_layout.addWidget(self.table2, 3, 2)

        self.setLayout(main_layout)

    @pyqtSlot()
    def calculate(self):
        try:
            freq = float(self.frequency_input.text()) * 1e6 # MHz a Hz
            tx_power = float(self.power_input.text())
            height_tx = float(self.tx_height_input.text())
            height_rx = float(self.rx_height_input.text())
            distance_start = float(self.distance_start_input.text()) * 1000 # km a m
            distance_end = float(self.distance_end_input.text()) * 1000 # km a m
            distance_step = float(self.distance_step_input.text()) * 1000 # km a m
            height_step = float(self.height_step_input.text())
            
            antenna_type_map = {
                'Dipolo de media longitud de onda': 0,
                'Monopolo de cuarto de longitud de onda': 1,
                'Isotrópica': 2
            }
            polarization_map = {
                'Horizontal': 0,
                'Vertical': 1
            }
            
            antenna_type = antenna_type_map[self.antenna_type_input.currentText()]
            polarization = polarization_map[self.polarization_input.currentText()]
            
            conductivity = float(self.conductivity_input.text())
            permitivity = float(self.permittivity_input.text())
            roughness = float(self.terrain_roughness_input.text())
            
            antenna_type = self.antenna_type_input.currentText()
            polarization = self.polarization_input.currentText()
            earth_radius_factor = float(self.earth_radius_factor_input.text())

            calculator = PropagationCalculator(freq, 
                                               tx_power, 
                                               conductivity, 
                                               permitivity, 
                                               roughness, 
                                               antenna_type, 
                                               polarization, 
                                               earth_radius_factor)
            
            #############################
            
            # punto a punto
            E_total, P_r = calculator.calculate_point_to_point(height_tx, height_rx, distance_end - distance_start)

            # punto a punto en la GUI
            self.received_power_label.setText(
                f'Potencia recibida (W): {P_r:.2e}')
            self.electric_field_label.setText(
                f'Campo eléctrico (V/m): {E_total:.2e}')
            
            #############################
            
            #############################
            
            # variación con la distancia
            distances, E_totals, P_rs = calculator.calculate_variation_with_distance(height_tx, height_rx, distance_start, distance_end, distance_step)

            # W a dBm si es necesario
            if self.power_unit_input.currentText() == 'dBm':
                P_rs = [10 * np.log10(p * 1e3) for p in P_rs]

            # gráfico de potencia recibida vs distancia
            self.figure1.clear()
            ax1 = self.figure1.add_subplot(111)
            ax1.plot(distances / 1000, P_rs)  # Convertir de metros a km
            ax1.set_title('Potencia recibida vs Distancia')
            ax1.set_xlabel('Distancia (km)')
            ax1.set_ylabel(f'Potencia recibida ({self.power_unit_input.currentText()})')
            if self.scatter_checkbox.isChecked():
                ax1.scatter(distances / 1000, P_rs, color='red', marker='x', alpha=0.5)
            ax1.grid()
            self.canvas1.draw()

            # gráfico de campo eléctrico vs distancia
            self.figure2.clear()
            ax2 = self.figure2.add_subplot(111)
            ax2.plot(distances / 1000, E_totals)  # Convertir de metros a km
            ax2.set_title('Campo eléctrico vs Distancia')
            ax2.set_xlabel('Distancia (km)')
            ax2.set_ylabel('Campo eléctrico (V/m)')
            ax2.set_yscale('log')
            if self.scatter_checkbox.isChecked():
                ax2.scatter(distances / 1000, E_totals, color='red', marker='x', alpha=0.5)
            ax2.grid()
            self.canvas2.draw()
            
            # tabla de variación con la distancia
            self.table1.setRowCount(len(distances))
            self.table1.setColumnCount(3)
            self.table1.setHorizontalHeaderLabels(['Distancia (km)', 'Potencia recibida (W)', 'Campo eléctrico (V/m)'])
            for i in range(len(distances)):
                self.table1.setItem(i, 0, QTableWidgetItem(f'{distances[i] / 1000:.2e}'))
                self.table1.setItem(i, 1, QTableWidgetItem(f'{P_rs[i]:.2e}'))
                self.table1.setItem(i, 2, QTableWidgetItem(f'{E_totals[i]:.2e}'))
            
            #############################
            
            #############################
            
            # qué antena variar
            vary_tx = self.height_vary_input.currentText() == 'Tx'

            # variación con la altura de la antena
            if vary_tx:
                heights, E_totals_height, P_rs_height = calculator.calculate_variation_with_height(1, 2 * np.max([height_rx, height_tx]), height_step, height_rx, distance_end - distance_start, vary_tx=True)
                fixed_height = height_rx
                fixed_label = 'Altura de la antena Rx'
            else:
                heights, E_totals_height, P_rs_height = calculator.calculate_variation_with_height(1, 2 * np.max([height_rx, height_tx]), height_step, height_tx, distance_end - distance_start, vary_tx=False)
                fixed_height = height_tx
                fixed_label = 'Altura de la antena Tx'
            
            # W a dBm si es necesario
            if self.power_unit_input.currentText() == 'dBm':
                P_rs_height = [10 * np.log10(p * 1e3) for p in P_rs_height]  # Convertir W a dBm
            
            # gráfico de potencia recibida vs altura de la antena
            self.figure3.clear()
            ax3 = self.figure3.add_subplot(111)
            ax3.plot(heights, P_rs_height)
            ax3.axvline(x=fixed_height, color='r', linestyle='--', label=f'{fixed_label}')
            ax3.set_title(f'Potencia recibida vs Altura de la antena {self.height_vary_input.currentText()}')
            ax3.set_xlabel(f'Altura de la antena {self.height_vary_input.currentText()} (m)')
            ax3.set_ylabel(f'Potencia recibida ({self.power_unit_input.currentText()})')
            if self.scatter_checkbox.isChecked():
                ax3.scatter(heights, P_rs_height, color='red', marker='x', alpha=0.5)
            ax3.legend()
            ax3.grid()
            self.canvas3.draw()

            # gráfico de campo eléctrico vs altura de la antena
            self.figure4.clear()
            ax4 = self.figure4.add_subplot(111)
            ax4.plot(heights, E_totals_height)
            ax4.axvline(x=fixed_height, color='r', linestyle='--', label=f'{fixed_label}')
            ax4.set_title(f'Campo eléctrico vs Altura de la antena {self.height_vary_input.currentText()}')
            ax4.set_xlabel(f'Altura de la antena {self.height_vary_input.currentText()} (m)')
            ax4.set_ylabel('Campo eléctrico (V/m)')
            ax4.set_yscale('log')
            if self.scatter_checkbox.isChecked():
                ax4.scatter(heights, E_totals_height, color='red', marker='x')
            ax4.legend()
            ax4.grid()
            self.canvas4.draw()
            
            # tabla de variación con la altura
            self.table2.setRowCount(len(heights))
            self.table2.setColumnCount(3)
            self.table2.setHorizontalHeaderLabels(['Altura (m)', 'Potencia recibida (W)', 'Campo eléctrico (V/m)'])
            for i in range(len(heights)):
                self.table2.setItem(i, 0, QTableWidgetItem(f'{heights[i]:.2e}'))
                self.table2.setItem(i, 1, QTableWidgetItem(f'{P_rs_height[i]:.2e}'))
                self.table2.setItem(i, 2, QTableWidgetItem(f'{E_totals_height[i]:.2e}'))
            
            
            # esquema 2D de las antenas
            self.figure5.clear()
            ax5 = self.figure5.add_subplot(111)
            ax5.plot([0, distance_end / 1000], [height_tx, height_rx], 'bo-', label='Trayectoria directa de la señal')
            ax5.scatter([0], [height_tx], color='blue', label='Antena Tx')
            ax5.scatter([distance_end / 1000], [height_rx], color='green', label='Antena Rx')
            ax5.set_title('Esquema 2D de las antenas')
            ax5.set_xlabel('Distancia (km)')
            ax5.set_ylabel('Altura (m)')
            ax5.set_ylim([0, max(height_tx, height_rx) + 10]) 
            ax5.legend()
            ax5.grid()
            self.canvas5.draw()

        except ValueError:
            self.show_error_message(
                "Error", "Por favor, ingrese valores numéricos válidos en todos los campos.")

    def show_error_message(self, title, message):
        QMessageBox.critical(self, title, message)