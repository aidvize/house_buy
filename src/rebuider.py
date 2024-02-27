import logging
import sys
import time
from pathlib import Path

from utils import utils
from utils.utils import (
    base_dataframe,
    configure_logging,
    get_page_number,
    intermediate_dataframe,
    load_config,
    load_env,
    performance_metrics,
    remove_duplicates,
    save_to_json,
    save_to_parquet,
    upload_file_s3,
)

# Add the parent directory of `src` to sys.path to resolve the `src` module
sys.path.append(str(Path(__file__).parent.parent))


@performance_metrics
def cred_parameters(page: str) -> tuple:
    """
    Executes the scraping function based on the specified page, saves the scraped
    data to a JSON file, and uploads the JSON file to an AWS S3 bucket.

    Parameters:
    - page (str): The name of the page or platform to scrape (e.g., 'imovirtual').

    Returns:
    - None
    """
    config = load_config()
    bucket_name, aws_access_key, aws_secret_key = load_env()
    base_url = config["url"][page]
    search = config["search"][page]
    typology = config["typology"][page][-1]
    return config, bucket_name, aws_access_key, aws_secret_key, base_url, search, typology


@performance_metrics
def extract(page: str) -> dict:
    """
    Executes the scraping function based on the specified page, saves the scraped
    data to a JSON file, and uploads the JSON file to an AWS S3 bucket.

    Parameters:
    - page (str): The name of the page or platform to scrape (e.g., 'imovirtual').

    Returns:
    - None
    """
    # Extract credentials and parameters
    (
        config,
        bucket_name,
        aws_access_key,
        aws_secret_key,
        base_url,
        search,
        typology,
    ) = cred_parameters(page)

    # Determine the scraping function to use
    func_name = page
    func = getattr(utils, func_name, None)

    if func is None:
        logging.info(f"Function {func_name} not found in utils module.")
        return {}

    max_pages = get_page_number(base_url, typology)
    parts = 10
    pages_per_part = max_pages // parts
    all_data_dict = {}

    for part in range(parts):
        start_page = part * pages_per_part + 1
        end_page = (start_page + pages_per_part) if part < parts - 1 else max_pages + 1

        # Call the scraping function with the current range of pages
        data = func(base_url, typology, search, start_page, end_page - 1)

        # Optional: Delay between parts to respect the server's load
        time.sleep(1)

        # Process the collected data
        removed = remove_duplicates(data)
        # all_data_dict.update(removed)
        save_to_json(removed, page, typology)
        upload_file_s3(bucket_name, aws_access_key, aws_secret_key)

        df = base_dataframe(list(removed.items()))
        df_enhanced = intermediate_dataframe(df)
        save_to_parquet(page, df_enhanced, typology)
        upload_file_s3(bucket_name, aws_access_key, aws_secret_key, "parquet")
    return all_data_dict


def main(page: str):
    configure_logging()
    extract(page)


if __name__ == "__main__":
    pages_to_scrape = ["imovirtual"]
    for pages in pages_to_scrape:
        try:
            logging.info(f"Processing {pages}")
            print(f"Processing {pages}")
            main(pages)
        except Exception as e:
            logging.info(f"Error during processing '{pages}': {e}")
            print(f"Error during processing '{pages}': {e}")
            continue
