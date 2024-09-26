import requests
import os
import subprocess
import sys

def get_modified_seeds():
    """
    Get the list of modified seed files from the GitHub environment variables.
    This assumes the GitHub Action sets the modified files in an environment variable.
    """
    modified_seeds = os.getenv('MODIFIED_SEEDS')
    if not modified_seeds:
        print("No modified seed files found in the environment variable.")
        return []
    
    # Split the environment variable string into a list of filenames.
    modified_seeds = modified_seeds.split()

    print(f"Modified seed files: {modified_seeds}")
    
    # Filter only .csv files in the seeds directory and subdirectories
    seed_files = [
        os.path.splitext(os.path.basename(f))[0]  # Get the file name without extension
        for f in modified_seeds 
        if f.startswith('seeds/') and f.endswith('.csv')
    ]

    print(f"Modified seed files names only: {seed_files}")

    return seed_files

def trigger_dbt_cloud_job(account_id, job_id, token, modified_seeds):
    # Construct the overridden dbt seed command
    if modified_seeds:
        dbt_command = f"dbt seed --select {' '.join(modified_seeds)} --full-refresh"
    else:
        print("No modified seed files found. Exiting...")
        sys.exit(0)

    print(f"Triggering dbt Cloud job with the following command: {dbt_command}")

    # Construct the URL and headers for dbt Cloud API request
    url = f"https://cloud.getdbt.com/api/v2/accounts/{account_id}/jobs/{job_id}/run/"
    headers = {
        "Authorization": f"Token {token}",
        "Content-Type": "application/json"
    }

    # Data payload with the overridden command
    data = {
        "cause": "Triggered by GitHub Action",
        "commands": [dbt_command]
    }

    # Trigger the dbt Cloud job
    response = requests.post(url, headers=headers, json=data)

    if response.status_code == 200:
        print("Job successfully triggered!")
        print("Response:", response.json())
    else:
        print(f"Failed to trigger the job. Status code: {response.status_code}")
        print("Response:", response.json())
        sys.exit(1)

if __name__ == "__main__":
    # Get dbt Cloud account details from environment variables
    dbt_account_id = os.getenv('DBT_ACCOUNT_ID')
    dbt_job_id = os.getenv('DBT_JOB_ID')
    dbt_api_token = os.getenv('DBT_API_TOKEN')

    if not all([dbt_account_id, dbt_job_id, dbt_api_token]):
        print("Error: DBT_ACCOUNT_ID, DBT_JOB_ID, and DBT_API_TOKEN must be set.")
        sys.exit(1)

    # Get the list of modified seed files
    modified_seeds = get_modified_seeds()

    # Trigger the dbt Cloud job with the modified seed files
    trigger_dbt_cloud_job(dbt_account_id, dbt_job_id, dbt_api_token, modified_seeds)
