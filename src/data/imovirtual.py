from src.utils.utils import save_to_json, scrape_imovirtual_listings

if __name__ == "__main__":
    base_url = "https://www.imovirtual.com/comprar/apartamento"
    titles, links = scrape_imovirtual_listings(base_url, start_page=1, max_pages=10)

    # Convert titles and links into a dictionary
    data = {title: link for title, link in zip(titles, links)}

    # Save the data to the JSON file
    save_to_json(data)
