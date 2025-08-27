import pandas as pd
import plotly.graph_objects as go
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import os
import pickle
from datetime import datetime
from sankeydiagram import create_and_plot_sankey_diagram_phd_data


def create_wordcloud(text_series, output_path, title):
    # TODO for each value "text_series" it is actually a list of words in itself potentially
    text = ' '.join(text_series.dropna().astype(str))
    wordcloud = WordCloud(width=800, height=400, background_color='white').generate(text)

    plt.figure(figsize=(10, 5))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')
    plt.title(title)
    plt.savefig(output_path)
    plt.close()
    
    return wordcloud


def count_route_lengths(row):
    # TODO
    return sum(pd.notna(row[f'loc{i}']) for i in range(1, 5))


def run_exploratory_analysis(data_only_included_file_path, output_dir, full_data_file_path):
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

    # Initialize results dictionary
    results = {}

    try:
        # Read the data
        included_df = pd.read_excel(data_only_included_file_path, sheet_name=0)
        df_full = pd.read_excel(full_data_file_path, sheet_name=0)
        # Convert Publication Date to datetime in both dataframes
        included_df['Publication Date'] = pd.to_datetime(included_df['Publication Date'], errors='coerce')
        df_full['Publication Date'] = pd.to_datetime(df_full['Publication Date'], errors='coerce')

        # 1.1 Count total number of articles in data (exclude all -2+)
        total_articles_count = len(df_full[(df_full['mergeID'].astype(str).str.endswith('-1') | df_full['mergeID'].astype(str).str.endswith('-') | df_full['mergeID'].astype(str).str.endswith('-0'))])
        results['total_articles_count'] = total_articles_count

        # 1.2 Count articles that are include=1 (article means only the first route which ends with -1 as the others are routes within that article)
        included_articles_count = len(included_df['mergeID'].str.endswith('-1'))
        print(f">Included articles count: {included_articles_count}")
        results['included_articles_count'] = included_articles_count

        # 2.1 Count articles per year ----------------------------------------------------------------------------------
        total_articles_per_year = df_full[(
                    df_full['mergeID'].astype(str).str.endswith('-1') | df_full['mergeID'].astype(str).str.endswith(
                '-') | df_full['mergeID'].astype(str).str.endswith('-0'))][
            'Publication Date'].dt.year.value_counts().sort_index()
        print(f">total_articles_per_year: {total_articles_per_year}")
        results['total_articles_per_year'] = total_articles_per_year

        # 2.2 Count included articles per year -------------------------------------------------------------------------
        included_articles_per_year = included_df[included_df['mergeID'].astype(str).str.endswith('-1')][
            'Publication Date'].dt.year.value_counts().sort_index()
        print(f">Included articles per year: {included_articles_per_year}")
        results['included_articles_per_year'] = included_articles_per_year

        # 2.3 Count included routes per year ---------------------------------------------------------------------------
        included_routes_per_year = included_df[
            'Publication Date'].dt.year.value_counts().sort_index()
        print(f">Included routes per year: {included_routes_per_year}")
        results['included_routes_per_year'] = included_routes_per_year

        # # 3. Count routes per article included -----------------------------------------------------------------------
        # # TODO count the -2 -3 -4 -5... and then calc
        #     # for this: truncate the mergeID at the "-", then count
        # routes_per_article = included_df['route_count'].value_counts().sort_index()
        # results['routes_per_article'] = routes_per_article
        #
        # # 4. Count routes of length 2, 3, and 4 ----------------------------------------------------------------------
        total_number_of_routes = len(included_df)
        def is_non_empty(col_name):
            col = included_df[col_name]
            return col.notna() & col.astype(str).str.strip().ne('')

        count_have_4 = is_non_empty('loc4 geoID').sum()
        count_have_3 = is_non_empty('loc3 geoID').sum()
        counts_by_length = pd.Series({
            4: int(count_have_4),
            3: int(count_have_3 - count_have_4),
            2: int(total_number_of_routes - count_have_3),
        }).sort_index()
        results['count_of_routes_per_length'] = counts_by_length
        print(f">Route lengths -> {results['count_of_routes_per_length'].to_dict()}")

        # 5. Create and save Sankey diagram ----------------------------------------------------------------------------
        print("plotting sankey diagram...")
        sankey_path = os.path.join(output_dir, 'sankey_diagram.html')
        create_and_plot_sankey_diagram_phd_data(results, sankey_path)

        # 6. Count medicine quality distribution (ratio of "falsified" to "indistinguishable"
        medicine_quality_counts = included_df['medicine quality'].value_counts()
        print(f"medicine_quality_counts: {medicine_quality_counts}")
        results['medicine_quality_counts'] = medicine_quality_counts

        # 7. Analyze individuals per route -----------------------------------------------------------------------------
        individuals_stats = pd.to_numeric(included_df['number of individuals'], errors='coerce').agg({
            'median': 'median',
            'mean': 'mean'
        })
        print(f"number of individuals_stats: {individuals_stats}")
        results['individuals_stats'] = individuals_stats

        # 8. collect FMP encountered and plot/save WordClouds ----------------------------------------------------------
        create_wordcloud(
            included_df['Medical Products'],
            os.path.join(output_dir, 'medical_products_wordcloud.png'),
            'Medical Products WordCloud'
        )

        create_wordcloud(
            included_df['wording_used'],
            os.path.join(output_dir, 'wording_used_wordcloud.png'),
            'Wording Used WordCloud'
        )

        # 9. Calculate manufacturing roles percentage ------------------------------------------------------------------
        manufacturing_percentage = (
                included_df['loc1 node role'].str.contains('manufacturing', case=False, na=False).mecan() * 100
        )
        print(f">Manufacturing percentage: {manufacturing_percentage}")
        results['manufacturing_percentage'] = manufacturing_percentage

        # 10. collect countries, plot/save WordClouds, do a set and count how many different ones ----------------------
        country_cols = [f'loc{i} geoname_country' for i in range(1, 5)]
        existing_country_cols = [c for c in country_cols if c in included_df.columns]
        countries_series = (
            included_df[existing_country_cols]
            .stack(dropna=True)
            .astype(str)
            .str.strip()
        )
        countries_series = countries_series[countries_series.ne('')]
        countries_list = countries_series.tolist()

        create_wordcloud(
            pd.Series(countries_list),
            os.path.join(output_dir, 'countries_wordcloud.png'),
            'Countries WordCloud'
        )
        print(f">Unique countries count: {results['unique_countries_count']}")
        results['unique_countries_count'] = int(countries_series.nunique())
        print(f">Unique countries list: {results['unique_countries_list']}")
        results['unique_countries_list'] = countries_series.nunique()

        # Save to Excel
        print("Saving exploratory analysis results to Excel...")
        with pd.ExcelWriter(os.path.join(output_dir, 'detailed_analysis.xlsx')) as writer:
            results['total_articles_count'].to_frame().to_excel(writer, sheet_name='Total_Articles')
            results['included_articles_count'].to_frame().to_excel(writer, sheet_name='Total_Included_Articles')
            total_articles_per_year.to_frame().to_excel(writer, sheet_name='Articles_per_Year')
            included_articles_per_year.to_frame().to_excel(writer, sheet_name='Included Articles_per_Year')
            results['included_routes_per_year'].to_frame().to_excel(writer, sheet_name='Included Routes_per_Year')
            results['count_of_routes_per_length'].to_frame().to_excel(writer, sheet_name='Routes_by_Length')
            medicine_quality_counts.to_frame().to_excel(writer, sheet_name='Medicine_Quality')
            individuals_stats.to_excel(writer, sheet_name='Individuals_Stats')
            results['manufacturing_percentage'].to_frame().to_excel(writer, sheet_name='Manufacturing_Percentage')
            results['unique_countries_count'].to_frame('count').to_excel(writer, sheet_name='Countries_count')
            results['unique_countries_list'].to_excel(writer, sheet_name='Countries_List')



    except Exception as e:
        print(results)
        print(f"Error handling dataframe : {e}")
        # Save results with timestamp
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        results_path = os.path.join(ANALYSIS_DIR, f"results_preliminary_analysis_{timestamp}.pkl")
        with open(results_path, "wb") as f:
            pickle.dump(results, f)
        print(f"Saved exploratory analysis results to: {results_path}")
        return results

    print("Full exploratory success")
    return results


if __name__ == "__main__":
    DATA_GEONAMES_FILENAME = "1.1_ENGdata_geoID.xlsx"
    DATA_WITH_LOCATIONS_FETCHED_FILENAME = "1.3_ENGdata_geonamesExtracted.xlsx"
    ANALYSIS_DIR = "C:/Users/aolliaro/OneDrive - Nexus365/dphil excels/phd_analysis_data/"
    # 1.3 to 1.4 exploratory analysis, diagrams and stats
    explo_analysis_results = run_exploratory_analysis(
        os.path.join(ANALYSIS_DIR, DATA_WITH_LOCATIONS_FETCHED_FILENAME),
        ANALYSIS_DIR,
        os.path.join(ANALYSIS_DIR, DATA_GEONAMES_FILENAME)
    )





