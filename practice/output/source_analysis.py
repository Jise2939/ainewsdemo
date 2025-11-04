import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

# Read CSV file
input_file = '/workspaces/ainewsdemo/data/trump_xi_meeting_fulltext_dedup-1657.csv'
df = pd.read_csv(input_file)

# Analyze source distribution
source_counts = df['source'].value_counts()
print("Article Source Distribution:")
print(source_counts)
print("\nTotal unique sources:", len(source_counts))

# Create visualizations
plt.figure(figsize=(15, 10))

# 1. Source distribution bar plot
plt.subplot(2, 1, 1)
source_counts.head(15).plot(kind='bar')
plt.title('Top 15 News Sources')
plt.xlabel('Source')
plt.ylabel('Number of Articles')
plt.xticks(rotation=45, ha='right')

# 2. Source distribution pie chart
plt.subplot(2, 1, 2)
# Combine small sources into "Others"
threshold = source_counts.max() * 0.05  # Sources with less than 5% of max count
major_sources = source_counts[source_counts >= threshold]
minor_sources = pd.Series({'Others': source_counts[source_counts < threshold].sum()})
plot_data = pd.concat([major_sources, minor_sources])

plt.pie(plot_data, labels=plot_data.index, autopct='%1.1f%%')
plt.title('Distribution of News Sources (With Sources < 5% Combined as "Others")')

# Save the visualization
plt.tight_layout()
plt.savefig('source_distribution_analysis.png', bbox_inches='tight')
print("\nSaved source distribution charts to: source_distribution_analysis.png")

# Generate Markdown report
markdown_content = f"""# News Source Analysis Report

## Source Distribution Statistics

### Top 10 Sources by Article Count:
{source_counts.head(10).to_frame('Article Count').to_markdown()}

### Summary
- Total unique sources: {len(source_counts)}
- Most frequent source: {source_counts.index[0]} ({source_counts.iloc[0]} articles)
- Sources with only one article: {sum(source_counts == 1)}

## Visualizations

See attachment `source_distribution_analysis.png`:
1. Bar chart showing the top 15 news sources by article count
2. Pie chart showing the distribution of news sources (with minor sources combined)

### Distribution Analysis
- Top source accounts for {(source_counts.iloc[0]/len(df)*100):.1f}% of all articles
- Top 5 sources account for {(source_counts.head(5).sum()/len(df)*100):.1f}% of all articles
- Top 10 sources account for {(source_counts.head(10).sum()/len(df)*100):.1f}% of all articles
"""

# Save Markdown report
with open('source_analysis_report.md', 'w', encoding='utf-8') as f:
    f.write(markdown_content)
print("\nGenerated source analysis report: source_analysis_report.md")