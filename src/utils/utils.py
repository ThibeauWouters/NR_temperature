"""This file contains the configuration for the CoRe database and utility functions
"""

from typing import Tuple
import json
import h5py
import re

# Point to the directory where the CoRe database is stored
CORE_DATABASE_DIR = "/Users/Woute029/Documents/Code/CoRe_DB2/"
CORE_DATABASE_INDEX_DIR = "/Users/Woute029/Documents/Code/CoRe_DB2/core_database_index/json/"

def load_index(which_index: str = "NR") -> dict:
    """Generate dictionary with keys being the entries of the CoRe database and values being the corresponding metadata.

    Args:
        which_index (str, optional): Options are "NR" and "Hyb", corresponding to the two metadata JSON files. Defaults to "NR".

    Returns:
        dict: Dictionary with keys being the entries of the CoRe database and values being the corresponding metadata.
    """
    result = {}
    
    # Load the index file, which is of JSON format
    with open(CORE_DATABASE_INDEX_DIR + f"DB_{which_index}.json") as f:
        index = json.load(f)
    
    data = index["data"]
    for d in data:
        key = d["database_key"].replace(":", "_")
        result[key] = d
    
    return result

def get_run_filenames(index: dict, which: str) -> tuple[str, str]:
    """Load the HDF5 file and metadata file of the most recent run of a given CoRe database entry.

    Args:
        index (dict): Metadata dict from the CoRe database index.
        which (str): Identifier of the run, e.g. BAM_0001

    Returns:
        tuple(str, str): String for the names of the HDF5 file and metadata file, respectively.
    """
    
    run_dir = CORE_DATABASE_DIR + f"{which}/"
    
    # First, check if the run directory exists
    if which not in index.keys():
        raise ValueError(f"Run {which} does not exist in the CoRe database.")
    
    # Look at index to find the available runs
    available_runs = index[which]["available_runs"]
    # Split available runs based on "," and also remove any whitespace
    available_runs = available_runs.split(",")
    available_runs = [r.strip() for r in available_runs]
    
    print(f"available_runs: ", available_runs)
    
    # TODO make it an option to choose the run
    # Choose the most recent run
    which_run = available_runs[-1]
    
    print(f"Chosen run: {which_run}")
    
    # Locate the HDF5 file
    hdf5_file = run_dir + f"{which_run}/data.h5"
    metadata = run_dir + f"{which_run}/metadata.txt"
    
    return hdf5_file, metadata

def load_metadata(metadata_file: str) -> dict:
    """Load the metadata file of a given run.

    Args:
        metadata_file (str): Path to the metadata file.

    Returns:
        dict: Dictionary with keys being the metadata keys and values being the corresponding values.
    """
    
    # Load metadata file
    with open(metadata_file) as f:
        lines = f.readlines()
        
    # Load in as keys and values: the keys are everything before an equal sign, the values everything after the equal sign up to \n
    metadata = {}
    for line in lines:
        # If there is no equal sign in this line, skip it
        if "=" not in line:
            continue
        key, value = line.split("=")
        metadata[key.strip()] = value.strip()
        
    return metadata

### Utilities related to HDF5 files

def extract_radius_from_filename(filename: str, no_match_number: int = 0) -> int:
    """Simple function that extracts the extraction radius from a filename.

    Args:
        filename (str): Filename of the data filename
        no_match_str (str, optional): Default string to be returned if there is no match. Defaults to "".

    Returns:
        str: The ra
    """
    pattern = r'_r(\d+)[.]'

    match = re.search(pattern, filename)
    if match:
        return int(match.group(1))
    else:
        return no_match_number
    
    
def extract_l_m_values(filename):
    match = re.match(r'Rh_l(\d+)_m(\d+)_r\d+', filename)
    if match:
        l_value = int(match.group(1))
        m_value = int(match.group(2))
        return l_value, m_value
    else:
        return None