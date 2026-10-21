@echo off
REM 1. Create a virtual environment
python -m venv vjepa_env

REM 2. Activate it
call vjepa_env\Scripts\activate.bat

REM 3. Upgrade pip
python -m pip install --upgrade pip

REM 4. Install everything except torch/torchvision (those need a CUDA-specific build)
pip install -r requirements.txt

echo.
echo ============================================================
echo  Base packages installed.
echo  Now install torch+torchvision matching YOUR GPU driver:
echo.
echo  1. Run: nvidia-smi
echo  2. Look at "CUDA Version: X.Y" in the top right
echo  3. Go to https://pytorch.org/get-started/locally/ and pick
echo     the matching CUDA version, then run the install command
echo     it gives you, e.g.:
echo       pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121
echo ============================================================
