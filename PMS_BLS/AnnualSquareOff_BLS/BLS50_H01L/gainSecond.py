# import pandas as pd
# from datetime import datetime
# import os

# # Load the data
# df = pd.read_csv("/root/equityResearch/PMS_BLS/AnnualSquareOff_BLS/BLS50_H01L/BacktestResults/AK_BLS50_H30K_Annual_SquareOff_v1/1/closePnl_AK_BLS50_H30K_Annual_SquareOff_v1_1.csv", parse_dates=["Key", "ExitTime"])

# # Function to categorize each trade
# def categorize_trade(row):
#     trade_duration = (row['ExitTime'] - row['Key']).days

#     if row['Pnl'] < 0:
#         if trade_duration > 365:
#             return "longtermlossmaking"
#         else:
#             return "shorttermlossmaking"
#     else:
#         if trade_duration > 365:
#             return "longtermprofitmaking"
#         else:
#             return "shorttermprofitmaking"

# # Apply categorization to the DataFrame
# df['Gain'] = df.apply(categorize_trade, axis=1)

# # Get the years from the 'Key' column (assuming it's a datetime column)
# df['Year'] = df['Key'].dt.year

# # Create the parent directory where all the yearly folders will be stored
# parent_dir = "yearly_trades"
# if not os.path.exists(parent_dir):
#     os.makedirs(parent_dir)

# # Iterate over each year and create separate CSV files
# for year in df['Year'].unique():
#     # Filter data for the current year
#     year_df = df[df['Year'] == year]
    
#     # Create a subdirectory for the year if it doesn't exist
#     year_dir = os.path.join(parent_dir, str(year))
#     if not os.path.exists(year_dir):
#         os.makedirs(year_dir)
    
#     # Further filter by each category and save separate CSVs for each category
#     for category in ['longtermlossmaking', 'shorttermlossmaking', 'longtermprofitmaking', 'shorttermprofitmaking']:
#         category_df = year_df[year_df['Gain'] == category]
        
#         # Define the filename based on the category and year
#         file_name = f"{category}_{year}.csv"
#         file_path = os.path.join(year_dir, file_name)
        
#         # Save the filtered data to a CSV file
#         category_df.to_csv(file_path, index=False)

# # Optionally, save the entire categorized dataframe to a final CSV
# df.to_csv("dfto_.csv", index=False)

# print("Files saved successfully.")



import pandas as pd
from datetime import datetime
import os

# Load the data
df = pd.read_csv("/root/equityResearch/PMS_BLS/AnnualSquareOff_BLS/BLS50_H01L/BacktestResults/AK_BLS50_H30K_Annual_SquareOff_v1/1/closePnl_AK_BLS50_H30K_Annual_SquareOff_v1_1.csv", parse_dates=["Key", "ExitTime"])

# Function to categorize each trade
def categorize_trade(row):
    trade_duration = (row['ExitTime'] - row['Key']).days

    if row['Pnl'] < 0:
        if trade_duration > 365:
            return "longtermlossmaking"
        else:
            return "shorttermlossmaking"
    else:
        if trade_duration > 365:
            return "longtermprofitmaking"
        else:
            return "shorttermprofitmaking"

# Apply categorization to the DataFrame
df['Gain'] = df.apply(categorize_trade, axis=1)

# Get the years from the 'Key' column (assuming it's a datetime column)
df['Year'] = df['Key'].dt.year

# Create the parent directory where all the yearly folders will be stored
parent_dir = "yearly_trades"
if not os.path.exists(parent_dir):
    os.makedirs(parent_dir)

# Open the report.txt file to write the summary
report_file = os.path.join(parent_dir, "report.txt")
with open(report_file, 'w') as report:

    # Write header to the report
    report.write("Yearly Trade Summary Report\n")
    report.write("===========================\n\n")

    # Iterate over each year and create separate CSV files
    for year in df['Year'].unique():
        # Filter data for the current year
        year_df = df[df['Year'] == year]
        
        # Create a subdirectory for the year if it doesn't exist
        year_dir = os.path.join(parent_dir, str(year))
        if not os.path.exists(year_dir):
            os.makedirs(year_dir)
        
        # Write year header in the report
        report.write(f"Year: {year}\n")
        
        # Initialize a dictionary to store the sum of PnL for each category
        pnl_sums = {
            "longtermlossmaking": 0,
            "shorttermlossmaking": 0,
            "longtermprofitmaking": 0,
            "shorttermprofitmaking": 0
        }
        
        # Further filter by each category and save separate CSVs for each category
        for category in pnl_sums.keys():
            category_df = year_df[year_df['Gain'] == category]
            
            # Calculate the sum of PnL for this category
            pnl_sums[category] = category_df['Pnl'].sum()
            
            # Define the filename based on the category and year
            file_name = f"{category}_{year}.csv"
            file_path = os.path.join(year_dir, file_name)
            
            # Save the filtered data to a CSV file
            category_df.to_csv(file_path, index=False)
        
        # Write the PnL summary for this year to the report
        report.write(f"  PnL Summary:\n")
        for category, pnl_sum in pnl_sums.items():
            report.write(f"    {category}: {pnl_sum:.2f}\n")
        
        # Calculate and write the overall PnL for the year
        total_pnl = sum(pnl_sums.values())
        report.write(f"  Total PnL for {year}: {total_pnl:.2f}\n")
        report.write("\n")

# Optionally, save the entire categorized dataframe to a final CSV
df.to_csv("dfto_.csv", index=False)

print("Files saved and report generated successfully.")
