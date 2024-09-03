$venv = ".\venv" #You can modify this path to customize the venv location

if (-not(Test-Path $venv)) {
    python -m venv $venv
    $init_venv = $true
}

& $venv\Scripts\activate

if ($init_venv) {
    python -m pip install --upgrade pip
    python -m pip install -r .\requirements.txt
}

python .\__init__.py