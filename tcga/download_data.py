import pandas as pd
import subprocess
import os
import shutil
import json
import requests
import multiprocessing
import logging
import time
from concurrent.futures import ProcessPoolExecutor
from functools import partial

# Configure logging for better traceability.
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def batch_fetch_cancer_types(file_ids):
    query = {
        "filters": {"op": "in", "content": {"field": "files.file_id", "value": file_ids}},
        "fields": "cases.disease_type,cases.project.project_id",
        "format": "JSON",
        "size": len(file_ids)
    }
    try:
        response = requests.post("https://api.gdc.cancer.gov/files", json=query)
        response.raise_for_status()
        data = response.json()
        return {
            entry["id"]: {
                "disease_type": entry["cases"][0]["disease_type"],
                "project_id": entry["cases"][0].get("project", {}).get("project_id", "Unknown")
            }
            for entry in data["data"]["hits"]
        }
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching cancer types: {e}")
        return {}

def download_and_process(row, cancer_type_dict):
    file_id = row["id"]
    expected_filename = row["filename"]
    download_path = os.path.join("data", file_id)
    max_attempts = 3  # Maximum retry attempts

    for attempt in range(1, max_attempts + 1):
        try:
            # Run the bash script to download the file.
            subprocess.run(["./download_data.sh", file_id], check=True, timeout=300)
            break  # If successful, exit the retry loop.
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as e:
            logging.error(f"Attempt {attempt}/{max_attempts} failed for file {file_id}: {e}")
            if attempt == max_attempts:
                logging.error(f"Exceeded maximum retries for file {file_id}. Skipping.")
                return None
            time.sleep(5)  # Wait before retrying.

    data_file = os.path.join(download_path, expected_filename)
    if not os.path.exists(data_file):
        logging.error(f"Expected file {expected_filename} not found in {download_path}")
        return None

    try:
        # Read the TSV file while skipping non-data rows.
        df = pd.read_csv(data_file, sep="\t", skiprows=[0, 2, 3, 4, 5])
    except Exception as e:
        logging.error(f"Error reading file {data_file}: {e}")
        return None

    try:
        # Extract all gene expressions—map every gene to its 'tpm_unstranded' value.
        gene_expressions = dict(zip(df['gene_name'], df['tpm_unstranded']))
    except KeyError as e:
        logging.error(f"Expected columns not found in {data_file}: {e}")
        return None

    # Retrieve cancer type information from the passed-in dictionary.
    cancer_info = cancer_type_dict.get(file_id, {"disease_type": "Unknown", "project_id": "Unknown"})
    result = {
        "id": file_id,
        "cancer_type": cancer_info["disease_type"],
        "project_id": cancer_info["project_id"]
    }
    result.update(gene_expressions)
    
    # Cleanup: Remove the download directory.
    if os.path.exists(download_path):
        shutil.rmtree(download_path)
    return result

def main():
    start_time = time.time()

    # Ensure the output directory exists.
    output_dir = "data"
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, "master_expression_data.tsv")

    # Fixed manifest file name.
    manifest_file = "data/manifest.tsv"
    try:
        df_manifest = pd.read_csv(manifest_file, sep="\t")
    except Exception as e:
        logging.error(f"Error reading manifest file '{manifest_file}': {e}")
        return

    df_manifest = df_manifest.loc[:, ["id", "filename"]]

    # Fetch cancer type data with caching.
    all_file_ids = df_manifest["id"].tolist()
    cancer_type_dict = {}
    json_cache_file = os.path.join("data", "cancer_type_data.json")
    if os.path.exists(json_cache_file):
        try:
            with open(json_cache_file, "r") as f:
                cancer_type_dict = json.load(f)
            logging.info("Loaded cancer type data from cache.")
        except Exception as e:
            logging.error(f"Error loading cancer type cache: {e}")
    else:
        cancer_type_dict = batch_fetch_cancer_types(all_file_ids)
        os.makedirs("data", exist_ok=True)
        with open(json_cache_file, "w") as f:
            json.dump(cancer_type_dict, f)
        logging.info("Saved cancer type data to cache.")

    # Resume processing if an output file already exists.
    if os.path.exists(output_file):
        try:
            processed_df = pd.read_csv(output_file, sep="\t")
            processed_ids = set(processed_df["id"])
            df_manifest = df_manifest[~df_manifest["id"].isin(processed_ids)]
        except Exception as e:
            logging.error(f"Error reading output file for resuming: {e}")

    total_files = len(df_manifest)
    logging.info(f"Processing {total_files} files...")

    num_workers = min(multiprocessing.cpu_count(), 10)
    batch_size = 100  # Save results in batches.

    # Create a partial function that includes cancer_type_dict.
    process_fn = partial(download_and_process, cancer_type_dict=cancer_type_dict)

    with ProcessPoolExecutor(max_workers=num_workers) as executor:
        results = []
        for i, result in enumerate(executor.map(process_fn, df_manifest.to_dict(orient="records")), start=1):
            if result is not None:
                results.append(result)

            if len(results) >= batch_size:
                temp_df = pd.DataFrame(results)
                temp_df.to_csv(output_file, sep="\t", index=False, mode="a", header=not os.path.exists(output_file))
                logging.info(f"Saved batch of {len(results)} files. Processed {i} / {total_files}.")
                results = []  # Reset batch results.

        if results:
            temp_df = pd.DataFrame(results)
            temp_df.to_csv(output_file, sep="\t", index=False, mode="a", header=not os.path.exists(output_file))
            logging.info(f"Saved final batch of {len(results)} files.")

    end_time = time.time()
    logging.info(f"Execution Time: {end_time - start_time:.2f} seconds")

if __name__ == "__main__":
    main()
