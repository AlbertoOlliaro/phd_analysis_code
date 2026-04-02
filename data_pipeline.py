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

from data2network import transform2network, remove_self_loops, group_countries_into_region, \
    create_verbose_edgelist_network, merge_edges
from data_cleanup import clean_categories
from exploratory_analysis import *
from geo2features import *

# Paths and filenames ==================================================================================================
## dictionaries and aux files ------------------------------------------------------------------------------------------
DICT_GEOID_FILENAME = "aux_geonames_ID_dictionary.xlsx"
DICT_CLEANUP_FILENAME = "aux_cleanup_dictionary.xlsx"
DICT_COUNTRY_TO_SUBREGION_FILENAME = "aux_country-to-region_sorted_clockwise_UNm49.xlsx" # matches each country to a subregion according to the UN m49 scheme
#DICT_TERMS2CATEGORY_FILENAME = "aux_cleanup_dictionary_merging_terms.xlsx"

## working output files serve as intermediary files for the pipeline ---------------------------------------------------
DATA_GEONAMES_FILENAME = "0.1_ENGdata_geoID.xlsx" # IMPORTANT! file 0.1 has a lot of manual cleaning, do NOT use 0.0
DATA_CLEANED = "0.2_ENGdata_cleanedCategories.xlsx"
INCLUDED_DATA_WITH_LOCATIONS_FETCHED_FILENAME = "0.3_ENGdata_geonamesExtracted.xlsx"
EXPLORATORY_ANALYSIS_FILENAME = "0.4_exploratory_analysis.xlsx"

## network files (Excel, sheet 1: nodes, sheet 2: edges) ---------------------------------------------------------------
NETWORK_STEP1_DATA_FILENAME = "step1_nodes_edges.xlsx"
NETWORK_STEP2_DATA_FILENAME = "step2_nodes_edges_weight1.xlsx"
NETWORK_STEP3_DATA_FILENAME = "step3_nodes_edges_noloops.xlsx"
NETWORK_VERBOSE_EDGELIST_DATA_FILENAME = "3.5_edges_verbose.csv"
NETWORK_STEP4_DATA_FILENAME = "step4_nodes_subregions_edges.xlsx"

