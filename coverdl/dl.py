import json
import os
import requests
from urllib.parse import urlparse
from pathlib import Path
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor
from collections import defaultdict

# 设置代理
# proxies = {
#     "http": "http://127.0.0.1:10808",
# }

def download_file(url, folder_path, progress_bar, position):
    try:
        # Create folder if it doesn't exist
        os.makedirs(folder_path, exist_ok=True)
        
        # Get filename from URL
        filename = os.path.basename(urlparse(url).path)
        if not filename.endswith('.png'):
            filename += '.png'
        
        # Full path for saving the file
        file_path = os.path.join(folder_path, filename)
        
        # Check if file already exists
        if os.path.exists(file_path):
            # tqdm.write(f"File already exists: {filename}")
            progress_bar.update(1)
            return True
        
        # Download the file
        # response = requests.get(url, proxies=proxies, stream=True, timeout=10)
        response = requests.get(url, stream=True, timeout=10)
        response.raise_for_status()
        
        total_size = int(response.headers.get('content-length', 0))
        with open(file_path, 'wb') as f:
            with tqdm(
                desc=filename,
                total=total_size,
                unit='iB',
                unit_scale=True,
                unit_divisor=1024,
                position=position,
                leave=False
            ) as bar:
                for data in response.iter_content(chunk_size=1024):
                    size = f.write(data)
                    bar.update(size)
        
        #tqdm.write(f"Successfully downloaded: {filename}")
        progress_bar.update(1)
        return True
    
    except Exception as e:
        tqdm.write(f"Error downloading {url}: {str(e)}")
        progress_bar.update(1)
        return False

def process_json_files(json_directory):
    # Create base directories for different types
    base_url_dir = "boxart"
    base_front_dir = "boxartfront"
    base_thumbnail_dir = "boxartsm"
    
    # Collect all download tasks
    download_tasks = set()  # Use a set to avoid duplicates
    url_count = defaultdict(int)  # Dictionary to count URL occurrences
    
    # Process each JSON file in the directory
    for filename in os.listdir(json_directory):
        if filename.endswith('.json'):
            try:
                tqdm.write(f"Processing file: {filename}")  # Debug information
                # Read JSON file
                file_path = os.path.join(json_directory, filename)
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Skip empty JSON files
                if not data:
                    tqdm.write(f"Skipping empty file: {filename}")
                    continue
                
                # Collect URLs to download
                for item in data:
                    if 'url' in item:
                        download_tasks.add((item['url'], base_url_dir))
                        url_count[item['url']] += 1
                    if 'front' in item:
                        download_tasks.add((item['front'], base_front_dir))
                        url_count[item['front']] += 1
                    if 'thumbnail' in item:
                        download_tasks.add((item['thumbnail'], base_thumbnail_dir))
                        url_count[item['thumbnail']] += 1
                
            except Exception as e:
                tqdm.write(f"Error processing {filename}: {str(e)}")
    
    # Print the number of unique download tasks for debugging
    tqdm.write(f"Total unique download tasks: {len(download_tasks)}")
    
    # Find and print duplicate URLs
    duplicates = {url: count for url, count in url_count.items() if count > 1}
    if duplicates:
        tqdm.write("Duplicate URLs found:")
        for url, count in duplicates.items():
            tqdm.write(f"{url}: {count} times")
    else:
        tqdm.write("No duplicate URLs found.")
    
    # Create a total progress bar
    total_size = len(download_tasks)
    with tqdm(total=total_size, unit='file', position=0) as progress_bar:
        # Download files using multithreading
        with ThreadPoolExecutor(max_workers=128) as executor:
            futures = [executor.submit(download_file, url, folder, progress_bar, i + 1) for i, (url, folder) in enumerate(download_tasks)]
            for future in futures:
                future.result()

if __name__ == "__main__":
    # Specify the directory containing JSON files
    json_directory = "json"  # Change this to your JSON files directory
    
    # Process all JSON files
    process_json_files(json_directory)