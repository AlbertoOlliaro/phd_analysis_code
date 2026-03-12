import os
import pandas as pd
from datetime import datetime

def add_timestamp_to_filename(file_path):
    root, ext = os.path.splitext(file_path)
    return f"{root}_{datetime.now().strftime("%Y%m%d%H%M%S")}{ext}"


def save_df_to_file(file_path, df):
    timestamped_file_path = add_timestamp_to_filename(file_path)
    df.to_excel(timestamped_file_path, index=False)
    return timestamped_file_path



# TODO
"""  this is a work in progress, the goal is to attemp to clean the falsified medical product category as well as
    giving the ["route stopped at", "discovery location"] columns a ref location (geoNameID)
"""
def clean_categories(data_file_path, cleanup_dictionary_path, output_file_path):
    skip_cleanup = False

    if os.path.exists(data_file_path):
        df = pd.read_excel(data_file_path, sheet_name=0)
    else:
        print("❌ No input file found, aborting method.")
        return None

    if os.path.exists(cleanup_dictionary_path):
        print("🔄 Loading existing GeoNames dictionary...")
        clean_fmp_dict_df = pd.read_excel(cleanup_dictionary_path, sheet_name=0)
        clean_fmp_dict_df_cache = clean_fmp_dict_df.set_index("key")['value'].to_dict()
    else:
        print("📁 No dictionary found.")
        skip_cleanup = True

    # Load only included data
    clean_df = df[df["include"] > 0]


    # columns to clean:
    # Medical Products
    def clean_fmp_text(fmp_text):

        # merge various terms (viagra and sildenafil) OR categorise them into a new column
        if pd.notna(fmp_text) :
            dirty_words = fmp_text.split(';')
            new_terms = ''
            # separate into items
            for term in dirty_words:
                # if term needs cleaning, then use the dict for the new value
                if term.strip().lower() in clean_fmp_dict_df_cache.keys():
                    new_term = clean_fmp_dict_df_cache.get(term.strip().lower())
                    new_terms += new_term + ";"
                    print(f"Term \'{term}\' converted to \'{new_term}\' ")
                else:
                    new_terms += term.strip() + ";"
            return new_terms
        else:
            # empty or not a reference to a location column loc1234, so return whatever is already there
            return fmp_text

    #
    for row in df.itertuples():
        for col in ["Medical Products"]:
            clean_df.at[row.Index, col] = clean_fmp_text(df.at[row.Index, col])

    # match the "route stopped at" and "discovery location" columns to the geonames_ID
    def match_to_geoID(row, loc_ref_name):
        if pd.isna(loc_ref_name) and loc_ref_name.strip in ["loc1", "loc2", "loc3", "loc4"]:
            return df.at[row.Index, loc_ref_name + " geoID"]
        else:
            # empty or not a reference to a location column loc1234, so return whatever is already there
            return loc_ref_name

    #for row in df.itertuples():
    #    for col in ["route stopped at", "discovery location"]:
    #        clean_df.at[row.Index, col] = match_to_geoID(row, df.at[row.Index, col])

    filepath_to_clean_excel = save_df_to_file(output_file_path, clean_df)

    return clean_df, filepath_to_clean_excel