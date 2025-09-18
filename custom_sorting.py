

def sort_countries_clockwise(list_of_countries):
    # Define the input list of countries
    input_countries = [
        "Australia", "Bangladesh", "Belgium", "Bhutan", "Bulgaria", "Cambodia", "Cameroon", "Canada", "China",
        "Colombia", "Denmark", "Ethiopia", "France", "Gabon", "Germany", "Ghana", "Guinea", "Honduras", "Hong Kong",
        "India", "Indonesia", "Iran", "Iraq", "Ireland", "Israel", "Italy", "Ivory Coast", "Jordan", "Kenya", "Liberia",
        "Lithuania", "Macao", "Malaysia", "Malta", "Mexico", "Morocco", "Namibia", "Nepal", "Niger", "Nigeria", "Oman",
        "Pakistan", "Palestine", "Philippines", "Poland", "Portugal", "Puerto Rico", "Russia", "Rwanda", "Saudi Arabia",
        "Senegal", "Serbia", "Singapore", "South Africa", "South Korea", "South Sudan", "Spain", "Sri Lanka", "Sudan",
        "Switzerland", "Taiwan", "Tanzania", "Thailand", "The Gambia", "The Netherlands", "Trinidad and Tobago",
        "Türkiye",
        "Uganda", "United Arab Emirates", "United Kingdom", "United States", "Vietnam", "Yemen"
    ]

    # Define the clockwise world map traversal order
    clockwise_order = [
        # Start with Ireland and UK
        "Iceland", "Ireland", "United Kingdom",
        # Western Europe
        "Portugal", "Spain", "Italy", "Malta", "France", "Belgium", "The Netherlands", "Germany", "Switzerland",
        # Northern and Central Europe
        "Denmark", "Lithuania", "Poland", "Serbia", "Bulgaria",
        # Middle East
        "Türkiye", "Israel", "Palestine", "Jordan", "Iraq", "Iran",
        # Russia
        "Russia",
        # Central Asia and East Asia
        "China", "Hong Kong", "Macao", "Taiwan", "South Korea", "Vietnam", "Thailand", "Cambodia", "Malaysia",
        "Singapore", "Indonesia", "Philippines",
        # South Asia
        "Pakistan", "India", "Nepal", "Bhutan", "Bangladesh", "Sri Lanka",
        # Oceania
        "Australia",
        # Arabian Peninsula
        "United Arab Emirates", "Oman", "Yemen", "Saudi Arabia",
        # North Africa
        "Morocco", "Sudan",
        # East Africa
        "South Sudan", "Ethiopia", "Kenya", "Uganda", "Rwanda", "Tanzania",
        # Southern Africa
        "Namibia", "South Africa",
        # West Africa
        "Senegal", "The Gambia", "Guinea", "Ghana", "Ivory Coast", "Liberia", "Nigeria", "Niger", "Cameroon", "Gabon",
        # South America (South to North)
        "Colombia", "Honduras", "Trinidad and Tobago", "Puerto Rico",
        # North America
        "Mexico", "United States", "Canada"]

    # Filter and sort the input countries based on the defined clockwise order
    sorted_countries = [country for country in clockwise_order if country in input_countries]

    # Print the sorted list
    for country in sorted_countries:
        print(country)

    return clockwise_order


