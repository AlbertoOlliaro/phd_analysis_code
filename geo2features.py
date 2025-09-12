from typing import Any, Hashable

import pandas as pd
import requests
import xml.etree.ElementTree as ET
from datetime import datetime
import os
import time

from numpy.f2py.auxfuncs import throw_error

USERNAME = 'albertoolliaro' # geonames API requires a private username to allow more queries
GEONAME_DICTIONARY_FILE_PATH = ""

test_geonameID = 7285904

def prep_phase(data_file_path, geoname_dictionary_file_path):

    # Load data and filter by 'include'
    if os.path.exists(data_file_path):
        df = pd.read_excel(data_file_path, sheet_name=0)
    else:
        print("❌ No input file found, aborting method.")
        return None

    df = df[df["include"] > 0]

    df = df.drop(columns=["Snippet", "Keywords Searched", "Snippet In English", "Comments", "comments in English"], errors="ignore")

    global GEONAME_DICTIONARY_FILE_PATH
    GEONAME_DICTIONARY_FILE_PATH = geoname_dictionary_file_path

    if os.path.exists(geoname_dictionary_file_path):
        print("🔄 Loading existing GeoNames dictionary...")
        geonames_dict_df = pd.read_excel(geoname_dictionary_file_path, sheet_name=0)
        geonames_dict_cache = geonames_dict_df.set_index("geonameId").to_dict(orient="index")
    else:
        print("📁 No dictionary found, starting fresh.")
        geonames_dict_cache = {}

    return df, geonames_dict_cache


def add_timestamp_to_filename(file_path):
    root, ext = os.path.splitext(file_path)
    return f"{root}_{datetime.now().strftime("%Y%m%d%H%M%S")}{ext}"


def save_df_to_file(file_path, df):
    timestamped_file_path = add_timestamp_to_filename(file_path)
    df.to_excel(timestamped_file_path, index=False)
    return timestamped_file_path


# queries geonames API to find location hierarchy and geonameID, lat, lon, of country
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

    geo_elements = root.findall("geoname")[1:] # removes the "earth" element

    result = {}
    if len(geo_elements) >= 1:
        result["continent"] = geo_elements[0].findtext("toponymName")
        result["geoname_continent_lat"] = geo_elements[0].findtext("lat")
        result["geoname_continent_lon"] = geo_elements[0].findtext("lng")
        if len(geo_elements) >= 2:
            result["geoname_countryName"] = geo_elements[1].findtext("name")
            result["geoname_country_geoId"] = geo_elements[1].findtext("geonameId")
            result["geoname_country_lat"] = geo_elements[1].findtext("lat")
            result["geoname_country_lon"] = geo_elements[1].findtext("lng")
            if len(geo_elements) >= 3:
                result["ADM1"] = geo_elements[2].findtext("toponymName") # admin levels often indicate "region, district, state"
                if len(geo_elements) >= 4:
                    result["ADM2"] = geo_elements[3].findtext("toponymName") # which is helpful to understand the context
                    if len(geo_elements) >= 5:
                        result["ADM3"] = geo_elements[4].findtext("toponymName") # especially on visual/graph/diagrams

    return result


# Fetch from cache (or update dictionary if needed) and return the country info, admin123 and continent
def get_geonames_data(geo_id, geonames_dict_cache, ):
    try:
        #ignore null, empty, or "world" geoIDs
        if pd.isna(geo_id) or str(geo_id).strip().lower() == "world" or str(geo_id).strip() == "":
            return {}

        #cast to int
        geo_id_int = int(float(geo_id))

        #if we already have/saved the geoID, return it
        if geo_id_int in geonames_dict_cache:
            return geonames_dict_cache[geo_id_int]

        # if not in dictionary: query API
        print(f"🔍 Querying new GeoNames ID: {geo_id_int}")
        result = query_geonames_api(geo_id_int)
        geonames_dict_cache[geo_id_int] = result

        # Save the updated dictionary immediately
        pd.DataFrame.from_dict(geonames_dict_cache, orient="index").reset_index().rename(
            columns={"index": "geonameId"}).to_excel(GEONAME_DICTIONARY_FILE_PATH, index=False)
        return result

    # we save the geonames dictionary if things crash, notably due to the API
    except RuntimeError:
        print("⚠️ Saving partial dictionary to avoid loss...")
        pd.DataFrame.from_dict(geonames_dict_cache, orient="index").reset_index().rename(
            columns={"index": "geonameId"}).to_excel(GEONAME_DICTIONARY_FILE_PATH, index=False)
        raise
    except Exception as e:
        print(f"Error handling geoID {geo_id}: {e}")
        return {}


