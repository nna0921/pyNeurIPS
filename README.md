# NeurIPS Paper Scrapers & AI-Powered Annotation

## Overview
This project automates the scraping, extraction, and annotation of NeurIPS research papers using Large Language Models (LLMs). It consists of:

- **Scraper**: Downloads NeurIPS papers year-wise and stores metadata.
- **AI Annotation Pipeline**: Extracts titles and abstracts from PDFs and classifies them into predefined AI research categories using Google Gemini API, Cohere, Hugging Face, and Ollama.
- **Resumable Execution**: Skips previously processed papers, handles API failures, and reduces redundant API calls with caching.

---

## Features

### Web Scraper
- Scrapes NeurIPS papers by year from `https://papers.nips.cc`.
- Downloads PDFs concurrently for efficiency.
- Saves metadata (title, authors, PDF link, year) in a CSV file.
- Supports Google Drive upload for cloud storage.

### AI Annotation Pipeline
- Extracts the title and abstract from research papers.
- Classifies papers into five categories:  
  - Deep Learning
  - NLP
  - Computer Vision
  - Reinforcement Learning
  - Optimization & Theoretical ML
- Uses Google Gemini API for classification (with fallback to Cohere, Hugging Face, and Ollama).
- Implements retry mechanisms for API failures.
- Uses caching to avoid redundant API calls.

### Prerequisites
Ensure you have Python 3+ installed and install the required dependencies:

```bash
pip install requests beautifulsoup4 pandas pydrive concurrent.futures pdfplumber google-generativeai cohere pickle-mixin
## Usage
###1. Run the Web Scraper
Google Drive Uploader
python scraper.py
Authenticates with Google Drive.
Downloads NeurIPS papers and uploads them to Google Drive.
Saves metadata to metadata.csv.
Local Saver
python local_scraper.py
Downloads NeurIPS papers to D://downloads/.
Saves metadata to meta.csv.
###2. Run the AI Annotation Pipeline
python annotator.py
Extracts title and abstract from downloaded PDFs.
Sends extracted text to the Google Gemini API for classification.
Handles API rate limits and quota exhaustion with retry mechanisms.
Caches previously classified papers to optimize processing.
Saves results to annotated_papers.csv.
##Configuration
Modify the following variables in scraper.py, local_scraper.py, and annotator.py as needed:

# Web Scraper Configuration
BASE_URL = "https://papers.nips.cc/"
DOWNLOAD_DIR = "D://downloads/"
CSV_FILE = "meta.csv"
THREAD_POOL_SIZE = 5  # Number of concurrent downloads

# AI Annotation Configuration
GEMINI_API_KEY = "your-google-gemini-api-key"
CATEGORIES = ["Deep Learning", "NLP", "Computer Vision", "Reinforcement Learning", "Optimization & Theoretical ML"]
CACHE_FILE = "processed_papers.pkl"  # Stores cached classifications

# API Retry Settings
RETRY_LIMIT = 3
WAIT_TIME = 60  # Seconds to wait before retrying on API failure
Notes
Ensure client_secrets.json is excluded from Git commits (.gitignore) when using Google Drive API.
If using Google Drive, authenticate before running scraper.py.
API quota limits may apply; consider using Ollama for offline classification.
The script is resumable and will skip previously processed papers.
Future Improvements
Improve title and abstract extraction using pdfminer.six.
Implement multi-label classification for papers that fit into multiple categories.
Optimize local LLMs for faster and more accurate processing.
Author
Published by nna0921 | Anna Zubair

Happy Scraping and Annotating!


