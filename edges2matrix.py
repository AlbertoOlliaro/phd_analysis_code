import os
import pandas as pd
import numpy as np


def read_edges_from_csv(file_path):
    # Read the edges from the CSV file
    col_names = ["node1","node2","node3","node4"]
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
    nodes_names = pd.read_excel(file_path, sheet_name='nodes', index_col='ID' )
    nodes_names = nodes_names['country_name']
    print("nodes_names list from Excel:")
    print(nodes_names)
    return edges, nodes_names


def create_adjacency_matrix(edges, nodes_geoid_to_name, norm=False):
    nodes_geoid_to_name = nodes_geoid_to_name.to_dict()

    countries_clockwise = ["Ireland","United Kingdom","Portugal","Spain","France","Belgium","The Netherlands","Switzerland","Italy","Malta","Germany","Denmark","Poland","Lithuania","Serbia","Bulgaria","Türkiye","Russia","China","Hong Kong","Macao","South Korea","Taiwan","Philippines","Australia","Indonesia","Singapore","Malaysia","Cambodia","Vietnam","Thailand","Sri Lanka","Bangladesh","Bhutan","India","Nepal","Pakistan","Iran","Iraq","Saudi Arabia","United Arab Emirates","Oman","Yemen","Jordan","Israel","Palestine","Morocco","Sudan","South Sudan","Ethiopia","Uganda","Kenya","Rwanda","Tanzania","South Africa","Namibia","Gabon","Cameroon","Nigeria","Niger","Ghana","Ivory Coast","Liberia","Guinea","The Gambia","Senegal","Trinidad and Tobago","Colombia","Puerto Rico","Honduras","Mexico","United States","Canada"]

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


def save_adjacency_matrix_to_txt_for_circos(matrix, nodes, txt_file_path):
    # Order nodes according to the countries_clockwise
    # TODO use the "C:/Users/aolliaro/OneDrive - Nexus365/DPhil data and analysis/countries_sorted_clockwise_byhand.xlsx" file instead of this hardcoded list
    # countries_clockwise = { "Ireland","United Kingdom","Portugal","Spain","France","Belgium","The Netherlands","Switzerland","Italy","Malta","Germany","Denmark","Poland","Lithuania","Serbia","Bulgaria","Türkiye","Russia","China","Hong Kong","Macao","South Korea","Taiwan","Philippines","Australia","Indonesia","Singapore","Malaysia","Cambodia","Vietnam","Thailand","Sri Lanka","Bangladesh","Bhutan","India","Nepal","Pakistan","Iran","Iraq","Saudi Arabia","United Arab Emirates","Oman","Yemen","Jordan","Israel","Palestine","Morocco","Sudan","South Sudan","Ethiopia","Uganda","Kenya","Rwanda","Tanzania","South Africa","Namibia","Gabon","Cameroon","Nigeria","Niger","Ghana","Ivory Coast","Liberia","Guinea","The Gambia","Senegal","Trinidad and Tobago","Colombia","Puerto Rico","Honduras","Mexico","United States","Canada"}

    # Ensure all elements in countries_clockwise exist in nodes
    # sorted_nodes = [country for country in countries_clockwise if country in nodes]

    # Create an index map to reorder the matrix
    index_map = {node: sorted_nodes.index(node) for node in nodes if node in sorted_nodes}

    # Reorder the matrix
    ordered_matrix = np.zeros_like(matrix)
    for i, node in enumerate(nodes):
        if node in index_map:
            for j, inner_node in enumerate(nodes):
                if inner_node in index_map:
                    ordered_matrix[index_map[node], index_map[inner_node]] = matrix[i, j]

    # Create DataFrame with order and labels as the first two columns
    order_column = list(range(1, len(sorted_nodes) + 1))
    matrix_df = pd.DataFrame(ordered_matrix, index=sorted_nodes, columns=sorted_nodes)
    matrix_df.insert(0, 'order', order_column)
    matrix_df.insert(1, 'labels', sorted_nodes)

    # Replace 0s with "-"
    matrix_df.replace(0, "-", inplace=True)

    # Save to TXT
    with open(txt_file_path, 'w') as f:
        # Write the header
        f.write("\t".join(["order", "labels"] + sorted_nodes) + "\n")
        # Write the rows including the node labels
        for idx, row in enumerate(matrix_df.iterrows()):
            _, row_values = row
            f.write(f"{order_column[idx]}\t{sorted_nodes[idx]}\t" + "\t".join(map(str, row_values.tolist()[2:])) + "\n")

    print(f"Adjacency matrix saved to {txt_file_path}")

