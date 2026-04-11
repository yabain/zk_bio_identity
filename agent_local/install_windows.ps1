param(
    [string]$Python = "python",
    [string]$ConfigPath = "config.yaml"
)

Write-Host "Creating virtual environment..."
& $Python -m venv .venv

Write-Host "Activating virtual environment..."
& .\.venv\Scripts\Activate.ps1

Write-Host "Installing dependencies..."
pip install -r requirements.txt

Write-Host "Done. Start the agent with:"
Write-Host ".\.venv\Scripts\Activate.ps1"
Write-Host "python main.py --config $ConfigPath"