# Process locations, by column loc 1234 then by row, to retrieve its hierarchy from the geonames API
def process_all_locations(data_file_path, geoname_dictionary_file_path, output_file_path):

    df, geonames_dict_cache = prep_phase(data_file_path, geoname_dictionary_file_path)


    for loc in ["loc1", "loc2", "loc3", "loc4"]:
        print(f"📍 Working on: {loc}")
        geoname_id_col = f"{loc} geoID"

        # Because I want the Excel to be human-readable,
        # I place the location's attributes from geonames (cont, country, admins)
        # in the columns after the raw(coded) location geonameID:
        # the pairs of [A, B]: new column A, which must come after column B
        new_columns = [
            ("geoname_cont", "location as stated"),
            ("geoname_country", "geoname_cont"),
            ("geoname_country_geoId", "geoname_country"),
            ("geoname_country_lat", "geoname_country_geoId"),
            ("geoname_country_lon", "geoname_country_lat"),
            ("geoname_ADM1", "geoname_country_lon"),
            ("geoname_ADM2", "geoname_ADM1"),
            ("geoname_ADM3", "geoname_ADM2"),
        ]

        # Create empty columns in the correct order (makes visual reading and debugging easier)
        for new_col_suffix, insert_after_suffix in new_columns:
            new_col_name = f"{loc} {new_col_suffix}"
            insert_after_col = f"{loc} {insert_after_suffix}"
            if new_col_name not in df.columns:
                insert_pos = df.columns.get_loc(insert_after_col) + 1
                df.insert(insert_pos, new_col_name, pd.NA)

        # Apply lookup on the get_geonames_data() for each row with lambdas
        try:
            df[f"{loc} geoname_cont"] = df[geoname_id_col].apply(lambda x: get_geonames_data(x, geonames_dict_cache).get("continent"))
            df[f"{loc} geoname_country"] = df[geoname_id_col].apply(
                lambda x: get_geonames_data(x, geonames_dict_cache).get("geoname_countryName"))
            df[f"{loc} geoname_country_geoId"] = df[geoname_id_col].apply(
                lambda x: get_geonames_data(x, geonames_dict_cache).get("geoname_country_geoId"))
            df[f"{loc} geoname_country_lat"] = df[geoname_id_col].apply(
                lambda x: get_geonames_data(x, geonames_dict_cache).get("geoname_country_lat"))
            df[f"{loc} geoname_country_lon"] = df[geoname_id_col].apply(
                lambda x: get_geonames_data(x, geonames_dict_cache).get("geoname_country_lon"))
            df[f"{loc} geoname_ADM1"] = df[geoname_id_col].apply(lambda x: get_geonames_data(x, geonames_dict_cache).get("ADM1"))
            df[f"{loc} geoname_ADM2"] = df[geoname_id_col].apply(lambda x: get_geonames_data(x, geonames_dict_cache).get("ADM2"))
            df[f"{loc} geoname_ADM3"] = df[geoname_id_col].apply(lambda x: get_geonames_data(x, geonames_dict_cache).get("ADM3"))
        except RuntimeError:
            print("⛔ Process halted due to API limit.")
            break
    # Save the final DataFrame with timestam
    output_file_path=  save_df_to_file(output_file_path, df)
    print("✅ All done. Output saved to:", output_file_path)
    return df, output_file_path


def test_query_geonames_api():
    """
    Test the query_geonames_api function to ensure the correct hierarchy is returned by
    calling http://api.geonames.org/hierarchy?geonameId=7285904&username=albertoolliaro
    """
    result_hierarchy = ["Europe", "Switzerland", "Canton de Genève", "Geneva", "Genthod",
                        "2658434", "47.00016", "8.01427"]
    # Arrange
    api_result = query_geonames_api(test_geonameID)

    cont = api_result.get("continent")
    country = api_result.get("geoname_countryName")
    admin1 = api_result.get("ADM1")
    admin2 = api_result.get("ADM2")
    admin3 = api_result.get("ADM3")
    country_geoId = api_result.get("geoname_country_geoId")
    country_lat = api_result.get("geoname_country_lat")
    country_lon = api_result.get("geoname_country_lon")

    # Assert
    assert result_hierarchy[0] == cont, f"Test failed! Expected '{result_hierarchy[0]}', but got '{cont}'."
    assert result_hierarchy[1] == country, f"Test failed! Expected '{result_hierarchy[1]}', but got '{country}'."
    assert result_hierarchy[2] == admin1, f"Test failed! Expected '{result_hierarchy[2]}', but got '{admin1}'."
    assert result_hierarchy[3] == admin2, f"Test failed! Expected '{result_hierarchy[3]}', but got '{admin2}'."
    assert result_hierarchy[4] == admin3, f"Test failed! Expected '{result_hierarchy[4]}', but got '{admin3}'."
    assert result_hierarchy[5] == country_geoId, f"Test failed! Expected '{result_hierarchy[5]}', but got '{country_geoId}'."
    assert result_hierarchy[6] == country_lat, f"Test failed! Expected '{result_hierarchy[6]}', but got '{country_lat}'."
    assert result_hierarchy[7] == country_lon, f"Test failed! Expected '{result_hierarchy[7]}', but got '{country_lon}'."

