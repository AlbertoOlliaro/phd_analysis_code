import os
import pandas as pd
import numpy as np



def read_edges_from_csv(file_path):
    # Read the edges from the CSV file
    col_names = ["node1", "node2", "node3", "node4"]
    edges = pd.read_csv(file_path, names=col_names, header=None)
    print("Edges list from CSV:")
    print(edges)
    return edges


def make_edges_list_from_excel(file_path, ad_hoc_label=False):
    # Read the edges from the Excel file
    cols = ['Source', 'Target']
    edges = pd.read_excel(file_path, sheet_name='edges')
    edges = edges[cols]
    print("Edges list from Excel:")
    print(edges)

    if not ad_hoc_label:
        nodes_names = pd.read_excel(file_path, sheet_name='nodes', index_col='ID')
        nodes_names = nodes_names.to_dict()['node_label']
        edges['Source'] = edges['Source'].apply(lambda x: nodes_names[x])
        edges['Target'] = edges['Target'].apply(lambda x: nodes_names[x])

    return edges


def create_adjacency_matrix(edges_verbose, peripheral_sorted_clockwise, norm=False):
    # Initialize an empty adjacency matrix
    size = len(peripheral_sorted_clockwise)
    adjacency_matrix = np.zeros((size, size), dtype=int)

    # Populate the adjacency matrix with edges
    for df_row_idx, edge in edges_verbose.iterrows():
        src_m_idx = peripheral_sorted_clockwise.index(edge['Source'])
        dest_m_idx = peripheral_sorted_clockwise.index(edge['Target'])
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


if __name__ == "__main__":
    # working directory
    wdir = 'C:/Users/aolliaro/OneDrive - Nexus365/DPhil data and analysis/phd_analysis_data'
    # File paths
    # TODO !! Careful: should use the file paths from the data_pipeline or make a config file
    #edges_verbose_file_path = os.path.join(wdir, "3.5_edges_verbose.csv")
    edges_file_name_list = ["step1_nodes_edges", "step2_nodes_edges_weight1", "step3_nodes_edges_noloops","step4_nodes_subregions_edges"]
    edge_file_ext = '.xlsx'
    ad_hoc_label = [False, False, False, True]
    input_countries_regions_file_path = os.path.join(wdir, 'aux_country-to-region_sorted_clockwise_UNm49.xlsx')

    output_csv_file_name = 'adjacency_matrix.csv'
    output_xlsx_file_name = 'adjacency_matrix.xlsx'
    output_txt_file_name = 'adjacency_matrix.txt'
    output_norm_txt_file_name = 'adjacency_matrix_norm.txt'

    # initialise the countries and regions sorted lists  -----------------------------
    df_countries_sorted_clockwise = pd.read_excel(
        input_countries_regions_file_path,
        index_col=0,
        sheet_name=0)
    # df of regions indexed by country
    df_regions_sorted_clockwise = pd.read_excel(
        input_countries_regions_file_path,
        usecols=['chord_geo_order', 'subregion_m49'],
        index_col='chord_geo_order',
        sheet_name=1
    )

    # list of countries sorted "clockwise" for a circular or chord graph display
    countries_clockwise = df_countries_sorted_clockwise['country'].tolist()
    print("countries sorted clockwise")
    print(countries_clockwise)
    # list of regions sorted "clockwise" for a circular or chord graph display
    regions_clockwise = df_regions_sorted_clockwise['subregion_m49'].tolist()
    print("regions sorted clockwise:")
    print(regions_clockwise)


    for i in range(len(edges_file_name_list)):
        # Read edges from the edges sheet
        edges = make_edges_list_from_excel(os.path.join(wdir,edges_file_name_list[i]+edge_file_ext), ad_hoc_label[i])

        if i == 3:
            nodes_clockwise = regions_clockwise
        else:
            nodes_clockwise = countries_clockwise

        # Create a weighted adjacency matrix
        output_adjacency_matrix = create_adjacency_matrix(edges, nodes_clockwise, norm=False)
        # Save weighted adjacency matrix to CSV and XLSX
        save_adjacency_matrix(
            output_adjacency_matrix,
            nodes_clockwise,
            os.path.join(wdir, edges_file_name_list[i]+output_csv_file_name),
            os.path.join(wdir, edges_file_name_list[i]+output_xlsx_file_name))
        # Save weighted adjacency matrix to TXT - for Circos chord graph visualisation
        save_adjacency_matrix_to_txt_for_circos(
            output_adjacency_matrix,
            nodes_clockwise,
            os.path.join(wdir, edges_file_name_list[i]+output_txt_file_name))