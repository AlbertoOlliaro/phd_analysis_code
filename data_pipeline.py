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
from data_cleanup import clean_categories
from exploratory_analysis import *
from geo2features import *

# Paths and filenames
## dictionaries and aux files
DICT_GEOID_FILENAME = "aux_geonames_ID_dictionary.xlsx"
DICT_CLEANUP_FILENAME = "aux_cleanup_dictionary.xlsx"
DICT_COUNTRY_TO_SUBREGION_FILENAME = "aux_country-to-region_sorted_clockwise_UNm49.xlsx" # matches each country to a subregion according to the UN m49 scheme
## output files
DATA_GEONAMES_FILENAME = "1.1_ENGdata_geoID.xlsx" # IMPORTANT! file 1.1 has a lot of manual cleaning, do not use 1.0
DATA_CLEANED = "1.2_ENGdata_cleanedCategories.xlsx"
INCLUDED_DATA_WITH_LOCATIONS_FETCHED_FILENAME = "1.3_ENGdata_geonamesExtracted.xlsx"
EXPLORATORY_ANALYSIS_FILENAME = "1.4_exploratory_analysis.xlsx"
NETWORK_DATA_FILENAME = "1.5_nodes_edges.xlsx"
## DIRs
#ANALYSIS_DIR = "C:/Users/aolliaro/OneDrive - Nexus365/DPhil data and analysis/phd_analysis_data/"
ANALYSIS_DIR = "C:/Users/alber/OneDrive - Nexus365/DPhil data and analysis/phd_analysis_data/"
## OTHERS


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

    pre_testing()



    start_from_step = 4
    end_step = 4

    # Step 1.1 to 1.2: from data and to cleaned categories, text, etc =================================================
    def step1to2():
        """
        TODO: node role and node type need cleaning into file v1.2 (match the locX mentioned to a node)
        """
        print("Step 1.1 to 1.2: from data and to cleaned categories, text, etc")
        df, latest_1_2_file_path = clean_categories(
            os.path.join(ANALYSIS_DIR, DATA_GEONAMES_FILENAME),
            os.path.join(ANALYSIS_DIR, DICT_CLEANUP_FILENAME),
            os.path.join(ANALYSIS_DIR, DATA_CLEANED)
        )
        # copy the latest file to a reusable file_name
        shutil.copy(latest_1_2_file_path, os.path.join(ANALYSIS_DIR, DATA_CLEANED))

    # Step 1.2 to 1.3: from data and geoID to geographical features ===================================================
    def step2to3():
        print("Step 1.2 to 1.3: from data and geoID to geographical features")
        df, latest_1_3_file_path = process_all_locations(
            os.path.join(ANALYSIS_DIR, DATA_CLEANED),
            os.path.join(ANALYSIS_DIR, DICT_GEOID_FILENAME),
            os.path.join(ANALYSIS_DIR, INCLUDED_DATA_WITH_LOCATIONS_FETCHED_FILENAME)
        )
        # copy the latest file to a reusable file_name
        shutil.copy(latest_1_3_file_path, os.path.join(ANALYSIS_DIR, INCLUDED_DATA_WITH_LOCATIONS_FETCHED_FILENAME))

    # Step 1.3 to 1.4: Exploratory analysis, diagrams and stats ======================================================
    def step3to4():
        print("Step 1.3 to 1.4: Exploratory analysis, diagrams and stats")
        explo_analysis_results, latest_1_4_file_path  = run_exploratory_analysis(
            os.path.join(ANALYSIS_DIR, INCLUDED_DATA_WITH_LOCATIONS_FETCHED_FILENAME),
            ANALYSIS_DIR,
            os.path.join(ANALYSIS_DIR, DATA_CLEANED),
            os.path.join(ANALYSIS_DIR, EXPLORATORY_ANALYSIS_FILENAME)
        )
        shutil.copy(latest_1_4_file_path, os.path.join(ANALYSIS_DIR, EXPLORATORY_ANALYSIS_FILENAME))

    # Step 1.3 to 1.5: transform data to edges pairs ==================================================================
    def step3to5():
        print("Step 1.3 to 1.5: transform data to edges pairs")
        network_data, network_nodes_edges_file_path = transform2network(
            os.path.join(ANALYSIS_DIR, INCLUDED_DATA_WITH_LOCATIONS_FETCHED_FILENAME),
            ANALYSIS_DIR,
            os.path.join(ANALYSIS_DIR, NETWORK_DATA_FILENAME))
        shutil.copy(network_nodes_edges_file_path, os.path.join(ANALYSIS_DIR, NETWORK_DATA_FILENAME))
        return network_data # returned as [nodes_df, edges_df]

    def rerun_on_subregions():
        print("Rerunning edge list on subregions...")
        print("...Removing same-country loop edges...")
        print("...Merging nodes strategy : summing variables") # sum the properties such as node category, origin, destination, manufacturing...?

    # sequence of the pipeline
    steps = {
        1: step1to2,
        2: step2to3,
        3: step3to4,
        4: step3to5,
    }

    for step in range(start_from_step, end_step+1):
        steps[step]()

