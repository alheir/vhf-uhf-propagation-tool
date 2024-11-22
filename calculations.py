import numpy as np
import matplotlib.pyplot as plt

C = 299792458.0  # velocidad de la luz en m/s
EPSILON_ZERO = 8.854187817e-12  # permitividad del vacío en F/m
MU_ZERO = 4 * np.pi * 1e-7  # permeabilidad magnética del vacío en H/m
ETA_ZERO = MU_ZERO / EPSILON_ZERO  # impedancia característica del vacío en Ohm

GAIN_DIPOLE = 1.641
GAIN_MONOPOLE = 3.282
GAIN_ISOTROPIC = 1

ANTENNA_GAINS = [GAIN_DIPOLE, GAIN_MONOPOLE, GAIN_ISOTROPIC]

EARTH_RADIUS = 6371e3  # radio de la tierra en m

class PropagationCalculator:
    def __init__(self, freq, tx_power, conductivity, permitivity, roughness, antenna_type, pol_angle_tx, pol_angle_rx, earth_radius_factor):
        self.freq = freq
        self.w = 2 * np.pi * self.freq
        self.Beta = self.w / C  # constante de propagación, = 2 * pi / lambda, lambda = c / f
        self.tx_power = tx_power
        self.sigma = conductivity
        self.epsilon_r = permitivity
        self.roughness = roughness
        self.antenna = antenna_type
        self.antenna_tx_gain = ANTENNA_GAINS[int(antenna_type)]
        self.antenna_rx_gain = ANTENNA_GAINS[int(antenna_type)]
        self.pol_angle_tx = pol_angle_tx
        self.pol_angle_rx = pol_angle_rx
        self.earth_radius_factor = earth_radius_factor

    def calculate_point_to_point(self, height_tx, height_rx, distance):
        
        re = self.earth_radius_factor * EARTH_RADIUS
        r = distance  # distancia entre Tx y Rx, sobre la superficie
        ht = height_tx
        hr = height_rx
        
        p = (2 / np.sqrt(3)) * np.sqrt(re * (ht + hr) + r*r/4)
        
        Xi = np.arcsin(2 * re * r * (ht - hr) / (p*p*p))
        
        r1 = r/2 - p * np.sin(Xi)
        r2 = r - r1
        
        phi1 = r1/re
        phi2 = r2/re
        
        R1 = np.sqrt(hr**2 + 4 * re * (re + hr) * (np.sin(phi1 / 2)**2))
        R2 = np.sqrt(ht**2 + 4 * re * (re + ht) * (np.sin(phi2 / 2)**2))
        
        Rd = np.sqrt((ht - hr)**2 + 4 * (re + ht) * (re + hr) * (np.sin((phi1 + phi2) / 2)**2)) # distancia entre Tx y Rx, real
        
        Psi = np.arcsin((ht / R1) - (R1 / (2 * re)))
        
        Delta_R = (4 * R1 * R2 * (np.sin(Psi)**2)) / (R1 + R2 + Rd)     # diferencia de camino físico    
        
        Delta = self.Beta * Delta_R                                     # diferencia de camino óptico
        


        P_t = self.tx_power  # potencia de transmisión
        E_zero = np.sqrt(30 * P_t) / Rd

        epsilon_c = self.epsilon_r - 1j * self.sigma / (self.w * EPSILON_ZERO)


        # Tierra esférica
        D_factor = 1 / np.sqrt(1 + (2 * r1 * r2)/(re * r * np.sin(Psi)))
        
        # Rugosidad
        roughness_factor = np.exp(-2 * (self.Beta * self.roughness * np.sin(Psi))**2)

        # Coeficientes de reflexión
        Gamma_perpendicular = (np.sin(Psi) - np.sqrt(epsilon_c - np.cos(Psi)**2)) / (np.sin(Psi) + np.sqrt(epsilon_c - np.cos(Psi)**2))
        Gamma_paralelo = (epsilon_c * np.sin(Psi) - np.sqrt(epsilon_c - np.cos(Psi)**2)) / (epsilon_c * np.sin(Psi) + np.sqrt(epsilon_c - np.cos(Psi)**2))
    
        Gamma_perpendicular = Gamma_perpendicular * D_factor * roughness_factor
        Gamma_paralelo = Gamma_paralelo * D_factor * roughness_factor
    
    
    
        # Factores de interferencia
        F_i_perpendicular = np.sqrt(1 + np.abs(Gamma_perpendicular)**2 + 2 * np.abs(Gamma_perpendicular) * np.cos(Delta + np.angle(Gamma_perpendicular)))
        F_i_paralelo = np.sqrt(1 + np.abs(Gamma_paralelo)**2 + 2 * np.abs(Gamma_paralelo) * np.cos(Delta + np.angle(Gamma_paralelo)))
        
    
        E_perpendicular = np.abs(E_zero * np.sin(self.pol_angle_tx)) * np.abs(F_i_perpendicular)
        E_paralelo = np.abs(E_zero * np.cos(self.pol_angle_tx)) * np.abs(F_i_paralelo)
        E_total = np.sqrt(E_perpendicular**2 + E_paralelo**2)

        P_r = (np.abs(E_total)**2 / ETA_ZERO) * (C / self.freq)**2 / (4 * np.pi)
        
        # Ganancia de antenas
        P_r = P_r * self.antenna_tx_gain * self.antenna_rx_gain
        
        # PLF
        plf = np.cos(np.deg2rad(self.pol_angle_tx - self.pol_angle_rx))**2
        P_r = P_r * plf

        return E_total, P_r

    def calculate_variation_with_distance(self, height_tx, height_rx, distance_start, distance_end, distance_step):
        distances = np.arange(distance_start, distance_end, distance_step)
        E_totals = []
        P_rs = []

        for distance in distances:
            E_total, P_r = self.calculate_point_to_point(height_tx, height_rx, (distance - distance_start) + distance_step)
            E_totals.append(E_total)
            P_rs.append(P_r)

        return distances, E_totals, P_rs

    def calculate_variation_with_height(self, height_start, height_end, height_step, height_fixed, distance, vary_tx=True):
        heights = np.arange(height_start, height_end, height_step)
        E_totals = []
        P_rs = []

        for height in heights:
            if vary_tx:
                E_total, P_r = self.calculate_point_to_point(height, height_fixed, distance)
            else:
                E_total, P_r = self.calculate_point_to_point(height_fixed, height, distance)
            E_totals.append(E_total)
            P_rs.append(P_r)

        return heights, E_totals, P_rs

    def plot_results(self, x_values, y_values, x_label, y_label, title):
        plt.figure()
        plt.plot(x_values, y_values)
        plt.xlabel(x_label)
        plt.ylabel(y_label)
        plt.title(title)
        plt.grid(True)
        plt.show()