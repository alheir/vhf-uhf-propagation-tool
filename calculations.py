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
            return None, None, None, None, None, None
        
        p = (2 / np.sqrt(3)) * np.sqrt(re * (hr + ht) + r*r/4)
        
        Xi = np.arcsin(2 * re * r * (hr - ht) / (p*p*p))
        
        r1 = r/2 - p * np.sin(Xi/3)
        r2 = r - r1
        
        phi1 = r1/re
        phi2 = r2/re
        
        R1 = np.sqrt(ht**2 + 4 * re * (re + ht) * (np.sin(phi1 / 2)**2))
        R2 = np.sqrt(hr**2 + 4 * re * (re + hr) * (np.sin(phi2 / 2)**2))
        
        Rd = np.sqrt((hr - ht)**2 + 4 * (re + hr) * (re + ht) * (np.sin((phi1 + phi2) / 2)**2)) # distancia entre Tx y Rx, real
         
        
        Delta_R = R1 + R2 - Rd
        
        sqrt_arg = Delta_R * (R1 + R2 + Rd) / (4 * R1 * R2)
        arcsin_arg = np .sqrt(sqrt_arg) 
        Psi = np.arcsin(arcsin_arg)
 
        Delta = self.Beta * Delta_R                                     # diferencia de camino óptico
        

        P_t = self.tx_power * self.antenna_tx_gain  # potencia de transmisión
        E_zero = np.sqrt(ETA_ZERO * P_t / (4 * np.pi)) / Rd

        epsilon_c = self.epsilon_r - 1j * self.sigma / (self.w * EPSILON_ZERO)


        # Tierra esférica
        D_factor = 1 / np.sqrt(1 + (2 * r1 * r2)/(re * r * np.sin(Psi)))
        
        # Rugosidad
        roughness_factor = np.exp(-2 * (self.Beta * self.roughness * np.sin(Psi))**2)

        # Coeficientes de reflexión
        if self.antenna_pol == ANTENNA_POL_H:
            Gamma = (epsilon_c * np.sin(Psi) - np.sqrt(epsilon_c - np.cos(Psi)**2)) / (epsilon_c * np.sin(Psi) + np.sqrt(epsilon_c - np.cos(Psi)**2))
        elif self.antenna_pol == ANTENNA_POL_V:
            Gamma = (np.sin(Psi) - np.sqrt(epsilon_c - np.cos(Psi)**2)) / (np.sin(Psi) + np.sqrt(epsilon_c - np.cos(Psi)**2))
            
        Gamma = Gamma * D_factor * roughness_factor  
    
        # Factor de interferencia
        F_i = np.sqrt(1 + np.abs(Gamma)**2 + 2 * np.abs(Gamma) * np.cos(Delta + np.angle(Gamma)))
        
        E_total = np.abs(E_zero) * np.abs(F_i)
        
        # print(f'E_total: {E_total:.2e}\t\t|E_zero|: {np.abs(E_zero):.2e}\t\t|F_i|: {np.abs(F_i):.2e}\t\t|Gamma|: {np.abs(Gamma):.2e}\n')
        
        P_r =   (np.abs(E_total)**2 / ETA_ZERO) * \
                (self.lambd**2 / (4 * np.pi)) * \
                self.antenna_rx_gain                       
        
        # Pérdida por espacio libre
        L_fs = (4 * np.pi * Rd / self.lambd) ** 2
        P_r_fs = (P_t / L_fs) * self.antenna_rx_gain
        E_fs = np.sqrt(ETA_ZERO * (P_r_fs / ((self.lambd**2 / (4 * np.pi)) * self.antenna_rx_gain)))
        
        return E_total, P_r, E_fs, P_r_fs, np.abs(Gamma), np.abs(F_i)

    def calculate_calc_los(self, height_tx, height_rx):
        re = self.earth_radius_factor * EARTH_RADIUS
        ht = height_tx
        hr = height_rx

        def delta_r_function(r):
            p = (2 / np.sqrt(3)) * np.sqrt(re * (hr + ht) + r*r/4)
            Xi = np.arcsin(2 * re * r * (hr - ht) / (p*p*p))
            r1 = r/2 - p * np.sin(Xi/3)
            r2 = r - r1
            phi1 = r1/re
            phi2 = r2/re
            R1 = np.sqrt(ht**2 + 4 * re * (re + ht) * (np.sin(phi1 / 2)**2))
            R2 = np.sqrt(hr**2 + 4 * re * (re + hr) * (np.sin(phi2 / 2)**2))
            Rd = np.sqrt((hr - ht)**2 + 4 * (re + hr) * (re + ht) * (np.sin((phi1 + phi2) / 2)**2))
            Delta_R = R1 + R2 - Rd
            return Delta_R

        
        r_initial_guess = 50e0
        r_solution = fsolve(delta_r_function, r_initial_guess)
        
        self.LOS_point_to_point = r_solution[0]
        
    
    def calculate_get_los(self):
        if self.LOS_point_to_point is None:
            raise Exception("LOS distance has not been calculated")
        
        return self.LOS_point_to_point
    

    def calculate_variation_with_distance(self, height_tx, height_rx, distance_start, distance_end, distance_step):
        distances = np.arange(distance_start, distance_end+distance_step, distance_step)
        
        E_totals = []
        P_rs = []
        E_fss = []
        P_r_fss = []
        Gammas = []
        F_is = []

        for distance in distances:
            E_total, P_r, E_fs, P_r_fs, Gamma, F_i = self.calculate_point_to_point(height_tx, height_rx, distance)
            
            if E_total is None or P_r is None:
                distances = distances[:len(E_totals)]
                break
            
            E_totals.append(E_total)
            P_rs.append(P_r)
            E_fss.append(E_fs)
            P_r_fss.append(P_r_fs)
            Gammas.append(Gamma)
            F_is.append(F_i)
            
            
            # distancia máxima dentro de radiohorizonte, stepizada
            self.max_distance = distances[len(E_totals)-1]
        
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
        
        if r >= self.LOS_point_to_point:
            return None, None, None, None, None, None
        
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
                
                if self.LOS_point_to_point is not None and distance >= self.LOS_point_to_point:
                    continue
                
                E_total, P_r, _, _, Gamma, F_i = self.calculate_point_to_point(height, height_fixed, distance)
                fresnel_zone = self.calculate_fresnel_zones_checker(height, height_fixed, distance)
                
            else:
                self.calculate_calc_los(height_fixed, height)
                
                if self.LOS_point_to_point is not None and distance >= self.LOS_point_to_point:
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