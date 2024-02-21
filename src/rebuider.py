import logging
import sys
from pathlib import Path

from utils import utils
from utils.utils import (
    base_dataframe,
    configure_logging,
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
    typology = config["typology"][page][2]
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
    (
        config,
        bucket_name,
        aws_access_key,
        aws_secret_key,
        base_url,
        search,
        typology,
    ) = cred_parameters(page)
    func_name = page
    func = getattr(utils, func_name, None)

    if func is None:
        logging.info(f"Function {func_name} not found in utils module.")

    data = func(base_url, typology, search)
    removed = remove_duplicates(data)
    save_to_json(removed, page, typology)
    upload_file_s3(bucket_name, aws_access_key, aws_secret_key)
    return removed


@performance_metrics
def transform(page: str, res: dict) -> None:
    """
    Executes the scraping function based on the specified page, saves the scraped
    data to a JSON file, and uploads the JSON file to an AWS S3 bucket.

    Parameters:
    - page (str): The name of the page or platform to scrape (e.g., 'imovirtual').

    Returns:
    - None
    """
    (
        config,
        bucket_name,
        aws_access_key,
        aws_secret_key,
        base_url,
        search,
        typology,
    ) = cred_parameters(page)
    df = base_dataframe(list(res.items()))
    df_enhanced = intermediate_dataframe(df)
    save_to_parquet(page, df_enhanced, typology)
    upload_file_s3(bucket_name, aws_access_key, aws_secret_key, "parquet")


def main(page: str):
    configure_logging()
    (
        config,
        bucket_name,
        aws_access_key,
        aws_secret_key,
        base_url,
        search,
        typology,
    ) = cred_parameters(page)

    extracted = extract(page)
    transform(page, extracted)


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
