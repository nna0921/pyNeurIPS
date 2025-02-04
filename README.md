NeurIPS Paper Scrapers
This project contains two Python scrapers to download NeurIPS research papers:

Google Drive Uploader (scraper.py): Downloads papers and uploads them to Google Drive.

Local Saver (local_scraper.py): Downloads and saves papers locally.

#Features
Scrapes NeurIPS papers by year.

Downloads PDFs concurrently for efficiency.

Saves metadata (title, authors, PDF link) in a CSV file.

Uploads papers to Google Drive (for scraper.py).

Avoids duplicate downloads.

#Setup
Prerequisites
Ensure you have Python 3+ installed and install the dependencies:

pip install requests beautifulsoup4 pandas pydrive concurrent.futures
For Google Drive authentication, follow this guide to set up OAuth credentials.

#Usage
1. Run the Google Drive Uploader
python scraper.py
Authenticates with Google Drive.

Downloads NeurIPS papers and uploads them to Drive.

Saves metadata to metadata.csv.

2. Run the Local Saver
python local_scraper.py
Downloads NeurIPS papers to D://downloads.

Saves metadata to meta.csv.

#Configuration
Modify the following variables in both scripts as needed:

BASE_URL: NeurIPS website base URL.

DOWNLOAD_DIR: Directory for saving PDFs.

CSV_FILE: Metadata storage file.

THREAD_POOL_SIZE: Number of concurrent downloads.

#Notes
Ensure client_secrets.json is excluded from Git commits (.gitignore).

If using Google Drive, authenticate before running scraper.py.

published by nna0921 | Anna Zubair 
Happy Scraping!

