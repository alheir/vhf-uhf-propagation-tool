import numpy as np
import matplotlib.pyplot as plt

def calculate_received_power(freq, tx_power, height_tx, height_rx, distance):
    """
    Cálculo simplificado de la potencia recibida en dBm.
    """
    wavelength = 300 / freq  # Frecuencia en MHz (convertida a longitud de onda en metros)
    path_loss = 20 * np.log10(distance / wavelength)  # Pérdida de propagación en espacio libre
    received_power = tx_power - path_loss  # Potencia recibida en dBm
    return received_power

def calculate_electric_field(received_power):
    """
    Cálculo simplificado del campo eléctrico basado en la potencia recibida.
    """
    E_field = np.sqrt(10**(received_power / 10) * 50)  # Asumiendo 50 ohm de impedancia
    return E_field

def plot_power_vs_distance(distances, power_values):
    """
    Generar un gráfico de la potencia recibida en función de la distancia.
    """
    plt.plot(distances / 1000, power_values)  # Convertir metros a km para el gráfico
    plt.xlabel('Distancia (km)')
    plt.ylabel('Potencia Recibida (dBm)')
    plt.title('Potencia recibida vs Distancia')
    plt.grid(True)
    plt.show()
