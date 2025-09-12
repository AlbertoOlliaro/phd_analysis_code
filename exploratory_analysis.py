import pandas as pd
from mywordcloud import create_wordcloud
import os
import pickle
from datetime import datetime
from sankeydiagram import create_and_plot_sankey_diagram_phd_data

def add_timestamp_to_filename(file_path):
    root, ext = os.path.splitext(file_path)
    return f"{root}_{datetime.now().strftime("%Y%m%d%H%M%S")}{ext}"


def run_exploratory_analysis(data_only_included_file_path, output_dir, full_data_file_path, exploratory_analysis_file_path):
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

    # Initialise results dictionary
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
        print(f">Included articles count: {total_articles_count}")

        # 1.2 Count articles that are include=1 (article means only the first route which ends with -1 as the others are routes within that article)
        included_articles_count = included_df['mergeID'].str.endswith('-1').sum()
        total_routes_count = len(included_df['mergeID'])
        results['included_articles_count'] = included_articles_count
        results['total_routes_count'] = total_routes_count
        print(f">Included articles count: {included_articles_count}")
        print(f">Total routes count: {total_routes_count}")

        # 2.1 Count articles per year ----------------------------------------------------------------------------------
        total_articles_per_year = df_full[(
                    df_full['mergeID'].astype(str).str.endswith('-1') | df_full['mergeID'].astype(str).str.endswith(
                '-') | df_full['mergeID'].astype(str).str.endswith('-0'))][
            'Publication Date'].dt.year.value_counts().sort_index()
        results['total_articles_per_year'] = total_articles_per_year
        print(f">total_articles_per_year: {total_articles_per_year}")

        # 2.2 Count included articles per year -------------------------------------------------------------------------
        included_articles_per_year = included_df[included_df['mergeID'].astype(str).str.endswith('-1')][
            'Publication Date'].dt.year.value_counts().sort_index()
        results['included_articles_per_year'] = included_articles_per_year
        print(f">Included articles per year: {included_articles_per_year}")

        # 2.3 Count included routes per year ---------------------------------------------------------------------------
        included_routes_per_year = included_df[
            'Publication Date'].dt.year.value_counts().sort_index()
        results['included_routes_per_year'] = included_routes_per_year
        print(f">Included routes per year: {included_routes_per_year}")

        # 3. Count routes of length 2, 3, and 4 ----------------------------------------------------------------------
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
        print(f">Route lengths: {results['count_of_routes_per_length'].to_dict()}")

        # 4. Create and save Sankey diagram ----------------------------------------------------------------------------
        print("plotting sankey diagram...")
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        sankey_diagram_file_path = os.path.join(output_dir, f"sankey_diagram_{timestamp}.html")
        create_and_plot_sankey_diagram_phd_data(results, sankey_diagram_file_path)

        # 5. Count medicine quality distribution (ratio of "falsified" to "indistinguishable"
        medicine_quality_counts = included_df['medicine quality'].value_counts()
        results['medicine_quality_counts'] = medicine_quality_counts
        print(f"medicine_quality_counts: {medicine_quality_counts}")

        # 6. Analyze individuals per route -----------------------------------------------------------------------------
        individuals_stats = pd.to_numeric(included_df['number of individuals'], errors='coerce').agg({
            'median': 'median',
            'mean': 'mean'
        })
        results['individuals_stats'] = individuals_stats
        print(f"number of individuals_stats: {individuals_stats}")

        # 7. collect FMP encountered and plot/save WordClouds ----------------------------------------------------------
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        create_wordcloud(
            included_df['Medical Products'],
            os.path.join(output_dir, f"medical_products_wordcloud_{timestamp}.png"),
            'Medical Products WordCloud'
        )
        # 8. collect FMP encountered and plot/save WordClouds ----------------------------------------------------------
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        create_wordcloud(
            included_df['wording used'],
            os.path.join(output_dir, f"wording_used_wordcloud_{timestamp}.png"),
            'Wording Used WordCloud'
        )

        # 9. Calculate manufacturing roles percentage ------------------------------------------------------------------
        manufacturing_percentage = (
                included_df['loc1 node role'].str.contains('manufacturing', case=False, na=False).mean() * 100
        )
        print(f">Manufacturing percentage: {manufacturing_percentage}%")

        # 9.1 Calculate origins as the first point role percentage -----------------------------------------------------
        origin_percentage = (
                included_df['loc1 node role'].str.contains('origin', case=False, na=False).mean() * 100
        )
        print(f">Origin percentage: {origin_percentage}%")

        # 9.2 Calculate clear intermediaries as first point role percentage --------------------------------------------
        intermediary_percentage = (
                included_df['loc1 node role'].str.contains('intermediary', case=False, na=False).mean() * 100
        )
        print(f"Intermediary_percentage: {intermediary_percentage}%")

        # 9.3 Calculate clear intermediaries as first point role percentage --------------------------------------------
        other_percentage = 100-manufacturing_percentage-origin_percentage-intermediary_percentage
        print(f"other_percentage: {other_percentage}%")

        first_node_stats = pd.Series({
            'origin': int(origin_percentage),
            'intermediary': int(intermediary_percentage),
            'manufacturing': int(manufacturing_percentage),
            'other': int(other_percentage) # assembly
        })
        results['first_node_stats'] = first_node_stats

        # 10. collect unique countries ---------------------------------------------------------------------------------
        country_cols = [f'loc{i} geoname_country' for i in range(1, 5)]
        # existing_country_cols = [c for c in country_cols if c in included_df.columns]
        countries_list = (
            included_df[country_cols]
            .stack(future_stack=True)
            .dropna()
            .astype(str)
            .str.strip()
        )
        countries_list = countries_list[countries_list.ne('')].tolist()
        countries_list_set = set(countries_list)

        results['unique_countries_list'] = countries_list_set
        print(f">Unique countries list: {results['unique_countries_list']}")
        results['unique_countries_count'] = int(len(countries_list_set))
        print(f">Unique countries count: {results['unique_countries_count']}")

        # Save to Excel
        print("Saving exploratory analysis results to Excel...")
        # Prepare writeables to avoid errors (no .to_frame() on scalars/sets)
        total_articles_count_df = pd.DataFrame({'total_articles_count': [results['total_articles_count']]})
        included_articles_count_df = pd.DataFrame({'included_articles_count': [results['included_articles_count']]})
        total_routes_count = pd.DataFrame({'total_routes_count': [results['total_routes_count']]})
        included_routes_per_year_df = results['included_routes_per_year'].to_frame(name='count')
        total_articles_per_year_df = total_articles_per_year.to_frame(name='count')
        included_articles_per_year_df = included_articles_per_year.to_frame(name='count')
        routes_by_length_df = results['count_of_routes_per_length'].to_frame(name='count')
        medicine_quality_counts_df = medicine_quality_counts.to_frame(name='count')
        individuals_stats_df = results['individuals_stats'].to_frame(name='value')
        first_node_stats_df = results['first_node_stats'].to_frame(name='percentage')
        unique_countries_count_df = pd.DataFrame({'unique_countries_count': [results['unique_countries_count']]})
        unique_countries_list_df = pd.Series(
            sorted(results['unique_countries_list'])
        ).to_frame(name='country')

        analysis_file_path = os.path.join(output_dir, add_timestamp_to_filename(exploratory_analysis_file_path))
        with pd.ExcelWriter(analysis_file_path) as writer:
            total_articles_count_df.to_excel(writer, sheet_name='Total_Articles', index=False)
            included_articles_count_df.to_excel(writer, sheet_name='Total_Included_Articles', index=False)
            total_routes_count.to_excel(writer, sheet_name='Total_Routes', index=False)
            total_articles_per_year_df.to_excel(writer, sheet_name='Articles_per_Year')
            included_articles_per_year_df.to_excel(writer, sheet_name='Included_Articles_per_Year')
            included_routes_per_year_df.to_excel(writer, sheet_name='Included_Routes_per_Year')
            routes_by_length_df.to_excel(writer, sheet_name='Routes_by_Length')
            medicine_quality_counts_df.to_excel(writer, sheet_name='Medicine_Quality')
            individuals_stats_df.to_excel(writer, sheet_name='Individuals_Stats')
            first_node_stats_df.to_excel(writer, sheet_name='First_node_stats')
            unique_countries_count_df.to_excel(writer, sheet_name='Countries_count', index=False)
            unique_countries_list_df.to_excel(writer, sheet_name='Countries_List', index=False)


    except Exception as e:
        print(results)
        print(f"Error handling dataframe : {e}")
        # Save results with timestamp
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        results_path = os.path.join(output_dir, f"results_preliminary_analysis_{timestamp}.pkl")
        with open(results_path, "wb") as f:
            pickle.dump(results, f)
        print(f"Saved exploratory analysis results to: {results_path}")
        return results, []

    print("Full exploratory analysis success")
    return results, analysis_file_path