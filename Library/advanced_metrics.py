"""Advanced metrics module for analyzing COVID-19 case trends and statistics."""

import pandas as pd

def compare_wave_intensity(df):
    """
    Compare COVID-19 wave intensity between 2021, 2022, and 2023.
    Returns a DataFrame with confirmed cases and percentage changes between years.
    """
    df = df.copy()
    df['year'] = pd.to_datetime(df['date']).dt.year

    yearly_data = (
        df.groupby(['country', 'year'])['confirmed_cases']
        .max()
        .unstack()
        .fillna(0)
        .astype(int)
    )
    yearly_data.columns = ['2021', '2022', '2023']

    yearly_data['2021→2022 (%)'] = (
        (yearly_data['2022'] - yearly_data['2021']) / yearly_data['2021'] * 100
    ).round(2)
    yearly_data['2022→2023 (%)'] = (
        (yearly_data['2023'] - yearly_data['2022']) / yearly_data['2022'] * 100
    ).round(2)
    yearly_data['2021→2023 (%)'] = (
        (yearly_data['2023'] - yearly_data['2021']) / yearly_data['2021'] * 100
    ).round(2)

    return yearly_data.reset_index()

def calculate_rates(df):
    """
    Calculate the average fatality and recovery rates per country.
    Returns a DataFrame with mean rates.
    """
    df = df.copy()
    df = df[df['confirmed_cases'] > 0]
    df['fatality_rate (%)'] = (df['deaths_cases'] / df['confirmed_cases']) * 100
    df['recovery_rate (%)'] = (df['recovered_cases'] / df['confirmed_cases']) * 100
    return (
        df[['country', 'fatality_rate (%)', 'recovery_rate (%)']]
        .groupby('country')
        .mean()
        .reset_index()
    )

def describe_cases(df):
    """
    Generate descriptive statistics for confirmed, death, and recovery cases.
    Returns a DataFrame with summary statistics.
    """
    stats = df[['confirmed_cases', 'deaths_cases', 'recovered_cases']].describe().round(2)
    return stats.reset_index().rename(columns={'index': 'Statistic'})

def generate_pivot(df):
    """
    Generate a pivot table showing maximum confirmed cases per country per year.
    Returns the pivoted DataFrame.
    """
    df['year'] = pd.to_datetime(df['date']).dt.year
    pivot = df.pivot_table(index='country', columns='year', values='confirmed_cases', aggfunc='max')
    return pivot.reset_index()
