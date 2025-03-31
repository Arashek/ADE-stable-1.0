from markdown2pdf import convert
import os

# Create docs directory if it doesn't exist
os.makedirs('docs', exist_ok=True)

# Convert markdown to PDF
convert('docs/programming_languages.md', 'docs/programming_languages.pdf') 