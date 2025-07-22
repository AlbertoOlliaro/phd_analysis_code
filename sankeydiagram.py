import plotly.graph_objects as go

# Define the data for the Sankey diagram based on the provided information
labels = [
    "English: 1057", "2018: 78", "2019: 148",
    "2018 reports: 14", "2018 routes: 28",
    "2019 reports: 24", "2019 routes: 29"
]

# Define the connections between the nodes
# Use the indices of the nodes in the 'labels' list
source = [0, 0, 1, 3, 2, 5]
target = [1, 2, 3, 4, 5, 6]
values = [78, 148, 14, 28, 24, 29]

# Create the Sankey diagram
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

# Add title and update the plot layout
fig.update_layout(
    title_text="Sankey diagram of the selection steps and their yields",
    title_font_size=20,  # Increased title font size
    font=dict(size=15)  # Increased font size for labels
)
fig.show()