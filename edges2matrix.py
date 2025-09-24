import os
import pandas as pd
import numpy as np

BASE_COUNTRY_ORDER = ["Ireland", "United Kingdom", "Portugal", "Spain", "France", "Belgium", "The Netherlands",
                      "Switzerland", "Italy", "Malta", "Germany", "Denmark", "Poland", "Lithuania", "Serbia",
                      "Bulgaria", "Türkiye", "Russia", "China", "Hong Kong", "Macao", "South Korea", "Taiwan",
                      "Philippines", "Australia", "Indonesia", "Singapore", "Malaysia", "Cambodia", "Vietnam",
                      "Thailand", "Sri Lanka", "Bangladesh", "Bhutan", "India", "Nepal", "Pakistan", "Iran", "Iraq",
                      "Saudi Arabia", "United Arab Emirates", "Oman", "Yemen", "Jordan", "Israel", "Palestine",
                      "Morocco", "Sudan", "South Sudan", "Ethiopia", "Uganda", "Kenya", "Rwanda", "Tanzania",
                      "South Africa", "Namibia", "Gabon", "Cameroon", "Nigeria", "Niger", "Ghana", "Ivory Coast",
                      "Liberia", "Guinea", "The Gambia", "Senegal", "Trinidad and Tobago", "Colombia", "Puerto Rico",
                      "Honduras", "Mexico", "United States", "Canada"]


def read_edges_from_csv(file_path):
    # Read the edges from the CSV file
    col_names = ["node1", "node2", "node3", "node4"]
    edges = pd.read_csv(file_path, names=col_names, header=None)
    print("Edges list from CSV:")
    print(edges)
    return edges


def read_edges_from_excel(file_path):
    # Read the edges from the Excel file
    cols = ['Source', 'Target']
    edges = pd.read_excel(file_path, sheet_name='edges')
    edges = edges[cols]
    print("Edges list from Excel:")
    print(edges)
    nodes_names = pd.read_excel(file_path, sheet_name='nodes', index_col='ID')
    nodes_names = nodes_names['country_name']
    print("nodes_names list from Excel:")
    print(nodes_names)
    return edges, nodes_names


def create_adjacency_matrix(edges, nodes_geoid_to_name, countries_clockwise, norm=False):
    nodes_geoid_to_name = nodes_geoid_to_name.to_dict()

    # Initialize an empty adjacency matrix
    size = len(nodes_geoid_to_name)
    adjacency_matrix = np.zeros((size, size), dtype=int)

    # Populate the adjacency matrix with edges
    for df_row_idx, edge in edges.iterrows():
        src_m_idx = countries_clockwise.index(nodes_geoid_to_name.get(edge['Source']))
        dest_m_idx = countries_clockwise.index(nodes_geoid_to_name.get(edge['Target']))
        if norm:
            adjacency_matrix[src_m_idx, dest_m_idx] = 1
        else:
            adjacency_matrix[src_m_idx, dest_m_idx] += 1

    return adjacency_matrix


def save_adjacency_matrix(matrix, nodes, csv_file_path, xlsx_file_path):
    # Convert the matrix to a DataFrame
    matrix_df = pd.DataFrame(matrix, index=nodes, columns=nodes)

    # Save the DataFrame to a CSV file
    matrix_df.to_csv(csv_file_path)
    print(f"Adjacency matrix saved to {csv_file_path}")

    # Save the DataFrame to an XLSX file
    matrix_df.to_excel(xlsx_file_path, engine='openpyxl')
    print(f"Adjacency matrix saved to {xlsx_file_path}")


def save_adjacency_matrix_to_txt_for_circos(ordered_matrix, labels_ordered_clockwise, output_txt_file_path):
    """
    Sort the columns and rows of the adjacency matrix according to the order of the countries_clockwise list
    output of this function is to be used on this webapp: https://mk.bcgsc.ca/tableviewer/
    Args:
        ordered_matrix: adjacency matrix with columns and row ordered according the countries_clockwise list's order
        labels_ordered_clockwise: Series of countries sorted "clockwise" for a circular or chord graph display
        output_txt_file_path: full path to the output file
    """

    def conform_label_to_circos(label):
        label = label.replace(" ", "")
        label = label.replace("'", "")
        label = label.replace("ü", "u")
        label = label.replace("HongKong", "HongKongSAR")
        return label

    countries_clockwise_stripped = [conform_label_to_circos(c) for c in labels_ordered_clockwise]

    # Create DataFrame with order and labels as the first two columns
    order_column = list(range(1, len(labels_ordered_clockwise) + 1))
    matrix_df = pd.DataFrame(ordered_matrix, columns=labels_ordered_clockwise)
    matrix_df.insert(0, 'order', order_column)
    matrix_df.insert(1, 'labels', countries_clockwise_stripped)

    # Replace 0s with "-"
    matrix_df.replace(0, "-", inplace=True)

    # Save to TXT
    with open(output_txt_file_path, 'w') as f:
        # Write the header
        f.write("\t".join(["order", "labels"] + countries_clockwise_stripped) + "\n")
        # Write the rows including the node labels
        for idx, row in enumerate(matrix_df.iterrows()):
            _, row_values = row
            f.write(f"{order_column[idx]}\t{countries_clockwise_stripped[idx]}\t" + "\t".join(
                map(str, row_values.tolist()[2:])) + "\n")

    print(f"Adjacency matrix saved to {output_txt_file_path}")


