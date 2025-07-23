import pandas as pd
import numpy as np
import plotly.graph_objects as go
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import os


def run_exploratory_analysis(input_file_path, output_dir):
    """
    Perform exploratory analysis on the input data and save results to the output directory.

    Parameters:
    -----------
    input_file_path : str
        Path to the input Excel file containing the data
    output_dir : str
        Directory where output files will be saved

    Returns:
    --------
    dict
        Dictionary containing summary statistics and analysis results
    """

    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # Initialize results dictionary
    results = {}

    # Read the data
    df = pd.read_excel(input_file_path)

    # 1. Count articles that are include=1
    included_articles = len(df[df['include'] == 1])
    results['included_articles'] = included_articles

    # 2. Count articles per year
    articles_per_year = df['year'].value_counts().sort_index()
    results['articles_per_year'] = articles_per_year

    # Create DataFrame for included articles
    included_df = df[df['include'] == 1]

    # 3. Count routes per article included
    routes_per_article = included_df['route_count'].value_counts().sort_index()
    results['routes_per_article'] = routes_per_article

    # 4. Count routes of length 2, 3, and 4
    def count_route_lengths(row):
        return sum(pd.notna(row[f'loc{i}']) for i in range(1, 5))

    included_df['route_length'] = included_df.apply(count_route_lengths, axis=1)
    route_lengths = included_df['route_length'].value_counts().sort_index()
    results['route_lengths'] = route_lengths

    # 5. Create and save Sankey diagram
    def create_sankey_diagram(df, output_path):
        total_articles = len(df)
        years = sorted(df['year'].unique())

        labels = ['All Articles']
        labels.extend([f'Year {year}' for year in years])

        source = []
        target = []
        values = []

        for i, year in enumerate(years, 1):
            year_count = len(df[df['year'] == year])
            source.append(0)
            target.append(i)
            values.append(year_count)

        fig = go.Figure(data=[go.Sankey(
            node=dict(
                pad=15,
                thickness=20,
                line=dict(color="black", width=0.5),
                label=labels,
            ),
            link=dict(
                source=source,
                target=target,
                value=values
            )
        )])

        fig.update_layout(title_text="Article Distribution Flow")
        fig.write_html(output_path)

    sankey_path = os.path.join(output_dir, 'sankey_diagram.html')
    create_sankey_diagram(included_df, sankey_path)

    # 6. Count medicine quality distribution
    medicine_quality_counts = df['medicine_quality'].value_counts()
    results['medicine_quality_counts'] = medicine_quality_counts

    # 7. Analyze individuals per route
    individuals_stats = included_df.groupby('route_length')['number_of_individuals'].agg({
        'median': 'median',
        'mean': 'mean'
    })
    results['individuals_stats'] = individuals_stats

    # 8. Create and save WordClouds
    def create_wordcloud(text_series, output_path, title):
        text = ' '.join(text_series.dropna().astype(str))
        wordcloud = WordCloud(width=800, height=400, background_color='white').generate(text)

        plt.figure(figsize=(10, 5))
        plt.imshow(wordcloud, interpolation='bilinear')
        plt.axis('off')
        plt.title(title)
        plt.savefig(output_path)
        plt.close()

    create_wordcloud(
        df['Medical Products'],
        os.path.join(output_dir, 'medical_products_wordcloud.png'),
        'Medical Products WordCloud'
    )

    create_wordcloud(
        df['wording_used'],
        os.path.join(output_dir, 'wording_used_wordcloud.png'),
        'Wording Used WordCloud'
    )

    # 9. Calculate manufacturing roles percentage
    manufacturing_percentage = (
            df['loc1_node_role'].str.contains('manufacturing', case=False, na=False).mean() * 100
    )
    results['manufacturing_percentage'] = manufacturing_percentage

    # Save summary statistics to Excel
    summary_dict = {
        'Metric': [
            'Total Included Articles',
            'Manufacturing Percentage in loc1',
        ],
        'Value': [
            included_articles,
            f"{manufacturing_percentage:.2f}%"
        ]
    }

    summary_df = pd.DataFrame(summary_dict)
    summary_df.to_excel(os.path.join(output_dir, 'analysis_summary.xlsx'), index=False)

    # Save detailed results to Excel
    with pd.ExcelWriter(os.path.join(output_dir, 'detailed_analysis.xlsx')) as writer:
        articles_per_year.to_frame('count').to_excel(writer, sheet_name='Articles_per_Year')
        routes_per_article.to_frame('count').to_excel(writer, sheet_name='Routes_per_Article')
        route_lengths.to_frame('count').to_excel(writer, sheet_name='Route_Lengths')
        medicine_quality_counts.to_frame('count').to_excel(writer, sheet_name='Medicine_Quality')
        individuals_stats.to_excel(writer, sheet_name='Individuals_Stats')

    return results


if __name__ == "__main__":
    # Example usage
    input_file = "path/to/your/input_file.xlsx"
    output_directory = "path/to/output/directory"

    try:
        results = run_exploratory_analysis(input_file, output_directory)
        print("Analysis completed successfully!")
        print("\nKey findings:")
        print(f"- Included articles: {results['included_articles']}")
        print(f"- Manufacturing percentage in loc1: {results['manufacturing_percentage']:.2f}%")
    except Exception as e:
        print(f"Error during analysis: {str(e)}")