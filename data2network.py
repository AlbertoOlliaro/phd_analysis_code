import os
import pandas as pd
from datetime import datetime


# transform data to two files suitable for Gephi.
# Gephi requires a nodes table and an edges table

# the nodes table is a list of locations with attributes such as lat and lon (currently locations are countries)
# the edges table is a list of connections between locations with attributes such as time interval
#     time interval according to https://gephi.org/users/supported-graph-formats/spreadsheet/

def add_timestamp_to_filename(file_path):
    root, ext = os.path.splitext(file_path)
    return f"{root}_{datetime.now().strftime("%Y%m%d%H%M%S")}{ext}"


def construct_nodes(indexed_df):
    """
    Constructs the list of nodes from the input dataframe as a dictionary table with columns:
    ID, lat, lon, country_name, country_geoId
    (for now, ID and country_geoId are the same)
    and returns it
    Args:
        indexed_df: dict keyed by mergeID where each value is a row dict

    Returns: nodes_df (pandas.DataFrame)

    """

    node_attributes_col = ["geoname_country", "geoname_country_geoId", "geoname_country_lat", "geoname_country_lon", "geoname_countryCode"]
    nodes_by_id = {}

# TODO use the "aux_geonames_ID_dictionary" file instead:
    #  use the country geoID and name and lat lon columns only, make a set, done
    for loc in ["loc1", "loc2", "loc3", "loc4"]:
        name_col = f"{loc} {node_attributes_col[0]}"
        geo_id_col = f"{loc} {node_attributes_col[1]}"
        lat_col = f"{loc} {node_attributes_col[2]}"
        lon_col = f"{loc} {node_attributes_col[3]}"
        country_code_col = f"{loc} {node_attributes_col[4]}"

        for _, row in indexed_df.items():
            geo_id = row.get(geo_id_col)
            if pd.isna(geo_id) or str(geo_id).strip() == "" or str(geo_id).strip().lower() == "world":
                continue

            node_id = str(int(float(geo_id))) if str(geo_id).strip().isdigit() or str(geo_id).replace(".", "", 1).isdigit() else str(geo_id).strip()
            if node_id not in nodes_by_id:
                # Fetch attributes (first occurrence wins)
                country_name = row.get(name_col)
                country_code = row.get(country_code_col)
                lat = row.get(lat_col)
                lon = row.get(lon_col)

                nodes_by_id[node_id] = {
                    "ID": node_id,
                    "lat": lat,
                    "lon": lon,
                    "country_name": None if pd.isna(country_name) else str(country_name),
                    "country_geoId": node_id,
                    "countryCode": country_code,
                }

    nodes_df = pd.DataFrame(list(nodes_by_id.values())).drop_duplicates(subset=["ID"]).reset_index(drop=True)
    return nodes_df


def construct_edges(indexed_df):
    """
    Construct the table of edges from the input dataframe with columns:
    ID, Source, Target, Label
    the ID is the mergeID of the route plus suffix of the route segment (i.e. _1, _2, _3)

    args: indexed_df
    Returns: edges_df
    """

    edge_attributes_col = ["Medical Products", "incident date"]
    edge_attributes_col_suffix = ["geoname_country", "geoname_country_geoId"]

    # loc 3 and/or 4 related columns might be empty
    # based on route length, there will be 1 2 or 3 edges with the same mergeID
    edges = []

    for merge_id, row in indexed_df.items():
        # Build ordered list of stops with both country name and geoId, skipping empties
        stops = []
        for loc in ["loc1", "loc2", "loc3", "loc4"]:
            name_col = f"{loc} {edge_attributes_col_suffix[0]}"
            id_col = f"{loc} {edge_attributes_col_suffix[1]}"
            name_val = row.get(name_col)
            id_val = row.get(id_col)
            if pd.isna(id_val) or str(id_val).strip() == "" or str(id_val).strip().lower() == "world":
                continue
            node_id = str(int(float(id_val))) if str(id_val).strip().isdigit() or str(id_val).replace(".", "", 1).isdigit() else str(id_val).strip()
            stops.append({
                "id": node_id,
                "name": None if pd.isna(name_val) else str(name_val)
            })

        # Create edges between consecutive valid stops
        if len(stops) < 2:
            continue

        medical_products = row.get(edge_attributes_col[0])
        incident_date = row.get(edge_attributes_col[1])

        for i in range(len(stops) - 1):
            src = stops[i]
            tgt = stops[i + 1]
            edges.append({
                "ID": f"{merge_id}_{i+1}", # looks like 12345-X_Y (X is the route number and Y is the segment in that route)
                "Source": src["id"],
                "Target": tgt["id"],
                "Label": f"{src['name']} -> {tgt['name']}" if src["name"] or tgt["name"] else "",
                "Medical Products": None if pd.isna(medical_products) else str(medical_products),
                "incident date": incident_date if (incident_date is None or not pd.isna(incident_date)) else None
            })

    edges_df = pd.DataFrame(edges).reset_index(drop=True)
    return edges_df