def aggregate_adjacency_by_region(
    adj_matrix_country: np.ndarray,
    country_to_region_dict: dict,
    binary: bool = False,
    remove_self_loops: bool = False,
) -> np.ndarray:
    """
    Aggregate a country-level adjacency matrix into a region-level adjacency matrix.
    This method achieves this by computing R = M^T * A * M
    R: region adjacency matrix (T transpose)
    A: country adjacency matrix
    M: incidence matrix (#regions * #countries)
    Args:
        adj_matrix_country: (Nc x Nc) numpy array. Rows/cols must align with countries_clockwise.
        countries_clockwise: list of Nc country names in the same order as adj_matrix_country axes.
        regions_clockwise: list of Nr region names in the desired output order.
        country_to_region_dict: dict mapping country -> region.
        binary: if True, convert any positive counts in the resulting region matrix to 1.
        remove_self_loops: if True, zero out the diagonal of the resulting region matrix.

    Returns:
        (Nr x Nr) numpy array where entry (i, j) is the sum of flows from region i to region j.
    """
    Nc = len(countries_clockwise)
    Nr = len(regions_clockwise)

    if adj_matrix_country.shape != (Nc, Nc):
        raise ValueError(
            f"adj_matrix_country shape {adj_matrix_country.shape} does not match "
            f"countries list length {Nc}"
        )

    # Build incidence matrix M (Nc x Nr): country -> region
    M = np.zeros((Nc, Nr), dtype=int)
    region_index = {r: idx for idx, r in enumerate(regions_clockwise)}

    missing_countries = []
    missing_regions = []
    for i, country in enumerate(countries_clockwise):
        region = country_to_region_dict.get(country)
        if region is None:
            missing_countries.append(country)
            continue
        j = region_index.get(region)
        if j is None:
            missing_regions.append(region)
            continue
        M[i, j] = 1

    if missing_countries:
        raise KeyError(f"Countries missing in country_to_region_dict: {missing_countries}")
    if missing_regions:
        raise KeyError(f"Regions not found in regions_clockwise: {sorted(set(missing_regions))}")

    # Aggregate: R = M^T * A * M
    region_adj = M.T @ adj_matrix_country @ M

    if binary:
        region_adj = (region_adj > 0).astype(int)

    if remove_self_loops:
        np.fill_diagonal(region_adj, 0)

    return region_adj



if __name__ == "__main__":
    # working directory
    wdir = 'C:/Users/aolliaro/OneDrive - Nexus365/DPhil data and analysis/phd_analysis_data'
    # File paths
    edges_file_path = os.path.join(wdir, '1.5_nodes_edges.xlsx')
    output_csv_file_path = os.path.join(wdir, 'adjacency_matrix.csv')
    output_xlsx_file_path = os.path.join(wdir, 'adjacency_matrix.xlsx')
    output_txt_file_path_norm = os.path.join(wdir, 'adjacency_matrix_norm.txt')
    output_txt_file_path_regions_norm = os.path.join(wdir, 'adjacency_matrix_regions_norm.txt')
    output_txt_file_path = os.path.join(wdir, 'adjacency_matrix.txt')
    input_countries_regions_file_path = os.path.join('C:/Users/aolliaro/OneDrive - Nexus365/DPhil data and analysis',
                                                     'country-to-region_sorted_clockwise_UNm49.xlsx')

    """CAREFUL this pairing list of sorted countries and corresponding regions
    has been extracted from the "1.3_ENGdata_geonamesExtracted.xlsx" file
    BUT the regions are assigned manually/matching to the UN m49 geoscheme subregions
    if new countries appear, this process has to be redone/expanded
    """
    # initialise the countries and regions dict and lists  -----------------------------
    df_countries_regions = pd.read_excel(input_countries_regions_file_path, index_col=0)
    # df of regions indexed by country
    regions = pd.read_excel(
        input_countries_regions_file_path,
        usecols=['country', 'region'],
        index_col='country'
    )
    # dict of regions indexed by country
    country_to_region_dict = regions['region'].to_dict()
    # list of countries sorted "clockwise" for a circular or chord graph display
    countries_clockwise = df_countries_regions['country'].tolist()
    # list of regions sorted "clockwise" for a circular or chord graph display
    regions_clockwise = regions['region'].unique()

    # Read edges from CSV
    edges, nodes_geoid_to_name = read_edges_from_excel(edges_file_path)

    # Create a weighted adjacency matrix
    output_adjacency_matrix = create_adjacency_matrix(edges, nodes_geoid_to_name, countries_clockwise, norm=False)
    # Create a non-weighted (normalised) adjacency matrix
    output_adjacency_matrix_norm = create_adjacency_matrix(edges, nodes_geoid_to_name, countries_clockwise, norm=True)
    # convert the country normalised matrixed to a regions' adjacency matrix
    output_adjacency_matrix_regions = aggregate_adjacency_by_region(output_adjacency_matrix_norm, country_to_region_dict)

    # Save weighted adjacency matrix to CSV and XLSX
    save_adjacency_matrix(output_adjacency_matrix, countries_clockwise, output_csv_file_path, output_xlsx_file_path)
    # Save weighted adjacency matrix to TXT - for Circos chord graph visualisation
    save_adjacency_matrix_to_txt_for_circos(output_adjacency_matrix, countries_clockwise, output_txt_file_path)
    # Save normalised adjacency matrix to TXT - for Circos chord graph visualisation
    save_adjacency_matrix_to_txt_for_circos(output_adjacency_matrix_norm, countries_clockwise,
                                            output_txt_file_path_norm)
    # Save normalised adjacency matrix of regions to .txt - for Circos chord graph visualisation
    save_adjacency_matrix_to_txt_for_circos(output_adjacency_matrix_regions, regions_clockwise,
                                            output_txt_file_path_regions_norm)
