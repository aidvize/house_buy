import functools
import json
import logging
import os
import time
from datetime import datetime
from logging.handlers import RotatingFileHandler
from pathlib import Path

import boto3
import pandas as pd
import psutil
import requests
import yaml
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from memory_profiler import memory_usage


def configure_logging(log_file_path="logs/logfile.log"):
    """
    Configures the logging for the application,
    directing logs to both a rotating file and standard output.

    Parameters:
    - log_file_path (str): Relative path from the project root to the log file.
    Defaults to "logs/logfile.log".
    """
    # Get the absolute path of the directory where this script is located
    current_script_path = Path(__file__).resolve()
    project_root = current_script_path.parent.parent  # Adjust based on actual structure

    # Construct an absolute path to the log file
    absolute_log_file_path = project_root / log_file_path

    # Ensure the log directory exists
    absolute_log_file_path.parent.mkdir(parents=True, exist_ok=True)

    logging.basicConfig(
        level=logging.INFO,  # Adjust as needed
        format="%(asctime)s %(levelname)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[
            RotatingFileHandler(
                absolute_log_file_path, maxBytes=10485760, backupCount=5
            ),  # 10MB file size
            logging.StreamHandler(),  # Also log to stderr
        ],
    )


def performance_metrics(func) -> callable:
    """
    A decorator that measures and prints the performance metrics of the decorated function,
    and saves these metrics to a JSON file in the 'metrics' folder.

    Parameters:
    - func (Callable): The function to measure. It can accept any number of positional
      and keyword arguments.

    Returns:
    - Callable: A wrapper function that, when called, executes the decorated function,
      measures its performance, prints and saves its metrics, and returns the function's result.
    """

    @functools.wraps(func)
    def wrapper_performance_metrics(*args, **kwargs):
        # Record the start time and CPU times
        start_time = time.time()
        start_cpu = psutil.cpu_percent(interval=None)

        # Record memory usage before execution
        mem_before = memory_usage(-1, interval=0.1, timeout=1)

        # Execute the function
        result = func(*args, **kwargs)

        # Record the end time, CPU times, and memory usage after execution
        end_time = time.time()
        end_cpu = psutil.cpu_percent(interval=None)
        mem_after = memory_usage(-1, interval=0.1, timeout=1)

        # Calculate metrics
        elapsed_time = end_time - start_time
        cpu_usage = end_cpu - start_cpu
        memory_used = max(mem_after) - min(mem_before)

        # Prepare the metrics dictionary
        metrics = {
            "file_executed": func.__name__,
            "date_executed": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "elapsed_time_seconds": elapsed_time,
            "cpu_percent_usage": cpu_usage,
            "memory_usage_mb": memory_used,
        }

        # Define the filename for the metrics JSON file
        metrics_file_path = Path(
            f"data/metrics/{func.__name__}_metrics_{datetime.now().strftime('%Y%m%d%H%M%S')}.json"
        )

        # Create the 'metrics' directory if it doesn't exist
        metrics_file_path.parent.mkdir(parents=True, exist_ok=True)

        # Save metrics to the JSON file
        with metrics_file_path.open("w", encoding="utf-8") as f:
            json.dump(metrics, f, ensure_ascii=False, indent=4)

        return result

    return wrapper_performance_metrics


def load_config(filename="parameters.yaml"):
    """
    Dynamically load the YAML configuration file located in the 'conf' directory,
    relative to this script's location.

    Parameters:
    - filename (str, optional): Name of the YAML configuration file. Defaults to "parameters.yaml".

    Returns:
    - dict: The configuration parameters loaded from the YAML file.
    """
    # Get project root
    project_root = Path(__file__).resolve().parents[2]

    # Find all instances of the configuration file within the project directory
    config_files = list(project_root.glob(f"**/{filename}"))

    if not config_files:
        logging.info(f"No configuration file named '{filename}' found in the project.")
        return None

    # If multiple configuration files are found, you might want to select one based on some criteria
    # Here, we simply take the first one found
    config_path = config_files[0]

    with open(config_path, "r", encoding="utf-8") as file:
        return yaml.safe_load(file)


def load_env() -> tuple:
    """
    Load the .ENV configuration file.

    Parameters:
    - env_path (str): Path to the .env configuration file.

    Returns:
    - bucket (str): Bucket name
    - access_key (str): AWS Access Key
    - access_key (str): AWS Secret Key
    """
    # Load environment variables from .env file
    load_dotenv()

    # Retrieve the environment variables
    bucket_name = os.getenv("BUCKET")
    aws_access_key = os.getenv("AWS_ACCESS_KEY_ID")
    aws_secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")

    return bucket_name, aws_access_key, aws_secret_key


def get_headers() -> dict:
    """
    Creates and returns headers to mimic a web browser for HTTP requests.

    Returns:
        dict: Headers with a User-Agent key to mimic a web browser.
    """
    return {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36"
    }


def find_element_after_sequence(values: list, seq: list):
    """
    Find the max page number per typology

    Parameters:
    - values (list): List of values extracted from li tag.
    - seq (list): sequence to search for.

    Returns:
        int: number of pages.
    """
    # Find the start of the sequence
    for i in range(len(values) - len(seq)):
        # If the sequence matches
        if values[i : i + len(seq)] == seq:
            # Check if there is an element after the sequence
            if i + len(seq) < len(values):
                return int(values[i + len(seq)])
    return None  # Return None if the sequence is not found or there is no element after


