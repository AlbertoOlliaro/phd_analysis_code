from exploratory_analysis import *
from geo2features import *

# Paths
DATA_GEONAMES_FILENAME = "1.1_ENGdata_geoID.xlsx"
DICT_GEOID_FILENAME = "aux_geonames_ID_dictionary.xlsx"
DATA_WITH_LOCATIONS_FETCHED_FILENAME = "1.3_ENGdata_geonamesExtracted.xlsx"
NETWORK_DATA_FILENAME = "1.5_ENGdata_network.xlsx"
ANALYSIS_DIR = "C:/Users/aolliaro/OneDrive - Nexus365/dphil excels/phd_analysis_data/"

def pre_testing():
    test_query_geonames_api()


if __name__ == "__main__":


    # Step 1.2 to 1.3: from data and geoID to geographical features
    process_all_locations()
    # Step 1.3 to 1.4: Exploratory analysis, diagrams and stats
    explo_analysis_results = run_exploratory_analysis(
        os.path.join(ANALYSIS_DIR, DATA_WITH_LOCATIONS_FETCHED_FILENAME),
        ANALYSIS_DIR,
        os.path.join(ANALYSIS_DIR, DATA_GEONAMES_FILENAME)
    )
    # Step 1.3 to 1.5: transform data to edges pairs
    network_data = transform2network( os.path.join(ANALYSIS_DIR, DATA_WITH_LOCATIONS_FETCHED_FILENAME), ANALYSIS_DIR, os.path.join(ANALYSIS_DIR, NETWORK_DATA_FILENAME))
