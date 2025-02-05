import pandas as pd

csv_file_path = "meta.csv"
output_csv_path = "updated_meta.xlsx"  # Saves the cleaned and updated data

# Load CSV safely, skipping problematic lines
try:
    df = pd.read_csv(csv_file_path, on_bad_lines='skip', quotechar='"', sep=",", encoding="utf-8")
except Exception as e:
    print(f"Error loading CSV: {e}")
    exit()

# Clean column names
df.columns = df.columns.str.strip()

# Ensure 'Year' column is properly formatted as string without decimals
if 'Year' in df.columns:
    df['Year'] = df['Year'].astype(str).str.replace(r'\.0$', '', regex=True)

# Strip extra spaces from text columns
if 'Title' in df.columns:
    df['Title'] = df['Title'].astype(str).str.strip()

if 'Authors' in df.columns:
    df['Authors'] = df['Authors'].astype(str).str.strip()

# --- INSIGHTS CALCULATION ---

# Total Papers Scraped
total_papers = len(df)

# Papers Published Per Year
papers_per_year = df['Year'].value_counts().sort_index()

# Author Analysis
author_counts = {}
total_authors_count = 0

for authors in df['Authors'].dropna():
    author_list = [author.strip() for author in authors.split(",")]
    total_authors_count += len(author_list)
    for author in author_list:
        author_counts[author] = author_counts.get(author, 0) + 1

# Average Number of Authors per Paper
avg_authors_per_paper = total_authors_count / total_papers if total_papers > 0 else 0

# Most Frequent Authors (Top 10)
top_authors = pd.Series(author_counts).sort_values(ascending=False).head(10)

# --- SAVE INSIGHTS TO EXCEL FILE ---

# Create DataFrames for insights
insights_df = pd.DataFrame({
    "Metric": ["Total Papers Scraped", "Avg Authors per Paper"],
    "Value": [total_papers, round(avg_authors_per_paper, 2)]
})

# Convert papers per year into DataFrame format
papers_per_year_df = papers_per_year.reset_index()
papers_per_year_df.columns = ["Year", "Papers Published"]

# Convert top authors into DataFrame format
top_authors_df = top_authors.reset_index()
top_authors_df.columns = ["Author", "Number of Papers"]

# Save original data and insights
with pd.ExcelWriter(output_csv_path, engine="xlsxwriter") as writer:
    df.to_excel(writer, sheet_name="Scraped Data", index=False)
    insights_df.to_excel(writer, sheet_name="General Insights", index=False)
    papers_per_year_df.to_excel(writer, sheet_name="Papers Per Year", index=False)
    top_authors_df.to_excel(writer, sheet_name="Top Authors", index=False)

print(f"Updated data saved as {output_csv_path}")

# --- PRINT INSIGHTS ---
print(f"\nTotal Papers Scraped: {total_papers}")
print("\nPapers Published Per Year:")
print(papers_per_year)
print(f"\nAverage Number of Authors per Paper: {round(avg_authors_per_paper, 2)}")
print("\nTop 10 Most Frequent Authors:")
print(top_authors)
