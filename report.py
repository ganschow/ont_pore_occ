import json, re
from bs4 import BeautifulSoup

# Load the HTML content from a file
with open('report_PAY11948_20240924_1136_e03a8d32.html', 'r') as file:
    html_content = file.read()

# Parse the HTML
soup = BeautifulSoup(html_content, 'html.parser')

# Find the first <script> tag containing the reportData variable
script_tag = soup.find('script')
script_content = script_tag.string

# Use a regular expression to find and load the JSON data assigned to the reportData variable
pattern = r'reportData\s*=\s*({.*})'
match = re.search(pattern, script_content)
report_data = json.loads(match.group(1))

# Extract the series_data
series_data = report_data['pore_activity_grouped']['series_data']

# Get the "data" lists for the first and third elements
sequencing = series_data[0]['data']   # First element in data = Pores sequencing in format [timestamp, value]
available = series_data[1]['data']    # Second element in data = Pores available in format [timestamp, value]

# Calculate pore occupancy, convert timestamps from seconds to hours
pore_occupancy = [[(s[0] / 3600), s[1] * 100 / (s[1] + a[1])] if a != 0 else None for s, a in zip(sequencing, available)]

# Find maximum pore occupancy
max_pore_occupancy = max(map(lambda x: x[1], pore_occupancy))

# Print the result
print("Sequencing")
print(sequencing)

print("Available")
print(available)

print("Pore Occupancy")
print(pore_occupancy)

print("Max Pore Occ")
print(max_pore_occupancy)