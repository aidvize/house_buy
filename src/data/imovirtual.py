from src.utils.utils import (
    load_config,
    performance_metrics,
    save_to_json,
    scrape_imovirtual_listings,
)


@performance_metrics
def imovirtual():
    config = load_config()

    base_url = config["imovirtual"]["base_url"]
    max_pages = config["imovirtual"]["max_pages"]

    titles, links = scrape_imovirtual_listings(base_url, start_page=1, max_pages=max_pages)
    data = {title: link for title, link in zip(titles, links)}
    save_to_json(data)


imovirtual()
