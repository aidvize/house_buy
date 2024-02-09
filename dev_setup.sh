#!/bin/bash

# Define project-specific variables
repo_name="house_buy"
repo_path=$(pwd)

# Initialize Conda in your script
# Make sure this path points to your actual 'conda.sh' location
# This might vary depending on where Anaconda/Miniconda is installed
source ~/miniconda3/etc/profile.d/conda.sh || source ~/anaconda3/etc/profile.d/conda.sh

# Create and activate a Conda environment
setup_env() {
    conda create -n "$repo_name" python=3.10 -y
    conda activate "$repo_name"
    # The 'conda develop' command is used for developing Python packages, not for general environment setup
    # If you're trying to make your current directory (or any other) importable, consider using 'pip install -e .'
    # or adjusting PYTHONPATH instead. Commenting out the following line:
    # conda develop "$CONDA_PREFIX"
}

# Install project requirements
install_requirements() {
    conda activate "$repo_name"
    # Assuming 'requirements.txt' is at the root of your repository
    pip install -r "$repo_path/requirements.txt"
    pre-commit install
}

# Check if the Conda environment exists by trying to activate it
if ! conda activate "$repo_name" &> /dev/null; then
    setup_env
else
    echo "Environment '$repo_name' already exists, activating it."
    conda activate "$repo_name"
fi

install_requirements

echo "Setup completed."
