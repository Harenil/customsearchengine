import os

# Function to read the content of a file
def read_file_content(filename):
    with open(filename, 'r', encoding='utf-8') as file:
        return file.read()

# Base directory and subdirectory
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
searchengine_dir = os.path.join(base_dir, 'searchengine')
# Files to read from
files = [
    os.path.join(base_dir, 'searchengine.py'),
    os.path.join(base_dir, 'setup.py'),
    os.path.join(searchengine_dir, 'search.py'),
    os.path.join(searchengine_dir, 'scraping.py'),
    os.path.join(searchengine_dir, 'routes.py'),
    os.path.join(searchengine_dir, 'database.py'),
    os.path.join(searchengine_dir, '__init__.py')
]

# File structure to be included in the text
file_structure = """customsearchengine/
│
├── searchengine/
│   ├── __init__.py
│   ├── database.py
│   ├── scraping.py
│   ├── search.py
│   └── routes.py
│
├── setup.py
└── searchengine.py
"""

# New string of text
new_text = "The following details a Python Flask tool developed in Visual Studio on Windows 10, including source code for all the modules and the file structure.\n\n"
new_text += "File Structure:\n```\n" + file_structure + "```\n\n"

# Read the content of each file and append it to the new string of text
for file in files:
    file_name = os.path.basename(file)
    new_text += f"{file_name}\n```python\n{read_file_content(file)}\n```\n\n"

# Copy the new string of text to the clipboard
try:
    import pyperclip
    pyperclip.copy(new_text)
    print("The combined text has been copied to the clipboard.")
except ImportError:
    print("pyperclip module not found. Please install it to copy the text to the clipboard.")