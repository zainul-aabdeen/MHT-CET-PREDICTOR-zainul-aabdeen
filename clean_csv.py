import pandas as pd

fieldnames = [
    "college_name", "highest_package_lpa", "average_package_lpa", 
    "median_package_lpa", "placement_percentage", "placement_year", 
    "top_recruiters", "confidence_score", "sources"
]

# Read with explicit names
df = pd.read_csv('college_packages.csv', names=fieldnames, header=0 if 'college_name' in open('college_packages.csv').readline() else None)

# Force numeric
df['highest_package_lpa'] = pd.to_numeric(df['highest_package_lpa'], errors='coerce')

valid_rows = df[(df['highest_package_lpa'] < 50) | (df['highest_package_lpa'].isna())]

dropped = df[df['highest_package_lpa'] >= 50]
print(f"Dropped {len(dropped)} outliers:")
print(dropped[['college_name', 'highest_package_lpa']])

valid_rows.to_csv('college_packages.csv', index=False)
