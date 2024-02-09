# Define project-specific variables
$repo_name = "house_buy"
$repo_path = Get-Location

$conda_folder_prefix = "$env:USERPROFILE\.conda\envs\$repo_name"
$python_path = "$conda_folder_prefix\python.exe"

# Create a Conda environment
Function SetupEnv {
    conda create -n $repo_name python=3.10 -y
    conda activate $repo_name
    conda develop $env:CONDA_PREFIX
}

# Install project requirements
Function InstallRequirements {
    conda activate $repo_name
    pip install -r requirements.txt
    pre-commit install
}

# Setup environment
if (-Not (Test-Path $conda_folder_prefix)) {
    SetupEnv
}

InstallRequirements

Write-Output "Setup completed."
