import json
import requests
import pandas as pd
import math
from os import getenv
from dotenv import load_dotenv
from io import StringIO
from urllib.parse import urlparse
from collections import defaultdict

## defines all Grist types that are not text by default.
column_types = {
    'download_counts': 'Numeric',
    'citations': 'Integer',
    'docker_downloads': 'Integer',
    'category': 'Choice',
    'sub_category': 'Choice',
    'language': 'Choice',
    'keywords': 'Choice List',
    'score': 'Numeric',
    'created_at': 'DateTime',
    'license': 'Choice'
}

assert load_dotenv(), 'Environment variables could not be loaded'

# Replace these with your values
API_KEY = getenv("GRIST")
DOC_ID = '8YWKLVW6EKD7sLxWP2H9ZY'
CSV_FILE_PATH = './csv/ost_deployment.csv'
MAX_BYTES = 500_000

TABLE_NAME_PROJECTS = 'Projects'
project_columns_to_create = []
project_records_url = f'https://api.getgrist.com/api/docs/{DOC_ID}/tables/{TABLE_NAME_PROJECTS}/records'
project_delete_url = f'https://api.getgrist.com/api/docs/{DOC_ID}/tables/{TABLE_NAME_PROJECTS}/data/delete'
project_columns_url = f'https://api.getgrist.com/api/docs/{DOC_ID}/tables/{TABLE_NAME_PROJECTS}/columns'

TABLE_NAME_ORGANIZATIONS = 'Organizations'
org_columns_to_create = []
org_records_url = f'https://api.getgrist.com/api/docs/{DOC_ID}/tables/{TABLE_NAME_ORGANIZATIONS}/records'
org_delete_url = f'https://api.getgrist.com/api/docs/{DOC_ID}/tables/{TABLE_NAME_ORGANIZATIONS}/data/delete'
org_columns_url = f'https://api.getgrist.com/api/docs/{DOC_ID}/tables/{TABLE_NAME_ORGANIZATIONS}/columns'

# Headers for API request
headers = {
    'Authorization': f'Bearer {API_KEY}',
    'Content-Type': 'application/json'
}

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
latest_commit_activity = []
listed_projects = []
funding_ymls = []

organization_name = []
total_listed_projects_in_organization = {}
organization_description = []
organization_location = []
organization_email = []
organization_twitter_handle = []
organization_osta_counts = []
organization_repositories_counts = []
organization_website = []
organization_created_at = []
organization_updated_at = []
organization_icon_url = []
organization_funding_links = []
organization_category = []
organization_sub_category = []

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
            latest_commit_activity.append(row['repository']['pushed_at'])
        else:
            total_commits.append(None)
            total_committers.append(None)
            development_distribution_score.append(None)
            latest_commit_activity.append(None)
    else:
        stars.append(None)
        license.append(None)
        homepage.append(row['url'])
        project_created_at.append(None)
        total_commits.append(None)
        total_committers.append(None)
        latest_commit_activity.append(None)
        development_distribution_score.append(None)

    if row['readme_doi_urls']:
        doi = urlparse(row['readme_doi_urls'][0]).path[1:]
        DOIs.append(doi)
    else:
        DOIs.append(None)
    
    if row['owner'] is not None and row['owner']['kind'] == 'organization':
        if row['owner']['name'] in total_listed_projects_in_organization:
            total_listed_projects_in_organization[row['owner']['name']] += 1
        else: 
            total_listed_projects_in_organization[row['owner']['name']] = 1 
        if row['owner']['name'] not in organization_name:
            organization_name.append(row['owner']['name'])
            organization_description.append(row['owner']['description'])
            organization_location.append(row['owner']['location'])
            organization_email.append(row['owner']['email'])
            organization_twitter_handle.append(row['owner']['twitter'])
            organization_repositories_counts.append(row['owner']['repositories_count'])
            organization_website.append(row['owner']['website']) 
            organization_created_at.append(row['owner']['created_at'])
            organization_updated_at.append(row['owner']['updated_at'])
            organization_icon_url.append(row['owner']['icon_url'])
            organization_funding_links.append(str(row['owner']['funding_links']))
            organization_category.append(row['category'])
            organization_sub_category.append(row['sub_category'])

