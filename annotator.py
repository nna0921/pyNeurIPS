import os
import pdfplumber
import google.generativeai as genai
import pandas as pd
import concurrent.futures
import re
import pickle  # To cache classifications
from time import sleep

# Set up Google Gemini API
GEMINI_API_KEY = "AIzaSyBreHt9SdvkNBtljDE-L0sCJHgpH5h9tlw"  # Replace with your valid API key
genai.configure(api_key=GEMINI_API_KEY)

# Define Categories
CATEGORIES = ["Deep Learning", "NLP", "Computer Vision", "Reinforcement Learning", "Optimization & Theoretical ML"]

# Root Directory containing year-wise folders
ROOT_DIR = "D://downloads/"
CSV_FILE = "annotated_papers.csv"  # File to store results
CACHE_FILE = "processed_papers.pkl"  # Cache file for API responses

# **Load existing annotated data to skip already processed PDFs**
if os.path.exists(CSV_FILE):
    existing_df = pd.read_csv(CSV_FILE)
    processed_pdfs = set(existing_df["PDF File"].tolist())  # Store processed PDF filenames
else:
    processed_pdfs = set()  # No existing data

# **Load API Classification Cache**
if os.path.exists(CACHE_FILE):
    with open(CACHE_FILE, "rb") as f:
        classification_cache = pickle.load(f)  # Load saved classifications
else:
    classification_cache = {}  # Empty cache

def extract_text_from_pdf(pdf_path):
    """Extracts the title and abstract from a PDF file."""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            text = "\n".join(
                page.extract_text() for page in pdf.pages[:2] if page.extract_text()
            )  # Read first two pages

        lines = text.split("\n")
        lines = [line.strip() for line in lines if line.strip()]  # Remove empty lines

        # **1️⃣ Extract Title (Improved Logic)**
        title = "Unknown Title"
        for i in range(min(5, len(lines))):  # Check first 5 lines
            line = lines[i].strip()
            if len(line) > 5 and not re.search(r'\d', line):  # Exclude numbers (avoid section numbers)
                title = line
                break

        # **2️⃣ Extract Abstract (Start from "Abstract" until First Section Heading)**
        abstract = ""
        capture = False
        for line in lines:
            if re.match(r'^\s*(Abstract|ABSTRACT)[.:]?', line, re.IGNORECASE):
                capture = True
                continue
            if re.match(r'^\s*[0-9]+\.\s*[A-Za-z]', line):  # Detects "1. INTRODUCTION"
                break
            if capture:
                abstract += " " + line

        abstract = abstract.strip()[:1000] if abstract else "No abstract found"

        return title, abstract

    except Exception as e:
        print(f"Error extracting text from {pdf_path}: {e}")
        return "Unknown Title", "No abstract found"

def classify_paper(title, abstract):
    """Classifies a research paper into predefined categories using Gemini API."""

    # **Check if already classified**
    cache_key = (title, abstract)
    if cache_key in classification_cache:
        return classification_cache[cache_key]  # Return cached result

    prompt = f"""
    Classify the following research paper into one of these categories: {CATEGORIES}.
    Respond with only the category name.

    Title: {title}
    Abstract: {abstract}
    """

    retries = 3
    wait_time = 60  # **Increased wait time**
    for attempt in range(retries):
        try:
            model = genai.GenerativeModel("gemini-pro")
            response = model.generate_content(prompt)

            category = response.text.strip()
            classification_cache[cache_key] = category  # **Save to cache**

            # **Save cache to file (every successful classification)**
            with open(CACHE_FILE, "wb") as f:
                pickle.dump(classification_cache, f)

            return category

        except Exception as e:
            if "429" in str(e):  # Rate limit error
                print(f"Rate limit reached. Waiting {wait_time}s before retrying... (Attempt {attempt + 1}/{retries})")
                sleep(wait_time)
            else:
                print(f"API Error: {e}")
                return "Unknown"

    return "Unknown"  # Return "Unknown" if all retries fail

def process_pdf(year_folder, pdf_file):
    """Processes a single PDF, extracts metadata, classifies it, and saves results."""
    pdf_path = os.path.join(ROOT_DIR, year_folder, pdf_file)

    # **Skip processing if already in CSV**
    if pdf_file in processed_pdfs:
        print(f"Skipping {pdf_file} (Already Annotated)")
        return None

    # Extract metadata
    title, abstract = extract_text_from_pdf(pdf_path)
    category = classify_paper(title, abstract)

    result = {
        "Title": title,
        "Abstract": abstract,
        "Category": category,
        "PDF File": pdf_file,
        "Year": year_folder
    }

    print(f"Processed: {pdf_file} ({year_folder}) -> {title[:30]}... -> {category}")

    # Save incrementally to CSV
    df = pd.DataFrame([result])
    if not os.path.exists(CSV_FILE):
        df.to_csv(CSV_FILE, index=False)  # Create file with headers
    else:
        df.to_csv(CSV_FILE, mode='a', index=False, header=False)  # Append without headers

    sleep(5)  # Prevent API rate limits
    return result

# Scan all year-wise subfolders and process PDFs in parallel
pdf_files = []

for year_folder in os.listdir(ROOT_DIR):
    year_path = os.path.join(ROOT_DIR, year_folder)

    if os.path.isdir(year_path):
        for pdf_file in os.listdir(year_path):
            if pdf_file.endswith(".pdf"):
                pdf_files.append((year_folder, pdf_file))

# Use ThreadPoolExecutor with fewer workers to avoid rate limits
with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
    future_to_pdf = {executor.submit(process_pdf, year, pdf): (year, pdf) for year, pdf in pdf_files}

    for future in concurrent.futures.as_completed(future_to_pdf):
        try:
            future.result()  # Process each PDF and save to CSV immediately
        except Exception as e:
            print(f"Error processing {future_to_pdf[future]}: {e}")

print(f"Annotation complete. Results saved to {CSV_FILE}.")