import h5py
import sys
sys.path.append('./utils/')
import utils
from utils import extract_radius_from_filename
import numpy as np
import re
from typing import Tuple

class MyHDF5:
    
    def __init__(self, hdf5_file: str, verbose: bool = True) -> None:
        """Read the HDF5 file and store the data in a pandas DataFrame.

        Args:
            hdf5_file (str): Path to the HDF5 file.
        """
        
        
        
        self.verbose = verbose
        self.hdf5_file = hdf5_file
        self.process_data()
        
    def process_data(self):
        
        self.data = {}
        
        with h5py.File(self.hdf5_file, "r") as file:
            # Read in the top-level groups and subgroups
            self.group_keys = list(file.keys())
            self.subgroup_keys = {}
            for key in self.group_keys:
                self.subgroup_keys[key] = list(file[key].keys())
                
            print(self.group_keys)
            print(self.subgroup_keys)
                
            # Read in the data
            for first_key in self.group_keys:
                self.data[first_key] = {}
                for second_key in self.subgroup_keys[first_key]:
                    self.data[first_key][second_key] = file[first_key][second_key][()]
                
            print("Reading data OK")
                
            # Save the key for strain and psi separately
            self.strain_key = [key for key in self.group_keys if "rh_" in key][0]
            self.psi_key = [key for key in self.group_keys if "psi4" in key][0]
            
            # Read in l and m values
            print(self.strain_key)
            result = re.search(r'(\d)(\d)$', self.strain_key)
            if result:
                l, m = result.groups()
            else:
                raise ValueError(f"Could not extract l and m values from {self.strain_key}")
            
            self.l = int(l)
            self.m = int(m)
            
            # Get the radii for strain and Psi
            self.strain_filenames = self.subgroup_keys[self.strain_key]
            self.radii_strain = np.array([extract_radius_from_filename(filename) for filename in self.strain_filenames])
            self.psi_filenames = self.subgroup_keys[self.psi_key]
            self.radii_psi = np.array([extract_radius_from_filename(filename) for filename in self.psi_filenames])
                
        
    def get_h(self, radius: int = None) -> tuple[np.ndarray, np.ndarray]:
        
        # If no radius is specified, take the largest radius
        if radius is None or radius not in self.radii_strain:
            print("INFO: No radius specified or radius not in data, taking largest radius")
            radius = self.radii_strain.max()
        
        # Get the strain data
        subgroup_key = [name for name in self.strain_filenames if str(radius) in name][0]
        result = self.data[self.strain_key][subgroup_key]
        
        x = result[:,0]
        y = result[:,1] + 1j * result[:,2]
        
        return x, y