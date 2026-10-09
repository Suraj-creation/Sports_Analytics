#!/bin/bash
set -e

# 1. Create a virtual environment
python3 -m venv vjepa_env

# 2. Activate it
source vjepa_env/bin/activate

# 3. Upgrade pip
pip install --upgrade pip

# 4. Install everything except torch/torchvision (those need a CUDA-specific build)
pip install -r requirements.txt

echo
echo "============================================================"
echo " Base packages installed."
echo " Now install torch+torchvision matching YOUR GPU driver:"
echo
echo " 1. Run: nvidia-smi"
echo " 2. Look at 'CUDA Version: X.Y' in the top right"
echo " 3. Go to https://pytorch.org/get-started/locally/ and pick"
echo "    the matching CUDA version, then run the install command"
echo "    it gives you, e.g.:"
echo "      pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121"
echo "============================================================"
