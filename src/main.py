import logging
import sys
from pathlib import Path

from src.utils import utils
from src.utils.utils import (
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
def main(page: str):
    """
    Executes the scraping function based on the specified page, saves the scraped
    data to a JSON file, and uploads the JSON file to an AWS S3 bucket.

    Parameters:
    - page (str): The name of the page or platform to scrape (e.g., 'imovirtual').

    Returns:
    - None
    """
    # Load global configuration and AWS credentials from environment variables
    configure_logging()
    config = load_config()
    bucket_name, aws_access_key, aws_secret_key = load_env()

    # Retrieve base URL and maximum number of pages to scrape from the configuration
    base_url = config["url"][page]
    typology = config["typology"][page]

    # Construct the function name as a string
    func_name = f"{page}"

    # Look up the function in the utils module's namespace
    func = getattr(utils, func_name, None)

    # Check if the function was found
    if func is None:
        print(f"Function {func_name} not found in utils module.")
        return

    # Scrape data, remove duplicates, save to JSON/PARQUET, and upload to S3
    for typ in typology:
        data = func(base_url, typ)
        res = remove_duplicates(data)
        df = base_dataframe(list(res.items()))
        df_enhanced = intermediate_dataframe(df)
        save_to_json(res, f"{page}", typ)
        save_to_parquet(page, df_enhanced)
    upload_file_s3(bucket_name, aws_access_key, aws_secret_key)
    upload_file_s3(bucket_name, aws_access_key, aws_secret_key, "paRQueT")


if __name__ == "__main__":
    pages_to_scrape = ["imovirtual"]
    for pages in pages_to_scrape:
        try:
            main(pages)
        except Exception as e:
            logging.info(f"Error during processing '{pages}': {e}")
            continue
