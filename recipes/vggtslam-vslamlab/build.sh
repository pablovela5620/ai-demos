set -e

# 1. Install Python dependencies
#echo "Installing base requirements..."
#pip3 install -r requirements.txt

# 2. Clone and install Salad
echo "Cloning and installing Salad..."
git clone https://github.com/Dominic101/salad.git
pip install ./salad --no-deps --no-build-isolation

# 3. Clone and install RAFT, RAFT is not used for optical flow by default
# echo "Cloning and installing RAFT..."
# git clone https://github.com/<omitted>/RAFT.git
# pip install -e ./RAFT
# cd RAFT
# echo "Downloading RAFT models..."
# ./download_models.sh
# cd ..

# 4. Clone and install VGGT
echo "Cloning and installing VGGT..."
#git clone https://github.com/facebookresearch/vggt.git
git clone https://github.com/VSLAM-LAB/vggt-VSLAM-LAB.git vggt
pip install ./vggt --no-deps --no-build-isolation

# 5. Install current repo in editable mode
echo "Installing current repo..."
pip install .  --no-deps --no-build-isolation

echo "Installation Complete"

