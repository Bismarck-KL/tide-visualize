import requests
from lxml import html
import numpy as np
import dotenv
import os

# Load environment variables
dotenv.load_dotenv()

# Get the year and filename from the environment variables
year = int(os.getenv('YEAR', 2024))
filename = os.getenv('FILENAME', f"page-{year}.html")

# Fetch data
if not os.path.exists(filename):
    page = requests.get(os.getenv('URL')).text
    with open(filename, 'w', encoding='UTF8') as f:
        f.write(page)
else:
    with open(filename, 'r', encoding='UTF8') as f:
        page = f.read()

# Parse the page to HTML
tree = html.fromstring(page)
rows = tree.xpath(os.getenv('ROW_XPATH'))

data_list = []
for row in rows: 
    parts = row.text_content().split()
    if parts[0] != "Date" and len(parts) == 25:
        data_list.append([float(x) for x in parts])

# Convert the data_list to a 2D NumPy array
data_array = np.array(data_list)
print("data_array:",data_array)

