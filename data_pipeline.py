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
INCLUDED_DATA_WITH_LOCATIONS_FETCHED_FILENAME = "1.3_ENGdata_geonamesExtracted.xlsx"
EXPLORATORY_ANALYSIS_FILENAME = "1.4_exploratory_analysis.xlsx"
NETWORK_DATA_FILENAME = "1.5_ENGdata_network.xlsx"
## DIRs
ANALYSIS_DIR = "C:/Users/aolliaro/OneDrive - Nexus365/dphil excels/phd_analysis_data/"

def pre_testing():
    """
    Performs pre-execution testing to validate GeoNames API connectivity.

    Tests the GeoNames API query functionality before running the main pipeline
    to ensure proper API access and response handling.
    """
    test_query_geonames_api()

 

if __name__ == "__main__":

    # Step 1.2 to 1.3: from data and geoID to geographical features ===================================================
    # SKIP as done and clean
    # TODO refactor all functions to use only the constants from this file and not local ones
    # TODO refactor saving functionnality to use file names as parameter and append timestamp and file extension locally
    # df, latest_1_3_file_path = process_all_locations()
    # copy latest file to reusable file_name
    # shutil.copy(latest_1_3_file_path, os.path.join(ANALYSIS_DIR, INCLUDED_DATA_WITH_LOCATIONS_FETCHED_FILENAME))

    # Step 1.3 to 1.4: Exploratory analysis, diagrams and stats ======================================================
    # SKIP as it is done
    # explo_analysis_results, analysis_latest_file_path  = run_exploratory_analysis(
    #     os.path.join(ANALYSIS_DIR, DATA_WITH_LOCATIONS_FETCHED_FILENAME),
    #     ANALYSIS_DIR,
    #     os.path.join(ANALYSIS_DIR, DATA_GEONAMES_FILENAME)
    # )
    # shutil.copy(latest_1_4_file_path, os.path.join(ANALYSIS_DIR, INCLUDED_DATA_WITH_LOCATIONS_FETCHED_FILENAME))


    # Step 1.3 to 1.5: transform data to edges pairs ==================================================================
    network_data = transform2network(os.path.join(ANALYSIS_DIR, INCLUDED_DATA_WITH_LOCATIONS_FETCHED_FILENAME), ANALYSIS_DIR, os.path.join(ANALYSIS_DIR, NETWORK_DATA_FILENAME))