def transform2network(only_included_routes_data_file_path, output_file_path):
    """
    Produces an Excel file with two sheets.
    The first sheet contains the list of nodes (set of unique countries)
    and the second sheet the list of edges with some additional information (what was traded and when).

    Args:
        only_included_routes_data_file_path:
        output_file_path:

    Returns:
        Path to the written Excel file
    """

    routes_df = pd.read_excel(only_included_routes_data_file_path, sheet_name=0)
    indexed_df = routes_df.set_index("mergeID").to_dict(orient="index")

    # Build nodes and edges
    nodes_df = construct_nodes(indexed_df)
    edges_df = construct_edges(indexed_df)
    timestamped_file_path = add_timestamp_to_filename(output_file_path)

    with pd.ExcelWriter(timestamped_file_path, engine="openpyxl") as writer:
        nodes_df.to_excel(writer, sheet_name="nodes", index=False) # save nodes on sheet 1 "nodes"
        edges_df.to_excel(writer, sheet_name="edges", index=False) # save edges on sheet 2 "edges"

    return [nodes_df, edges_df], timestamped_file_path


def merge_edges(network_data_file_path, output_file_path):
    """
        Produces an Excel file with network data but merging edges, effectively setting all edges weight to 1;
        The first sheet contains the list of nodes (set of unique countries)
        and the second sheet the list of edges (now each pair will be unique).

        Args:
            network_data_file_path:
            output_file_path:

        Returns:
            A paired node_df and edge_df, Path to the written Excel file
        """
    # retrieve nodes and edges (produced in previous step transform2network
    nodes_df = pd.read_excel(network_data_file_path, sheet_name="nodes")
    edges_df = pd.read_excel(network_data_file_path, sheet_name="edges")

    # TODO : implement instead a function which before dropping aggregates the other values such as medical products and dates
    #  https://stackoverflow.com/questions/50242968/check-for-duplicate-values-in-pandas-dataframe-column
    new_edges_df = edges_df.drop_duplicates(subset=['Source', 'Target'], inplace=False)

    timestamped_file_path = add_timestamp_to_filename(output_file_path)

    with pd.ExcelWriter(timestamped_file_path, engine="openpyxl") as writer:
        nodes_df.to_excel(writer, sheet_name="nodes", index=False)  # save nodes on sheet 1 "nodes"
        new_edges_df.to_excel(writer, sheet_name="edges", index=False)  # save edges on sheet 2 "edges"

    return [nodes_df, new_edges_df], timestamped_file_path


def remove_self_loops(network_data_file_path, output_file_path):
    """
        Produces an Excel file with network data but without loops;
        The first sheet contains the list of nodes (set of unique countries)
        and the second sheet the list of edges.

        Args:
            network_data_file_path:
            output_dir:
            output_file_path:

        Returns:
            A paired node_df and edge_df, Path to the written Excel file
        """
    # retrieve nodes and edges (produced in previous step transform2network
    nodes_df = pd.read_excel(network_data_file_path, sheet_name="nodes")
    edges_df = pd.read_excel(network_data_file_path, sheet_name="edges")

    edges_df = edges_df[edges_df["Source"] != edges_df["Target"]]

    timestamped_file_path = add_timestamp_to_filename(output_file_path)

    with pd.ExcelWriter(timestamped_file_path, engine="openpyxl") as writer:
        nodes_df.to_excel(writer, sheet_name="nodes", index=False)  # save nodes on sheet 1 "nodes"
        edges_df.to_excel(writer, sheet_name="edges", index=False)  # save edges on sheet 2 "edges"

    return [nodes_df, edges_df], timestamped_file_path

