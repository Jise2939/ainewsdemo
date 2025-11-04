import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

# 读取CSV文件
input_file = '/workspaces/ainewsdemo/data/trump_xi_meeting_fulltext_dedup-1657.csv'
df = pd.read_csv(input_file)

# Count total articles
article_count = len(df)
print(f"Total articles: {article_count}")

# Calculate word count for each article
df['word_count'] = df['body'].str.split().str.len()

# Basic statistics
stats = df['word_count'].describe()
print("\nWord count statistics:")
print(stats)

# Save CSV file with word count
output_csv = Path('output_with_wordcount.csv')
df.to_csv(output_csv, index=False)
print(f"\nSaved CSV file with word count to: {output_csv}")

# Create statistical charts
plt.figure(figsize=(12, 6))

# 1. Word count distribution histogram
plt.subplot(1, 2, 1)
sns.histplot(data=df, x='word_count', bins=30)
plt.title('Article Word Count Distribution')
plt.xlabel('Word Count')
plt.ylabel('Number of Articles')

# 2. Word count box plot
plt.subplot(1, 2, 2)
sns.boxplot(y=df['word_count'])
plt.title('Article Word Count Box Plot')
plt.ylabel('Word Count')

# 保存图表
plt.tight_layout()
plt.savefig('word_count_analysis.png')
print("\n已保存统计图表到: word_count_analysis.png")

# Generate Markdown report
markdown_content = f"""# Article Statistics Analysis Report

## Basic Statistics

- Total Articles: {article_count}
- Average Word Count: {stats['mean']:.2f}
- Minimum Word Count: {stats['min']:.0f}
- Maximum Word Count: {stats['max']:.0f}
- Median Word Count: {stats['50%']:.0f}

## Word Count Percentiles

- 25th Percentile: {stats['25%']:.0f} words
- 50th Percentile: {stats['50%']:.0f} words
- 75th Percentile: {stats['75%']:.0f} words

## Visualizations

See attachment `word_count_analysis.png`:
- Left: Article Word Count Distribution Histogram
- Right: Article Word Count Box Plot

## Data File

Complete data file with word count statistics has been saved as: `output_with_wordcount.csv`
"""

# 保存Markdown报告
with open('analysis_report.md', 'w', encoding='utf-8') as f:
    f.write(markdown_content)
print("\n已生成分析报告: analysis_report.md")