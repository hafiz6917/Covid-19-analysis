"""Module for generating and saving tabulated reports from DataFrames."""

import os
from datetime import datetime
from tabulate import tabulate

def save_report(df, filename, base_dir, title=None, description=None):
    """
    Save a tabulated report from a DataFrame to a text file with optional metadata.

    Args:
        df (pd.DataFrame): The data to include in the report.
        filename (str): The name of the output file.
        title (str, optional): Title for the report.
        description (str, optional): Additional description to include.
    """
    output_dir = os.path.join(base_dir, 'Output', 'reports')
    os.makedirs(output_dir, exist_ok=True)

    file_path = os.path.join(output_dir, filename)

    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    header = f"{title}\nGenerated on: {now}\n"
    if description:
        header += f"\n{description}\n"

    table = tabulate(df, headers='keys', tablefmt='github', showindex=False)

    summary = ""
    required_columns = {'confirmed_cases', 'deaths_cases', 'recovered_cases', 'country'}
    date_columns_absent = all(col not in df.columns for col in ['month_year', 'year', 'date'])

    if required_columns.issubset(df.columns) and date_columns_absent:
        total_confirmed = df['confirmed_cases'].sum()
        total_deaths = df['deaths_cases'].sum()
        total_recovered = df['recovered_cases'].sum()

        summary += "\n------------------------------------------------------------\n"
        summary += f"Total Confirmed Cases:  {total_confirmed:,}\n"
        summary += f"Total Deaths:           {total_deaths:,}\n"
        summary += f"Total Recoveries:       {total_recovered:,}\n"

        top_countries = df[['country', 'confirmed_cases']].sort_values(by='confirmed_cases', ascending=False).head(3)
        summary += "\nTop 3 countries by confirmed cases:\n"
        for i, row in enumerate(top_countries.itertuples(index=False), 1):
            summary += f"{i}. {row.country:<12} - {row.confirmed_cases:,}\n"

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(header + "\n" + table + summary)

    print(f"✅ Report saved to {file_path}")
