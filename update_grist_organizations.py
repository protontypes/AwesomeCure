import json
import os
import requests
import pandas as pd
import math
from os import getenv
from dotenv import load_dotenv

assert load_dotenv(), 'Environment variables could not be loaded'

# Replace these with your values
API_KEY = getenv("GRIST")
DOC_ID = 'gSscJkc5Rb1Rw45gh1o1Yc'
TABLE_NAME = 'Organizations'
CSV_FILE_PATH = './csv/github_organizations.csv'
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
df = pd.read_csv(CSV_FILE_PATH)  # Load data from CSV file
df = df.where(pd.notna(df), None)  # Replace NaN values with None

with requests.Session() as session:  # Using requests.Session for multiple requests
    session.headers.update(headers)  # Update session headers

    # Fetch column data from API
    columns_url = f'https://api.getgrist.com/api/docs/{DOC_ID}/tables/{TABLE_NAME}/columns'
    response = handle_response(session.get(columns_url))  # Handle response

    # Create a mapping from label to colRef (column ID)
    columns_data = response.json()
    column_mapping = {col["fields"]["label"]: col["id"] for col in columns_data["columns"]}

    # Check if all columns in dataframe exist in Grist table
    for col in df.columns:
        if col not in column_mapping.keys():
            print(f"Column '{col}' does not exist in Grist table. Removing it from dataframe.")
            df = df.drop(columns=[col])  # Remove non-existent columns

    # Rename columns
    df = df.rename(columns=column_mapping)
    data_list = df.to_dict(orient='records')  # Convert dataframe to list of dictionaries

    # Convert NaN values to None after converting to dictionary - AGAIN!
    for record in data_list:
        for key, value in record.items():
            if isinstance(value, float) and math.isnan(value):
                record[key] = None  # Replace NaN values with None

    grist_data = [{"fields": record} for record in data_list]  # Prepare data for Grist

    # Endpoint URL for fetching/updating the table
    url = f'https://api.getgrist.com/api/docs/{DOC_ID}/tables/{TABLE_NAME}/records'

    # Get all rowIds and delete existing records
    response = handle_response(session.get(url))  # Handle response
    row_ids = [r["id"] for r in response.json()["records"]]  # Get row ids
    delete_url = f'https://api.getgrist.com/api/docs/{DOC_ID}/tables/{TABLE_NAME}/data/delete'
    response = handle_response(session.post(delete_url, json=row_ids))  # Delete existing records

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
