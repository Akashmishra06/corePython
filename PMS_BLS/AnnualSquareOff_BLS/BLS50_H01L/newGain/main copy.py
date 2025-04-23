import pandas as pd
import os

# Read the dataframe (replace 'your_file.csv' with the path to your file)
df = pd.read_csv('/root/equityResearch/PMS_BLS/AnnualSquareOff_BLS/BLS50_H01L/gain_trades.csv')


# Ensure 'ExitTime' is in datetime format
df['ExitTime'] = pd.to_datetime(df['ExitTime'])

# Define the categories for filtering
categories = ['shorttermprofitmaking', 'longtermlossmaking', 'shorttermlossmaking', 'longtermprofitmaking']

# Dictionary to store the PnL sum for each year
yearly_report = {}

# Function to classify and save trades for each financial year
def classify_and_save_trades(start_date, end_date, year):
    # Filter trades that have 'ExitTime' within the financial year
    filtered_trades = df[(df['ExitTime'] >= start_date) & (df['ExitTime'] <= end_date)]
    
    # Create directory for the year if it doesn't exist
    year_dir = os.path.join(root_dir, str(year))
    if not os.path.exists(year_dir):
        os.makedirs(year_dir)

    # Dictionary to store filtered trades for each category
    categorized_data = {category: pd.DataFrame() for category in categories}
    
    # Initialize a dictionary to hold PnL sum for this year
    pnl_sum_by_category = {category: 0 for category in categories}
    
    # Filter trades by category and save them to the dictionary
    for category in categories:
        categorized_data[category] = filtered_trades[filtered_trades['Gain'] == category]
        
        # Calculate the sum of PnL for this category and year
        pnl_sum_by_category[category] = categorized_data[category]['Pnl'].sum()

        # Save the categorized trades to CSV
        category_file = os.path.join(year_dir, f'{category}.csv')
        categorized_data[category].to_csv(category_file, index=False)

    return pnl_sum_by_category

# Create a root directory for the output
root_dir = 'Financial_Year_Trades'
if not os.path.exists(root_dir):
    os.makedirs(root_dir)

# Process for all years (2019, 2020, 2021, etc.)
for year in range(2019, 2025):  # Adjust as necessary for the years you have
    if year == 2019:
        # For 2019, the period is from 1st Jan 2019 to 31st March 2019
        start_date = pd.Timestamp(f'{year}-01-01')
        end_date = pd.Timestamp(f'{year}-03-31')
    else:
        # For subsequent years, the period is from 1st April to 31st March of the next year
        start_date = pd.Timestamp(f'{year}-04-01')
        end_date = pd.Timestamp(f'{year+1}-03-31')

    # Get the PnL sums for this year
    pnl_sums = classify_and_save_trades(start_date, end_date, year)
    
    # Add the PnL sums for the year to the yearly_report dictionary
    yearly_report[year] = pnl_sums

    print(f"Year {year} trades have been saved.")

# Now write the summary report to a 'report.txt' file
report_file = os.path.join(root_dir, 'report.txt')
with open(report_file, 'w') as report:
    for year, pnl_sums in yearly_report.items():
        report.write(f"Financial Year: {year}-{year+1}\n")
        for category, pnl_sum in pnl_sums.items():
            report.write(f"  {category}: {pnl_sum}\n")
        report.write("\n")

print("Report generated: 'report.txt'.")