def get_page_number(url: str, typology: int) -> int:
    """
    Get the max page number per typology.

    Parameters:
    - url (str): The base URL to scrape.
    - typology (str): The typology to scrape.

    Returns:
    - int: The number of the page for each typology.
    """
    values = []
    full_url = f"{url}{typology}/?page=1"

    response = requests.get(full_url, headers=get_headers())
    soup = BeautifulSoup(response.text, "html.parser")
    li_tags = soup.find_all("li", class_="")

    if not li_tags:
        logging.info(f"No results found at {full_url}. Stopping.")

    for span_tag in li_tags:
        values.append(span_tag.text.strip())

    # Define the sequence to search for
    sequence = ["1", "2", "3"]

    max_pages = find_element_after_sequence(values, sequence)
    return max_pages


def imovirtual(url: str, typology: int) -> dict:
    """
    Scrapes listing titles and links from Imovirtual website until no more listings are found.

    Parameters:
    - url (str): The base URL to scrape.
    - typology (str): The typology to scrape.

    Returns:
    - dict: A dictionary with listing titles as keys and corresponding links.
    """
    title = []
    links = []
    max_pages = get_page_number(url, typology)

    for num in range(1, max_pages + 1):
        try:
            page = requests.get(f"{url}{typology}/?page={num}", headers=get_headers())
            soup = BeautifulSoup(page.text, "html.parser")
            span_tags = soup.find_all("span", class_="offer-item-title")

            if not span_tags:
                logging.info(f"No results found at page {num}. Stopping.")
                break  # Exit the loop if no listings are found or if the same listings are repeated

            for span_tag in span_tags:
                title.append(span_tag.text.strip())
                a_tag = span_tag.find_parent("a")
                if a_tag and a_tag.has_attr("href"):
                    links.append(a_tag["href"])

            time.sleep(1)  # Respectful delay between requests
            print(
                f"Page {num} of {max_pages} processed for {typology}",
                f"{round((num / max_pages), 4) * 100}% remains",
            )

        except requests.exceptions.RequestException as e:
            logging.error(f"Request failed: {e}")
            pass

    data = {title: link for title, link in zip(title, links)}
    return data


def get_json():
    # Get project root and construct path to the raw data directory
    project_root = Path(__file__).resolve().parents[2]
    raw_data_dir = project_root / "src" / "data" / "raw"

    # Check if the directory exists and list all JSON files
    if raw_data_dir.exists():
        return list(raw_data_dir.glob("*.json"))
    else:
        return None


def read_json(json_file: str) -> list:
    """
    Read json data and convert into list

    Parameters:
    - json_file (str): Json filename.

    Returns:
    - data (list): json converted
    """
    # Opening JSON file
    f = open(f"{json_file}")

    # returns JSON object as a dictionary
    data = json.load(f)

    # convert into list
    data = list(data.items())

    return data


def get_details(url: str, tag: str, class_name: str):
    """
    Scrapes listing and get all details of each property.

    Parameters:
    - url (str): The base URL to scrape.
    - tag (str): The typology to scrape.
    - tag (str): The typology to scrape.

    Returns:
    - dict: A dictionary with listing titles as keys and corresponding links.
    """
    page = requests.get(url, headers=get_headers())
    soup = BeautifulSoup(page.content, "html.parser")
    return [element.text.strip() for element in soup.find_all(tag, class_=class_name)]


def create_dataframe(json_file: str, full_address: list, prices: list, prices_m2: list):
    """
    Create a base DataFrame for the whole process

    Parameters:
    - full_address (list): List that contain full address.
    - prices (list): List that contain prices.
    - prices_m2 (list): List that contain prices per m2.

    Returns:
    - df (dataframe): The base dataframe
    """
    # Create a base DataFrame
    df = pd.DataFrame(read_json(json_file), columns=["title", "url"])
    df["full_address"], df["prices"], df["prices_m2"] = full_address, prices, prices_m2
    return df


def remove_duplicates(data: dict) -> dict:
    """
    Remove duplicate records in the dict

    Parameters:
    - data (dict): The data to save, with titles as keys and links as values.
    """
    temp = {val: key for key, val in data.items()}
    res = {val: key for key, val in temp.items()}
    return res


def save_to_json(data: dict, page: str, typology: str, dest: str = "data/raw/") -> None:
    """
    Saves the given data to a JSON file. If the target directory doesn't exist,
    it will be created.

    Parameters:
    - data (dict): The data to save, with titles as keys and links as values.
    - page (str): The path to the JSON file where the data will be saved.
    - typology (str): The typology to scrape, formatted to include pagination.
    - dest (str): The destination folder where data will be added.
    """
    # Ensure file_path is a Path object
    file_path = Path(f"{dest}{page}_{typology}_{datetime.now().strftime('%Y%m%d%H%M%S')}.json")
    # Create the target directory if it doesn't exist
    file_path.parent.mkdir(parents=True, exist_ok=True)

    # Attempt to save the data to the specified file
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
    except Exception as e:
        logging.error(f"Error saving data to JSON: {e}")


def upload_file_s3(bucket_name: str, access_key: str, secret_key: str, dest: str = "raw/") -> None:
    """
    Uploads all JSON files in the src/data/raw directory to an AWS S3 bucket.

    Parameters:
    - bucket_name (str): The name of the AWS S3 bucket.
    - access_key (str): The AWS access key.
    - secret_key (str): The AWS secret access key.
    - dest (str): The destination folder where data will be added.
    """
    s3 = boto3.client("s3", aws_access_key_id=access_key, aws_secret_access_key=secret_key)

    json_files = get_json()

    # Upload each file to S3
    for json_file in json_files:
        file_key = f"{dest}{json_file.name}"
        try:
            s3.upload_file(str(json_file), bucket_name, file_key)
        except Exception as e:
            logging.error(f"Failed to upload {json_file.name}: {e}")
