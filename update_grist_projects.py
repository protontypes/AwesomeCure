import json
import requests
import pandas as pd
import math
from os import getenv
from dotenv import load_dotenv
from io import StringIO
from urllib.parse import urlparse


URL = "https://ost.ecosyste.ms/api/v1/projects?reviewed=true&per_page=3000"
FILE_TO_SAVE_AS = "ecosystems_repository_downloads.json" # the name you want to save file as

resp = requests.get(URL) # making requests to server

with open(FILE_TO_SAVE_AS, "wb") as f: # opening a file handler to create new file 
    f.write(resp.content) # writing content to file
df_ecosystems = pd.read_json(StringIO(resp.content.decode()))

stars = []
homepage = []
license = []
DOIs = []
project_created_at = []
total_commits = []
total_committers = []
development_distribution_score = []

for index, row in df_ecosystems.iterrows():
    if row['repository'] is not None:
        stars.append(row['repository']['stargazers_count'])
        license.append(row['repository']['license']) 
        homepage.append(row['repository']['homepage'])
        project_created_at.append(row['repository']['created_at'])
        if row['repository']['commit_stats'] is not None:
            total_commits.append(row['repository']['commit_stats']['total_commits'])
            total_committers.append(row['repository']['commit_stats']['total_committers'])
            development_distribution_score.append(row['repository']['commit_stats']['dds'])
        else:
            total_commits.append(None)
            total_committers.append(None)
            development_distribution_score.append(None)
    else:
        stars.append(None)
        license.append(None)
        homepage.append(row['url'])
        project_created_at.append(None)
        total_commits.append(None)
        total_committers.append(None)
        development_distribution_score.append(None)

    if row['readme_doi_urls']:
        doi = urlparse(row['readme_doi_urls'][0]).path[1:]
        DOIs.append(doi)
    else:
        DOIs.append(None)

df_grist = pd.DataFrame()
df_grist['git_url'] = df_ecosystems['url'].astype(str)
df_grist['project_names'] = df_ecosystems['name'].astype(str)
df_grist['description'] = df_ecosystems['description'].astype(str)
df_grist['category'] = df_ecosystems['category'].astype(str)
df_grist['sub_category'] = df_ecosystems['sub_category'].astype(str)
df_grist['keywords'] = df_ecosystems['keywords'].astype(str).apply(lambda x: x.replace('[','').replace(']','').replace('\'',''))
df_grist['language'] = df_ecosystems['language'].astype(str).tolist()
df_grist['downloads_last_month'] = df_ecosystems['monthly_downloads'].astype(str)
df_grist['citations'] = df_ecosystems['total_citations'].astype(str)
df_grist['score'] = df_ecosystems['score'].astype(str)
df_grist['readme_doi_urls'] = df_ecosystems['readme_doi_urls'].astype(str).apply(lambda x: x.replace('[','').replace(']','').replace('\'',''))
df_grist['funding_links'] = df_ecosystems['funding_links'].astype(str).apply(lambda x: x.replace('[','').replace(']','').replace('\'',''))
df_grist['last_synced_at'] = df_ecosystems['last_synced_at'].astype(str)
df_grist['entry_created_at'] = df_ecosystems['created_at'].astype(str)
df_grist['project_updated_at'] = df_ecosystems['updated_at'].astype(str)
df_grist['avatar_url'] = df_ecosystems['avatar_url'].astype(str)
df_grist['stars'] = stars
df_grist['license'] = license
df_grist['homepage'] = homepage
df_grist['project_created_at'] = project_created_at
df_grist['total_commits'] = total_commits
df_grist['total_committers'] = total_committers
df_grist['development_distribution_score'] = development_distribution_score


#df_grist['packages'] = df_ecosystems['packages'].astype(str).tolist()


column_types = {
    'project_names': 'Text',
    'download_counts': 'Numeric',
    'citations': 'Integer',
    'doi': 'Text',
    'docker_downloads': 'Integer',
    'sub_category': 'Text',
    'git_url': 'Text',
    'description': 'Text',
    'language': 'Text',
    'keywords': 'Choice List',
    'score': 'Numeric',
    'created_at': 'DateTime',
}

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

# Load and clean data
df = df_grist # Load data from CSV file
df = df.where(pd.notna(df_grist), None)  # Replace NaN values with None

column_names = list(df.columns.values)

columns_to_create = []
records_url = f'https://api.getgrist.com/api/docs/{DOC_ID}/tables/{TABLE_NAME}/records'
delete_url = f'https://api.getgrist.com/api/docs/{DOC_ID}/tables/{TABLE_NAME}/data/delete'
columns_url = f'https://api.getgrist.com/api/docs/{DOC_ID}/tables/{TABLE_NAME}/columns'



print("Columns defined:",column_names)

with requests.Session() as session:  # Using requests.Session for multiple requests
    session.headers.update(headers)  # Update session headers

    # Get all rowIds and delete existing records
    response = handle_response(session.get(records_url))  # Handle response
    row_ids = [r["id"] for r in response.json()["records"]]  # Get row ids
    delete_url = f'https://api.getgrist.com/api/docs/{DOC_ID}/tables/{TABLE_NAME}/data/delete'
    response = handle_response(session.post(delete_url, json=row_ids))  # Delete existing records

    # Validate the response
    if response.status_code != 200:
        print("Failed to delete existing records")
        print(response.json())
        exit()

    response = handle_response(session.get(columns_url))  # Handle response

        # Validate the response
    if response.status_code != 200:
        print("Failed to get existing columns")
        print(response.json())
        exit()

    # Create a mapping from label to colRef (column ID)
    columns_data = response.json()
    column_mapping = {col["fields"]["label"]: col["id"] for col in columns_data["columns"]}

#   ## Check if all columns in dataframe exist in Grist table
    for col in column_names:
        if col not in column_mapping.keys():
            print(f"Column '{col}' does not exist in Grist table. Creating new column")
            columns_to_create.append(col)  # Remove non-existent columns

    if len(columns_to_create) > 0:
        columns_to_defined = [
            {
                'id': column_name.replace(" ", "_").lower(),  
                'label': column_name,                        
                'type': column_types.get(column_name, 'Text')
            }
            for column_name in columns_to_create
        ]
        response = handle_response(session.post(columns_url, json={'columns': columns_to_defined}))
    
        if response.status_code != 200:
            print("Failed to create column")
            print(response.json())
            exit()

    data_list = df.to_dict(orient='records')  # Convert dataframe to list of dictionaries

    #Convert NaN values to None after converting to dictionary - AGAIN!
    for record in data_list:
        for key, value in record.items():
            if isinstance(value, float) and math.isnan(value):
                record[key] = None  # Replace NaN values with None
            
    grist_data = [{"fields": record} for record in data_list]  # Prepare data for Grist

    # Upload new data from the CSV in batches
    for batch in create_batched_requests_by_size(grist_data, MAX_BYTES):
        print(f"Adding {len(batch)} records")
        response = handle_response(session.post(records_url, json={"records": batch}))  # Upload data

print("Data uploaded successfully!")
