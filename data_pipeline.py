"""
Data Pipeline Script

This script orchestrates the data processing pipeline for geographic network analysis:
1. Processes location data and assigns GeoID identifiers
2. Extracts geographical features using GeoNames API
3. Performs exploratory analysis and generates statistics
4. Transforms processed data into network format for visualization

The pipeline uses intermediary files between steps for data persistence, validation and manual avoiding repeating steps.
"""

import shutil

from data2network import transform2network
from exploratory_analysis import *
from geo2features import *

# Paths and filenames
## dictionaries and aux files
DICT_GEOID_FILENAME = "aux_geonames_ID_dictionary.xlsx"
## output files
DATA_GEONAMES_FILENAME = "1.1_ENGdata_geoID.xlsx"
# 1.2 deprecated
INCLUDED_DATA_WITH_LOCATIONS_FETCHED_FILENAME = "1.3_ENGdata_geonamesExtracted.xlsx"
EXPLORATORY_ANALYSIS_FILENAME = "1.4_exploratory_analysis.xlsx"
NETWORK_DATA_FILENAME = "1.5_nodes_edges.xlsx"
## DIRs
ANALYSIS_DIR = "C:/Users/aolliaro/OneDrive - Nexus365/DPhil data and analysis/phd_analysis_data/"
## OTHERS
GROUP_EUROPE = True

def add_suffix_to_filename(file_path, suffix):
    root, ext = os.path.splitext(file_path)
    return f"{root}_{suffix}{ext}"

def pre_testing():
    """
    Performs pre-execution testing to validate GeoNames API connectivity.

    Tests the GeoNames API query functionality before running the main pipeline
    to ensure proper API access and response handling.
    """
    test_query_geonames_api()

 

if __name__ == "__main__":

    if GROUP_EUROPE:
        ## output files
        DATA_GEONAMES_FILENAME = add_suffix_to_filename(DATA_GEONAMES_FILENAME, "_grpEU")
        # 1.2 deprecated
        INCLUDED_DATA_WITH_LOCATIONS_FETCHED_FILENAME = add_suffix_to_filename(INCLUDED_DATA_WITH_LOCATIONS_FETCHED_FILENAME, "_grpEU")
        EXPLORATORY_ANALYSIS_FILENAME = add_suffix_to_filename(EXPLORATORY_ANALYSIS_FILENAME, "_grpEU")
        NETWORK_DATA_FILENAME = add_suffix_to_filename(NETWORK_DATA_FILENAME, "_grpEU")

    start_from_step = 1
    end_step = 3

    # Step 1.1 to 1.3: from data and geoID to geographical features ===================================================
    def step1to3():
        df, latest_1_3_file_path = process_all_locations(
            os.path.join(ANALYSIS_DIR, DATA_GEONAMES_FILENAME),
            os.path.join(ANALYSIS_DIR, DICT_GEOID_FILENAME),
            os.path.join(ANALYSIS_DIR, INCLUDED_DATA_WITH_LOCATIONS_FETCHED_FILENAME)
        )
        # copy the latest file to a reusable file_name
        shutil.copy(latest_1_3_file_path, os.path.join(ANALYSIS_DIR, INCLUDED_DATA_WITH_LOCATIONS_FETCHED_FILENAME))

    # Step 1.3 to 1.4: Exploratory analysis, diagrams and stats ======================================================
    def step3to4():
        explo_analysis_results, latest_1_4_file_path  = run_exploratory_analysis(
            os.path.join(ANALYSIS_DIR, INCLUDED_DATA_WITH_LOCATIONS_FETCHED_FILENAME),
            ANALYSIS_DIR,
            os.path.join(ANALYSIS_DIR, DATA_GEONAMES_FILENAME),
            os.path.join(ANALYSIS_DIR, EXPLORATORY_ANALYSIS_FILENAME)
        )
        shutil.copy(latest_1_4_file_path, os.path.join(ANALYSIS_DIR, EXPLORATORY_ANALYSIS_FILENAME))

    # Step 1.3 to 1.5: transform data to edges pairs ==================================================================
    def step3to5():
        network_data, network_nodes_edges_file_path = transform2network(
            os.path.join(ANALYSIS_DIR, INCLUDED_DATA_WITH_LOCATIONS_FETCHED_FILENAME),
            ANALYSIS_DIR,
            os.path.join(ANALYSIS_DIR, NETWORK_DATA_FILENAME))
        shutil.copy(network_nodes_edges_file_path, os.path.join(ANALYSIS_DIR, NETWORK_DATA_FILENAME))


    # Map a sequence of pipeline
    steps = {
        1: step1to3,
        2: step3to4,
        3: step3to5,
    }

    for step in range(start_from_step, end_step+1):
        steps[step]()

