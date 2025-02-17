import pandas as pd
import matplotlib.pyplot as plt
from collections import Counter
import seaborn as sns

# Load the CSV file
CSV_FILE = "annotated_papers.csv"  # Update if needed
df = pd.read_csv(CSV_FILE)

# 1️⃣ Count papers in each category
category_counts = df["Category"].value_counts()
print("📊 Number of Papers per Category:\n", category_counts)

# 2️⃣ Count papers per year
year_counts = df["Year"].value_counts().sort_index()
print("\n📅 Papers Distribution by Year:\n", year_counts)

# 3️⃣ Count missing abstracts
missing_abstracts = df["Abstract"].str.strip().eq("No abstract found").sum()
print(f"\n❌ Papers with Missing Abstracts: {missing_abstracts}")

# 4️⃣ Find most common words in titles (excluding stop words)
stop_words = {"a", "an", "the", "in", "on", "of", "and", "for", "to", "with", "at", "by"}
all_words = " ".join(df["Title"].dropna()).lower().split()
filtered_words = [word for word in all_words if word not in stop_words and len(word) > 3]
word_counts = Counter(filtered_words).most_common(10)

print("\n🔠 Most Common Words in Titles:")
for word, count in word_counts:
    print(f"{word}: {count}")

# 📊 Plot Category Distribution
plt.figure(figsize=(10, 5))
sns.barplot(x=category_counts.index, y=category_counts.values, palette="viridis")
plt.xticks(rotation=30)
plt.xlabel("Category")
plt.ylabel("Number of Papers")
plt.title("📊 Research Paper Category Distribution")
plt.show()

# 📅 Plot Papers Over Time
plt.figure(figsize=(12, 5))
sns.lineplot(x=year_counts.index, y=year_counts.values, marker="o", color="b")
plt.xlabel("Year")
plt.ylabel("Number of Papers")
plt.title("📅 Papers Published Over Time")
plt.grid()
plt.show()
