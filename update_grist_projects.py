import json
import requests
import pandas as pd
import math
from os import getenv
from dotenv import load_dotenv


from habanero import counts

from semanticscholar import SemanticScholar
sch = SemanticScholar()

URL = "https://ost.ecosyste.ms/api/v1/projects?reviewed=true&per_page=3000"
FILE_TO_SAVE_AS = "ecosystems_repository_downloads.json" # the name you want to save file as

pages=20
resp = requests.get(URL) # making requests to server

#all_data = {}
#for page in range(1, pages + 1):
#    data = requests.get(URL.format(page)).json()
#    all_data.extend(data)
    
    
#for page in range(1, pages + 1):
#    print("Page:",page)
#    data = requests.get(URL.format(page)).json()
#    if 'status' in data:
#        break
#    all_data = {**all_data, **data[0]}

with open(FILE_TO_SAVE_AS, "wb") as f: # opening a file handler to create new file 
    f.write(resp.content) # writing content to file
df_ecosystems = pd.read_json(resp.content.decode())


from urllib.parse import urlparse
names = []
download_counts = []
url = []
description = []
category = []
sub_category = []
language = []
docker_downloads = []
DOIs = []
total_citations = []

for index, row in df_ecosystems.iterrows():
    names.append(row['name'])
    package_downloads = 0
    docker_download_count = 0
    for package_manager in range(len(row['packages'])):
        if row['packages'][package_manager]['downloads']:
            if row['packages'][package_manager]['downloads_period'] == "last-month":
                package_downloads += row['packages'][package_manager]['downloads']
        if row['packages'][package_manager]['docker_downloads_count']:
            docker_download_count = row['packages'][package_manager]['docker_downloads_count']
        else:
            docker_download_count = 0
    download_counts.append(package_downloads)
    docker_downloads.append(docker_download_count)
    url.append(row['url'])
    description.append(row['description'])
    category.append(row['category'])
    sub_category.append(row['sub_category'])
    language.append(row['language'])
    total_citations.append(row['total_citations']) 
    if row['readme_doi_urls']:
        doi = urlparse(row['readme_doi_urls'][0]).path[1:]
        DOIs.append(doi)
    else:
        DOIs.append(None)


df_extract = pd.DataFrame()
df_extract['project_names'] = names
df_extract['download_counts'] = download_counts
df_extract['citations'] = total_citations
df_extract['doi'] = DOIs
df_extract['docker_downloads'] = docker_downloads
#df_extract['category'] = category
df_extract['sub_category'] = sub_category
df_extract['git_url'] = url
df_extract['description'] = description
df_extract['language'] = language
df_extract['docker_downloads'] = docker_downloads


assert load_dotenv(), 'Environment variables could not be loaded'

# Replace these with your values
API_KEY = getenv("GRIST")
DOC_ID = '8YWKLVW6EKD7sLxWP2H9ZY'
TABLE_NAME = 'Projects'
CSV_FILE_PATH = './csv/ost_deployment.csv'
MAX_BYTES = 500_000

# Headers for API request
headers = {
    'Authorization': f'Bearer {API_KEY}',
    'Content-Type': 'application/json'
}

def calculate_size_in_bytes(data):
    """
    Function to calculate the size of the data in bytes.
    Args:
    data : The data whose size is to be calculated.
    Returns:
    The size of the data in bytes.
    """
    serialized = json.dumps(data, ensure_ascii=False)
    return len(serialized.encode('utf-8'))

def create_batched_requests_by_size(data, max_bytes):
    """
    Function to create batches of data that do not exceed the maximum byte size.
    Args:
    data : The data to be batched.
    max_bytes : The maximum byte size of a batch.
    Yields:
    The next batch of data.
    """
    batch = []
    current_size = 0
    for row in data:
        row_size = calculate_size_in_bytes(row)
        if (current_size + row_size) > max_bytes:
            yield batch
            batch = []
            current_size = 0
        batch.append(row)
        current_size += row_size
    if batch:
        yield batch

