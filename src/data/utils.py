import json
import time
from datetime import date
from pathlib import Path

import requests
from bs4 import BeautifulSoup


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
