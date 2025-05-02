import pandas as pd
import os

# Set your paths
csvs_folder_path = '/root/equityResearch/annualWeeklyDaily/Horizontal50/BacktestResults/NA_Vertical50_v1/1/CandleData'  # <-- your folder with multiple stock csvs
dates_csv_path = '/root/equityResearch/annualWeeklyDaily/expiryDateRange.csv'  # <-- your special Dates CSV
output_folder_path = '/root/equityResearch/annualWeeklyDaily/Horizontal50/candleData/'  # <-- new folder to save updated CSVs

# Create output folder if not exists
os.makedirs(output_folder_path, exist_ok=True)

# Read the Dates CSV
dates_df = pd.read_csv(dates_csv_path)
dates_list = dates_df['Dates'].tolist()

# Convert dates to standard format for comparison
dates_list = pd.to_datetime(dates_list).strftime('%Y-%m-%d').tolist()

# Process each CSV in the original folder
for filename in os.listdir(csvs_folder_path):
    if filename.endswith('.csv'):
        file_path = os.path.join(csvs_folder_path, filename)
        
        # Read the stock CSV
        df = pd.read_csv(file_path)

        # Ensure 'date' column is in correct format
        df['date'] = pd.to_datetime(df['date']).dt.strftime('%Y-%m-%d')

        # Create 'columnRange' based on matching dates
        df['columnRange'] = df['date'].apply(lambda x: 'yes' if x in dates_list else '')

        # Save to new folder
        output_file_path = os.path.join(output_folder_path, filename)
        df.to_csv(output_file_path, index=False)
        
        print(f"✅ Saved updated file: {output_file_path}")

print("\n🎯 All files processed and saved to new folder!")