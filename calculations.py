import numpy as np

C = 299792458.0  # velocidad de la luz en m/s
EPSILON_ZERO = 8.854187817e-12  # permitividad del vacío en F/m
MU_ZERO = 4 * np.pi * 1e-7  # permeabilidad magnética del vacío en H/m
ETA_ZERO = MU_ZERO / EPSILON_ZERO  # impedancia característica del vacío en Ohm

class PropagationCalculator:
    def __init__(self, freq, tx_power, height_tx, height_rx, distance_start, distance_end, distance_step,
                 conductivity, permitivity, roughness, antenna_type, polarization, earth_radius_factor):
        self.freq = freq
        self.w = 2 * np.pi * self.freq
        self.Beta = self.w / C # constante de propagación, = 2 * pi / lambda, lambda = c / f
        self.tx_power = tx_power
        self.h_t = height_tx
        self.h_r = height_rx
        self.distance_start = distance_start
        self.distance_end = distance_end
        self.distance_step = distance_step
        
        self.sigma = conductivity
        self.epsilon_r = permitivity
        self.roughness = roughness
        
        self.antenna = antenna_type
        self.polarization = polarization
        
        self.earth_radius_factor = earth_radius_factor
        
        # antenna_type_map = {
        #     'Dipolo de media longitud de onda': 0,
        #     'Monopolo de cuarto de longitud de onda': 1,
        #     'Isotrópica': 2
        # }
        # polarization_map = {
        #     'Horizontal': 0,
        #     'Vertical': 1
        # }
        
        R = self.distance_end - self.distance_start # distancia entre Tx y Rx, horizontal
        R_zero = np.sqrt((R**2) + (self.h_t - self.h_r)**2) # distancia entre Tx y Rx, real
        Delta_R = 2 * self.h_t * self.h_r / R # diferencia de camino físico
        Delta = self.Beta * Delta_R # diferencia de camino óptico
        Psi = np.arctan((self.h_t + self.h_r) / R) # ángulo de ataque
        
        P_t = self.tx_power # potencia de transmisión
        E_zero = np.sqrt(30 * P_t) / R_zero
        
        epsilon_c = self.epsilon_r - 1j * self.sigma / (self.w * EPSILON_ZERO)
        
        Gamma_perpendicular = (np.sin(Psi) - np.sqrt(epsilon_c - np.cos(Psi)**2)) / (np.sin(Psi) + np.sqrt(epsilon_c - np.cos(Psi)**2))
        Gamma_paralelo = (epsilon_c * np.sin(Psi) - np.sqrt(epsilon_c - np.cos(Psi)**2)) / (epsilon_c * np.sin(Psi) + np.sqrt(epsilon_c - np.cos(Psi)**2))
        
        # Factores de interferencia
        F_i_perpendicular = np.sqrt(1 + np.abs(Gamma_perpendicular)**2 + 2 * np.abs(Gamma_perpendicular) * np.cos(Delta + np.angle(Gamma_perpendicular)))
        F_i_paralelo = np.sqrt(1 + np.abs(Gamma_paralelo)**2 + 2 * np.abs(Gamma_paralelo) * np.cos(Delta + np.angle(Gamma_paralelo)))
        
        E_perpendicular = np.abs(E_zero) * np.abs(F_i_perpendicular)
        E_paralelo = np.abs(E_zero) * np.abs(F_i_paralelo)
        self.E_total = np.sqrt(E_perpendicular**2 + E_paralelo**2)
        
        self.P_r = (np.abs(self.E_total)**2 / ETA_ZERO) * (C / self.freq)**2 / (4 * np.pi)
        
    def calculate_received_power(self, distance):
        return self.P_r

    def calculate_electric_field(self, received_power):
        return self.E_total