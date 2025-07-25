"""Module for generating COVID-19 statistics by country, month, year, or custom date range."""

import pandas as pd

def stats_by_country(df):
    """
    Show final total confirmed, deaths, recovered per country.
    """
    country_stats = df.groupby('country').agg({
        'confirmed_cases': 'max',
        'deaths_cases': 'max',
        'recovered_cases': 'max'
    }).reset_index()
    return country_stats

def stats_by_month(df):
    """
    Show total confirmed, deaths, recovered per country by month.
    """
    df['month_year'] = df['date'].apply(lambda x: x.strftime('%Y-%m'))

    month_stats = df.groupby(['country', 'month_year']).agg({
        'confirmed_cases': 'max',
        'deaths_cases': 'max',
        'recovered_cases': 'max'
    }).reset_index()
    return month_stats

def stats_by_year(df):
    """
    Show total confirmed, deaths, recovered per country by year.
    """
    df['year'] = df['date'].apply(lambda x: x.year)

    year_stats = df.groupby(['country', 'year']).agg({
        'confirmed_cases': 'max',
        'deaths_cases': 'max',
        'recovered_cases': 'max'
    }).reset_index()
    return year_stats

def stats_by_date_range(df, start_date, end_date):
    """
    Returns the difference in stats between two dates (inclusive).
    Assumes the data is cumulative and may contain multiple rows per country per date.
    """
    df_start = (
        df[df['date'] == start_date]
        .groupby('country')[['confirmed_cases', 'deaths_cases', 'recovered_cases']]
        .sum()
        .reset_index()
    )

    df_end = (
        df[df['date'] == end_date]
        .groupby('country')[['confirmed_cases', 'deaths_cases', 'recovered_cases']]
        .sum()
        .reset_index()
    )

    df_merged = df_end.merge(df_start, on='country', suffixes=('_end', '_start'))

    df_merged['confirmed_cases'] = df_merged['confirmed_cases_end'] - df_merged['confirmed_cases_start']
    df_merged['deaths_cases'] = df_merged['deaths_cases_end'] - df_merged['deaths_cases_start']
    df_merged['recovered_cases'] = df_merged['recovered_cases_end'] - df_merged['recovered_cases_start']

    return df_merged[['country', 'confirmed_cases', 'deaths_cases', 'recovered_cases']]


def filter_data(df, year, month, country):
    """
    Filters the DataFrame by year, month, and country, then 
    returns aggregated data by date and country.
    """
    if 'date' in df.columns:
        df['date'] = pd.to_datetime(df['date'], errors='coerce')

    df_filtered = df.copy()

    # Apply filters
    if year:
        df_filtered = df_filtered[df_filtered['date'].dt.year == int(year)]
    if month:
        df_filtered = df_filtered[df_filtered['date'].dt.month == int(month)]
    if country and 'country' in df_filtered.columns:
        df_filtered = df_filtered[df_filtered['country'] == country]

    # Drop province (optional: or just don’t include it in final output)
    if 'province' in df_filtered.columns:
        df_filtered = df_filtered.drop(columns=['province'])

    # Group by country and date, aggregate numeric columns
    df_grouped = df_filtered.groupby(['country', 'date'], as_index=False).agg({
        'confirmed_cases': 'sum',
        'deaths_cases': 'sum',
        'recovered_cases': 'sum',
        'latitude': 'mean',
        'longitude': 'mean'
    })

    return df_grouped
