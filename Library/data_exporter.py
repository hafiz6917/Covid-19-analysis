"""Module for exporting data to CSV files in the specified output directory."""

import os

def export_to_csv(df, filename, base_dir):
    """
    Export the given DataFrame to a CSV file in the Output/exports directory.

    Args:
        df (pd.DataFrame): The data to export.
        filename (str): The name of the CSV file to create.
    """
    output_dir = os.path.join(base_dir, 'Output', 'exports')
    os.makedirs(output_dir, exist_ok=True)

    file_path = os.path.join(output_dir, filename)
    df.to_csv(file_path, index=False, encoding='utf-8')
    print(f"✅ CSV export saved to {file_path}")
