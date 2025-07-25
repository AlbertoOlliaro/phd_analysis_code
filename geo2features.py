import pandas as pd
import requests
import xml.etree.ElementTree as ET
from datetime import datetime
import os
import time

# Paths
DATA_FULL_FILENAME = "1.1_ENGdata_geoID.xlsx"
DICT_GEOID_FILENAME = "aux_geonames_ID_dictionary.xlsx"
OUTPUT_FILE_FETCHED_LOC = "1.3_ENGdata_geonamesExtracted"
ANALYSIS_DIR = "C:/Users/aolliaro/OneDrive - Nexus365/dphil excels/phd_analysis_data/"

USERNAME = 'albertoolliaro' # for geonames API

test_geonameID = 7285904

# Load data and filter by 'include'
df = pd.read_excel(os.path.join(ANALYSIS_DIR, DATA_FULL_FILENAME), sheet_name=0)
df = df[df["include"] > 0]

# Load or initialize geonames dictionary
DICT_GEOID_PATH = os.path.join(ANALYSIS_DIR, DICT_GEOID_FILENAME)

if os.path.exists(DICT_GEOID_PATH):
    print("🔄 Loading existing GeoNames dictionary...")
    geonames_df = pd.read_excel(DICT_GEOID_PATH, sheet_name=0)
    geonames_cache = geonames_df.set_index("geonameId").to_dict(orient="index")
else:
    print("📁 No dictionary found, starting fresh.")
    geonames_cache = {}


# queries geonames API to find location hierarchy
def query_geonames_api(geoname_id):
    url = f"http://api.geonames.org/hierarchy?geonameId={geoname_id}&username={USERNAME}"
    time.sleep(0.6)  # Throttle to stay under 1000/hour
    response = requests.get(url)

    root = ET.fromstring(response.content)

    # Check rate-limit
    status = root.find("status")
    if status is not None and "hourly limit" in status.attrib.get("message", "").lower():
        print("⚠️ Hourly limit met")
        raise RuntimeError("hourly limit met")

    geo_elements = root.findall("geoname")[1:]

    result = {}
    if len(geo_elements) >= 1:
        result["continent"] = geo_elements[0].findtext("toponymName")
    if len(geo_elements) >= 2:
        result["geoname_countryName"] = geo_elements[1].findtext("toponymName")
    if len(geo_elements) >= 3:
        result["ADM1"] = geo_elements[2].findtext("toponymName")
    if len(geo_elements) >= 4:
        result["ADM2"] = geo_elements[3].findtext("toponymName")
    if len(geo_elements) >= 5:
        result["ADM3"] = geo_elements[4].findtext("toponymName")

    return result


# Fetch from cache or update dictionary if needed
def get_geonames_data(geo_id):
    try:
        #ignore null, empty, or "world" geoIDs
        if pd.isna(geo_id) or str(geo_id).strip().lower() == "world" or str(geo_id).strip() == "":
            return {}

        #cast to int
        geo_id_int = int(float(geo_id))

        #if we already have/saved the geoID, return it
        if geo_id_int in geonames_cache:
            return geonames_cache[geo_id_int]

        # if not in dictionary: query API
        print(f"🔍 Querying new GeoNames ID: {geo_id_int}")
        result = query_geonames_api(geo_id_int)
        geonames_cache[geo_id_int] = result

        # Save the updated dictionary immediately
        pd.DataFrame.from_dict(geonames_cache, orient="index").reset_index().rename(
            columns={"index": "geonameId"}).to_excel(DICT_GEOID_PATH, index=False)
        return result

    # we save the geonames dictionary if things crash, notably due to the API
    except RuntimeError:
        print("⚠️ Saving partial dictionary to avoid loss...")
        pd.DataFrame.from_dict(geonames_cache, orient="index").reset_index().rename(
            columns={"index": "geonameId"}).to_excel(DICT_GEOID_PATH, index=False)
        raise
    except Exception as e:
        print(f"Error handling geoID {geo_id}: {e}")
        return {}


# Process locations, by column loc 1234 then by row, to retrieve its hierarchy from geonames
def process_all_locations():
    for loc in ["loc1", "loc2", "loc3", "loc4"]:
        print(f"📍 Working on: {loc}")
        geoname_id_col = f"{loc} geoID"

        # pairs of [A, B]: new column name A, which comes after the column B
        new_columns = [
            ("geoname_cont", " location as stated"),
            ("geoname_country", " geoname_cont"),
            ("geoname_ADM1", " geoname_country"),
            ("geoname_ADM2", " geoname_ADM1"),
            ("geoname_ADM3", " geoname_ADM2"),
        ]

        # Create empty columns in the correct order (makes visual reading and debugging easier)
        for new_col_suffix, insert_after_suffix in new_columns:
            new_col_name = f"{loc} {new_col_suffix}"
            insert_after_col = f"{loc}{insert_after_suffix}"
            if new_col_name not in df.columns:
                insert_pos = df.columns.get_loc(insert_after_col) + 1
                df.insert(insert_pos, new_col_name, pd.NA)

        # Apply lookup for each row with lambdas
        try:
            df[f"{loc} geoname_cont"] = df[geoname_id_col].apply(lambda x: get_geonames_data(x).get("continent"))
            df[f"{loc} geoname_country"] = df[geoname_id_col].apply(
                lambda x: get_geonames_data(x).get("geoname_countryName"))
            df[f"{loc} geoname_ADM1"] = df[geoname_id_col].apply(lambda x: get_geonames_data(x).get("ADM1"))
            df[f"{loc} geoname_ADM2"] = df[geoname_id_col].apply(lambda x: get_geonames_data(x).get("ADM2"))
            df[f"{loc} geoname_ADM3"] = df[geoname_id_col].apply(lambda x: get_geonames_data(x).get("ADM3"))
        except RuntimeError:
            print("⛔ Process halted due to API limit.")
            break
    # Save the final DataFrame with timestamp
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    output_path = os.path.join(ANALYSIS_DIR, f"{OUTPUT_FILE_FETCHED_LOC}_{timestamp}.xlsx")
    df.to_excel(output_path, index=False)
    print("✅ All done. Output saved to:", output_path)


def test_query_geonames_api():
    """
    Test the query_geonames_api function to ensure the correct hierarchy is returned.
    """
    result_hierarchy = ["Europe", "Switzerland", "Canton de Genève", "Geneva", "Genthod"]
    # Arrange
    api_result = query_geonames_api(test_geonameID)

    cont = api_result.get("continent")
    country = api_result.get("geoname_countryName")
    admin1 = api_result.get("ADM1")
    admin2 = api_result.get("ADM2")
    admin3 = api_result.get("ADM3")

    # Assert
    assert result_hierarchy[0] == cont, f"Test failed! Expected '{result_hierarchy[0]}', but got '{cont}'."
    assert result_hierarchy[1] == country, f"Test failed! Expected '{result_hierarchy[1]}', but got '{country}'."
    assert result_hierarchy[2] == admin1, f"Test failed! Expected '{result_hierarchy[2]}', but got '{admin1}'."
    assert result_hierarchy[3] == admin2, f"Test failed! Expected '{result_hierarchy[3]}', but got '{admin2}'."
    assert result_hierarchy[4] == admin3, f"Test failed! Expected '{result_hierarchy[4]}', but got '{admin3}'."

