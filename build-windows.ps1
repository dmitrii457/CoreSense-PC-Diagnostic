param([string]$OutputDirectory = "$PSScriptRoot/dist")

$ErrorActionPreference = 'Stop'
Push-Location $PSScriptRoot
try {
    & '.venv/Scripts/python.exe' -m PyInstaller --noconfirm --windowed --onedir --name CoreSense --distpath $OutputDirectory --collect-data customtkinter --hidden-import sklearn.ensemble._forest --hidden-import sklearn.neural_network._multilayer_perceptron --hidden-import sklearn.pipeline --hidden-import sklearn.preprocessing._data --add-data 'assets;assets' --add-data 'knowledge;knowledge' --add-data 'models;models' --add-data 'reports;reports' CoreSense-launch.py
    if ($LASTEXITCODE -ne 0) { throw "PyInstaller failed with exit code $LASTEXITCODE" }
} finally {
    Pop-Location
}
