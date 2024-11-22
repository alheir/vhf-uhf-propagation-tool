from PyQt6.QtWidgets import QApplication, QMainWindow, QTableWidget, QTableWidgetItem, QSizePolicy
from design import Ui_MainWindow  
from matplotlib import pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backend_bases import MouseEvent
from PyQt6.QtCore import pyqtSlot
from calculations import PropagationCalculator
import numpy as np
import mplcursors

class Cursor:
    """
    A cross hair cursor.
    """
    def __init__(self, ax):
        self.ax = ax
        self.horizontal_line = ax.axhline(color='w', lw=0.8, ls='--')
        self.vertical_line = ax.axvline(color='w', lw=0.8, ls='--')
        # text location in axes coordinates
        self.text = ax.text(0.72, 0.9, '', transform=ax.transAxes)

    def set_cross_hair_visible(self, visible):
        need_redraw = self.horizontal_line.get_visible() != visible
        self.horizontal_line.set_visible(visible)
        self.vertical_line.set_visible(visible)
        self.text.set_visible(visible)
        return need_redraw

    def on_mouse_move(self, event):
        if not event.inaxes:
            need_redraw = self.set_cross_hair_visible(False)
            if need_redraw:
                self.ax.figure.canvas.draw()
        else:
            self.set_cross_hair_visible(True)
            x, y = event.xdata, event.ydata
            # update the line positions
            self.horizontal_line.set_ydata([y])
            self.vertical_line.set_xdata([x])
            self.text.set_text(f'x={x:1.2f}, y={y:1.2f}')
            self.ax.figure.canvas.draw()


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        plt.style.use('dark_background')
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)  # Set up the UI
        
        self.figure1 = plt.figure()
        self.canvas1 = FigureCanvas(self.figure1)
        self.ui.main_layout.addWidget(self.canvas1, 0, 1)
        
        self.figure2 = plt.figure()
        self.canvas2 = FigureCanvas(self.figure2)
        self.ui.main_layout.addWidget(self.canvas2, 0, 2)
        
        self.figure3 = plt.figure()
        self.canvas3 = FigureCanvas(self.figure3)
        self.ui.main_layout.addWidget(self.canvas3, 1, 1)
        
        self.figure4 = plt.figure()
        self.canvas4 = FigureCanvas(self.figure4)
        self.ui.main_layout.addWidget(self.canvas4, 1, 2)

        
        self.table1 = QTableWidget()
        #self.table1.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.ui.table_layout.addWidget(self.table1)

        self.table2 = QTableWidget()
        self.ui.table_layout.addWidget(self.table2)
        
        self.ui.calculate_button.clicked.connect(self.calculate)
    
    @pyqtSlot()
    def calculate(self):
        try:
            freq = float(self.ui.frequency_input.text()) * 1e6 # MHz a Hz
            tx_power = float(self.ui.power_input.text())
            height_tx = float(self.ui.tx_height_input.text())
            height_rx = float(self.ui.rx_height_input.text())
            distance_start = float(self.ui.distance_start_input.text()) * 1000 # km a m
            distance_end = float(self.ui.distance_end_input.text()) * 1000 # km a m
            distance_step = float(self.ui.distance_step_input.text()) * 1000 # km a m
            height_step = float(self.ui.height_step_input.text())
            
            antenna_type_map = {
                'Dipolo de media longitud de onda': 0,
                'Monopolo de cuarto de longitud de onda': 1,
                'Isotrópica': 2
            }
            polarization_map = {
                'Horizontal': 0,
                'Vertical': 1
            }
            
            antenna_type = antenna_type_map[self.ui.antenna_type_input.currentText()]
            polarization = self.ui.polarization_input.text()
            
            conductivity = float(self.ui.conductivity_input.text())
            permitivity = float(self.ui.permittivity_input.text())
            roughness = float(self.ui.terrain_roughness_input.text())
            
            antenna_type = self.ui.antenna_type_input.currentText()
            polarization = self.ui.polarization_input.text()
            earth_radius_factor = float(self.ui.earth_radius_factor_input.text())

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
            '''
            self.received_power_label.setText(
                f'Potencia recibida (W): {P_r:.2e}')
            self.electric_field_label.setText(
                f'Campo eléctrico (V/m): {E_total:.2e}')
            '''
            #############################
            
            #############################
            
            # variación con la distancia
            distances, E_totals, P_rs = calculator.calculate_variation_with_distance(height_tx, height_rx, distance_start, distance_end, distance_step)

            # W a dBm si es necesario
            if self.ui.power_unit_input.currentText() == 'dBm':
                P_rs = [10 * np.log10(p * 1e3) for p in P_rs]

            # gráfico de potencia recibida vs distancia
            self.figure1.clear()
            ax1 = self.figure1.add_subplot(111)
            ax1.plot(distances / 1000, P_rs)  # Convertir de metros a km
            mplcursors.cursor() 
            ax1.set_title('Potencia recibida vs Distancia')
            ax1.set_xlabel('Distancia (km)')
            ax1.set_ylabel(f'Potencia recibida ({self.ui.power_unit_input.currentText()})')
            if self.ui.scatter_checkbox.isChecked():
                ax1.scatter(distances / 1000, P_rs, color='red', marker='x', alpha=0.5)
            ax1.grid()
            
            
            cursor1 = Cursor(ax1)
            self.canvas1.mpl_connect('motion_notify_event', cursor1.on_mouse_move)
            
            self.canvas1.draw()

            # gráfico de campo eléctrico vs distancia
            self.figure2.clear()
            ax2 = self.figure2.add_subplot(111)
            ax2.plot(distances / 1000, E_totals)  # Convertir de metros a km
            mplcursors.cursor() 
            ax2.set_title('Campo eléctrico vs Distancia')
            ax2.set_xlabel('Distancia (km)')
            ax2.set_ylabel('Campo eléctrico (V/m)')
            ax2.set_yscale('log')
            if self.ui.scatter_checkbox.isChecked():
                ax2.scatter(distances / 1000, E_totals, color='red', marker='x', alpha=0.5)
            ax2.grid()
            
            cursor2 = Cursor(ax2)
            self.canvas2.mpl_connect('motion_notify_event', cursor2.on_mouse_move)
            
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
            vary_tx = self.ui.height_vary_input.currentText() == 'Tx'

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
            if self.ui.power_unit_input.currentText() == 'dBm':
                P_rs_height = [10 * np.log10(p * 1e3) for p in P_rs_height]  # Convertir W a dBm
            
            # gráfico de potencia recibida vs altura de la antena
            self.figure3.clear()
            ax3 = self.figure3.add_subplot(111)
            ax3.plot(heights, P_rs_height)
            mplcursors.cursor() 
            ax3.axvline(x=fixed_height, color='r', linestyle='--', label=f'{fixed_label}')
            ax3.set_title(f'Potencia recibida vs Altura de la antena {self.ui.height_vary_input.currentText()}')
            ax3.set_xlabel(f'Altura de la antena {self.ui.height_vary_input.currentText()} (m)')
            ax3.set_ylabel(f'Potencia recibida ({self.ui.power_unit_input.currentText()})')
            if self.ui.scatter_checkbox.isChecked():
                ax3.scatter(heights, P_rs_height, color='red', marker='x', alpha=0.5)
            ax3.legend()
            ax3.grid()
            
            cursor3 = Cursor(ax3)
            self.canvas3.mpl_connect('motion_notify_event', cursor3.on_mouse_move)
            
            self.canvas3.draw()

            # gráfico de campo eléctrico vs altura de la antena
            self.figure4.clear()
            ax4 = self.figure4.add_subplot(111)
            ax4.plot(heights, E_totals_height)
            mplcursors.cursor() 
            ax4.axvline(x=fixed_height, color='r', linestyle='--', label=f'{fixed_label}')
            ax4.set_title(f'Campo eléctrico vs Altura de la antena {self.ui.height_vary_input.currentText()}')
            ax4.set_xlabel(f'Altura de la antena {self.ui.height_vary_input.currentText()} (m)')
            ax4.set_ylabel('Campo eléctrico (V/m)')
            ax4.set_yscale('log')
            if self.ui.scatter_checkbox.isChecked():
                ax4.scatter(heights, E_totals_height, color='red', marker='x')
            ax4.legend()
            ax4.grid()
            
            cursor4 = Cursor(ax4)
            self.canvas4.mpl_connect('motion_notify_event', cursor4.on_mouse_move)
            
            self.canvas4.draw()
            
            # tabla de variación con la altura
            self.table2.setRowCount(len(heights))
            self.table2.setColumnCount(3)
            self.table2.setHorizontalHeaderLabels(['Altura (m)', 'Potencia recibida (W)', 'Campo eléctrico (V/m)'])
            for i in range(len(heights)):
                self.table2.setItem(i, 0, QTableWidgetItem(f'{heights[i]:.2e}'))
                self.table2.setItem(i, 1, QTableWidgetItem(f'{P_rs_height[i]:.2e}'))
                self.table2.setItem(i, 2, QTableWidgetItem(f'{E_totals_height[i]:.2e}'))
            
        except ValueError:
            #self.show_error_message(
            #    "Error", "Por favor, ingrese valores numéricos válidos en todos los campos.")
            print('error xd')