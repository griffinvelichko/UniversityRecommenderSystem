import requests
import pandas as pd
from bs4 import BeautifulSoup

# URL of the UBC programs page
url = 'https://you.ubc.ca/programs/'

# Send a GET request to the URL
headers = {'User-Agent': 'Mozilla/5.0'}
response = requests.get(url, headers=headers)

# Check if request was successful
if response.status_code != 200:
    print("Failed to retrieve the webpage")
    exit()

# Parse the HTML content
soup = BeautifulSoup(response.text, 'html.parser')

# Find all program entries
programs = soup.find_all('div', class_='program-name')  # Adjust the class name based on actual HTML structure

# List to store extracted data
program_list = []

# Loop through each program and extract the name and description
for program in programs:
    name_tag = program.find('h3')  # Adjust tag based on actual structure
    desc_tag = program.find('p')  # Adjust tag based on actual structure

    name = name_tag.text.strip() if name_tag else 'N/A'
    description = desc_tag.text.strip() if desc_tag else 'N/A'

    # Print extracted data for debugging
    print(f"Program Name: {name}")
    print(f"Description: {description}")
    print('-' * 40)

    program_list.append({'Program Name': name, 'Description': description})

# Convert list to DataFrame
df = pd.DataFrame(program_list)

# Save DataFrame to CSV
csv_filename = 'ubc_programs.csv'
df.to_csv(csv_filename, index=False, encoding='utf-8')

print(f"Data saved to {csv_filename}")
