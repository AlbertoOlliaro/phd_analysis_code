import pandas as pd
import requests
import xml.etree.ElementTree as ET
from datetime import datetime
import os
import time
from geo2features import *

# Paths
DATA_GEONAMES_FILENAME = "1.2_ENGdata_geonamesExtra.xlsx"
DICT_GEOID_FILENAME = "aux_geonames_ID_dictionary.xlsx"
OUTPUT_FILE_FETCHED_LOC = "1.3_ENGdata_geonamesExtracted"
ANALYSIS_DIR = "C:/Users/aolliaro/OneDrive - Nexus365/dphil excels/phd_analysis_data/"

USERNAME = 'albertoolliaro'

def pre_testing():
    test_query_geonames_api()


if __name__ == "__main__":

    process_all_locations()
