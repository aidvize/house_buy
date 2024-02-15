from src.utils import utils
from src.utils.utils import load_config, performance_metrics, save_to_json


@performance_metrics
def main(page: str):
    config = load_config()

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

    data = func(base_url, max_pages=max_pages)
    save_to_json(data, f"{page}")


if __name__ == "__main__":
    try:
        main("imovirtual")
        main("casa_sapo")
    except BaseException as e:
        print(f"Error: {e}")