df_grist_projects = pd.DataFrame()
df_grist_projects['project_names'] = df_ecosystems['name'].astype(str)
df_grist_projects['git_url'] = df_ecosystems['url'].astype(str)
df_grist_projects['description'] = df_ecosystems['description'].astype(str)
df_grist_projects['homepage'] = homepage
df_grist_projects['category'] = df_ecosystems['category'].astype(str)
df_grist_projects['sub_category'] = df_ecosystems['sub_category'].astype(str)
df_grist_projects['latest_commit_activity'] = latest_commit_activity
df_grist_projects['keywords'] = df_ecosystems['keywords'].astype(str).apply(lambda x: x.replace('[','').replace(']','').replace('\'',''))
df_grist_projects['language'] = df_ecosystems['language'].astype(str)
df_grist_projects['license'] = license
df_grist_projects['downloads_last_month'] = df_ecosystems['monthly_downloads'].astype(str)
df_grist_projects['stars'] = stars
df_grist_projects['development_distribution_score'] = development_distribution_score
df_grist_projects['score'] = df_ecosystems['score'].astype(str)
df_grist_projects['total_committers'] = total_committers
df_grist_projects['citations'] = df_ecosystems['total_citations'].astype(str)
df_grist_projects['project_created_at'] = project_created_at
df_grist_projects['total_commits'] = total_commits
df_grist_projects['readme_doi_urls'] = df_ecosystems['readme_doi_urls'].astype(str).apply(lambda x: x.replace('[','').replace(']','').replace('\'',''))
df_grist_projects['funding_links'] = df_ecosystems['funding_links'].astype(str).apply(lambda x: x.replace('[','').replace(']','').replace('\'',''))
df_grist_projects['avatar_url'] = df_ecosystems['avatar_url'].astype(str)
df_grist_projects['last_synced_at'] = df_ecosystems['last_synced_at'].astype(str)
df_grist_projects['entry_created_at'] = df_ecosystems['created_at'].astype(str)
df_grist_projects['project_updated_at'] = df_ecosystems['updated_at'].astype(str)


df_grist_organization = pd.DataFrame()
df_grist_organization['organization_name'] = organization_name
df_grist_organization['organization_description'] = organization_description
df_grist_organization['organization_location'] = organization_location
df_grist_organization['organization_email'] = organization_email
df_grist_organization['total_listed_projects_in_organization'] = total_listed_projects_in_organization.values()
df_grist_organization['organization_twitter_handle'] = organization_twitter_handle
df_grist_organization['organization_repositories_counts'] = organization_repositories_counts
df_grist_organization['organization_website'] = organization_website
df_grist_organization['organization_created_at'] = organization_created_at
df_grist_organization['organization_updated_at'] = organization_updated_at
df_grist_organization['organization_icon_url'] = organization_icon_url
df_grist_organization['organization_funding_links'] = organization_funding_links
df_grist_organization['organization_category'] = organization_category
df_grist_organization['organization_sub_category'] = organization_sub_category

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
df = df_grist_projects # Load data from CSV file
df = df.where(pd.notna(df_grist_projects), None)  # Replace NaN values with None

column_names = list(df.columns.values)
print("Columns defined:",column_names)

with requests.Session() as session:  # Using requests.Session for multiple requests
    session.headers.update(headers)  # Update session headers

    # Get all rowIds and delete existing records
    response = handle_response(session.get(project_records_url))  # Handle response
    row_ids = [r["id"] for r in response.json()["records"]]  # Get row ids
    response = handle_response(session.post(project_delete_url, json=row_ids))  # Delete existing records

    # Validate the response
    if response.status_code != 200:
        print("Failed to delete existing records")
        print(response.json())
        exit()

    response = handle_response(session.get(project_columns_url))  # Handle response

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
            project_columns_to_create.append(col)  # Remove non-existent columns

    if len(project_columns_to_create) > 0:
        columns_to_defined = [
            {
                'id': column_name.replace(" ", "_").lower(),  
                'label': column_name,                        
                'type': column_types.get(column_name, 'Text')
            }
            for column_name in project_columns_to_create
        ]
        response = handle_response(session.post(project_columns_url, json={'columns': columns_to_defined}))
    
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
        response = handle_response(session.post(project_records_url, json={"records": batch}))  # Upload data

print("Project Data uploaded successfully!")


df = df_grist_organization # Load data from CSV file
df = df.where(pd.notna(df_grist_organization), None)  # Replace NaN values with None

column_names = list(df.columns.values)
print("Columns defined:",column_names)

with requests.Session() as session:  # Using requests.Session for multiple requests
    session.headers.update(headers)  # Update session headers

    # Get all rowIds and delete existing records
    response = handle_response(session.get(org_records_url))  # Handle response
    row_ids = [r["id"] for r in response.json()["records"]]  # Get row ids
    response = handle_response(session.post(org_delete_url, json=row_ids))  # Delete existing records

    # Validate the response
    if response.status_code != 200:
        print("Failed to delete existing records")
        print(response.json())
        exit()

    response = handle_response(session.get(org_columns_url))  # Handle response

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
            org_columns_to_create.append(col)  # Remove non-existent columns

    if len(org_columns_to_create) > 0:
        columns_to_defined = [
            {
                'id': column_name.replace(" ", "_").lower(),  
                'label': column_name,                        
                #'type': column_types.get(column_name, 'Text')
            }
            for column_name in org_columns_to_create
        ]
        response = handle_response(session.post(org_columns_url, json={'columns': columns_to_defined}))
    
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
        response = handle_response(session.post(org_records_url, json={"records": batch}))  # Upload data

print("Organization Data uploaded successfully!")