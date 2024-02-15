import functools
import json
import time
from datetime import date, datetime
from pathlib import Path

import psutil
import requests
import yaml
from bs4 import BeautifulSoup
from memory_profiler import memory_usage


def performance_metrics(func):
    """
    A decorator that measures and prints the performance metrics of the decorated function,
    and saves these metrics to a JSON file in the 'metrics' folder.
    Metrics include elapsed time, CPU usage, and memory usage during the function's execution.

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
            f"metrics/{func.__name__}_metrics_{datetime.now().strftime('%Y%m%d%H%M%S')}.json"
        )

        # Create the 'metrics' directory if it doesn't exist
        metrics_file_path.parent.mkdir(parents=True, exist_ok=True)

        # Save metrics to the JSON file
        with metrics_file_path.open("w", encoding="utf-8") as f:
            json.dump(metrics, f, ensure_ascii=False, indent=4)

        return result

    return wrapper_performance_metrics


def load_config(config_path=".github/workflows/parameters.yaml"):
    """
    Load the YAML configuration file.

    Parameters:
    - config_path (str): Path to the YAML configuration file.

    Returns:
    - dict: The configuration parameters.
    """
    with open(config_path, "r") as file:
        return yaml.safe_load(file)


def get_headers():
    """
    Creates and returns headers to mimic a web browser for HTTP requests.

    Returns:
        dict: Headers with a User-Agent key to mimic a web browser.
    """
    return {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36"
    }


def imovirtual(url: str, max_pages: int) -> dict:
    """
    Scrapes listing titles and links from Imovirtual website for a specified number of pages.

    This function navigates through the specified number of pages on the Casa Sapo website,
    collecting titles and corresponding links for property listings. It applies a respectful
    delay between requests to avoid overloading the server. If no more listings are found on
    a page, the scraping stops early. Encountered errors during requests are caught and logged.

    Parameters:
    - url (str): The base URL to scrape, formatted to include pagination.
    - max_pages (int): The maximum number of pages to scrape.

    Returns:
    - dict: A dictionary with listing titles as keys and corresponding links
    """
    title = []
    links = []

    for num in range(1, max_pages + 1):
        try:
            page = requests.get(f"{url}{num}", headers=get_headers())
            soup = BeautifulSoup(page.text, "html.parser")

            span_tags = soup.find_all("span", class_="offer-item-title")

            # Dynamic stop condition: No listings found on page
            if not span_tags:
                break

            for span_tag in span_tags:
                title.append(span_tag.text.strip())
                a_tag = span_tag.find_parent("a")
                if a_tag and a_tag.has_attr("href"):
                    links.append(a_tag["href"])

            time.sleep(1)  # Respectful delay between requests

        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
            break
    data = {title: link for title, link in zip(title, links)}
    return data


def casa_sapo(url: str, max_pages: int) -> dict:
    """
    Scrapes listing titles and links from Casa Sapo website for a specified number of pages.

    This function navigates through the specified number of pages on the Casa Sapo website,
    collecting titles and corresponding links for property listings. It applies a respectful
    delay between requests to avoid overloading the server. If no more listings are found on
    a page, the scraping stops early. Encountered errors during requests are caught and logged.

    Parameters:
    - url (str): The base URL to scrape, formatted to include pagination.
    - max_pages (int): The maximum number of pages to scrape.

    Returns:
    - dict: A dictionary with listing titles as keys and corresponding links
    """
    title = []
    links = []

    for num in range(1, max_pages + 1):
        try:
            page = requests.get(f"{url}{num}", headers=get_headers())
            soup = BeautifulSoup(page.text, "html.parser")

            span_tags = soup.find_all("div", class_="property-type")

            # Dynamic stop condition: No listings found on page
            if not span_tags:
                break

            for span_tag in span_tags:
                title.append(span_tag.text.strip())
                a_tag = span_tag.find_parent("a")
                if a_tag and a_tag.has_attr("href"):
                    links.append(a_tag["href"][112:])

            time.sleep(1)  # Respectful delay between requests

        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
            break
    data = {title: link for title, link in zip(title, links)}
    return data


def save_to_json(data: dict, page: str):
    """
    Saves the given data to a JSON file. If the target directory doesn't exist,
    it will be created.

    Parameters:
    - data (dict): The data to save, with titles as keys and links as values.
    - file_path (str or Path): The path to the JSON file where the data will be saved.
    """
    # get today
    today = date.today()

    # Ensure file_path is a Path object
    file_path = Path(f"data/raw/{page}_{today}.json")
    # Create the target directory if it doesn't exist
    file_path.parent.mkdir(parents=True, exist_ok=True)

    # Attempt to save the data to the specified file
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
    except Exception as e:
        print(f"Error saving data to JSON: {e}")