## directory -----------------------------------------------------------------------------------------------------------
ANALYSIS_DIR = "C:/Users/aolliaro/OneDrive - Nexus365/DPhil data and analysis/phd_analysis_data/"
#ANALYSIS_DIR = "C:/Users/alber/OneDrive - Nexus365/DPhil data and analysis/phd_analysis_data/"
#=======================================================================================================================

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

    start_from_step = 1
    end_step = 7

    # Step 0.1 to 0.2: cleaning free text data and typos =============================================================
    def step01to02():
        """
        TODO: node role and node type need cleaning into file v1.2 (match the locX mentioned to a node)
        """
        print("Step 0.1 to 0.2: from data and to cleaner categories...")
        df, latest_0_2_file_path = clean_categories(
            os.path.join(ANALYSIS_DIR, DATA_GEONAMES_FILENAME),
            os.path.join(ANALYSIS_DIR, DICT_CLEANUP_FILENAME),
            os.path.join(ANALYSIS_DIR, DATA_CLEANED)
        )
        # copy the latest file to a reusable file_name
        shutil.copy(latest_0_2_file_path, os.path.join(ANALYSIS_DIR, DATA_CLEANED))

    # Step 0.2 to 0.3: add geographical features from geonames API (or the stored cache) ==============================
    def step02to03():
        print("Step 0.2 to 0.3: from data and geoID to geographical features...")
        df, latest_1_3_file_path = process_all_locations(
            os.path.join(ANALYSIS_DIR, DATA_CLEANED),
            os.path.join(ANALYSIS_DIR, DICT_GEOID_FILENAME),
            os.path.join(ANALYSIS_DIR, INCLUDED_DATA_WITH_LOCATIONS_FETCHED_FILENAME)
        )
        # copy the latest file to a reusable file_name
        shutil.copy(latest_1_3_file_path, os.path.join(ANALYSIS_DIR, INCLUDED_DATA_WITH_LOCATIONS_FETCHED_FILENAME))

    # Step 0.3 to 0.4: Exploratory analysis, diagrams and stats ======================================================
    def step03to04():
        print("Step 0.3 to 0.4: Exploratory analysis, diagrams and stats...")
        explo_analysis_results, latest_1_4_file_path  = run_exploratory_analysis(
            os.path.join(ANALYSIS_DIR, INCLUDED_DATA_WITH_LOCATIONS_FETCHED_FILENAME),
            ANALYSIS_DIR,
            os.path.join(ANALYSIS_DIR, DATA_CLEANED))
        shutil.copy(latest_1_4_file_path, os.path.join(ANALYSIS_DIR, EXPLORATORY_ANALYSIS_FILENAME))

    # Step 0.3 to 1: transform data to network data in the form of nodes list and edges pairs =========================
    def step03to1():
        print("Step 0.3 to 1: transform data to edges pairs...")
        network_data, network_nodes_edges_file_path = transform2network(
            os.path.join(ANALYSIS_DIR, INCLUDED_DATA_WITH_LOCATIONS_FETCHED_FILENAME),
            os.path.join(ANALYSIS_DIR, NETWORK_STEP1_DATA_FILENAME))
        shutil.copy(network_nodes_edges_file_path, os.path.join(ANALYSIS_DIR, NETWORK_STEP1_DATA_FILENAME))


    # Step 1 to 2: remove weights from edges by removing (merging) edges with the same source and target ==============
    def step1to2():
        print("Step 1 to 2: edge weights to 1...")
        network_data, network_nodes_edges_w1_file_path = merge_edges(
            os.path.join(ANALYSIS_DIR, NETWORK_STEP1_DATA_FILENAME),
            os.path.join(ANALYSIS_DIR, NETWORK_STEP2_DATA_FILENAME))
        shutil.copy(network_nodes_edges_w1_file_path, os.path.join(ANALYSIS_DIR, NETWORK_STEP2_DATA_FILENAME))


    # Step 2 to 3: remove self-loops from the network by removing edges where source=target ===========================
    def step2to3():
        print("Step 2 to 3: remove same-country loop edges...")
        network_data_noloop, network_nodes_edges_noloop_file_path = remove_self_loops(
            os.path.join(ANALYSIS_DIR, NETWORK_STEP2_DATA_FILENAME),
            os.path.join(ANALYSIS_DIR, NETWORK_STEP3_DATA_FILENAME))
        shutil.copy(network_nodes_edges_noloop_file_path, os.path.join(ANALYSIS_DIR, NETWORK_STEP3_DATA_FILENAME))
    # Step 3 to 3.5: we create a new edge list (.csv) with country names instead of geoIDs ============================
        print("Updating Step 3 to 3.5: create the edge list with countries instead of geoIDs...")
        network_edgelist_verbose_noloop, network_verbose_edgelist_noloop_file_path = create_verbose_edgelist_network(
            network_data_noloop,
            os.path.join(ANALYSIS_DIR, NETWORK_VERBOSE_EDGELIST_DATA_FILENAME))
        shutil.copy(network_verbose_edgelist_noloop_file_path, os.path.join(ANALYSIS_DIR, NETWORK_VERBOSE_EDGELIST_DATA_FILENAME))


    # Step 3 to 4: merge countries into subregions based on the UN m49 scheme dictionary file =========================
    def step3to4():
        print("Step 3 to 4: merging countries into subregions...")
        network_data_subregions, network_nodes_edges_subregions_file_path = group_countries_into_region(
            os.path.join(ANALYSIS_DIR, NETWORK_STEP3_DATA_FILENAME),
            os.path.join(ANALYSIS_DIR, DICT_COUNTRY_TO_SUBREGION_FILENAME),
            os.path.join(ANALYSIS_DIR, NETWORK_STEP4_DATA_FILENAME))
        shutil.copy(network_nodes_edges_subregions_file_path, os.path.join(ANALYSIS_DIR, NETWORK_STEP4_DATA_FILENAME))


    # sequence of the pipeline
    steps = {
        1: step01to02,
        2: step02to03,
        3: step03to04,
        4: step03to1,
        5: step1to2,
        6: step2to3,
        7: step3to4
    }

    for step in range(start_from_step, end_step+1):
        steps[step]()

