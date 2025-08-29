import plotly.graph_objects as go


def create_and_plot_sankey_diagram_phd_data(data, output_path):
    years = ['2018', '2019', '2020', '2021', '2022']
    years_count = len(years)
    # Define the Sankey labels BASED ON THE ANALYSIS DATA 2018 TO 2022
    labels = [
        "English",
        "2018", "2019", "2020", "2021", "2022",  # articles per year
        "2018 reports", "2019 reports", "2020 reports", "2021 reports", "2022 reports",  # included articles per year
        "2018 routes", "2019 routes", "2020 routes", "2021 routes", "2022 routes"  # included routes per year
    ]

    # The source[x] target[x] pairs define the connections between the nodes
    # Uses the indices of the nodes in the 'labels' list
    source = [0, 0, 0, 0, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    target = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]
    # values are the "thickness" of each chord
    values = []

    labels[0] = labels[0] + ": " + str(data['total_articles_count'])

    # Build a flat list of numeric values in the order required by source/target
    years_int = [int(y) for y in years]
    values.extend([int(data['total_articles_per_year'].get(y, 0)) for y in years_int])
    values.extend([int(data['included_articles_per_year'].get(y, 0)) for y in years_int])
    values.extend([int(data['included_routes_per_year'].get(y, 0)) for y in years_int])

    for year in years:
        indx = years.index(year) + 1
        # number of TOTAL ARTICLES per year
        labels[indx] = labels[indx] + ": " + str(data['total_articles_per_year'].get(int(year), 0))
        # number of INCLUDED ARTICLES per year
        labels[indx + years_count] = labels[indx + years_count] + ": " + str(
            data['included_articles_per_year'].get(int(year), 0))
        # number of ROUTES per year
        labels[indx + years_count * 2] = labels[indx + years_count * 2] + ": " + str(
            data['included_routes_per_year'].get(int(year), 0))

    # Create the Sankey diagram ----------------------------------------------------------------------------------------
    fig = go.Figure(go.Sankey(
        node=dict(
            pad=15,
            thickness=20,  # restored original thickness
            line=dict(color="black", width=0.5),
            label=labels,
        ),
        link=dict(
            source=source,
            target=target,
            value=values,
        )
    ))

    # Add title and update the plot layout -----------------------------------------------------------------------------
    fig.update_layout(
        title_text="Sankey diagram of the selection steps and their yields",
        title_font_size=20,  # Increased title font size
        font=dict(size=15)  # Increased font size for labels
    )
    fig.show()

    fig.update_layout(title_text="Article and Routes Distribution Flow Per Year")
    fig.write_html(output_path)
