from src.utils import utils
from src.utils.utils import load_config, load_env, performance_metrics, save_to_json, upload_file_s3


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
    config = load_config()
    bucket_name, aws_access_key, aws_secret_key = load_env()

    # Retrieve base URL and maximum number of pages to scrape from the configuration
    base_url = config[page]["base_url"]
    max_pages = config[page]["max_pages"]

    # Construct the function name as a string
    func_name = f"{page}"

    # Look up the function in the utils module's namespace
    func = getattr(utils, func_name, None)

    # Check if the function was found
    if func is None:
        print(f"Function {func_name} not found in utils module.")
        return

    # Scrape data, save to JSON, and upload to S3
    data = func(base_url, max_pages=max_pages)
    save_to_json(data, f"{page}")
    upload_file_s3(bucket_name, aws_access_key, aws_secret_key)


if __name__ == "__main__":
    try:
        main("imovirtual")
    except BaseException as e:
        print(f"Error: {e}")
