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


###
# output of this function is to be used on this webapp: https://mk.bcgsc.ca/tableviewer/
def save_adjacency_matrix_to_txt_for_circos(ordered_matrix, countries_clockwise, txt_file_path):
    # Order nodes according to the countries_clockwise
    # TODO use the "C:/Users/aolliaro/OneDrive - Nexus365/DPhil data and analysis/countries_sorted_clockwise_byhand.xlsx" file instead of this hardcoded list

    def conform_label_to_circus(country):
        country = country.replace(" ", "")
        country = country.replace("'", "")
        country = country.replace("ü", "u")
        return country


    countries_clockwise_stripped = [ conform_label_to_circus(c) for c in countries_clockwise ]

    # Create DataFrame with order and labels as the first two columns
    order_column = list(range(1, len(countries_clockwise) + 1))
    matrix_df = pd.DataFrame(ordered_matrix, columns=countries_clockwise)
    matrix_df.insert(0, 'order', order_column)
    matrix_df.insert(1, 'labels', countries_clockwise_stripped)

    # Replace 0s with "-"
    matrix_df.replace(0, "-", inplace=True)

    # Save to TXT
    with open(txt_file_path, 'w') as f:
        # Write the header
        f.write("\t".join(["order", "labels"] + countries_clockwise_stripped) + "\n")
        # Write the rows including the node labels
        for idx, row in enumerate(matrix_df.iterrows()):
            _, row_values = row
            f.write(f"{order_column[idx]}\t{countries_clockwise_stripped[idx]}\t" + "\t".join(
                map(str, row_values.tolist()[2:])) + "\n")

    print(f"Adjacency matrix saved to {txt_file_path}")


def group_countries_by_region():
    Europe_CentralAsia = ["Ireland", "United Kingdom", "Portugal", "Spain", "France", "Belgium", "The Netherlands",
                           "Switzerland", "Italy", "Malta", "Germany", "Denmark", "Poland", "Lithuania", "Serbia",
                           "Bulgaria", "Türkiye", "Russia"]
    EastAsia_Pacific = ["China", "Hong Kong", "Macao", "South Korea", "Taiwan",
                           "Philippines", "Australia","Indonesia", "Singapore", "Malaysia", "Cambodia", "Vietnam",
                           "Thailand"]
    SouthAsia = ["Sri Lanka", "Bangladesh", "Bhutan", "India", "Nepal", "Pakistan"]
    MiddleEast_NorthAfrica = [ "Iran", "Iraq", "Saudi Arabia", "United Arab Emirates", "Oman", "Yemen", "Jordan", "Israel",
                           "Palestine", "Morocco"]
    EastSouthAfrica = [ "Sudan", "South Sudan", "Ethiopia", "Uganda", "Kenya", "Rwanda", "Tanzania"]
    SouthWestAfrica = ["South Africa", "Namibia", "Gabon", "Cameroon",]
    WestAfrica = [ "Nigeria", "Niger", "Ghana", "Ivory Coast", "Liberia", "Guinea", "The Gambia", "Senegal"]
    SouthAmerica = ["Trinidad and Tobago", "Colombia"]
    NorthAmerica = ["Puerto Rico", "Honduras", "Mexico", "United States", "Canada"]

if __name__ == "__main__":
    # working directory
    wdir = 'C:/Users/aolliaro/OneDrive - Nexus365/DPhil data and analysis/phd_analysis_data'
    # File paths
    edges_file_path = os.path.join(wdir, '1.5_nodes_edges.xlsx')
    output_csv_file_path = os.path.join(wdir, 'adjacency_matrix.csv')
    output_xlsx_file_path = os.path.join(wdir, 'adjacency_matrix.xlsx')
    output_txt_file_path_norm = os.path.join(wdir, 'adjacency_matrix_norm.txt')
    output_txt_file_path = os.path.join(wdir, 'adjacency_matrix.txt')

    # diff_data_temp()

    # countries sorted "clockwise" for a circular or chord graph display
    countries_clockwise = ["Ireland", "United Kingdom", "Portugal", "Spain", "France", "Belgium", "The Netherlands",
                           "Switzerland", "Italy", "Malta", "Germany", "Denmark", "Poland", "Lithuania", "Serbia",
                           "Bulgaria", "Türkiye", "Russia", "China", "Hong Kong", "Macao", "South Korea", "Taiwan",
                           "Philippines", "Australia", "Indonesia", "Singapore", "Malaysia", "Cambodia", "Vietnam",
                           "Thailand", "Sri Lanka", "Bangladesh", "Bhutan", "India", "Nepal", "Pakistan", "Iran",
                           "Iraq", "Saudi Arabia", "United Arab Emirates", "Oman", "Yemen", "Jordan", "Israel",
                           "Palestine", "Morocco", "Sudan", "South Sudan", "Ethiopia", "Uganda", "Kenya", "Rwanda",
                           "Tanzania", "South Africa", "Namibia", "Gabon", "Cameroon", "Nigeria", "Niger", "Ghana",
                           "Ivory Coast", "Liberia", "Guinea", "The Gambia", "Senegal", "Trinidad and Tobago",
                           "Colombia", "Puerto Rico", "Honduras", "Mexico", "United States", "Canada"]

    # Read edges from CSV
    edges, nodes_geoid_to_name = read_edges_from_excel(edges_file_path)

    # Create a weighted adjacency matrix
    output_adjacency_matrix = create_adjacency_matrix(edges, nodes_geoid_to_name, countries_clockwise, norm=False)
    # Create a non-weighted (normalised) adjacency matrix
    output_adjacency_matrix_norm = create_adjacency_matrix(edges, nodes_geoid_to_name, countries_clockwise, norm=True)

    # Save weighted adjacency matrix to CSV and XLSX
    save_adjacency_matrix(output_adjacency_matrix, countries_clockwise, output_csv_file_path, output_xlsx_file_path)

    # Save weighted adjacency matrix to TXT - for Circos chord graph visualisation
    save_adjacency_matrix_to_txt_for_circos(output_adjacency_matrix_norm, countries_clockwise, output_txt_file_path_norm)
    save_adjacency_matrix_to_txt_for_circos(output_adjacency_matrix, countries_clockwise, output_txt_file_path)
