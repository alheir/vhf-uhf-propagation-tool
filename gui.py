from PyQt6.QtWidgets import QApplication, QMainWindow, QTableWidget, QTableWidgetItem, QSizePolicy
from design import Ui_MainWindow  
from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QVBoxLayout, QPushButton, QComboBox, QMessageBox, QGridLayout, QTableWidget, QTableWidgetItem, QCheckBox, QFileDialog, QFormLayout
from PyQt6.QtCore import pyqtSlot
from matplotlib import pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.backend_bases import MouseEvent
from PyQt6.QtCore import pyqtSlot
from PyQt6.QtWidgets import QVBoxLayout
from calculations import PropagationCalculator
import numpy as np
import mplcursors
import csv

PLOT_Y_MARGIN = 5
PLOT_Y_MARGIN_FACTOR = 0.1
PLOT_X_MARGIN_FACTOR = 0.05

class Cursor:
    """
    A cross hair cursor.
    """
    def __init__(self, ax):
        self.ax = ax
        self.horizontal_line = ax.axhline(color='w', lw=0.8, ls='--')
        self.vertical_line = ax.axvline(color='w', lw=0.8, ls='--')
        # text location in axes coordinates
        #self.text = ax.text(0.72, 0.9, '', transform=ax.transAxes)

    def set_cross_hair_visible(self, visible):
        need_redraw = self.horizontal_line.get_visible() != visible
        self.horizontal_line.set_visible(visible)
        self.vertical_line.set_visible(visible)
        #self.text.set_visible(visible)
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
            #self.text.set_text(f'x={x:1.2f}, y={y:1.2f}')
            self.ax.figure.canvas.draw()


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        # plt.style.use('dark_background')
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)  # Set up the UI
        
        self.figure1 = plt.figure()
        self.canvas1 = FigureCanvas(self.figure1)
        self.toolbar1 = NavigationToolbar(self.canvas1, self)
        layout1 = QVBoxLayout()
        layout1.addWidget(self.toolbar1)
        layout1.addWidget(self.canvas1)
        self.ui.main_layout.addLayout(layout1, 0, 1)
        self.figure1.set_constrained_layout(True)
        
        self.figure2 = plt.figure()
        self.canvas2 = FigureCanvas(self.figure2)
        self.toolbar2 = NavigationToolbar(self.canvas2, self)      
        layout2 = QVBoxLayout()
        layout2.addWidget(self.toolbar2)
        layout2.addWidget(self.canvas2)
        self.ui.main_layout.addLayout(layout2, 0, 2)
        self.figure2.set_constrained_layout(True)
        
        self.figure3 = plt.figure()
        self.canvas3 = FigureCanvas(self.figure3)
        self.toolbar3 = NavigationToolbar(self.canvas3, self)       
        layout3 = QVBoxLayout()
        layout3.addWidget(self.toolbar3)
        layout3.addWidget(self.canvas3)
        self.ui.main_layout.addLayout(layout3, 1, 1)
        self.figure3.set_constrained_layout(True)
        
        self.figure4 = plt.figure()
        self.canvas4 = FigureCanvas(self.figure4)
        self.toolbar4 = NavigationToolbar(self.canvas4, self)
        layout4 = QVBoxLayout()
        layout4.addWidget(self.toolbar4)
        layout4.addWidget(self.canvas4)
        self.ui.main_layout.addLayout(layout4, 1, 2)
        self.figure4.set_constrained_layout(True)
        

        
        self.table1 = QTableWidget()
        #self.table1.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.ui.table_layout.addWidget(self.table1)

        self.table2 = QTableWidget()
        self.ui.table_layout.addWidget(self.table2)
        
        self.ui.calculate_button.clicked.connect(self.calculate)
        
        self.ui.pushExp1.clicked.connect(lambda: self.export_table_to_csv(self.table1, 'vs_distancia.csv'))
        self.ui.pushExp2.clicked.connect(lambda: self.export_table_to_csv(self.table2, 'vs_altura.csv'))
        
        self.metadata_str = ''
    
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
            
            if distance_start == 0: distance_start = distance_step
            
            antenna_type_map = {
                'Dipolo λ/2': 0,          # g = 1.641
                'Monopolo λ/4': 1,    # g = 3.282
                'Isotrópica': 2                                 # g = 1
            }
            
            antenna_pol_map = {
                'Horizontal': 0,         
                'Vertical': 1,
            }
            
            antenna_type = antenna_type_map[self.ui.antenna_type_input.currentText()]
            antenna_pol = antenna_pol_map[self.ui.antenna_pol_input.currentText()]
            
            conductivity = float(self.ui.conductivity_input.text())
            permitivity = float(self.ui.permittivity_input.text())
            roughness = float(self.ui.terrain_roughness_input.text())
            
            earth_radius_factor = float(self.ui.earth_radius_factor_input.text())

            calculator = PropagationCalculator(freq, 
                                               tx_power, 
                                               conductivity, 
                                               permitivity, 
                                               roughness, 
                                               antenna_type,
                                               antenna_pol,
                                               earth_radius_factor)
            
            calculator.calculate_calc_los(height_tx, height_rx)
            LOS = calculator.calcualte_get_los()
            
            #############################
            
            # punto a punto
            # E_total, P_r = calculator.calculate_point_to_point(height_tx, height_rx, distance_end)

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
            distances, E_totals, P_rs, E_fss, P_r_fss = calculator.calculate_variation_with_distance(height_tx, height_rx, distance_start, distance_end, distance_step)
            
            # V/m a dBuV/cm
            E_totals = [20 * np.log10(e_tot * 1e6 / 100e0) for e_tot in E_totals]
            E_fss = [20 * np.log10(e_fs * 1e6 / 100e0) for e_fs in E_fss]

            # W a dBm 
            P_rs = [10 * np.log10(p * 1e3) for p in P_rs]
            P_r_fss = [10 * np.log10(p_fs * 1e3) for p_fs in P_r_fss]

            # gráfico de potencia recibida vs distancia
            self.figure1.clear()
            ax1 = self.figure1.add_subplot(111)
            ax1.plot(distances / 1000, P_rs, color='r')  # Convertir de metros a km
            ax1.plot(distances / 1000, P_r_fss, label='FS', color='b')  # Convertir de metros a km
            mplcursors.cursor() 
            ax1.set_title('Potencia recibida vs Distancia')
            ax1.set_xlabel('Distancia (km)')
            ax1.set_ylabel('Potencia recibida (dBm)')
            ax1.set_ylim(bottom=np.min(P_rs) - (np.max(P_r_fss) - np.min(P_rs))*PLOT_Y_MARGIN_FACTOR, top=np.max(P_r_fss) + (np.max(P_r_fss) - np.min(P_rs))*PLOT_Y_MARGIN_FACTOR)
            if self.ui.scatter_checkbox.isChecked():
                ax1.scatter(distances / 1000, P_rs, color='r', marker='x', alpha=0.5)
                ax1.scatter(distances / 1000, P_r_fss, color='b', marker='o', alpha=0.5)
                
            if distance_end >= LOS:
                ax1.axvline(x=LOS / 1000, color='g', linestyle='--')
            
            ax1.set_xlim(left=(distance_start / 1000) - (distance_end/1000 - distance_start/1000)*PLOT_X_MARGIN_FACTOR, right=(distance_end / 1000) + (distance_end/1000 - distance_start/1000)*PLOT_X_MARGIN_FACTOR)
            ax1.legend()
                     
            ax1.grid()
            textstr = '\n'.join((
                f'f: {freq / 1e6:.2f} MHz',
                f'ht: {height_tx:.1f} m',
                f'hr: {height_rx:.1f} m',
                f'Pt: {tx_power:.2f} W',
                f'K: {earth_radius_factor:.3f}',
                f'hrms: {roughness:.2f} m',
                f'σ: {conductivity:.1e} S/m',
                f'εr : {permitivity:.0f}',
                f'Pol: {self.ui.antenna_pol_input.currentText()}',
                f'Ant: {self.ui.antenna_type_input.currentText()}',
                f'',
                f'Rad hor: {LOS / 1000:.1f} km'
            ))

            props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
            ax1.text(0.96, 0.96, textstr, transform=ax1.transAxes, fontsize=8,
                     verticalalignment='top', horizontalalignment='right', bbox=props)
            
            
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
            ax2.set_ylabel('Campo eléctrico (dBuV/cm)')

            ax2.set_ylim(bottom=np.min(E_totals) - (np.max(E_totals) - np.min(E_totals))*PLOT_Y_MARGIN_FACTOR, top=np.max(E_totals) + (np.max(E_totals) - np.min(E_totals))*PLOT_Y_MARGIN_FACTOR)
            if self.ui.scatter_checkbox.isChecked():
                ax2.scatter(distances / 1000, E_totals, color='red', marker='x', alpha=0.5)
            ax2.grid()
            
            if distance_end >= LOS:
                ax2.axvline(x=LOS / 1000, color='g', linestyle='--')
                
            ax2.set_xlim(left=(distance_start / 1000) - (distance_end/1000 - distance_start/1000)*PLOT_X_MARGIN_FACTOR, right=(distance_end / 1000) + (distance_end/1000 - distance_start/1000)*PLOT_X_MARGIN_FACTOR)

            ax2.text(0.96, 0.96, textstr, transform=ax2.transAxes, fontsize=8,
                     verticalalignment='top', horizontalalignment='right', bbox=props)
            
            cursor2 = Cursor(ax2)
            self.canvas2.mpl_connect('motion_notify_event', cursor2.on_mouse_move)
            
            self.canvas2.draw()
            
            # tabla de variación con la distancia
            self.table1.setRowCount(len(distances))
            self.table1.setColumnCount(3)
            self.table1.setHorizontalHeaderLabels(['Distancia (km)', 'Potencia recibida (dBm)', 'Campo eléctrico (dBuV/cm)'])
            for i in range(len(distances)):
                self.table1.setItem(i, 0, QTableWidgetItem(f'{distances[i] / 1000:.2e}'))
                self.table1.setItem(i, 1, QTableWidgetItem(f'{P_rs[i]:.2e}'))
                self.table1.setItem(i, 2, QTableWidgetItem(f'{E_totals[i]:.2e}'))
            self.table1.resizeColumnsToContents()
            
            #############################
            
            #############################
            
            # qué antena variar
            vary_tx = self.ui.height_vary_input.currentText() == 'Tx'

            # variación con la altura de la antena
            if vary_tx:
                heights, E_totals_height, P_rs_height = calculator.calculate_variation_with_height(1, 2 * np.max([height_rx, height_tx]), height_step, height_rx, vary_tx=True)
                fixed_height = height_rx
                fixed_label = 'Altura de la antena Rx'
            else:
                heights, E_totals_height, P_rs_height = calculator.calculate_variation_with_height(1, 2 * np.max([height_rx, height_tx]), height_step, height_tx, vary_tx=False)
                fixed_height = height_tx
                fixed_label = 'Altura de la antena Tx'
            
            # V/m a dBuV/cm 
            E_totals_height = [20 * np.log10(e_tot * 1e6 / 100e0) for e_tot in E_totals_height]  
            
            # W a dBm  
            P_rs_height = [10 * np.log10(p * 1e3) for p in P_rs_height]
            
            # gráfico de potencia recibida vs altura de la antena
            self.figure3.clear()
            ax3 = self.figure3.add_subplot(111)
            ax3.plot(heights, P_rs_height)
            mplcursors.cursor() 
            ax3.axvline(x=fixed_height, color='r', linestyle='--', label=f'{fixed_label}')
            ax3.set_title(f'Potencia recibida vs Altura de la antena {self.ui.height_vary_input.currentText()}')
            ax3.set_xlabel(f'Altura de la antena {self.ui.height_vary_input.currentText()} (m)')
            ax3.set_ylabel('Potencia recibida (dBm)')
            ax3.set_ylim(bottom=np.min(P_rs_height) - (np.max(P_rs_height) - np.min(P_rs_height))*PLOT_Y_MARGIN_FACTOR, top=np.max(P_rs_height) + (np.max(P_rs_height) - np.min(P_rs_height))*PLOT_Y_MARGIN_FACTOR)
            if self.ui.scatter_checkbox.isChecked():
                ax3.scatter(heights, P_rs_height, color='red', marker='x', alpha=0.5)
            ax3.legend(fontsize=8)
            ax3.grid()
            
            ax3.set_xlim(left=(heights[0]) - (heights[-1] - heights[0])*PLOT_X_MARGIN_FACTOR, right=(heights[-1]) + (heights[-1] - heights[0])*PLOT_X_MARGIN_FACTOR)
            
            textstr += f'\nd: {distances[-1] / 1000:.1F} km'
            ax3.text(0.98, 0.96, textstr, transform=ax3.transAxes, fontsize=8,
                     verticalalignment='top', horizontalalignment='right', bbox=props)
            
            self.figure3.tight_layout()
            
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
            ax4.set_ylabel('Campo eléctrico (dBuV/cm)')
            ax4.set_ylim(bottom=np.min(E_totals_height) - (np.max(E_totals_height) - np.min(E_totals_height))*PLOT_Y_MARGIN_FACTOR, top=np.max(E_totals_height) + (np.max(E_totals_height) - np.min(E_totals_height))*PLOT_Y_MARGIN_FACTOR)
            if self.ui.scatter_checkbox.isChecked():
                ax4.scatter(heights, E_totals_height, color='red', marker='x')
            ax4.legend(fontsize=8)
            ax4.grid()
            
            ax4.set_xlim(left=(heights[0]) - (heights[-1] - heights[0])*PLOT_X_MARGIN_FACTOR, right=(heights[-1]) + (heights[-1] - heights[0])*PLOT_X_MARGIN_FACTOR)
            
            ax4.text(0.98, 0.96, textstr, transform=ax4.transAxes, fontsize=8,
                     verticalalignment='top', horizontalalignment='right', bbox=props)           
            
            cursor4 = Cursor(ax4)
            self.canvas4.mpl_connect('motion_notify_event', cursor4.on_mouse_move)
            
            self.canvas4.draw()
            
            # tabla de variación con la altura
            self.table2.setRowCount(len(heights))
            self.table2.setColumnCount(3)
            self.table2.setHorizontalHeaderLabels(['Altura (m)', 'Potencia recibida (dBm)', 'Campo eléctrico (dBuV/cm)'])
            for i in range(len(heights)):
                self.table2.setItem(i, 0, QTableWidgetItem(f'{heights[i]:.2e}'))
                self.table2.setItem(i, 1, QTableWidgetItem(f'{P_rs_height[i]:.2e}'))
                self.table2.setItem(i, 2, QTableWidgetItem(f'{E_totals_height[i]:.2e}'))
            self.table2.resizeColumnsToContents()
            
        except ValueError:
            #self.show_error_message(
            #    "Error", "Por favor, ingrese valores numéricos válidos en todos los campos.")
            print('error xd')

    def export_table_to_csv(self, table, default_filename):
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getSaveFileName(self, "Guardar tabla como CSV", default_filename, "CSV Files (*.csv);;All Files (*)", options=options)
        if file_path:
            with open(file_path, 'w', newline='') as file:
                writer = csv.writer(file)
                # Escribir encabezados
                headers = [table.horizontalHeaderItem(i).text() for i in range(table.columnCount())]
                writer.writerow(headers)
                # Escribir datos de la tabla
                for row in range(table.rowCount()):
                    row_data = [table.item(row, col).text() if table.item(row, col) is not None else '' for col in range(table.columnCount())]
                    writer.writerow(row_data)
                           
                # Escribir metadata
                writer.writerow([])
                writer.writerow(['Metadata'])
                writer.writerow([self.metadata_str])
    