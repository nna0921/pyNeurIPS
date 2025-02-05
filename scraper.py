from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
import os
import requests
import pandas as pd
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor

BASE_URL = "https://papers.nips.cc/"
DOWNLOAD_DIR = "downloads"
THREAD_POOL_SIZE = 5  # Adjust based on your system
CSV_FILE = "metadata.csv"

# Authenticate and create GoogleDrive instance
gauth = GoogleAuth()
gauth.LocalWebserverAuth()  # Opens a browser for authentication
drive = GoogleDrive(gauth)


def get_conference_years():
    response = requests.get(BASE_URL)
    soup = BeautifulSoup(response.text, "html.parser")

    year_links = soup.select("a[href*='/paper_files/']")
    years = {}

    for link in year_links:
        year_url = BASE_URL + link["href"]
        year = "".join(filter(str.isdigit, year_url))  # Extract year from URL
        years[year] = year_url

    return years


def scrape_papers_for_year(year, year_url):
    print(f"Processing year: {year}")

    response = requests.get(year_url)
    soup = BeautifulSoup(response.text, "html.parser")

    paper_links = soup.select("a[href*='/paper/']")
    paper_urls = [BASE_URL + link["href"] for link in paper_links]

    # Get or create the Google Drive folder for this year
    drive_folder_id = get_or_create_drive_folder(year)

    # Download and upload concurrently
    with ThreadPoolExecutor(max_workers=THREAD_POOL_SIZE) as executor:
        for paper_url in paper_urls:
            executor.submit(scrape_and_upload_paper, paper_url, year, drive_folder_id)


def scrape_and_upload_paper(paper_url, year, drive_folder_id):
    """Download and immediately upload a paper."""
    try:
        response = requests.get(paper_url)
        soup = BeautifulSoup(response.text, "html.parser")

        title_tag = soup.find("h4")
        title = title_tag.text.strip() if title_tag else "Unknown Title"

        author_tag = soup.find("h4", string="Authors")
        authors = author_tag.find_next("p").text.strip() if author_tag else "Unknown Authors"

        pdf_button = soup.find("a", string="Paper")

        if pdf_button:
            pdf_url = BASE_URL + pdf_button["href"]
            print(f"Downloading: {pdf_url}")

            file_name = pdf_url.split("/")[-1]
            file_path = os.path.join(DOWNLOAD_DIR, year, file_name)

            # Download PDF
            download_pdf(pdf_url, file_path)

            # Upload to Drive concurrently
            upload_to_drive(file_path, drive_folder_id)

            # Save metadata to CSV
            save_metadata_to_csv(title, authors, pdf_url, year)

    except Exception as e:
        print(f"Error processing paper {paper_url}: {e}")


def download_pdf(pdf_url, save_path):
    """Downloads a PDF file."""
    try:
        os.makedirs(os.path.dirname(save_path), exist_ok=True)

        response = requests.get(pdf_url, stream=True)
        with open(save_path, "wb") as file:
            for chunk in response.iter_content(1024):
                file.write(chunk)

        print(f"PDF saved: {save_path}")

    except Exception as e:
        print(f"Failed to download {pdf_url}: {e}")


def get_or_create_drive_folder(folder_name):
    """Get or create a folder in Google Drive."""
    query = f"title='{folder_name}' and mimeType='application/vnd.google-apps.folder' and trashed=false"
    file_list = drive.ListFile({'q': query}).GetList()

    if file_list:
        print(f"Found existing folder: {folder_name}")
        return file_list[0]['id']

    folder_metadata = {
        'title': folder_name,
        'mimeType': 'application/vnd.google-apps.folder'
    }
    folder = drive.CreateFile(folder_metadata)
    folder.Upload()
    print(f"Created new folder: {folder_name}")

    return folder['id']


def upload_to_drive(file_path, drive_folder_id):
    """Uploads a PDF to Google Drive in the specified folder."""
    file_name = os.path.basename(file_path)

    gfile = drive.CreateFile({'title': file_name, 'parents': [{'id': drive_folder_id}]})
    gfile.SetContentFile(file_path)
    gfile.Upload()

    print(f"Uploaded {file_name} to Google Drive")


def save_metadata_to_csv(title, authors, pdf_url, year):
    """Save metadata (Title, Authors, PDF Link, Year) to a local CSV file using Pandas."""
    metadata = {
        "Title": [title],
        "Authors": [authors],
        "PDF Link": [pdf_url],
        "Year": [year]
    }

    df = pd.DataFrame(metadata)

    if os.path.exists(CSV_FILE):
        df.to_csv(CSV_FILE, mode="a", header=False, index=False)
    else:
        df.to_csv(CSV_FILE, mode="w", header=True, index=False)

    print(f"Metadata saved for: {title}")


if __name__ == "__main__":
    years = get_conference_years()

    # Process each year concurrently
    with ThreadPoolExecutor(max_workers=THREAD_POOL_SIZE) as executor:
        for year, year_url in years.items():
            executor.submit(scrape_papers_for_year, year, year_url)