def handle_response(response):
    """
    Function to handle the response from the API request.
    Args:
    response : The response from the API request.
    Returns:
    The response if the request was successful.
    Raises:
    HTTPError : If the request was not successful.
    """
    try:
        response.raise_for_status()
        return response
    except requests.HTTPError as e:
        try:
            error_message = response.json()["error"]
            print("\n\nERROR MESSAGE: ", error_message)
            raise requests.HTTPError(f"{e.response.status_code}: {error_message}")
        except (ValueError, KeyError):
            raise e


# Function to create a new column in the table
def create_column(column_name, column_type='Text'):
    # Define the API endpoint for adding a column
    url = f'{BASE_URL}/tables/{TABLE_ID}/columns'
    
    # Data to be sent in the request body
    data = {
        'fields': {
            'id': column_name.replace(" ", "_").lower(),  # Convert to snake_case for ID
            'label': column_name,                        # The column name as it appears in the UI
            'type': column_type,                         # The type of the column ('Text', 'Numeric', etc.)
        }
    }
    
    # Make the POST request to create the column
    response = requests.post(url, json=data, headers=headers)
    
    # Check if the request was successful
    if response.status_code == 200:
        print(f"Column '{column_name}' created successfully!")
    else:
        print(f"Failed to create column '{column_name}'. Status Code: {response.status_code}")


# Load and clean data
df = df_extract # Load data from CSV file
df = df.where(pd.notna(df_extract), None)  # Replace NaN values with None

column_names = list(df.columns.values)


column_types = {
    'project_names': 'Text',
    'download_counts': 'Numeric',
    'citations': 'Integer',
    'doi': 'Text',
    'docker_downloads': 'Integer',
    'sub_category': 'Text',
    'git_url': 'Text',
    'description': 'Text',
    'language': 'Text'
}

columns_to_create = [
    {
        'id': column_name.replace(" ", "_").lower(),  
        'label': column_name,                        
    }
    for column_name in column_names
]

print("Columns defined:",column_names)

with requests.Session() as session:  # Using requests.Session for multiple requests
    session.headers.update(headers)  # Update session headers

    # Fetch column data from API
    columns_url = f'https://api.getgrist.com/api/docs/{DOC_ID}/tables/{TABLE_NAME}/columns'
    
    response = handle_response(session.post(columns_url, json={'columns': columns_to_create}))
    if response.status_code != 200:
        print("Failed to create columns existing records")
        print(response.json())
        exit()

    data_list = df.to_dict(orient='records')  # Convert dataframe to list of dictionaries

    # Convert NaN values to None after converting to dictionary - AGAIN!
    #for record in data_list:
    #    for key, value in record.items():
    #        if isinstance(value, float) and math.isnan(value):
    #            record[key] = None  # Replace NaN values with None
            
    grist_data = [{"fields": record} for record in data_list]  # Prepare data for Grist

    # Endpoint URL for fetching/updating the table
    url = f'https://api.getgrist.com/api/docs/{DOC_ID}/tables/{TABLE_NAME}/records'

    # Get all rowIds and delete existing records
    #response = handle_response(session.get(url))  # Handle response
    #row_ids = [r["id"] for r in response.json()["records"]]  # Get row ids
    #delete_url = f'https://api.getgrist.com/api/docs/{DOC_ID}/tables/{TABLE_NAME}/data/delete'
    #response = handle_response(session.post(delete_url, json=row_ids))  # Delete existing records

    # Validate the response
    if response.status_code != 200:
        print("Failed to delete existing records")
        print(response.json())
        exit()

    # Upload new data from the CSV in batches
    for batch in create_batched_requests_by_size(grist_data, MAX_BYTES):
        print(f"Adding {len(batch)} records")
        response = handle_response(session.post(url, json={"records": batch}))  # Upload data

print("Data uploaded successfully!")
