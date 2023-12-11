import h5py
import numpy as np
from typing import Tuple

my_default_extraction_keys = ["density", "temperature", "ye"]

#####################
### Tabulated EOS ###
#####################

class TabulatedEOS:
    
    def __init__(self, eos_filename: str, extraction_keys: list = my_default_extraction_keys):
        self.eos_filename = eos_filename
        self.extraction_keys = extraction_keys
        
        self.eos = self.load_eos()
        
    def load_eos(self) -> dict:
        """Loads in the EOS data and extracts the relevant quantities.

        Returns:
            dict: Dictionary containing the desired values.
        """
        
        eos_data = {}
        with h5py.File(self.eos_filename, "r") as file:
            # TODO Save all keys present in the dataset for later on, mainly for debugging later on
            self.all_keys = list(file.keys())
            # Save the desired keys to a dictionary
            for key in self.extraction_keys:
                eos_data[key] = file[key][()]
                
        self.eos_data = eos_data 
        
        # Get the size as attributes
        # TODO improve?
        if "density" in eos_data.keys():
            self.pointsrho = len(eos_data["density"])
        else:
            self.pointsrho = 0
        if "temperature" in eos_data.keys():
            self.pointstemp = len(eos_data["temperature"])
        else:
            self.pointstemp = 0
        if "ye" in eos_data.keys():
            self.pointsye = len(eos_data["ye"])
        else:
            self.pointsye = 0
        
        return eos_data
    
######################
### Polytropic EOS ###
######################

POLYTROPIC_EOS_NAMES = ["2B", "2H", "ALF2", "ENG", "H4", "MPA1", "MS1", "MS1b", "SLy"]

def polytropic_eos_pressure(rho_values: np.array, K: float, Gamma: float) -> np.array:
    """
    This computes the pressure for a polytropic EOS with given K and Gamma.

    Args:
        rho_values (np.array): The density values for which to compute the pressure.
        K (float): Polytropic constant.
        Gamma (float): Polytropic exponent.

    Returns:
        np.array: Pressure values.
    """
    return K * rho_values ** Gamma

def polytropic_eos_energy(rho_values: np.array, K: float, Gamma: float, a: float) -> np.array:
    """
    This computes the energy density for a polytropic EOS with given K, Gamma and a.

    Args:
        rho_values (np.array): The density values for which to compute the energy density.
        K (float): Polytropic constant.
        Gamma (float): Polytropic exponent.
        a (float): Polytropic constant.

    Returns:
        np.array: Energy density values.
    """
    
    return (1 + a) * rho_values + (K * rho_values ** Gamma) / (Gamma - 1)

class PolytropicEOS:
    
    def __init__(self, eos_name: str):
        
        if eos_name not in POLYTROPIC_EOS_NAMES:
            raise ValueError(f"EOS name {eos_name} not recognized.")
        self.eos_name = eos_name
        self.eos_path = f"/Users/Woute029/Documents/Code/CoRe_DB2/eos/polytropic/{eos_name}.txt"
        self.parameters = self.load_parameters()
        
    def load_parameters(self) -> dict:
        
        def my_format(string):
            string = string.replace("=", "")
            string = string.replace(",", "")
            string = string.replace("]", "")
            string = string.replace("[", "")
            return string

        # Initialize empty dictionaries to store the extracted values
        parameters = {
            "rho_th": [],
            "a": [],
            "e": [],
            "K": [],
            "Gamma": []
        }

        # Read the file and extract the values
        with open(self.eos_path, 'r') as file:
            lines = file.readlines()
            for line in lines:
                # Remove leading and trailing whitespaces
                line = line.strip()

                # Skip comments and empty lines
                if line.startswith("#") or not line:
                    continue

                # Split each line into parameter name and values
                param_name, *param_values = line.split()
                print(param_name, param_values)

                # Convert values to float and update the dictionary
                for string_value in param_values:
                    if "=" in string_value:
                        continue
                    
                    string_value = my_format(string_value)
                    value = float(string_value)
                    parameters[param_name].append(value)
            
        # TODO why one a less than K and gamma?
        parameters["a"] = [0] + parameters["a"]
        
        return parameters
    
    def get_pressure(self, rho_min: float = 1e-10) -> Tuple[np.array, np.array]:
        """
        Compute the pressure values of the piecewise polytropic EOS.

        Args:
            rho_min (float, optional): Lowest density at which to evalaute. Defaults to 1e-10.

        Returns:
            Tuple[np.array, np.array]: Density values and pressure values, respectively.
        """
        # TODO double check this, but how?
        rho_max = np.max(self.parameters["rho_th"])
        
        rho_values = np.linspace(rho_min, rho_max, 1000)
        
        rho_thresholds = [rho_min] + self.parameters["rho_th"]
        
        # Note: this assumes K and gamma are of equal length
        # Build the different pieces of the EOS
        all_pressure_values = [polytropic_eos_pressure(rho_values, self.parameters["K"][i], self.parameters["Gamma"][i]) for i in range(len(self.parameters["K"]))]
        # Use a heavyside step function to get the complete values
        pressure_values = np.zeros_like(rho_values)
        for i in range(len(rho_thresholds) - 1):
            pressure_values += np.heaviside(rho_values - rho_thresholds[i], 0.5) * np.heaviside(rho_thresholds[i+1] - rho_values, 0.5) * all_pressure_values[i]
        # Final part separately:
        pressure_values += np.heaviside(rho_values - rho_thresholds[-1], 0.5) * all_pressure_values[-1]
        
        return rho_values, pressure_values

# Load the polytropic EOS dict for the given names
POLYTROPIC_EOS_DICT = {key: PolytropicEOS(key) for key in POLYTROPIC_EOS_NAMES}