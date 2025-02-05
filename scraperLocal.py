import os
import requests
import pandas as pd
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor

BASE_URL = "https://papers.nips.cc/"
DOWNLOAD_DIR = "D://downloads"
THREAD_POOL_SIZE = 5  # Adjust based on your system
CSV_FILE = "meta.csv"


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

    # Create a directory for this year
    year_folder = os.path.join(DOWNLOAD_DIR, year)
    os.makedirs(year_folder, exist_ok=True)

    # Download concurrently
    with ThreadPoolExecutor(max_workers=THREAD_POOL_SIZE) as executor:
        for paper_url in paper_urls:
            executor.submit(scrape_and_download_paper, paper_url, year_folder, year)


def scrape_and_download_paper(paper_url, year_folder, year):
    """Download and save a paper locally only if it does not already exist."""
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
            file_name = pdf_url.split("/")[-1]
            file_path = os.path.join(year_folder, file_name)

            # Check if the file already exists before downloading
            if os.path.exists(file_path):
                print(f"File already exists, skipping: {file_path}")
            else:
                print(f"Downloading: {pdf_url}")
                download_pdf(pdf_url, file_path)
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
