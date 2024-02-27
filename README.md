# "House Buy" Project Development Setup Guide

Welcome to the **House Buy** project! This guide will walk you through setting up your development environment, outline our commit message conventions, and explain how to use our configuration files to maintain code quality and consistency.

## **Project Structure Overview**

Our project leverages several configuration files and scripts to streamline the development process and ensure code quality:

- **`.pre-commit-config.yaml`**: Configures pre-commit hooks to enforce code standards before commits are made.
- **`dev_setup.bat` (Windows)** and **`dev_setup.sh` (Unix-like)**: Scripts to automate the setup of the development environment, including the creation and activation of a Conda environment, and installation of project dependencies.
- **`pyproject.toml`**: Contains configurations for Python tools such as `black` for code formatting and `isort` for import sorting.
- **`requirements.txt`**: Lists all Python package dependencies necessary for the project.

## **Setting Up Your Development Environment**

### Unix-like Systems (macOS/Linux)

1. **Prepare Script**: Ensure `dev_setup.sh` is executable.
   
   ```bash
   chmod +x dev_setup.sh
   ```
   
2. **Execute Script**: Run `dev_setup.sh` to set up your Conda environment.
   
   ```bash
   ./dev_setup.sh
   ```

### Common Steps

Both setup scripts will:
- Create and activate a Conda environment specific to this project.
- Install Python dependencies listed in `requirements.txt`.
- Install and configure pre-commit hooks as specified in `.pre-commit-config.yaml`.

## **Pre-commit Configuration**

Our project uses pre-commit hooks to ensure that code commits meet our standards for code quality and style.

- **Installation**: If you haven't already, install pre-commit globally using pip.
  
  ```bash
  pip install pre-commit
  ```

- **Activation**: In the project root directory, activate pre-commit hooks with:
  
  ```bash
  pre-commit install
  ```

## **Commit Message Guidelines**

To maintain clarity and consistency in our project history, we follow a specific pattern for commit messages:

```
[type] - message
```

- **`[type]`**: Indicates the nature of the change. Use `fix` for bug fixes and `feat` for new features.
- **`message`**: A concise description of what was changed.

### Examples

- `[fix] - correct typo in README`
- `[feat] - add login functionality`

## **Python Tools Configuration**

The `pyproject.toml` file is used to configure Python tools for code formatting and import sorting:

- **Black**: Formats your code in compliance with PEP 8.
  
  To run Black, use:
  
  ```bash
  black .
  ```

- **isort**: Sorts your imports alphabetically, and automatically separates them into sections.
  
  To run isort, use:
  
  ```bash
  isort .
  ```

  - **flake8**: Verify unused imports and variables.
  
  To run flake8, use:
  
  ```bash
  flake8
  ```

Make sure these commands are run within the project's root directory and your Conda environment is activated.

By adhering to these setup instructions and guidelines, you'll be contributing to the consistency and quality of the **House Buy** project's codebase. Happy coding!
