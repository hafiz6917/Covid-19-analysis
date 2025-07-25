"""Module for generating various COVID-19 related plots and visualizations."""

import os
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

def _graphics_output_dir(base_dir):
    """Return the path to the graphics output directory."""
    return os.path.join(base_dir, 'Graphics')

def correlation_heatmap(df, base_dir):
    """Generate and save a heatmap of correlations between case types."""
    output_dir = _graphics_output_dir(base_dir)
    os.makedirs(output_dir, exist_ok=True)

    corr = df[['confirmed_cases', 'deaths_cases', 'recovered_cases']].corr()
    plt.figure(figsize=(8, 6))
    sns.heatmap(corr, annot=True, cmap='coolwarm', fmt=".2f")
    plt.title('Correlation Heatmap: Confirmed, Deaths, Recovered')
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'correlation_heatmap.png'))
    plt.close()
    print("✅ correlation_heatmap.png saved")


def bar_total_cases(df, base_dir):
    """Generate and save a bar plot of total confirmed cases by country."""
    output_dir = _graphics_output_dir(base_dir)
    os.makedirs(output_dir, exist_ok=True)

    country_totals = (
        df.groupby('country')['confirmed_cases']
        .max()
        .sort_values(ascending=False)
    )
    plt.figure(figsize=(10, 6))
    sns.barplot(
        x=country_totals.values,
        y=country_totals.index,
        hue=country_totals.index,
        palette='Blues_d',
        legend=False
    )
    plt.title("Total Confirmed Cases by Country")
    plt.xlabel("Confirmed Cases")
    plt.ylabel("Country")
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'bar_total_cases.png'))
    plt.close()
    print("✅ bar_total_cases.png saved")

def line_trend_by_country(df, base_dir):
    """Generate and save a line chart showing case trends by country over time."""
    output_dir = _graphics_output_dir(base_dir)
    os.makedirs(output_dir, exist_ok=True)

    df['month'] = pd.to_datetime(df['date']).dt.to_period('M').astype(str)
    monthly = (
        df.groupby(['country', 'month'])['confirmed_cases']
        .max()
        .reset_index()
    )
    plt.figure(figsize=(12, 6))
    sns.lineplot(data=monthly, x='month', y='confirmed_cases', hue='country')
    plt.xticks(rotation=45)
    plt.title("Confirmed Case Trend by Country")
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'line_trend_by_country.png'))
    plt.close()
    print("✅ line_trend_by_country.png saved")

def boxplot_cases_by_month(df, base_dir):
    """Generate and save a boxplot of confirmed cases per calendar month."""
    output_dir = _graphics_output_dir(base_dir)
    os.makedirs(output_dir, exist_ok=True)

    df['month'] = pd.to_datetime(df['date']).dt.month
    plt.figure(figsize=(8, 6))
    sns.boxplot(x='month', y='confirmed_cases', data=df)
    plt.title("Distribution of Confirmed Cases by Month")
    plt.xlabel("Month")
    plt.ylabel("Confirmed Cases")
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'boxplot_cases_by_month.png'))
    plt.close()
    print("✅ boxplot_cases_by_month.png saved")

def scatter_deaths_vs_cases(df, base_dir):
    """Generate and save a scatter plot comparing deaths and confirmed cases."""
    output_dir = _graphics_output_dir(base_dir)
    os.makedirs(output_dir, exist_ok=True)

    df_grouped = (
        df.groupby('country')[['confirmed_cases', 'deaths_cases']]
        .max()
        .reset_index()
    )
    plt.figure(figsize=(8, 6))
    sns.scatterplot(
        data=df_grouped,
        x='confirmed_cases',
        y='deaths_cases',
        hue='country',
        s=100
    )
    plt.title("Deaths vs Confirmed Cases by Country")
    plt.xlabel("Confirmed Cases")
    plt.ylabel("Deaths")
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'scatter_deaths_vs_cases.png'))
    plt.close()
    print("✅ scatter_deaths_vs_cases.png saved")
