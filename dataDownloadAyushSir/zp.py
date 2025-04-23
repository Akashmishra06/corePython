import shutil

def create_zip_from_dir(directory_path, zip_name):
    # Creating a ZIP archive from the directory
    shutil.make_archive(zip_name, 'zip', directory_path)

# Example usage:
directory_path = '/root/equityResearch/dataDownloadAyushSir/BacktestResults/NA_DataDownloadAniket_v1/1/CandleData'  # replace with your directory path
zip_name = 'output_zip_file_name'          # replace with desired zip file name (without .zip)
create_zip_from_dir(directory_path, zip_name)