# def diff_data_temp():
#     countries_clockwise = { "Ireland","United Kingdom","Portugal","Spain","France","Belgium","The Netherlands","Switzerland","Italy","Malta","Germany","Denmark","Poland","Lithuania","Serbia","Bulgaria","Türkiye","Russia","China","Hong Kong","Macao","South Korea","Taiwan","Philippines","Australia","Indonesia","Singapore","Malaysia","Cambodia","Vietnam","Thailand","Sri Lanka","Bangladesh","Bhutan","India","Nepal","Pakistan","Iran","Iraq","Saudi Arabia","United Arab Emirates","Oman","Yemen","Jordan","Israel","Palestine","Morocco","Sudan","South Sudan","Ethiopia","Uganda","Kenya","Rwanda","Tanzania","South Africa","Namibia","Gabon","Cameroon","Nigeria","Niger","Ghana","Ivory Coast","Liberia","Guinea","The Gambia","Senegal","Trinidad and Tobago","Colombia","Puerto Rico","Honduras","Mexico","United States","Canada"}
#
#     # Function to read edges from CSV
#     def read_edges_from_csv(file_path):
#         edges = pd.read_csv(file_path, header=None)
#         print("Edges list from CSV:")
#         print(edges)
#         return edges
#
#     # Extract the set of countries from the edges DataFrame
#     def extract_countries_from_edges(edges):
#         countries_set = set(edges[0]).union(set(edges[1]))
#         return countries_set
#
#     # Path to the edges CSV file
#     edges_file_path = 'edge_pairs2018-2019_v3.csv'
#
#     # Reading edges from CSV
#     edges = read_edges_from_csv(edges_file_path)
#
#     # Extracting countries from edges
#     countries_from_edges = extract_countries_from_edges(edges)
#
#     # Compute the diff between the two sets
#     diff_clockwise_not_in_edges = countries_clockwise.difference(countries_from_edges)
#     diff_edges_not_in_clockwise = countries_from_edges.difference(countries_clockwise)
#
#     print("Countries in 'countries_clockwise' but not in edges:", diff_clockwise_not_in_edges)
#     print("Countries in edges but not in 'countries_clockwise':", diff_edges_not_in_clockwise)


if __name__ == "__main__":
    # working directory
    wdir = 'C:/Users/aolliaro/OneDrive - Nexus365/DPhil data and analysis/phd_analysis_data'
    # File paths
    edges_file_path = os.path.join(wdir, '1.5_nodes_edges.xlsx')
    output_csv_file_path = os.path.join(wdir, 'adjacency_matrix.csv')
    output_xlsx_file_path = os.path.join(wdir,'adjacency_matrix.xlsx')
    output_txt_file_path_norm = os.path.join(wdir, 'adjacency_matrix_norm.txt')
    output_txt_file_path = os.path.join(wdir, 'adjacency_matrix.txt')

    # diff_data_temp()

    # Read edges from CSV
    edges, nodes_names = read_edges_from_excel(edges_file_path)

    # Create a weighted adjacency matrix
    output_adjacency_matrix = create_adjacency_matrix(edges, nodes_names, norm=False)
    # Create a non-weighted (normalised) adjacency matrix
    adjacency_matrix_norm = create_adjacency_matrix(edges, nodes_names, norm=True)

    # Save weighted adjacency matrix to CSV and XLSX
    save_adjacency_matrix(output_adjacency_matrix, nodes_names, output_csv_file_path, output_xlsx_file_path)

    # Save weighted adjacency matrix to TXT - for Circos chord graph visualisation
    save_adjacency_matrix_to_txt_for_circos(adjacency_matrix_norm, nodes_names, output_txt_file_path_norm)
    save_adjacency_matrix_to_txt_for_circos(output_adjacency_matrix, nodes_names, output_txt_file_path)

