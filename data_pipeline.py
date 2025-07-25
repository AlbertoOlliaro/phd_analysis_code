from exploratory_analysis import *
from geo2features import *

# Paths
DATA_GEONAMES_FILENAME = "1.1_ENGdata_geoID.xlsx"
DICT_GEOID_FILENAME = "aux_geonames_ID_dictionary.xlsx"
DATA_WITH_LOCATIONS_FETCHED_FILENAME = "1.3_ENGdata_geonamesExtracted.xlsx"
ANALYSIS_DIR = "C:/Users/aolliaro/OneDrive - Nexus365/dphil excels/phd_analysis_data/"

def pre_testing():
    test_query_geonames_api()


if __name__ == "__main__":


    # advances from step 1.2 to 1.3: from data and geoID to geographical features
    process_all_locations()
    # 1.3 to 1.4 exploratory analysis, diagrams and stats
    explo_analysis_results = run_exploratory_analysis(
        os.path.join(ANALYSIS_DIR, DATA_WITH_LOCATIONS_FETCHED_FILENAME),
        ANALYSIS_DIR,
        os.path.join(ANALYSIS_DIR, DATA_FULL_FILENAME)
    )
