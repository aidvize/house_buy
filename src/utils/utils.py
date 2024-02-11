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


def load_config(
    config_path=".github/workflows/config_template.yaml",
):
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


def make_request(url, headers):
    """
    Performs an HTTP GET request to the specified URL using the provided headers.

    Parameters:
        - url (str): The URL to which the GET request is made.
        - headers (dict): The headers to include in the request.

    Returns:
        requests.Response: The response object from the request if successful, otherwise None.
    """
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raises an exception for 4XX or 5XX errors
        return response
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return None


def parse_html(html_content):
    """
    Parses the given HTML content string using BeautifulSoup.

    Parameters:
        - html_content (str): The HTML content to parse.

    Returns:
        BeautifulSoup: The BeautifulSoup object parsed from the HTML content.
    """
    return BeautifulSoup(html_content, "html.parser")


def extract_listing_data(soup):
    """
    Extracts and returns the listing data such as titles and links from the parsed HTML.

    Parameters:
        - soup (BeautifulSoup): The BeautifulSoup object containing the parsed HTML data.

    Returns:
        tuple: A tuple containing two lists (titles, links), or (None, None) if no data.
    """
    titles = []
    links = []

    span_tags = soup.find_all("span", class_="offer-item-title")
    if not span_tags:
        return None, None  # Indicates no more data to scrape

    for span_tag in span_tags:
        titles.append(span_tag.text.strip())
        a_tag = span_tag.find_parent("a")
        if a_tag and a_tag.has_attr("href"):
            links.append(a_tag["href"])

    return titles, links


def scrape_imovirtual_listings(base_url, start_page=1, max_pages=10):
    """
    Scrapes property listings from a given URL, iterating through a defined number of pages.

    Parameters:
        - base_url (str): The base URL to start scraping from.
        - start_page (int): The starting page number for scraping.
        - max_pages (int): The maximum number of pages to scrape.

    Returns:
        tuple: Two lists containing the titles and links of the listings extracted.
    """
    headers = get_headers()
    titles = []
    links = []

    for num in range(start_page, start_page + max_pages):
        url = f"{base_url}?page={num}"
        response = make_request(url, headers)

        if response:
            soup = parse_html(response.text)
            page_titles, page_links = extract_listing_data(soup)

            if page_titles is None:  # No more listings found
                print(f"No more results found at page {num}. Stopping.")
                break

            titles.extend(page_titles)
            links.extend(page_links)

            time.sleep(1)  # Respectful delay between requests

    return titles, links


def save_to_json(data):
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
    file_path = Path(f"raw/scraped_data_{today}.json")

    # Create the target directory if it doesn't exist
    file_path.parent.mkdir(parents=True, exist_ok=True)

    # Attempt to save the data to the specified file
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        print(f"Data successfully saved to {file_path}")
    except Exception as e:
        print(f"Error saving data to JSON: {e}")