def group_countries_into_region(network_data_file_path, country_to_region_dict_file_path, output_file_path):
    """
        Produces an Excel file with countries grouped into subregions using the dictionary provdied (UN m49 scheme);

        In both files, the first sheet contains the list of nodes (set of unique countries/regions)
        and the second sheet the list of edges.

        Args:
            network_data_file_path: path to the network data file (nodes and edges)
            country_to_region_dict_file_path: path to the dictionary file that matches countries to subregions
            output_file_path: output path with the new network data

        Returns:
            A paired node_df and edge_df, Path to the written Excel file
        """
    # retrieve nodes and edges (produced in previous step transform2network
    nodes_df = pd.read_excel(network_data_file_path, sheet_name="nodes")
    edges_df = pd.read_excel(network_data_file_path, sheet_name="edges")

    if os.path.exists(country_to_region_dict_file_path):
        print("🔄 Loading dictionary 'nodes as a geoID to country_name' ...")
        geo_id_to_country_name_dict = nodes_df.set_index("ID")['country_name'].to_dict()

        print("🔄 Loading dictionary 'country to m49 subregion' ...")
        country_to_region_dict_temp = pd.read_excel(country_to_region_dict_file_path, sheet_name=0)
        country_to_region_dict = country_to_region_dict_temp.set_index("country")['subregion_m49'].to_dict()

        print("🔄 Loading dictionary 'subregion m49 IDs' ...")
        region_to_feature_dict_temp = pd.read_excel(country_to_region_dict_file_path, sheet_name=1)

    else:
        print("📁 No dictionary found.")
        return None

    # process the edges
    # need to go have a look at the edges2matrix file and how I did it there
    new_edges_df = edges_df.copy()
    new_edges_df["Source"] = edges_df["Source"].map(geo_id_to_country_name_dict).map(country_to_region_dict)
    new_edges_df["Target"] = edges_df["Target"].map(geo_id_to_country_name_dict).map(country_to_region_dict)

    # processing the nodes is simply replacing the country_nodes tables with the region_nodes tables
    new_nodes_df = region_to_feature_dict_temp.copy()
    new_nodes_df["ID"] = new_nodes_df["subregion_m49"]
    new_nodes_df.set_index("ID")

    # print("...Merging nodes strategy : summing variables")
    # sum the properties such as node category, origin, destination, manufacturing...?

    timestamped_file_path = add_timestamp_to_filename(output_file_path)

    with pd.ExcelWriter(timestamped_file_path, engine="openpyxl") as writer:
        new_nodes_df.to_excel(writer, sheet_name="nodes", index=False)  # save nodes on sheet 1 "nodes"
        new_edges_df.to_excel(writer, sheet_name="edges", index=False)  # save edges on sheet 2 "edges"

    return [new_nodes_df, new_edges_df], timestamped_file_path


def create_verbose_edgelist_network(nodes_edges, verbose_edgelist_output_file_path):
    """
    Produces an Excel file with one sheet.
    with the list of edges with some additional information (what was traded and when).

    Args:
        nodes_edges: in the form of a pair of dataframes (nodes and edges) created in transform2network [nodes_df, edges_df]
        verbose_edgelist_output_file_path:

    Returns:
        Path to the written Excel file
    """

    nodes_df = nodes_edges[0]
    edges_df = nodes_edges[1]

    # Build edges list with the country names instead of geoIDs
    geo_id_to_country_name_dict = nodes_df.set_index("ID")['country_name'].to_dict()
    edges_verbose_df = edges_df.copy()
    edges_verbose_df["Source"] = edges_verbose_df["Source"].map(geo_id_to_country_name_dict)
    edges_verbose_df["Target"] = edges_verbose_df["Target"].map(geo_id_to_country_name_dict)
    verbose_edgelist_output_timestamped_file_path = add_timestamp_to_filename(verbose_edgelist_output_file_path)

    edges_verbose_df.to_csv(verbose_edgelist_output_timestamped_file_path) # save edges on sheet 2 "edges"

    return edges_verbose_df, verbose_edgelist_output_timestamped_file_path