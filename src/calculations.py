"""
This module contains the PropagationCalculator class, which provides methods to calculate various propagation characteristics
for VHF and UHF signals, including point-to-point propagation, line-of-sight (LOS) distance, variation with distance, Fresnel zones, 
and variation with height.
    
Classes:
    PropagationCalculator: A class to calculate various propagation characteristics for VHF and UHF signals.
    
Methods:
    __init__(self, freq, tx_power, conductivity, permitivity, roughness, antenna_type, antenna_pol, earth_radius_factor):
        Initializes the PropagationCalculator with the given parameters.
    calculate_point_to_point(self, height_tx, height_rx, distance):
        Calculates the point-to-point propagation characteristics between a transmitter and receiver.
    calculate_calc_los(self, height_tx, height_rx):
        Calculates the line-of-sight (LOS) distance between a transmitter and receiver.
    calculate_get_los(self):
        Returns the calculated LOS distance.
    calculate_variation_with_distance(self, height_tx, height_rx, distance_start, distance_end, distance_step):
        Calculates the variation of propagation characteristics with distance.
    calculate_fresnel_zones_checker(self, ht, hr, distance):
        Checks the Fresnel zones for the given transmitter and receiver heights and distance.
    calculate_variation_with_height(self, height_start, height_end, height_step, height_fixed, vary_tx=True):
        Calculates the variation of propagation characteristics with height.
    plot_results(self, x_values, y_values, x_label, y_label, title):
        Plots the results of the calculations.
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import fsolve

C = 299792458.0  # velocidad de la luz en m/s
EPSILON_ZERO = 8.854187817e-12  # permitividad del vacío en F/m
MU_ZERO = 4 * np.pi * 1e-7  # permeabilidad magnética del vacío en H/m
ETA_ZERO = np.sqrt(MU_ZERO / EPSILON_ZERO)  # impedancia característica del vacío en Ohm

GAIN_DIPOLE = 1.641
GAIN_MONOPOLE = 3.282
GAIN_ISOTROPIC = 1

ANTENNA_GAINS = [GAIN_DIPOLE, GAIN_MONOPOLE, GAIN_ISOTROPIC]

ANTENNA_POL_H = 0
ANTENNA_POL_V = 1

ANTENNA_POLS = [ANTENNA_POL_H, ANTENNA_POL_V]

EARTH_RADIUS = 6371e3  # radio de la tierra en m

class PropagationCalculator:
    def __init__(self, freq, tx_power, conductivity, permitivity, roughness, antenna_type, antenna_pol, earth_radius_factor):
        self.freq = freq
        self.w = 2 * np.pi * self.freq
        self.lambd = C / self.freq
        self.Beta = self.w / C  # constante de propagación, = 2 * pi / lambda, lambda = c / f
        self.tx_power = tx_power
        self.sigma = conductivity
        self.epsilon_r = permitivity
        self.roughness = roughness
        self.antenna = antenna_type
        self.antenna_tx_gain = ANTENNA_GAINS[int(antenna_type)]
        self.antenna_rx_gain = ANTENNA_GAINS[int(antenna_type)]
        self.earth_radius_factor = earth_radius_factor
        self.antenna_pol = antenna_pol
        self.LOS_point_to_point = None
        self.max_distance = None

    def calculate_point_to_point(self, height_tx, height_rx, distance):
        
        re = self.earth_radius_factor * EARTH_RADIUS
        r = distance  # distancia entre Tx y Rx, sobre la superficie
        ht = height_tx
        hr = height_rx

        if r >= self.LOS_point_to_point:
            return None, None, None, None, None, None, None
        
        # if r < self.LOS_point_to_point:
        
        p = (2 / np.sqrt(3)) * np.sqrt(re * (hr + ht) + r*r/4)
        
        Xi = np.arcsin(2 * re * r * (hr - ht) / (p*p*p))
        
        r1 = r/2 - p * np.sin(Xi/3)
        r2 = r - r1
        
        phi1 = r1/re
        phi2 = r2/re
        
        self.ht_eff = ht - 0.5 * re * phi1**2
        self.hr_eff = hr - 0.5 * re * phi2**2
        
        R1 = np.sqrt(ht**2 + 4 * re * (re + ht) * (np.sin(phi1 / 2)**2))
        R2 = np.sqrt(hr**2 + 4 * re * (re + hr) * (np.sin(phi2 / 2)**2))
        
        Rd = np.sqrt((hr - ht)**2 + 4 * (re + hr) * (re + ht) * (np.sin((phi1 + phi2) / 2)**2)) # distancia entre Tx y Rx, real
        
        
        Delta_R = R1 + R2 - Rd
        
        sqrt_arg = Delta_R * (R1 + R2 + Rd) / (4 * R1 * R2)
        arcsin_arg = np .sqrt(sqrt_arg) 
        Psi = np.arcsin(arcsin_arg)
        # Psi = np.arcsin(ht_eff / R1)
        
        lim_psi = np.deg2rad(0.1)
        Psi = Psi if Psi > lim_psi else lim_psi

        Delta = self.Beta * Delta_R                                     # diferencia de camino óptico
    

        epsilon_c = self.epsilon_r - 1j * self.sigma / (self.w * EPSILON_ZERO)
        
        # Coeficientes de reflexión
        if self.antenna_pol == ANTENNA_POL_H:
            Gamma = (epsilon_c * np.sin(Psi) - np.sqrt(epsilon_c - np.cos(Psi)**2)) / (epsilon_c * np.sin(Psi) + np.sqrt(epsilon_c - np.cos(Psi)**2))
        elif self.antenna_pol == ANTENNA_POL_V:
            Gamma = (np.sin(Psi) - np.sqrt(epsilon_c - np.cos(Psi)**2)) / (np.sin(Psi) + np.sqrt(epsilon_c - np.cos(Psi)**2))
        
        # Factor de divergencia por superficie curva
        D_factor = 1 / np.sqrt(1 + (2 * r1 * r2) / (re * r * np.sin(Psi)))
        
        # Rugosidad
        roughness_factor = np.exp(-2 * (self.Beta * self.roughness * np.sin(Psi))**2)
        
        Gamma = Gamma * D_factor * roughness_factor
        
        # Factor de interferencia
        F_i = np.sqrt(1 + np.abs(Gamma)**2 + 2 * np.abs(Gamma) * np.cos(Delta + np.angle(Gamma)))
        
        
        
        # lim_psi = np.deg2rad(0.1)
        # if Psi < lim_psi:
        #     F_i = 1
        
            
        # else:
        #     Gamma = 0
        #     D_factor = 0
        #     roughness_factor = 0
        #     Psi = 0
        #     F_i = 1
        #     Rd = r
                   
        P_t = self.tx_power * self.antenna_tx_gain  # potencia de transmisión
        E_zero = np.sqrt(ETA_ZERO * P_t / (4 * np.pi)) / Rd

        E_total = np.abs(E_zero) * np.abs(F_i)
        P_r =   (np.abs(E_total)**2 / ETA_ZERO) * \
                    (self.lambd**2 / (4 * np.pi)) * \
                    self.antenna_rx_gain       
                
        # if Psi > lim_psi:
        #     P_r =   (np.abs(E_total)**2 / ETA_ZERO) * \
        #             (self.lambd**2 / (4 * np.pi)) * \
        #             self.antenna_rx_gain
                    
        #     self.last_P_r = P_r
        # else:
        #     P_r = P_t * (ht**2 * hr**2) / (Rd**4)
            
        #     if self.first_aprox_run:
        #         self.aprox_P_r_offset = (self.last_P_r - P_r) * 0.9
        #         self.first_aprox_run = False
                
        #     P_r = P_r + self.aprox_P_r_offset
                  
        #     E_total = np.sqrt(ETA_ZERO * P_r / ((self.lambd**2 / (4 * np.pi)) * self.antenna_rx_gain))
        
        # Pérdida por espacio libre
        L_fs = (4 * np.pi * Rd / self.lambd) ** 2
        P_r_fs = (P_t / L_fs) * self.antenna_rx_gain
        E_fs = np.sqrt(ETA_ZERO * (P_r_fs / ((self.lambd**2 / (4 * np.pi)) * self.antenna_rx_gain)))
        
        
        # d_1 = np.sqrt(2 * re) * (np.sqrt(ht) + np.sqrt(0))
        # d_2 = np.sqrt(2 * re) * (np.sqrt(0) + np.sqrt(hr))
        # D_0 = d_1 + d_2
        # d_3 = r - D_0
        
        # d_ns = [d_1, d_2, d_3]
        # def calc_chi_n(n):
        #     d_n = d_ns[n-1]
        #     return (2*np.pi*d_n/self.lambd) / ((2*np.pi*re)**(2/3))
        
        # def calc_F_s_n(chi_n):
        #     logged = (-0.048 * chi_n**3 + 1.0875 * chi_n**2 + 4.0782 * chi_n - 0.8806)
        #     return (10 ** (logged/20))
        
        # def calc_N_n(n):
        #     chi_n = calc_chi_n(n)
        #     logged = (-0.5 + 35*np.log10(chi_n) + 10 * np.log10(calc_F_s_n(chi_n)))
        #     return (10 ** (logged/20)), chi_n
        
        # N_1, chi_1 = calc_N_n(1)
        # N_2, _ = calc_N_n(2)
        # chi_3 = calc_chi_n(3)
        
       
        # D_f = 0.000389 * (self.freq / 1e6) * ht * hr # frequency-dependent factor
        # D_h = self.LOS_point_to_point # asymptotic term
        # D_06 = (D_f * D_h) / (D_f + D_h) # path length of a clearance of 0.6 FFZ
        # D_06 = D_06 * 1000 # to meters
        
        # L_1 = 20 * np.log10(N_1 / np.sqrt(5.656 * np.pi * chi_1))
        # L_2 = 20 * np.log10(N_2)
        # L_3 = 0.0086 * chi_3**3 + 0.2063 * chi_3**2 + 11.0997 * chi_3 - 0.8934
        
        # L = None
        # if r >= (d_1 + d_2):
        #     L = L_1 + L_2 - np.abs(L_3)
        # elif r > D_06:
        #     L = L_1 + L_2 + np.abs(L_3)
        # else:
        #     L = 0
        
        # L = 10 ** (L/10)
        
        # P_r = P_r / L
        # E_total = np.sqrt(ETA_ZERO * (P_r / ((self.lambd**2 / (4 * np.pi)) * self.antenna_rx_gain)))
        
        
        
        
        return E_total, P_r, E_fs, P_r_fs, np.abs(Gamma), np.abs(F_i)

    # def calculate_calc_los(self, height_tx, height_rx):
    #     re = self.earth_radius_factor * EARTH_RADIUS
    #     ht = height_tx
    #     hr = height_rx

    #     def delta_r_function(r):
    #         p = (2 / np.sqrt(3)) * np.sqrt(re * (hr + ht) + r*r/4)
    #         Xi = np.arcsin(2 * re * r * (hr - ht) / (p*p*p))
    #         r1 = r/2 - p * np.sin(Xi/3)
    #         r2 = r - r1
    #         phi1 = r1/re
    #         phi2 = r2/re
    #         R1 = np.sqrt(ht**2 + 4 * re * (re + ht) * (np.sin(phi1 / 2)**2))
    #         R2 = np.sqrt(hr**2 + 4 * re * (re + hr) * (np.sin(phi2 / 2)**2))
    #         Rd = np.sqrt((hr - ht)**2 + 4 * (re + hr) * (re + ht) * (np.sin((phi1 + phi2) / 2)**2))
    #         Delta_R = R1 + R2 - Rd
    #         return Delta_R

        
    #     r_initial_guess = 50e0
    #     r_solution = fsolve(delta_r_function, r_initial_guess)
        
    #     self.LOS_point_to_point = r_solution[0]
    
    def calculate_calc_los(self, height_tx, height_rx):
        re = self.earth_radius_factor * EARTH_RADIUS
        ht = height_tx
        self.LOS_point_to_point = np.sqrt(2 * re) * (np.sqrt(height_tx) + np.sqrt(height_rx)) # radio horizonte
        
    
    def calculate_get_los(self):
        if self.LOS_point_to_point is None:
            raise Exception("LOS distance has not been calculated")
        
        return self.LOS_point_to_point
    

    def calculate_variation_with_distance(self, height_tx, height_rx, distance_start, distance_end, distance_step):
        distances = np.arange(distance_start, distance_end+distance_step, distance_step)
        
        distances = distances[distances <= self.LOS_point_to_point]
        
        E_totals = []
        P_rs = []
        E_fss = []
        P_r_fss = []
        Gammas = []
        F_is = []

        for distance in distances:
            E_total, P_r, E_fs, P_r_fs, Gamma, F_i = self.calculate_point_to_point(height_tx, height_rx, distance)
            
            E_totals.append(E_total)
            P_rs.append(P_r)
            E_fss.append(E_fs)
            P_r_fss.append(P_r_fs)
            Gammas.append(Gamma)
            F_is.append(F_i)
            
            # distancia máxima dentro de radiohorizonte, stepizada
            self.max_distance = distances[len(E_totals)-1]
            # self.max_distance = self.LOS_point_to_point
        
        return distances, E_totals, P_rs, E_fss, P_r_fss, Gammas, F_is
    
    # def calculate_fresnel_zones_checker(self, ht, hstart, hend, distance):
    #     re = self.earth_radius_factor * EARTH_RADIUS
    #     r = distance  # distancia entre Tx y Rx, sobre la superficie
    #     h1 = ht
        
    #     # h2 = None
        
    #     # n = 1
    #     # # hp = ((h1 * r2 + h2 * r1) / (r1 + r2)) - (r1*r2 / (2 * re))
        
    #     # hpn = np.sqrt(n * self.lambd * r1 * r2 / (r1 + r2))
        
    #     # h2 = ((hpn + (r1 * r2 / (2 * re))) * (r1 + r2) - h1 * r2 ) / r1

    #     # p = (2 / np.sqrt(3)) * np.sqrt(re * (h2 + h1) + r*r/4)
    #     # Xi = np.arcsin(2 * re * r * (h2 - h1) / (p*p*p))
    #     # r1 = r/2 - p * np.sin(Xi/3)
    #     # r2 = r - r1
    
    def calculate_fresnel_zones_checker(self, ht, hr, distance):
        re = self.earth_radius_factor * EARTH_RADIUS
        r = distance
        
        p = (2 / np.sqrt(3)) * np.sqrt(re * (hr + ht) + r*r/4)
        
        Xi = np.arcsin(2 * re * r * (hr - ht) / (p*p*p))
        
        r1 = r/2 - p * np.sin(Xi/3)
        r2 = r - r1
        
        # https://openjicareport.jica.go.jp/pdf/10455350_03.pdf
        # página 5
        # Se aproximaron d1 y d2 del PDF con las distancias curvas r1 y r2
        # Además, el PDF no considera hp perpendicular a propagation line path
        hp = ((ht * r2 + hr * r1) / (r1 + r2)) - (r1*r2 / (2 * re))
        
        n = 0
        while(True):
            fresnel_zn = np.sqrt((n + 1) * r1 * r2 * self.lambd / (r1 + r2))

            if hp < fresnel_zn:
                break
            
            n += 1
        
        return n # "si n==0, no se pudo despejar ni la 1ra zona de fresnel"

    def calculate_variation_with_height(self, height_start, height_end, height_step, height_fixed, vary_tx=True):
        heights = np.arange(height_start, height_end+height_step, height_step)
        E_totals = []
        P_rs = []
        Gammas = []
        F_is = []
        fresnel_zones = []
        
        distance = self.max_distance

        valid_heights = []

        for height in heights:
            if vary_tx:
                self.calculate_calc_los(height, height_fixed)
                
                if distance >= self.LOS_point_to_point:
                    continue
                
                E_total, P_r, _, _, Gamma, F_i = self.calculate_point_to_point(height, height_fixed, distance)
                fresnel_zone = self.calculate_fresnel_zones_checker(height, height_fixed, distance)
                
            else:
                self.calculate_calc_los(height_fixed, height)
                
                if distance >= self.LOS_point_to_point:
                    continue
                
                E_total, P_r, _, _, Gamma, F_i = self.calculate_point_to_point(height_fixed, height, distance)
                fresnel_zone = self.calculate_fresnel_zones_checker(height, height_fixed, distance)
                
            valid_heights.append(height)
            E_totals.append(E_total)
            P_rs.append(P_r)
            Gammas.append(Gamma)
            F_is.append(F_i)
            fresnel_zones.append(fresnel_zone)

        return valid_heights, E_totals, P_rs, Gammas, F_is, fresnel_zones

    def plot_results(self, x_values, y_values, x_label, y_label, title):
        plt.figure()
        plt.plot(x_values, y_values)
        plt.xlabel(x_label)
        plt.ylabel(y_label)
        plt.title(title)
        plt.grid(True)
        plt.show()